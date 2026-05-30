---
name: performance-profiling
description: |
  【性能分析】系统性性能分析和优化，包含 CPU/内存/IO 分析、瓶颈定位、优化方案、监控指标。

  触发时机：
  - 用户要求"性能分析"、"性能优化"、"分析瓶颈"
  - 系统响应慢需要定位原因
  - 需要建立性能监控

  支持 Python/Node.js/数据库/系统级分析。
category: reference
---

# Performance Profiling — 性能分析技能

系统性性能分析，从指标采集到瓶颈定位再到优化方案。


## Goal

系统性性能分析和优化，包含 CPU/内存/IO 分析、瓶颈定位、优化方案、监控指标

## Trigger

- 用户要求"性能分析"、"性能优化"、"分析瓶颈"
  - 系统响应慢需要定位原因
  - 需要建立性能监控

## 分析流程

```
问题定义 → 指标采集 → 瓶颈定位 → 优化方案 → 效果验证 → 持续监控
```

## 性能指标体系

### 应用层指标

| 指标 | 含义 | 健康范围 |
|------|------|----------|
| P50 响应时间 | 50% 请求的延迟 | < 200ms |
| P95 响应时间 | 95% 请求的延迟 | < 500ms |
| P99 响应时间 | 99% 请求的延迟 | < 1000ms |
| TPS/QPS | 每秒事务/查询数 | 业务预期的 1.5 倍 |
| 错误率 | 失败请求占比 | < 0.1% |
| 并发数 | 同时处理的请求数 | < 连接池大小 |

### 系统层指标

| 指标 | 含义 | 健康范围 |
|------|------|----------|
| CPU 使用率 | 处理器负载 | < 70% |
| 内存使用率 | 内存占用 | < 80% |
| 磁盘 I/O | 磁盘读写 | < 80% 利用率 |
| 网络 I/O | 网络带宽 | < 70% 带宽 |
| 连接数 | 数据库/HTTP 连接 | < 连接池 80% |

### 数据库指标

| 指标 | 含义 | 健康范围 |
|------|------|----------|
| 查询延迟 | 单次查询耗时 | < 10ms (简单查询) |
| 慢查询数 | 超过阈值的查询 | < 1/分钟 |
| 连接池使用率 | 活跃连接占比 | < 80% |
| 缓存命中率 | 缓存有效率 | > 90% |
| 锁等待时间 | 等待锁的时间 | < 100ms |

## Python 性能分析

### cProfile 基础分析

```bash
# 分析整个脚本
python -m cProfile -s cumtime script.py

# 输出到文件
python -m cProfile -o output.prof script.py

# 可视化分析
pip install snakeviz
snakeviz output.prof
```

### line_profiler 逐行分析

```python
# 安装: pip install line_profiler
# 使用 @profile 装饰器
@profile
def slow_function():
    data = load_data()          # Line 3
    processed = process(data)   # Line 4
    result = calculate(processed)  # Line 5
    return result
```

```bash
# 运行分析
kernprof -l -v script.py
```

### memory_profiler 内存分析

```python
# 安装: pip install memory_profiler
# 使用 @profile 装饰器
@profile
def memory_intensive():
    big_list = [i for i in range(1000000)]  # Line 3: +8MB
    filtered = [x for x in big_list if x % 2 == 0]  # Line 4: +4MB
    return filtered
```

```bash
# 运行分析
python -m memory_profiler script.py
```

### py-spy 生产环境分析

```bash
# 实时查看热点
py-spy top --pid 12345

# 生成火焰图
py-spy record -o flamegraph.svg --pid 12345

# 分析脚本
py-spy record -o flamegraph.svg -- python script.py
```

### 常见 Python 性能问题

| 问题 | 现象 | 优化方案 |
|------|------|----------|
| 循环中 append | O(n²) | 列表推导式 |
| 字符串拼接 | O(n²) | "".join() |
| 全局变量访问 | 慢 | 改为局部变量 |
| 重复计算 | 浪费 | 缓存/lru_cache |
| 大对象复制 | 内存高 | 使用生成器 |

