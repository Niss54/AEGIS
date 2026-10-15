"""
TERRA-SENTINEL Production Specification: Phase 13
Module: terra_sentinel.phase_13.ratelimiter
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant

Mathematical Governing Equation:
Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))
Where:
- C: Burst capacity (maximum token ceiling)
- r: Refill rate (tokens per second)
- t - t_0: Time elapsed since last update in seconds
- Tokens(t_0): Previous token count at timestamp t_0

If Tokens(t) >= cost:
    Tokens'(t) = Tokens(t) - cost
    allowed = True
    retry_after = 0.0
Else:
    Tokens'(t) = Tokens(t)
    allowed = False
    retry_after = (cost - Tokens(t)) / r
"""
import time
import math
import logging
from typing import Dict, Any, Optional, Tuple, Callable
from pydantic import BaseModel, Field
from fastapi import Request, HTTPException, status

from backend.app.cache import redis_bus_controller, RedisBusController

logger = logging.getLogger("terra_sentinel.rate_limiter")


class RateLimitResult(BaseModel):
    """
    Validation schema for rate limit evaluations conforming to RFC 6585 and HTTP 429 semantics.
    """
    allowed: bool = Field(..., description="Whether the request is permitted")
    key: str = Field(..., description="Rate-limited identifier (IP, client_id, station_id)")
    tokens_remaining: float = Field(..., description="Available tokens remaining after evaluation")
    capacity: float = Field(..., description="Burst capacity limit C")
    refill_rate: float = Field(..., description="Refill rate r (tokens/second)")
    cost: float = Field(..., description="Tokens demanded by operation")
    retry_after_seconds: float = Field(0.0, description="Seconds until sufficient tokens refill if throttled")
    execution_tier: str = Field("REDIS_DISTRIBUTED", description="Execution tier: REDIS_DISTRIBUTED or LOCAL_IN_MEMORY_FALLBACK")
    headers: Dict[str, str] = Field(default_factory=dict, description="Standard HTTP rate limit headers")


class InMemoryBucketStore:
    """
    Thread-safe, high-performance in-memory store for Token Bucket state.
    Used for local execution or when Redis is in circuit breaker OPEN state.
    """
    def __init__(self):
        # key -> (tokens, last_updated_epoch, capacity, refill_rate)
        self._buckets: Dict[str, Tuple[float, float, float, float]] = {}

    def get(self, key: str) -> Optional[Tuple[float, float, float, float]]:
        return self._buckets.get(key)

    def set(self, key: str, tokens: float, last_updated: float, capacity: float, refill_rate: float) -> None:
        self._buckets[key] = (tokens, last_updated, capacity, refill_rate)

    def reset(self, key: Optional[str] = None) -> None:
        if key:
            self._buckets.pop(key, None)
        else:
            self._buckets.clear()

    def size(self) -> int:
        return len(self._buckets)


