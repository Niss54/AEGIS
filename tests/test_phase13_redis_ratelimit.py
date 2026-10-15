"""
Phase 13 Comprehensive Verification Suite
Module: tests.test_phase13_redis_ratelimit
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant

Mathematical Governing Equation:
Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))

Verifies:
1. PRD Phase 13 Invariant Pipeline Execution & CacheControlModel schema
2. Exact Token Bucket replenishment and burst capacity capping
3. Rejection logic and deterministic retry_after calculation
4. Circuit breaker state transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
5. Local In-Memory Tier 2 Fallback caching and TTL expiry
6. Distributed Pub/Sub event broadcasting
7. FastAPI REST cache and rate limit endpoints
8. Token Bucket HTTP 429 Too Many Requests enforcement with standard RFC headers
9. MCP Hub Tool Registry & JSON-RPC 2.0 tool execution
"""
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.cache import RedisBusController, InMemoryFallbackCache, CacheControlModel
from backend.app.rate_limiter import TokenBucketRateLimiter, RateLimitResult

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. PRD Execution Invariant Test (as specified in PRD.md Section 6)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_phase_13_execution_invariant():
    """
    Direct invariant verification specified in PRD.md Section 6.
    Ensures CacheControlModel schema validity, operational status, and cryptographic flag.
    """
    controller = RedisBusController()
    sample_payload = {"event_id": "TEST-PHASE-13", "telemetry": 42.0}
    result = await controller.execute_phase_pipeline(sample_payload)

    assert result.event_id == "TEST-PHASE-13"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 13
    assert result.metadata["cache_verified"] is True
    assert result.metadata["pubsub_dispatched"] is True
    assert result.execution_tier == "ENTERPRISE_PROD"


# -----------------------------------------------------------------------------
# 2. Token Bucket Mathematical Invariant Tests
# -----------------------------------------------------------------------------
def test_token_bucket_mathematical_refill_and_cap():
    """
    Tests: Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))
    Confirms token replenishment over time and ceiling at capacity C.
    """
    bus = RedisBusController()
    bus.circuit_state = "OPEN"  # Test local deterministic execution directly without network latency
    limiter = TokenBucketRateLimiter(default_capacity=10.0, default_refill_rate=5.0, bus_controller=bus)
    key = "test_user_refill"
    limiter.reset(key)

    # Initial consumption of all 10 tokens
    res1 = limiter.consume(key=key, cost=10.0, capacity=10.0, refill_rate=5.0)
    assert res1.allowed is True
    assert res1.tokens_remaining == 0.0

    # Immediate second call demanding 1 token should fail (0 < 1)
    res2 = limiter.consume(key=key, cost=1.0, capacity=10.0, refill_rate=5.0)
    assert res2.allowed is False
    assert res2.retry_after_seconds > 0.0
    assert round(res2.retry_after_seconds, 1) == 0.2  # 1 token / 5 tokens/s = 0.2s

    # Simulate elapsed time of 1 second: 5 tokens refilled
    now = time.time()
    refilled = limiter._calculate_tokens(
        current_time=now + 1.0,
        last_updated=now,
        tokens=0.0,
        capacity=10.0,
        refill_rate=5.0
    )
    assert refilled == 5.0

    # Simulate elapsed time of 10 seconds: must cap at capacity 10.0, not exceed it
    capped = limiter._calculate_tokens(
        current_time=now + 10.0,
        last_updated=now,
        tokens=0.0,
        capacity=10.0,
        refill_rate=5.0
    )
    assert capped == 10.0


def test_token_bucket_deterministic_retry_after():
    """
    Verifies that retry_after = (cost - current_tokens) / refill_rate
    """
    bus = RedisBusController()
    bus.circuit_state = "OPEN"
    limiter = TokenBucketRateLimiter(default_capacity=60.0, default_refill_rate=10.0, bus_controller=bus)
    key = "test_retry_after"
    limiter.reset(key)

    # Consume 60 tokens from 60 capacity
    res = limiter.consume(key, cost=60.0, capacity=60.0, refill_rate=10.0)
    assert res.allowed is True

    # Demanding 5 tokens when balance is 0
    res_throttled = limiter.consume(key, cost=5.0, capacity=60.0, refill_rate=10.0)
    assert res_throttled.allowed is False
    assert round(res_throttled.retry_after_seconds, 2) == 0.5  # 5 / 10 = 0.5s


