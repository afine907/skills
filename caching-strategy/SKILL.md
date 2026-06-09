---
name: caching-strategy
description: |
  【缓存策略】设计和实现缓存方案，包含缓存选型、缓存模式、失效策略、缓存穿透/击穿/雪崩防护。

  触发时机：
  - 用户要求"设计缓存方案"、"优化缓存"
  - 系统性能瓶颈在数据库查询
  - 需要实现分布式缓存

  支持 Redis/Memcached/本地缓存方案设计。
category: development
user-invocable: false
---

# Caching Strategy — 缓存策略技能

设计系统性缓存方案，解决高并发读取性能问题。


## Goal

设计和实现缓存方案，包含缓存选型、缓存模式、失效策略、缓存穿透/击穿/雪崩防护

## Trigger

- 用户要求"设计缓存方案"、"优化缓存"
  - 系统性能瓶颈在数据库查询
  - 需要实现分布式缓存

## 缓存选型

| 类型 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| 本地缓存 | 单实例、高频读 | 零网络开销 | 不支持分布式 |
| Redis | 分布式、丰富数据结构 | 高性能、持久化 | 需要额外服务 |
| Memcached | 简单 KV、多线程 | 简单高效 | 功能有限 |
| CDN | 静态资源 | 全球加速 | 仅限静态内容 |

## 缓存模式

### 1. Cache-Aside（旁路缓存）

最常用的模式，应用层控制缓存。

```
读流程:
1. 先查缓存
2. 缓存命中 → 返回
3. 缓存未命中 → 查数据库
4. 写入缓存
5. 返回数据

写流程:
1. 更新数据库
2. 删除缓存（而非更新）
```

```python
async def get_user(user_id: str) -> User:
    # 1. 查缓存
    cache_key = f"user:{user_id}"
    cached = await redis.get(cache_key)
    if cached:
        return User.model_validate_json(cached)
    
    # 2. 查数据库
    user = await db.get_user(user_id)
    if user is None:
        # 缓存空值，防止缓存穿透
        await redis.setex(cache_key, 60, "null")
        return None
    
    # 3. 写入缓存
    await redis.setex(cache_key, 3600, user.model_dump_json())
    return user

async def update_user(user_id: str, data: UserUpdate):
    # 1. 更新数据库
    await db.update_user(user_id, data)
    # 2. 删除缓存
    await redis.delete(f"user:{user_id}")
```

### 2. Read-Through / Write-Through

缓存层代理数据库操作。

```
读流程:
1. 查缓存
2. 缓存未命中 → 缓存层自动从 DB 加载
3. 返回数据

写流程:
1. 写入缓存
2. 缓存层自动同步到 DB
```

### 3. Write-Behind（异步写入）

写入只到缓存，异步批量同步到 DB。

```
写流程:
1. 写入缓存（立即返回）
2. 异步批量写入 DB

适用场景:
- 写入量大
- 允许短暂数据不一致
- 如：计数器、日志收集
```

## 缓存失效策略

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| TTL | 设置过期时间 | 大多数场景 |
| LRU | 最近最少使用淘汰 | 内存有限时 |
| LFU | 最不经常使用淘汰 | 热点数据明显 |
| 手动失效 | 主动删除/更新 | 数据一致性要求高 |

## 缓存问题与防护

### 缓存穿透

**问题**: 查询不存在的数据，每次都穿透到数据库。

**防护**:
```python
# 方案1: 缓存空值
if result is None:
    await redis.setex(key, 60, "null")  # 短过期时间

# 方案2: 布隆过滤器
if not bloom_filter.exists(key):
    return None  # 一定不存在，直接返回

# 方案3: 请求合并
async def get_users_batch(user_ids: list[str]):
    # 一次性查询多个，减少穿透
    cached = await redis.mget([f"user:{id}" for id in user_ids])
    miss_ids = [id for id, v in zip(user_ids, cached) if v is None]
    if miss_ids:
        db_users = await db.get_users(miss_ids)
        # 批量写入缓存
```

### 缓存击穿

**问题**: 热点 key 过期瞬间，大量请求同时穿透。

**防护**:
```python
# 方案1: 互斥锁
async def get_hot_data(key: str):
    data = await redis.get(key)
    if data:
        return data
    
    # 尝试获取锁
    lock_key = f"lock:{key}"
    if await redis.set(lock_key, "1", nx=True, ex=10):
        try:
            # 获取锁成功，查 DB 并更新缓存
            data = await db.query(key)
            await redis.setex(key, 3600, data)
            return data
        finally:
            await redis.delete(lock_key)
    else:
        # 获取锁失败，等待后重试
        await asyncio.sleep(0.1)
        return await get_hot_data(key)

# 方案2: 逻辑过期
async def get_with_logical_expire(key: str):
    cache_data = await redis.get(key)
    if cache_data:
        data, expire_time = parse_cache(cache_data)
        if expire_time > time.time():
            return data  # 未过期
        # 已过期，异步更新
        asyncio.create_task(refresh_cache(key))
        return data  # 返回旧数据
```

### 缓存雪崩

**问题**: 大量 key 同时过期，数据库压力骤增。

**防护**:
```python
# 方案1: 过期时间加随机值
import random
ttl = 3600 + random.randint(0, 300)  # 3600-3900 秒
await redis.setex(key, ttl, data)

# 方案2: 多级缓存
L1_CACHE = {}  # 本地缓存（秒级）
L2_CACHE = redis  # Redis（分钟级）

# 方案3: 缓存预热
async def warm_up_cache():
    """服务启动时预热热点数据"""
    hot_keys = await get_hot_keys()
    for key in hot_keys:
        data = await db.query(key)
        await redis.setex(key, 3600, data)
```

## 缓存设计模板

```yaml
缓存方案:
  - 资源: {资源名称}
    缓存模式: Cache-Aside
    缓存层: Redis
    Key 格式: "{resource}:{id}"
    数据格式: JSON
    过期策略: 
      TTL: 3600s
      随机偏移: 300s
    失效策略:
      写操作: 删除缓存
      批量操作: 延迟双删
    特殊处理:
      空值: 缓存 60s
      热点: 互斥锁
    监控:
      命中率: > 90%
      命中延迟: < 5ms
```

## 快速使用

```
# 设计缓存方案
为商品详情接口设计缓存方案

# 实现缓存逻辑
实现用户信息的 Cache-Aside 缓存

# 排查缓存问题
缓存命中率很低，帮我分析原因

# 优化现有缓存
优化以下缓存代码的性能：[粘贴代码]
```

## 参考资料

- Redis 最佳实践: [references/redis-best-practices.md](references/redis-best-practices.md)
- 缓存模式详解: [references/cache-patterns.md](references/cache-patterns.md)
