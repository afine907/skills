# Redis Best Practices

## Connection Management

### Connection Pooling

```python
import redis

pool = redis.ConnectionPool(
    host="redis-host",
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)
client = redis.Redis(connection_pool=pool)
```

### Health Checks

```python
def check_redis_health() -> bool:
    try:
        return client.ping()
    except redis.ConnectionError:
        return False
```

## Key Design

### Naming Convention

```
{service}:{entity}:{id}:{attribute}

Examples:
  user:profile:12345
  session:token:abc-def
  cache:product:list:page:1
  rate:api:/users:192.168.1.1
```

### TTL Strategy

| Data Type | Recommended TTL | Rationale |
|-----------|----------------|-----------|
| Session data | 24h | User should re-authenticate daily |
| API cache | 5-60 min | Balance freshness vs performance |
| Rate limit counters | 1 min - 1 hour | Matches rate limit window |
| Temporary tokens | 10-15 min | Security best practice |
| Config cache | 5 min | Quick propagation of changes |

```python
client.setex("cache:user:123", 300, json.dumps(user_data))
```

## Data Structure Selection

### Strings

Best for: Simple key-value, counters, flags.

```python
# Caching a serialized object
client.setex("cache:product:456", 600, json.dumps(product))

# Atomic counter
client.incr("stats:page:views:/home")
client.incrbyfloat("metrics:response_time:sum", 0.234)
```

### Hashes

Best for: Object fields, user profiles, configuration.

```python
client.hset("user:123", mapping={
    "name": "Alice",
    "email": "alice@example.com",
    "role": "admin",
})
client.hincrby("user:123", "login_count", 1)

# Get specific field
email = client.hget("user:123", "email")

# Get all fields
user = client.hgetall("user:123")
```

### Sorted Sets

Best for: Leaderboards, time-series, priority queues.

```python
# Leaderboard
client.zadd("leaderboard", {"player:alice": 1500, "player:bob": 1200})
top_players = client.zrevrange("leaderboard", 0, 9, withscores=True)

# Rate limiting with sliding window
now = time.time()
pipe = client.pipeline()
pipe.zremrangebyscore("rate:user:123", 0, now - 60)
pipe.zadd("rate:user:123", {str(now): now})
pipe.zcard("rate:user:123")
pipe.expire("rate:user:123", 60)
_, _, request_count, _ = pipe.execute()
```

### Lists

Best for: Queues, recent items, activity feeds.

```python
# Job queue (reliable with BRPOPLPUSH)
client.lpush("queue:jobs", json.dumps(job))
job = client.brpop("queue:jobs", timeout=30)

# Recent items (bounded list)
client.lpush("recent:searches:user:123", query)
client.ltrim("recent:searches:user:123", 0, 49)  # Keep last 50
```

### Sets

Best for: Unique collections, tags, relationships.

```python
client.sadd("user:123:tags", "python", "redis", "backend")
client.sadd("user:456:tags", "python", "frontend")
common = client.sinter("user:123:tags", "user:456:tags")
```

## Performance Guidelines

### Pipeline Commands

```python
# Bad: N round trips
for key in keys:
    client.get(key)

# Good: 1 round trip
pipe = client.pipeline()
for key in keys:
    pipe.get(key)
results = pipe.execute()
```

### Lua Scripts for Atomic Operations

```python
# Atomic compare-and-swap
lua_script = """
local current = redis.call('GET', KEYS[1])
if current == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[3])
    return 1
end
return 0
"""
cas = client.register_script(lua_script)
cas(keys=["lock:resource"], args=[old_value, new_value, 300])
```

## Memory Management

### Eviction Policies

| Policy | Behavior | Best For |
|--------|----------|----------|
| `volatile-lru` | Evict least-recently-used with TTL set | Mixed cache + persistent |
| `allkeys-lru` | Evict least-recently-used any key | Pure cache |
| `volatile-ttl` | Evict shortest TTL first | Auto-expiring data |
| `noeviction` | Return error on memory limit | Critical data, never lose |

### Monitor Memory

```bash
redis-cli INFO memory
redis-cli MEMORY USAGE <key>
redis-cli --bigkeys
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Using KEYS in production | Blocks Redis, O(n) scan | Use SCAN or maintain an index |
| Large values (>1MB) | Memory waste, slow network | Compress, split, or use hashes |
| No TTL on cache keys | Unbounded memory growth | Always set TTL |
| Single key hot-spot | Uneven load, contention | Shard across multiple keys |
| Storing sensitive data in plaintext | Security risk | Encrypt before storing |