class TokenBucketRateLimiter:
    """
    Executive Token Bucket Rate Limiter for Phase 13.
    Implements deterministic token replenishment and consumption with distributed Redis synchronization
    and local in-memory fallback.
    """
    def __init__(
        self,
        default_capacity: float = 60.0,
        default_refill_rate: float = 10.0,
        bus_controller: Optional[RedisBusController] = None
    ):
        self.default_capacity = float(default_capacity)
        self.default_refill_rate = float(default_refill_rate)
        self.bus_controller = bus_controller or redis_bus_controller
        self.local_store = InMemoryBucketStore()
        
        # Telemetry metrics
        self.metrics = {
            "total_evaluations": 0,
            "total_allowed": 0,
            "total_throttled": 0,
            "local_fallback_evaluations": 0
        }

    def _calculate_tokens(
        self,
        current_time: float,
        last_updated: float,
        tokens: float,
        capacity: float,
        refill_rate: float
    ) -> float:
        """
        Calculates replenished token count obeying:
        Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))
        """
        elapsed = max(0.0, current_time - last_updated)
        replenished = tokens + (refill_rate * elapsed)
        return min(capacity, replenished)

    def consume(
        self,
        key: str,
        cost: float = 1.0,
        capacity: Optional[float] = None,
        refill_rate: Optional[float] = None
    ) -> RateLimitResult:
        """
        Evaluates and consumes tokens for a key.
        Deterministic and bounded.
        """
        self.metrics["total_evaluations"] += 1
        now = time.time()
        cap = float(capacity) if capacity is not None else self.default_capacity
        rate = float(refill_rate) if refill_rate is not None else self.default_refill_rate
        cost = float(cost)

        # Validate inputs
        if cap <= 0.0 or rate <= 0.0 or cost < 0.0:
            raise ValueError(f"Invalid rate limit parameters: capacity={cap}, refill_rate={rate}, cost={cost}")

        redis_client = self.bus_controller._get_redis() if self.bus_controller.circuit_state != "OPEN" else None
        tier = "REDIS_DISTRIBUTED" if redis_client is not None else "LOCAL_IN_MEMORY_FALLBACK"

        tokens_before = cap
        last_updated = now

        # 1. Attempt Redis distributed token retrieval
        redis_evaluated = False
        redis_key = f"terra:ratelimit:{key}"

        if redis_client is not None:
            try:
                data = redis_client.hgetall(redis_key)
                if data and "tokens" in data and "last_updated" in data:
                    tokens_before = float(data["tokens"])
                    last_updated = float(data["last_updated"])
                else:
                    tokens_before = cap
                    last_updated = now

                # Replenish mathematically
                refilled_tokens = self._calculate_tokens(now, last_updated, tokens_before, cap, rate)

                if refilled_tokens >= cost:
                    new_tokens = refilled_tokens - cost
                    allowed = True
                    retry_after = 0.0
                else:
                    new_tokens = refilled_tokens
                    allowed = False
                    retry_after = round((cost - refilled_tokens) / rate, 3)

                # Store back into Redis with TTL (so inactive keys expire)
                ttl_seconds = max(60, int(math.ceil(cap / rate) * 2))
                pipe = redis_client.pipeline()
                pipe.hset(redis_key, mapping={
                    "tokens": str(new_tokens),
                    "last_updated": str(now),
                    "capacity": str(cap),
                    "refill_rate": str(rate)
                })
                pipe.expire(redis_key, ttl_seconds)
                pipe.execute()

                redis_evaluated = True
                remaining_tokens = new_tokens
            except Exception as exc:
                self.bus_controller._record_failure(exc)
                redis_evaluated = False
                tier = "LOCAL_IN_MEMORY_FALLBACK"

        # 2. Local Fallback if Redis was unavailable or failed
        if not redis_evaluated:
            self.metrics["local_fallback_evaluations"] += 1
            bucket = self.local_store.get(key)
            if bucket is not None:
                stored_tokens, stored_last_updated, _, _ = bucket
                tokens_before = stored_tokens
                last_updated = stored_last_updated
            else:
                tokens_before = cap
                last_updated = now

            refilled_tokens = self._calculate_tokens(now, last_updated, tokens_before, cap, rate)

            if refilled_tokens >= cost:
                new_tokens = refilled_tokens - cost
                allowed = True
                retry_after = 0.0
            else:
                new_tokens = refilled_tokens
                allowed = False
                retry_after = round((cost - refilled_tokens) / rate, 3)

            self.local_store.set(key, new_tokens, now, cap, rate)
            remaining_tokens = new_tokens

        # Telemetry updates
        if allowed:
            self.metrics["total_allowed"] += 1
        else:
            self.metrics["total_throttled"] += 1

        # Standard RFC HTTP Rate Limit Headers
        headers = {
            "X-RateLimit-Limit": str(int(cap)),
            "X-RateLimit-Remaining": str(max(0, int(remaining_tokens))),
            "X-RateLimit-Reset": str(int(now + (cap - remaining_tokens) / rate if rate > 0 else now)),
        }
        if not allowed:
            headers["Retry-After"] = str(math.ceil(retry_after))

        return RateLimitResult(
            allowed=allowed,
            key=key,
            tokens_remaining=round(remaining_tokens, 4),
            capacity=cap,
            refill_rate=rate,
            cost=cost,
            retry_after_seconds=retry_after,
            execution_tier=tier,
            headers=headers
        )

    def reset(self, key: Optional[str] = None) -> None:
        """Resets token bucket state for a key or clears all."""
        self.local_store.reset(key)
        redis_client = self.bus_controller._get_redis()
        if redis_client is not None:
            try:
                if key:
                    redis_client.delete(f"terra:ratelimit:{key}")
                else:
                    keys = redis_client.keys("terra:ratelimit:*")
                    if keys:
                        redis_client.delete(*keys)
            except Exception:
                pass


# Global singleton rate limiter instance
token_bucket_limiter = TokenBucketRateLimiter()


def rate_limit_guard(
    cost: float = 1.0,
    capacity: Optional[float] = None,
    refill_rate: Optional[float] = None
) -> Callable:
    """
    FastAPI Dependency Factory for token bucket rate limiting on sensitive routes.
    Extracts client IP or API key and rejects throttled requests with 429.
    """
    async def dependency(request: Request):
        # Determine client identifier
        client_ip = request.client.host if request.client else "127.0.0.1"
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        identifier = api_key or (auth_header[-12:] if auth_header else client_ip)

        result = token_bucket_limiter.consume(
            key=f"{request.url.path}:{identifier}",
            cost=cost,
            capacity=capacity,
            refill_rate=refill_rate
        )

        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded (Token Bucket Throttled)",
                    "retry_after_seconds": result.retry_after_seconds,
                    "tokens_remaining": result.tokens_remaining,
                    "capacity": result.capacity,
                    "execution_tier": result.execution_tier
                },
                headers=result.headers
            )
        return result

    return dependency
