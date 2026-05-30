# Cache Patterns Reference

## Cache-Aside (Lazy Loading)

The application manages the cache explicitly.

```python
async def get_user(user_id: str) -> User:
    # 1. Check cache
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return User.parse_raw(cached)

    # 2. Cache miss - fetch from DB
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        return None

    # 3. Populate cache
    await redis.setex(f"user:{user_id}", 300, user.json())
    return user
```

**Pros**: Only caches data that is actually requested; resilient to cache failure.
**Cons**: Cache miss is slow (two trips); stale data possible.

## Write-Through

Every write goes to both cache and database synchronously.

```python
async def update_user(user_id: str, data: dict) -> User:
    # Write to DB
    user = await db.users.update_one({"_id": user_id}, {"$set": data})

    # Write to cache (same transaction feel)
    await redis.setex(f"user:{user_id}", 300, user.json())

    return user
```

**Pros**: Cache is always fresh; reads are always fast.
**Cons**: Write latency increases; caches data that may never be read.

## Write-Behind (Write-Back)

Writes go to cache immediately, database is updated asynchronously.

```python
async def update_user(user_id: str, data: dict):
    # Write to cache immediately
    user_data = {**data, "updated_at": time.time()}
    await redis.set(f"user:{user_id}", json.dumps(user_data))

    # Queue async DB write
    await queue.publish("user.updates", {
        "user_id": user_id,
        "data": data,
    })

# Worker processes the queue
async def process_user_update(message):
    await db.users.update_one(
        {"_id": message["user_id"]},
        {"$set": message["data"]},
    )
```

**Pros**: Fastest writes; absorbs write spikes.
**Cons**: Risk of data loss if cache fails before DB sync; eventual consistency.

## Read-Through

Cache itself is responsible for loading data from the database on miss.

```python
class ReadThroughCache:
    def __init__(self, redis_client, loader_fn, ttl=300):
        self.redis = redis_client
        self.loader = loader_fn
        self.ttl = ttl

    async def get(self, key: str):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Cache loads from source automatically
        data = await self.loader(key)
        if data is not None:
            await self.redis.setex(key, self.ttl, json.dumps(data))
        return data

# Usage
user_cache = ReadThroughCache(redis, load_user_from_db)
user = await user_cache.get("user:123")
```

## Cache Invalidation Patterns

### Time-Based (TTL)

```python
await redis.setex("product:456", 300, data)  # Expires in 5 minutes
```

### Event-Based

```python
# On user update, invalidate cache
async def on_user_updated(user_id: str):
    await redis.delete(f"user:{user_id}")
    await redis.delete(f"user:{user_id}:profile")
    await redis.delete(f"user:{user_id}:permissions")
```

### Version-Based

```python
# Increment version on update
await redis.incr("config:version")

# Cache key includes version
version = await redis.get("config:version")
cache_key = f"config:v{version}"
```

## Cache Stampede Prevention

### Lock-Based

```python
async def get_with_lock(key: str, loader, ttl=300):
    data = await redis.get(key)
    if data:
        return json.loads(data)

    lock_key = f"lock:{key}"
    if await redis.set(lock_key, "1", nx=True, ex=10):
        try:
            data = await loader()
            await redis.setex(key, ttl, json.dumps(data))
            return data
        finally:
            await redis.delete(lock_key)
    else:
        # Another process is loading, wait and retry
        await asyncio.sleep(0.1)
        return await get_with_lock(key, loader, ttl)
```

### Probabilistic Early Refresh

```python
import random

async def get_with_early_refresh(key: str, loader, ttl=300):
    data = await redis.get(key)
    ttl_remaining = await redis.ttl(key)

    if data and ttl_remaining > ttl * 0.1 * random.random():
        return json.loads(data)

    # Refresh before actual expiry (probabilistic)
    data = await loader()
    await redis.setex(key, ttl, json.dumps(data))
    return data
```

## Multi-Level Caching

```python
class MultiLevelCache:
    def __init__(self):
        self.l1 = {}  # In-memory (per-request)
        self.l2 = redis  # Shared (Redis)

    async def get(self, key: str):
        # L1: in-memory
        if key in self.l1:
            return self.l1[key]

        # L2: Redis
        data = await self.l2.get(key)
        if data:
            self.l1[key] = json.loads(data)
            return self.l1[key]

        return None

    async def set(self, key: str, value, ttl=300):
        self.l1[key] = value
        await self.l2.setex(key, ttl, json.dumps(value))
```

## Pattern Selection Guide

| Pattern | Consistency | Write Speed | Read Speed | Complexity |
|---------|-------------|-------------|------------|------------|
| Cache-Aside | Eventual | Normal | Fast (hit) | Low |
| Write-Through | Strong | Slower | Always fast | Medium |
| Write-Behind | Eventual | Fastest | Always fast | High |
| Read-Through | Eventual | Normal | Fast (hit) | Medium |
