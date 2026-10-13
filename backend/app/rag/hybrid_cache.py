"""
AEGIS Hybrid Regulatory Cache (Redis L1 / L2 Architecture)
High-performance semantic vector query caching layer inspired by GreenLink.
Combines sub-millisecond in-memory L1 cache with Redis L2 cluster fallback
to eliminate redundant dense embedding searches and achieve < 5ms retrieval latencies.
"""
import time
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional

try:
    import redis
    HAS_REDIS = True
except ImportError:
    redis = None
    HAS_REDIS = False

from backend.app.config import settings

logger = logging.getLogger("aegis.rag.hybrid_cache")


class HybridRegulatoryCache:
    def __init__(self, default_ttl_sec: int = 3600):
        self.default_ttl = default_ttl_sec
        self._l1_cache: Dict[str, Dict[str, Any]] = {}
        self.redis_client = None
        self.redis_available = False
        
        # Telemetry metrics
        self.total_queries = 0
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
        self.total_latency_ms = 0.0

        self._init_redis()

    def _init_redis(self):
        """Attempts to connect to Redis server with strict timeout."""
        if not HAS_REDIS or not settings.REDIS_URL:
            logger.info("Redis package not available or REDIS_URL not configured. Using in-memory L1 cache.")
            return

        try:
            client = redis.Redis.from_url(
                settings.REDIS_URL,
                socket_timeout=0.25,
                socket_connect_timeout=0.25,
                decode_responses=True
            )
            # Lightweight health ping
            client.ping()
            self.redis_client = client
            self.redis_available = True
            logger.info(f"Connected to Redis cache at {settings.REDIS_URL}")
        except Exception as e:
            self.redis_client = None
            self.redis_available = False
            logger.info(f"Redis L2 cache offline ({e}). Operating in resilient in-memory L1 cache mode.")

    def compute_cache_key(
        self,
        query_text: str,
        region: Optional[str] = None,
        sector: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """Computes deterministic SHA-256 fingerprint for query parameters."""
        normalized_q = query_text.strip().lower()
        normalized_r = (region or "global").strip().lower()
        normalized_s = (sector or "general").strip().lower()
        raw_key = f"{normalized_q}|{normalized_r}|{normalized_s}|{top_k}"
        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return f"aegis:rag:{digest[:32]}"

    def get(
        self,
        query_text: str,
        region: Optional[str] = None,
        sector: Optional[str] = None,
        top_k: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves cached regulatory clauses.
        1. Checks in-memory L1 cache (< 1ms).
        2. If miss and Redis available, checks Redis L2 (< 5ms).
        """
        t0 = time.time()
        self.total_queries += 1
        key = self.compute_cache_key(query_text, region, sector, top_k)
        now = time.time()

        # Step 1: L1 In-Memory Check
        if key in self._l1_cache:
            entry = self._l1_cache[key]
            if entry["expires_at"] > now:
                latency = (time.time() - t0) * 1000.0
                self.l1_hits += 1
                self.total_latency_ms += latency
                return entry["data"]
            else:
                # Expired
                del self._l1_cache[key]

        # Step 2: L2 Redis Check
        if self.redis_available and self.redis_client:
            try:
                cached_json = self.redis_client.get(key)
                if cached_json:
                    data = json.loads(cached_json)
                    # Promote back into L1
                    self._l1_cache[key] = {
                        "data": data,
                        "created_at": now,
                        "expires_at": now + self.default_ttl
                    }
                    latency = (time.time() - t0) * 1000.0
                    self.l2_hits += 1
                    self.total_latency_ms += latency
                    return data
            except Exception as e:
                logger.debug(f"Redis get error: {e}")
                self.redis_available = False

        self.misses += 1
        latency = (time.time() - t0) * 1000.0
        self.total_latency_ms += latency
        return None

    def set(
        self,
        query_text: str,
        results: List[Dict[str, Any]],
        region: Optional[str] = None,
        sector: Optional[str] = None,
        top_k: int = 3,
        ttl_sec: Optional[int] = None
    ):
        """Sets cache entry in L1 and asynchronously in Redis L2."""
        key = self.compute_cache_key(query_text, region, sector, top_k)
        ttl = ttl_sec or self.default_ttl
        now = time.time()

        # Store in L1
        self._l1_cache[key] = {
            "data": results,
            "created_at": now,
            "expires_at": now + ttl
        }

        # Store in Redis L2 if online
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(results))
            except Exception as e:
                logger.debug(f"Redis setex error: {e}")
                self.redis_available = False

    def clear(self):
        """Purges local L1 and Redis cache entries."""
        self._l1_cache.clear()
        if self.redis_available and self.redis_client:
            try:
                # Delete keys matching aegis:rag:*
                keys = self.redis_client.keys("aegis:rag:*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception:
                pass

    def get_stats(self) -> Dict[str, Any]:
        """Returns cache telemetry statistics."""
        total_hits = self.l1_hits + self.l2_hits
        hit_rate = (total_hits / self.total_queries * 100.0) if self.total_queries > 0 else 0.0
        avg_latency = (self.total_latency_ms / self.total_queries) if self.total_queries > 0 else 0.0

        return {
            "total_queries": self.total_queries,
            "cache_hits": total_hits,
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "cache_misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
            "avg_latency_ms": round(avg_latency, 3),
            "l1_size": len(self._l1_cache),
            "redis_available": self.redis_available
        }


# Global singleton instance
hybrid_cache = HybridRegulatoryCache()
