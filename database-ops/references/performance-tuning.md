# 性能调优指南

## 连接池配置

### Python (SQLAlchemy)

```python
from sqlalchemy import create_async_engine

engine = create_async_engine(
    database_url,
    pool_size=10,          # 常驻连接数 = worker数 × 2
    max_overflow=10,       # 峰值时额外连接数
    pool_timeout=30,       # 获取连接超时（秒）
    pool_recycle=3600,     # 连接回收时间（防止 MySQL 8h 断开）
    pool_pre_ping=True,    # 每次取连接前检测活性
)
```

### Go (database/sql)

```go
db, _ := sql.Open("postgres", dsn)
db.SetMaxOpenConns(25)                 // 最大连接数
db.SetMaxIdleConns(10)                 // 空闲连接数
db.SetConnMaxLifetime(5 * time.Minute) // 连接最大生命周期
db.SetConnMaxIdleTime(3 * time.Minute) // 空闲连接最大时间
```

### Node.js (Prisma)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")  // ?connection_limit=20&pool_timeout=10
}
```

### Java (HikariCP)

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 300000
      max-lifetime: 1800000
      connection-timeout: 30000
```

### 连接池大小估算

```
连接数 = CPU 核数 × 2 + 磁盘数
```

- 一般应用：10-20 个连接足够
- 高并发：先优化查询，再加连接数
- 连接数过多反而降低性能（上下文切换开销）

## 慢查询排查

### MySQL 慢查询日志

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 超过 1 秒记录
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- 查看慢查询日志位置
SHOW VARIABLES LIKE 'slow_query_log_file';

-- 以上为临时设置，重启后失效。持久化需写入 my.cnf 的 [mysqld] 段：
-- [mysqld]
-- slow_query_log = ON
-- long_query_time = 1
-- log_queries_not_using_indexes = ON
```

### EXPLAIN 分析

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 123 AND status = 'paid';
```

关键字段：

| 字段 | 好 | 差 |
|------|-----|-----|
| type | const, eq_ref, ref | ALL（全表扫描） |
| key | 使用了索引 | NULL（无索引） |
| rows | 扫描行数少 | 扫描行数多 |
| Extra | Using index（覆盖索引） | Using filesort, Using temporary |

### PostgreSQL 慢查询

```sql
-- 开启慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 超过 1 秒
ALTER SYSTEM SET log_statement = 'none';

-- 查看当前查询
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '5 seconds';

-- 杀死慢查询（将 12345 替换为上面查询到的 pid）
SELECT pg_terminate_backend(12345);
```

### EXPLAIN ANALYZE（PostgreSQL）

```sql
EXPLAIN ANALYZE
SELECT u.username, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.is_deleted = false
GROUP BY u.username
ORDER BY order_count DESC
LIMIT 10;
```

## 常见性能问题与解决

### N+1 查询

```python
# ❌ N+1 问题
users = db.query(User).all()
for user in users:
    orders = db.query(Order).filter(Order.user_id == user.id).all()  # 每次循环一次查询

# ✅ 预加载
users = db.query(User).options(joinedload(User.orders)).all()

# ✅ 批量查询
user_ids = [u.id for u in users]
orders = db.query(Order).filter(Order.user_id.in_(user_ids)).all()
```

### 缺少索引导致全表扫描

```sql
-- ❌ 全表扫描（EXPLAIN 显示 type=ALL）
SELECT * FROM orders WHERE user_id = 123;

-- ✅ 添加索引
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

### SELECT *

```python
# ❌ 查询所有字段
users = db.query(User).all()

# ✅ 只查需要的字段
users = db.query(User.id, User.username, User.email).all()
```

### 大事务

```python
# ❌ 大事务（锁持有时间长）
with db.begin():
    for i in range(100000):
        db.execute(insert(Order).values(...))

# ✅ 分批提交
for batch in chunks(records, 1000):
    db.execute(insert(Order).values(batch))
    db.commit()
```

## 分库分表

### 何时分库分表

| 指标 | 阈值 | 说明 |
|------|------|------|
| 单表行数 | > 5000 万 | 查询变慢，索引效率下降 |
| 单库数据量 | > 500GB | 备份恢复时间过长 |
| 单库写入 QPS | > 5000 | 主库压力过大 |
| 单表大小 | > 30GB | DDL 操作耗时 |

### 扩展顺序（推荐）

```
优化索引 → 读写分离 → 垂直拆分（按业务域） → 水平分片
```

每一步都应该在上一步的优化空间用尽之后再推进。

### 读写分离

```yaml
# 写操作 → 主库
# 读操作 → 从库（注意复制延迟）
# 关键路径（如下单后立即查询）→ 强制走主库
```

### 分布式 ID 方案

| 方案 | 优点 | 缺点 |
|------|------|------|
| 雪花算法 | 有序、高性能 | 时钟回拨问题 |
| UUID | 简单、全局唯一 | 无序、占 16 字节 |
| 号段模式 | 简单 | 数据库瓶颈 |
| Redis INCR | 高性能 | 依赖 Redis |

## 数据库参数调优

### MySQL 关键参数

```ini
# InnoDB 缓冲池（建议物理内存的 70-80%）
innodb_buffer_pool_size = 4G

# 日志文件大小
innodb_log_file_size = 1G

# 并发线程
innodb_thread_concurrency = 0  # 自动

# 连接数
max_connections = 500

# 临时表大小
tmp_table_size = 64M
max_heap_table_size = 64M

# 排序缓冲区（每连接分配，500 连接 × 4M = 2GB，按实际调整）
sort_buffer_size = 4M

# JOIN 缓冲区（每连接分配，按实际调整）
join_buffer_size = 4M
```

### PostgreSQL 关键参数

```ini
# 内存（建议物理内存的 25%）
shared_buffers = 4GB

# 工作内存（每个连接排序/哈希操作）
work_mem = 64MB

# 维护内存（VACUUM/CREATE INDEX）
maintenance_work_mem = 512MB

# 最大连接数
max_connections = 200

# WAL 缓存
wal_buffers = 64MB

# 有效缓存（OS 缓存 + PG 缓存）
effective_cache_size = 12GB

# 并行查询
max_parallel_workers_per_gather = 4
```

## 监控指标

### 关键监控项

| 指标 | MySQL | PostgreSQL | 告警阈值 |
|------|-------|-----------|---------|
| 连接数 | `SHOW STATUS LIKE 'Threads_connected'` | `SELECT count(*) FROM pg_stat_activity` | > 80% max |
| QPS | `SHOW STATUS LIKE 'Queries'` | `SELECT sum(xact_commit) FROM pg_stat_database` | 基线对比 |
| 慢查询 | 慢查询日志 | `pg_stat_statements` | 突增 |
| 锁等待 | `SHOW ENGINE INNODB STATUS` | `pg_locks` + `pg_stat_activity` | > 10s |
| 缓冲池命中率 | `Innodb_buffer_pool_read_requests / reads` | `blks_hit / (blks_hit + blks_read)` | < 99% |
| 复制延迟 | `SHOW SLAVE STATUS` | `pg_stat_replication` | > 5s |

### Prometheus + Grafana

- MySQL: `mysqld_exporter`
- PostgreSQL: `postgres_exporter`
- MongoDB: `mongodb_exporter`
- Redis: `redis_exporter`

## 性能优化检查清单

- [ ] 索引覆盖高频查询
- [ ] EXPLAIN 无 ALL（全表扫描）
- [ ] 无 N+1 查询
- [ ] 连接池大小合理
- [ ] 慢查询日志已开启
- [ ] 大表已分区或归档
- [ ] 读写分离（如需要）
- [ ] 监控告警已配置
