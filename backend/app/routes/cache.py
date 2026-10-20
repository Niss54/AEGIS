"""
AEGIS-CLIMATE Redis Distributed Caching & Token Bucket Rate Limiting Router
Module: backend.app.routes.cache
Phase 13: Distributed Cache, Pub/Sub Bus, & Token Bucket Rate Limiting
"""
import time
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Response

from backend.app.cache import redis_bus_controller, CacheControlModel
from backend.app.rate_limiter import token_bucket_limiter, RateLimitResult, rate_limit_guard

logger = logging.getLogger("aegis.routes.cache")

router = APIRouter(prefix="/cache", tags=["Distributed Caching & Token Bucket Rate Limiting"])


class CacheSetRequest(BaseModel):
    key: str = Field(..., description="Cache key identifier")
    value: Any = Field(..., description="Payload data to cache (dict, list, str, number)")
    ttl_seconds: Optional[int] = Field(300, description="Time to live in seconds (default: 300)")


class CachePublishRequest(BaseModel):
    channel: str = Field(..., description="Pub/Sub channel name")
    message: Dict[str, Any] = Field(..., description="Message payload to broadcast")


class RateLimitCheckRequest(BaseModel):
    identifier: str = Field(..., description="Client identifier (e.g. IP, station_id, user_id)")
    cost: float = Field(1.0, description="Tokens demanded by operation")
    capacity: Optional[float] = Field(None, description="Burst capacity override")
    refill_rate: Optional[float] = Field(None, description="Refill rate override (tokens/sec)")


@router.get("/health")
async def get_cache_health():
    """
    Returns Redis cluster connectivity, circuit breaker status, and active execution tier.
    """
    return redis_bus_controller.get_health()


@router.post("/set")
async def set_cache_entry(req: CacheSetRequest):
    """
    Sets a key-value entry in the distributed cache with TTL.
    """
    success = redis_bus_controller.set(req.key, req.value, ttl_seconds=req.ttl_seconds)
    return {
        "status": "success" if success else "failed",
        "key": req.key,
        "ttl_seconds": req.ttl_seconds,
        "active_tier": redis_bus_controller.get_health()["active_tier"]
    }


@router.get("/get/{key:path}")
async def get_cache_entry(key: str):
    """
    Retrieves a cached value by key.
    """
    val = redis_bus_controller.get(key)
    hit = val is not None
    return {
        "key": key,
        "hit": hit,
        "value": val,
        "active_tier": redis_bus_controller.get_health()["active_tier"]
    }


@router.delete("/delete/{key:path}")
async def delete_cache_entry(key: str):
    """
    Invalidates a cache entry.
    """
    deleted = redis_bus_controller.delete(key)
    return {
        "key": key,
        "deleted": deleted
    }


@router.post("/publish")
async def publish_message(req: CachePublishRequest):
    """
    Publishes an event message to the distributed Redis Pub/Sub bus.
    """
    recipients = redis_bus_controller.publish(req.channel, req.message)
    return {
        "channel": req.channel,
        "subscribers_notified": recipients,
        "timestamp_epoch": time.time()
    }


@router.post("/rate-limit/check", response_model=RateLimitResult)
async def check_rate_limit(req: RateLimitCheckRequest):
    """
    Evaluates token bucket rate limit for an identifier conforming to mathematical invariant:
    Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))
    """
    return token_bucket_limiter.consume(
        key=req.identifier,
        cost=req.cost,
        capacity=req.capacity,
        refill_rate=req.refill_rate
    )


@router.post("/pipeline", response_model=CacheControlModel)
async def execute_phase13_pipeline(payload: Dict[str, Any]):
    """
    Executes standard PRD Phase 13 operational pipeline.
    """
    try:
        return await redis_bus_controller.execute_phase_pipeline(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/stats")
async def get_cache_and_limiter_stats():
    """
    Returns aggregated metrics for Redis caching and Token Bucket rate limiter.
    """
    health = redis_bus_controller.get_health()
    return {
        "cache": health,
        "rate_limiter": {
            "metrics": token_bucket_limiter.metrics,
            "tracked_local_buckets": token_bucket_limiter.local_store.size(),
            "default_capacity": token_bucket_limiter.default_capacity,
            "default_refill_rate": token_bucket_limiter.default_refill_rate
        }
    }


@router.get("/guarded-demo")
async def guarded_demo_endpoint(
    response: Response,
    limiter_result: RateLimitResult = Depends(rate_limit_guard(cost=1.0, capacity=5.0, refill_rate=1.0))
):
    """
    Demonstration endpoint protected by Token Bucket Rate Limiting (capacity: 5, refill: 1 token/sec).
    """
    for k, v in limiter_result.headers.items():
        response.headers[k] = v
    return {
        "status": "ALLOWED",
        "message": "Request processed successfully through token bucket gate.",
        "tokens_remaining": limiter_result.tokens_remaining,
        "execution_tier": limiter_result.execution_tier
    }
