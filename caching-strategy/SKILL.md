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

## 工作流程

### Step 1: 性能分析 (Profile)

识别慢查询和读写比例：
- 分析数据库慢查询日志，找出高频读取的资源
- 统计各接口的读写比例（读多写少的接口适合缓存）
- 确认性能瓶颈确实在数据库查询层

**诊断命令**：
```bash
# 查看 Redis 当前状态
redis-cli info stats | grep -E "keyspace_hits|keyspace_misses"

# 分析慢查询
redis-cli slowlog get 10
```

**成功标准**：明确缓存目标资源，读写比例 > 3:1 的接口优先。

### Step 2: 数据分类 (Classify)

| 数据类型 | 特征 | 缓存策略 |
|----------|------|----------|
| 静态数据 | 很少变化（配置、字典） | 长 TTL + 主动失效 |
| 半静态数据 | 偶尔变化（用户信息、商品详情） | 中等 TTL + 写时删除 |
| 动态数据 | 频繁变化（库存、余额） | 短 TTL 或不缓存 |

### Step 3: 选择缓存类型 (Choose Cache Type)

根据分布式需求选择：
- 单实例：本地缓存（Guava/Caffeine）
- 分布式：Redis 或 Memcached
- 静态资源：CDN

### Step 4: 选择缓存模式 (Select Pattern)

| 一致性需求 | 读写比 | 推荐模式 | 原因 |
|------------|--------|----------|------|
| 强一致 | 读多写少 | Cache-Aside | 应用层控制，最灵活 |
| 强一致 | 均衡 | Read-Through | 缓存层代理，减少重复代码 |
| 最终一致 | 写多 | Write-Behind | 异步批量写入 DB，减少 DB 压力 |

### Step 5: 设计 Key 策略 (Design Keys)

定义 Key 格式、TTL、失效规则：
- Key 格式：`{resource}:{id}`（如 `user:123`、`product:SKU001`）
- TTL：基础 TTL + 随机偏移（防止雪崩）
- 失效：写操作时删除缓存（Cache-Aside）

### Step 6: 防护设计 (Defend)

针对三大缓存问题添加防护：
- **缓存穿透**：空值缓存 + 布隆过滤器
- **缓存击穿**：互斥锁 / 逻辑过期
- **缓存雪崩**：随机 TTL + 多级缓存 + 预热

### Step 7: 监控验证 (Monitor)

设置监控指标并验证效果：
- 命中率 > 90%
- 缓存延迟 < 5ms
- 缓存与 DB 数据一致性检查

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

### 填写示例（电商商品详情缓存）

```yaml
缓存方案:
  - 资源: 商品详情
    缓存模式: Cache-Aside
    缓存层: Redis
    Key 格式: "product:{sku}"
    数据格式: JSON
    过期策略:
      TTL: 1800s
      随机偏移: 300s
    失效策略:
      写操作: 删除缓存（商品更新时）
      批量操作: 延迟双删（批量导入时）
    特殊处理:
      空值: 缓存 60s（防穿透，商品不存在时缓存 "null"）
      热点: 互斥锁（前 100 个 SKU 设置逻辑过期）
    监控:
      命中率: > 95%
      命中延迟: < 2ms
```

**缓存前**：
```python
# 每次请求都查数据库
async def get_product(sku: str):
    return await db.query("SELECT * FROM products WHERE sku = %s", sku)
```

**缓存后**：
```python
async def get_product(sku: str):
    cache_key = f"product:{sku}"
    cached = await redis.get(cache_key)
    if cached:
        if cached == "null":
            return None
        return Product.model_validate_json(cached)

    product = await db.query("SELECT * FROM products WHERE sku = %s", sku)
    if product is None:
        await redis.setex(cache_key, 60, "null")  # 空值缓存
    else:
        ttl = 1800 + random.randint(0, 300)
        await redis.setex(cache_key, ttl, product.model_dump_json())
    return product
```

## 不适用

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 写密集型工作负载（> 50% 写操作） | 缓存增加复杂度但无法减少 DB 压力 | 优化数据库写入（批量写入、分库分表） |
| 强一致性要求（金融交易） | 缓存与 DB 之间的延迟可能导致数据不一致 | 使用 DB 事务 + 同步复制，不使用缓存 |
| 数据每次请求都不同（随机值） | 缓存命中率为零，无意义 | 不使用缓存，优化查询本身 |
| 低流量系统（< 100 req/s） | 数据库完全能承受，缓存是过度设计 | 直接查询数据库 |

**重定向**：
- 数据库查询优化（不涉及缓存）：考虑索引优化、查询重构、分库分表等数据库层面的优化。
- 高并发写入：使用消息队列削峰，或分库分表分散写入压力。

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