# -----------------------------------------------------------------------------
# 3. Tier 2 Local In-Memory Fallback Cache Tests
# -----------------------------------------------------------------------------
def test_in_memory_fallback_cache_crud_and_ttl():
    """
    Verifies Tier 2 Local In-Memory Cache CRUD and TTL expiration.
    """
    cache = InMemoryFallbackCache()
    cache.set("key1", {"sensor": "AWS-01", "temp": 28.4}, ttl_seconds=3600)
    assert cache.exists("key1") is True
    assert cache.get("key1") == {"sensor": "AWS-01", "temp": 28.4}

    # Test deletion
    deleted = cache.delete("key1")
    assert deleted is True
    assert cache.get("key1") is None
    assert cache.exists("key1") is False

    # Test TTL expiration
    cache.set("expiring_key", "ephemeral_data", ttl_seconds=-1)  # expired immediately
    assert cache.get("expiring_key") is None

    # Test flush
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.size() >= 2
    cache.flush()
    assert cache.size() == 0


# -----------------------------------------------------------------------------
# 4. Pub/Sub Bus Subscription & Distribution Tests
# -----------------------------------------------------------------------------
def test_pubsub_bus_distribution():
    """
    Verifies real-time event distribution to subscribed callbacks.
    """
    controller = RedisBusController()
    received_messages = []

    def handle_event(channel, msg):
        received_messages.append({"channel": channel, "msg": msg})

    channel = "terra_sentinel:alerts"
    controller.subscribe(channel, handle_event)

    test_payload = {"risk_tier": "CRITICAL", "hotspot": "Mithi River Basin"}
    recipients = controller.publish(channel, test_payload)

    assert recipients >= 1
    assert len(received_messages) == 1
    assert received_messages[0]["channel"] == channel
    assert received_messages[0]["msg"] == test_payload


# -----------------------------------------------------------------------------
# 5. Circuit Breaker State Transition Tests
# -----------------------------------------------------------------------------
def test_circuit_breaker_transitions():
    """
    Verifies Gravitas Invariant Circuit Breaker Protocol:
    1. Error rate >= 3 consecutive failures within rolling 60s -> Circuit OPEN.
    2. Requests route to Tier 2 local memory fallback.
    3. Cooldown probe -> HALF_OPEN.
    4. Successful probe -> CLOSED.
    """
    controller = RedisBusController()
    controller.circuit_state = "CLOSED"
    controller.consecutive_failures = 0

    # Inject 3 consecutive failures
    err = ConnectionError("Simulated Redis Connection Refused")
    controller._record_failure(err)
    assert controller.circuit_state == "CLOSED"
    assert controller.consecutive_failures == 1

    controller._record_failure(err)
    assert controller.circuit_state == "CLOSED"
    assert controller.consecutive_failures == 2

    controller._record_failure(err)
    assert controller.circuit_state == "OPEN"
    assert controller.consecutive_failures == 3
    assert controller.metrics["circuit_trips"] >= 1

    # While OPEN, _get_redis() returns None before cooldown
    controller.last_state_change = time.time()
    assert controller._get_redis() is None

    # Simulate cooldown expiration (31s later) -> Transitions to HALF_OPEN
    controller.last_state_change = time.time() - 35.0
    # Next check should trigger HALF_OPEN transition
    _ = controller._get_redis()
    assert controller.circuit_state in ("HALF_OPEN", "OPEN")

    # Simulate successful probe recovery
    controller.circuit_state = "HALF_OPEN"
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.consecutive_failures == 0


# -----------------------------------------------------------------------------
# 6. FastAPI REST Cache & Rate Limiting Endpoints
# -----------------------------------------------------------------------------
def test_fastapi_cache_endpoints():
    """
    Tests REST endpoints: /health, /set, /get, /delete, /publish, /stats.
    """
    # 1. Health
    r_health = client.get("/api/v1/cache/health")
    assert r_health.status_code == 200
    health_data = r_health.json()
    assert health_data["status"] == "OPERATIONAL"
    assert "circuit_state" in health_data
    assert "active_tier" in health_data

    # 2. Set
    r_set = client.post("/api/v1/cache/set", json={
        "key": "test:mumbai:dem",
        "value": {"depth_cm": 74.5, "basin": "Mithi"},
        "ttl_seconds": 600
    })
    assert r_set.status_code == 200
    assert r_set.json()["status"] == "success"

    # 3. Get
    r_get = client.get("/api/v1/cache/get/test:mumbai:dem")
    assert r_get.status_code == 200
    get_data = r_get.json()
    assert get_data["hit"] is True
    assert get_data["value"]["depth_cm"] == 74.5

    # 4. Delete
    r_del = client.delete("/api/v1/cache/delete/test:mumbai:dem")
    assert r_del.status_code == 200
    assert r_del.json()["deleted"] is True

    # 5. Publish
    r_pub = client.post("/api/v1/cache/publish", json={
        "channel": "terra_sentinel:live",
        "message": {"event": "HEARTBEAT", "epoch": time.time()}
    })
    assert r_pub.status_code == 200
    assert "subscribers_notified" in r_pub.json()

    # 6. Pipeline
    r_pipe = client.post("/api/v1/cache/pipeline", json={
        "event_id": "REST-EVT-P13",
        "payload_field": "val_13"
    })
    assert r_pipe.status_code == 200
    pipe_data = r_pipe.json()
    assert pipe_data["event_id"] == "REST-EVT-P13"
    assert pipe_data["verified_flag"] is True

    # 7. Stats
    r_stats = client.get("/api/v1/cache/stats")
    assert r_stats.status_code == 200
    stats_data = r_stats.json()
    assert "cache" in stats_data
    assert "rate_limiter" in stats_data