```python
# ❌ 慢
result = ""
for s in strings:
    result += s

# ✅ 快
result = "".join(strings)

# ❌ 慢
squares = []
for i in range(1000000):
    squares.append(i * i)

# ✅ 快
squares = [i * i for i in range(1000000)]

# ❌ 慢
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# ✅ 快（带缓存）
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## Node.js 性能分析

### V8 内置分析

```bash
# CPU 分析
node --prof app.js
node --prof-process isolate-*.log > processed.txt

# 更详细的 CPU 分析
node --cpu-prof app.js

# 堆内存分析
node --heapt-snapshot app.js
```

### clinic.js 可视化分析

```bash
# 安装
npm install -g clinic

# 综合诊断
clinic doctor -- node app.js

# 火焰图
clinic flame -- node app.js

# 气泡图
clinic bubbleprof -- node app.js
```

### 常见 Node.js 性能问题

| 问题 | 现象 | 优化方案 |
|------|------|----------|
| 阻塞事件循环 | 响应延迟 | 使用 Worker Threads |
| 内存泄漏 | 内存持续增长 | 检查闭包和监听器 |
| 回调地狱 | 代码难维护 | 使用 async/await |
| 大 JSON 解析 | CPU 高 | 流式解析 |

## 数据库性能分析

### MySQL 慢查询分析

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;

-- 分析查询计划
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 查看索引使用情况
SELECT * FROM sys.schema_unused_indexes;
SELECT * FROM sys.statements_with_full_table_scans LIMIT 10;
```

### PostgreSQL 分析

```sql
-- 查看查询计划
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE email = 'test@example.com';

-- 查看活跃查询
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle' ORDER BY duration DESC;

-- 查看表统计
SELECT schemaname, relname, seq_scan, idx_scan
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
```

### 索引优化

```sql
-- 查找缺失索引
-- MySQL
SELECT * FROM sys.statements_with_full_table_scans LIMIT 10;

-- PostgreSQL
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- 添加索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);
```

## 系统级分析

### Linux 性能工具

```bash
# CPU 使用率
top -o %CPU
htop

# 内存使用
free -h
vmstat 1 10

# 磁盘 I/O
iostat -x 1 10
iotop

# 网络
iftop
nethogs

# 综合监控
dstat
nmon
```

### 火焰图生成

```bash
# 使用 perf 采集
perf record -F 99 -p 12345 -g -- sleep 30
perf script > out.perf

# 生成火焰图
git clone https://github.com/brendangregg/FlameGraph
cd FlameGraph
./stackcollapse-perf.pl ../out.perf > out.folded
./flamegraph.pl out.folded > flamegraph.svg
```

## 优化检查清单

### 应用层
- [ ] 算法复杂度是否合理
- [ ] 是否有 N+1 查询
- [ ] 是否有重复计算
- [ ] 是否使用缓存
- [ ] 是否有内存泄漏

### 数据库层
- [ ] 是否有合适索引
- [ ] 是否有全表扫描
- [ ] 查询是否只取需要的列
- [ ] 是否使用连接池
- [ ] 是否有锁竞争

### 系统层
- [ ] CPU 是否过高
- [ ] 内存是否充足
- [ ] 磁盘 I/O 是否瓶颈
- [ ] 网络带宽是否足够
- [ ] 文件描述符是否够用

## 快速使用

```
# 分析 Python 性能
分析这个 Python 脚本的性能瓶颈

# 定位慢查询
帮我找出数据库的慢查询并优化

# 生成火焰图
为这个 Node.js 应用生成火焰图

# 制定优化方案
系统响应时间 P99 超过 2 秒，帮我制定优化方案
```

## 参考资料

- Python 分析: [references/python.md](references/python.md)
- Node.js 分析: [references/nodejs.md](references/nodejs.md)
- 数据库优化: [references/database.md](references/database.md)
- 系统性能: [references/system.md](references/system.md)
- Web 压测: [references/load-test.md](references/load-test.md)
