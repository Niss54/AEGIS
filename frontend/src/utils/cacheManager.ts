/**
 * TERRA-SENTINEL Frontend Distributed Cache & Token Bucket Client
 * Module: frontend/src/utils/cacheManager.ts
 * Governance: Gravitas Reliability Runtime · Phase 13 Compliance
 *
 * Mathematical Governing Equation:
 * Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))
 * Where:
 * - C: Burst Capacity limit
 * - r: Refill rate (tokens/sec)
 * - t - t_0: Time elapsed since last update in seconds
 * - Tokens(t_0): Previous token count
 */

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  expireAtEpoch: number | null;
  cachedAtEpoch: number;
}

export interface ClientRateLimitState {
  tokens: number;
  lastUpdated: number;
  capacity: number;
  refillRate: number;
}

export interface ClientRateLimitResult {
  allowed: boolean;
  tokensRemaining: number;
  retryAfterSeconds: number;
  tier: 'CLIENT_TOKEN_BUCKET' | 'BACKEND_SYNCHRONIZED';
}

export class DistributedCacheManager {
  private static instance: DistributedCacheManager;
  private cacheStore: Map<string, CacheEntry> = new Map();
  private bucketStates: Map<string, ClientRateLimitState> = new Map();

  private defaultCapacity: number = 60.0;
  private defaultRefillRate: number = 10.0;

  private constructor() {
    this.restoreLocalCache();
  }

  public static getInstance(): DistributedCacheManager {
    if (!DistributedCacheManager.instance) {
      DistributedCacheManager.instance = new DistributedCacheManager();
    }
    return DistributedCacheManager.instance;
  }

  private restoreLocalCache(): void {
    try {
      const serialized = localStorage.getItem('terra_client_cache_v1');
      if (serialized) {
        const parsed = JSON.parse(serialized);
        const now = Date.now() / 1000;
        for (const [k, v] of Object.entries(parsed)) {
          const entry = v as CacheEntry;
          if (!entry.expireAtEpoch || entry.expireAtEpoch > now) {
            this.cacheStore.set(k, entry);
          }
        }
      }
    } catch {
      // LocalStorage unavailable, in-memory Map operates cleanly
    }
  }

  private persistLocalCache(): void {
    try {
      const obj: Record<string, CacheEntry> = {};
      const now = Date.now() / 1000;
      this.cacheStore.forEach((v, k) => {
        if (!v.expireAtEpoch || v.expireAtEpoch > now) {
          obj[k] = v;
        }
      });
      localStorage.setItem('terra_client_cache_v1', JSON.stringify(obj));
    } catch {
      // Best effort persistence
    }
  }

  /**
   * Sets value in client cache with optional TTL seconds.
   */
  public set<T = any>(key: string, value: T, ttlSeconds: number = 300): void {
    const now = Date.now() / 1000;
    const entry: CacheEntry<T> = {
      key,
      value,
      cachedAtEpoch: now,
      expireAtEpoch: ttlSeconds > 0 ? now + ttlSeconds : null
    };
    this.cacheStore.set(key, entry);
    this.persistLocalCache();
  }

  /**
   * Retrieves value from client cache if not expired.
   */
  public get<T = any>(key: string): T | null {
    const entry = this.cacheStore.get(key);
    if (!entry) return null;

    const now = Date.now() / 1000;
    if (entry.expireAtEpoch && now > entry.expireAtEpoch) {
      this.cacheStore.delete(key);
      this.persistLocalCache();
      return null;
    }
    return entry.value as T;
  }

  public delete(key: string): boolean {
    const deleted = this.cacheStore.delete(key);
    if (deleted) this.persistLocalCache();
    return deleted;
  }

  public clear(): void {
    this.cacheStore.clear();
    try {
      localStorage.removeItem('terra_client_cache_v1');
    } catch {
      // Ignore
    }
  }

  /**
   * Deterministic client-side Token Bucket evaluation conforming to:
   * Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0))
   */
  public consumeTokenBucket(
    key: string,
    cost: number = 1.0,
    capacity?: number,
    refillRate?: number
  ): ClientRateLimitResult {
    const now = Date.now() / 1000;
    const cap = capacity ?? this.defaultCapacity;
    const rate = refillRate ?? this.defaultRefillRate;

    let state = this.bucketStates.get(key);
    if (!state) {
      state = {
        tokens: cap,
        lastUpdated: now,
        capacity: cap,
        refillRate: rate
      };
    }

    // Replenish tokens mathematically
    const elapsed = Math.max(0, now - state.lastUpdated);
    const replenishedTokens = Math.min(cap, state.tokens + rate * elapsed);

    let allowed = false;
    let tokensRemaining = replenishedTokens;
    let retryAfterSeconds = 0;

    if (replenishedTokens >= cost) {
      allowed = true;
      tokensRemaining = replenishedTokens - cost;
      state.tokens = tokensRemaining;
      state.lastUpdated = now;
    } else {
      allowed = false;
      tokensRemaining = replenishedTokens;
      retryAfterSeconds = Math.round(((cost - replenishedTokens) / rate) * 1000) / 1000;
      state.tokens = replenishedTokens;
      state.lastUpdated = now;
    }

    this.bucketStates.set(key, state);

    return {
      allowed,
      tokensRemaining: Math.round(tokensRemaining * 1000) / 1000,
      retryAfterSeconds,
      tier: 'CLIENT_TOKEN_BUCKET'
    };
  }

  /**
   * Wraps an async fetch or execution with token bucket throttling & caching.
   */
  public async executeWithRateLimit<T>(
    endpointKey: string,
    action: () => Promise<T>,
    cost: number = 1.0
  ): Promise<T> {
    const bucketCheck = this.consumeTokenBucket(endpointKey, cost);
    if (!bucketCheck.allowed) {
      throw new Error(
        `[RateLimit] Operation throttled on key '${endpointKey}'. Retry in ${bucketCheck.retryAfterSeconds}s.`
      );
    }
    return await action();
  }
}

export const distributedCacheManager = DistributedCacheManager.getInstance();