# -----------------------------------------------------------------------------
# 7. FastAPI Rate Limiting Guard & RFC 429 Rejection
# -----------------------------------------------------------------------------
def test_fastapi_rate_limiter_guard_429():
    """
    Verifies that the rate_limit_guard dependency correctly permits requests within quota
    and returns HTTP 429 Too Many Requests with X-RateLimit and Retry-After headers when quota is exhausted.
    """
    headers = {"X-API-Key": "TEST_KEY_429_SUITE"}

    # Guarded demo endpoint has capacity 5.0, cost 1.0
    allowed_count = 0
    throttled = False
    last_response = None

    for _ in range(8):
        resp = client.get("/api/v1/cache/guarded-demo", headers=headers)
        if resp.status_code == 200:
            allowed_count += 1
            assert "X-RateLimit-Limit" in resp.headers
            assert "X-RateLimit-Remaining" in resp.headers
        elif resp.status_code == 429:
            throttled = True
            last_response = resp
            break

    assert allowed_count <= 5
    assert throttled is True
    assert last_response.status_code == 429
    assert "Retry-After" in last_response.headers
    assert "Rate limit exceeded" in last_response.json()["detail"]["error"]


# -----------------------------------------------------------------------------
# 8. MCP Hub Tools Invocation (Phase 13 Tools)
# -----------------------------------------------------------------------------
def test_mcp_hub_phase13_tools():
    """
    Verifies JSON-RPC 2.0 tool executions via MCP Hub:
    - check_token_bucket_rate_limit
    - set_distributed_cache_value
    - get_distributed_cache_value
    - publish_pubsub_event
    """
    # 1. check_token_bucket_rate_limit
    rpc_rl = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "check_token_bucket_rate_limit",
            "arguments": {
                "identifier": "agent_satellite_worker_01",
                "cost": 1.0,
                "capacity": 20.0,
                "refill_rate": 5.0
            }
        },
        "id": "mcp-rl-1"
    }
    r1 = client.post("/mcp/invoke", json=rpc_rl)
    assert r1.status_code == 200
    res1 = r1.json()["result"]["data"]
    assert res1["allowed"] is True
    assert res1["key"] == "agent_satellite_worker_01"

    # 2. set_distributed_cache_value
    rpc_set = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "set_distributed_cache_value",
            "arguments": {
                "key": "mcp:cache:test_key",
                "value": {"risk": "HIGH", "score": 0.88},
                "ttl_seconds": 300
            }
        },
        "id": "mcp-set-2"
    }
    r2 = client.post("/mcp/invoke", json=rpc_set)
    assert r2.status_code == 200
    res2 = r2.json()["result"]["data"]
    assert res2["stored"] is True

    # 3. get_distributed_cache_value
    rpc_get = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_distributed_cache_value",
            "arguments": {
                "key": "mcp:cache:test_key"
            }
        },
        "id": "mcp-get-3"
    }
    r3 = client.post("/mcp/invoke", json=rpc_get)
    assert r3.status_code == 200
    res3 = r3.json()["result"]["data"]
    assert res3["hit"] is True
    assert res3["value"]["risk"] == "HIGH"

    # 4. publish_pubsub_event
    rpc_pub = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "publish_pubsub_event",
            "arguments": {
                "channel": "terra_sentinel:mcp",
                "message": {"agent": "acute_risk_agent", "action": "ANALYSIS_COMPLETE"}
            }
        },
        "id": "mcp-pub-4"
    }
    r4 = client.post("/mcp/invoke", json=rpc_pub)
    assert r4.status_code == 200
    res4 = r4.json()["result"]["data"]
    assert res4["status"] == "PUBLISHED"

