---
name: performance-profiling
description: 性能分析和调优工具速查，覆盖 Python、Node.js、数据库性能分析和 Linux 系统调优。
homepage: https://docs.python.org/3/library/profile.html
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":["python"]}}}
---

# Performance Profiling

性能分析和调优工具速查。

## Python 性能分析

### cProfile
```python
# 命令行使用
python -m cProfile script.py
python -m cProfile -s cumtime script.py  # 按累计时间排序
python -m cProfile -o output.prof script.py  # 输出到文件

# 代码中使用
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 要分析的代码
result = expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # 显示前 20 个

# 保存分析结果
profiler.dump_stats('profile.prof')
```

### line_profiler (逐行分析)
```bash
# 安装
pip install line_profiler

# 使用装饰器
@profile
def slow_function():
    ...

# 运行
kernprof -l -v script.py
```

### memory_profiler (内存分析)
```bash
# 安装
pip install memory_profiler

# 使用
@profile
def memory_intensive():
    ...

# 运行
python -m memory_profiler script.py
```

### py-spy (采样分析)
```bash
# 安装
pip install py-spy

# 分析运行中的程序
py-spy top --pid 12345

# 生成火焰图
py-spy record -o flamegraph.svg --pid 12345

# 分析脚本
py-spy record -o flamegraph.svg python script.py
```

### 常见性能问题
```python
# 字符串拼接 - 避免在循环中 +
# 慢
result = ""
for s in strings:
    result += s

# 快
result = "".join(strings)

# 列表推导式更快
result = [i * 2 for i in range(1000)]

# 使用生成器节省内存
result = (i * 2 for i in range(1000000))

# 使用内置函数
total = sum(numbers)

# 字典查找比列表快
if item in my_set:  # O(1)
    ...
```

## Node.js 性能分析

### 内置分析
```bash
# V8 分析
node --prof app.js

# 查看结果
node --prof-process isolate-*.log

# 生成 CPU 分析
node --cpu-prof app.js

# 生成堆快照
node --heap-prof app.js
```

### clinic.js
```bash
# 安装
npm install -g clinic

# CPU 分析
clinic doctor -- node app.js

# 事件循环延迟
clinic bubbleprof -- node app.js

# 内存分析
clinic heapprofiler -- node app.js

# 火焰图
clinic flame -- node app.js
```

### Node.js 调试
```javascript
// 使用 console.time
console.time('operation');
// ... 代码
console.timeEnd('operation');

// 使用 performance API
const { performance } = require('perf_hooks');
const start = performance.now();
// ... 代码
const end = performance.now();
console.log(`耗时: ${end - start}ms`);

// 内存使用
const used = process.memoryUsage();
console.log({
  rss: `${used.rss / 1024 / 1024} MB`,
  heapUsed: `${used.heapUsed / 1024 / 1024} MB`,
});
```

## 数据库性能分析

### MySQL
```sql
-- 慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- EXPLAIN 分析
EXPLAIN SELECT * FROM users WHERE name = 'Alice';
EXPLAIN ANALYZE SELECT * FROM users WHERE name = 'Alice';

-- 查看索引
SHOW INDEX FROM users;

-- 查看进程
SHOW PROCESSLIST;
```

### PostgreSQL
```sql
-- EXPLAIN 分析
EXPLAIN SELECT * FROM users WHERE name = 'Alice';
EXPLAIN ANALYZE SELECT * FROM users WHERE name = 'Alice';

-- 查看活动查询
SELECT * FROM pg_stat_activity;

-- 表统计信息
SELECT * FROM pg_stat_user_tables;
```

### Redis
```bash
# 慢查询日志
redis-cli SLOWLOG GET 10

# 查看统计信息
redis-cli INFO
redis-cli INFO memory

# 实时监控
redis-cli MONITOR

# 基准测试
redis-benchmark -t set,get -n 100000 -c 50
```

## 系统性能分析

### CPU 分析
```bash
# CPU 使用情况
top -o %CPU
htop
mpstat 1

# 生成火焰图
perf record -g -p PID
perf report
```

### 内存分析
```bash
# 内存使用
free -h
vmstat 1

# 进程内存
pmap -x PID
cat /proc/PID/status | grep Vm

# 查找内存泄漏
valgrind --leak-check=full ./program
```

### I/O 分析
```bash
# I/O 统计
iostat -x 1
iotop

# 进程 I/O
pidstat -d 1
cat /proc/PID/io
```

## Web 应用性能

### 压测工具
```bash
# Apache Bench
ab -n 1000 -c 10 https://example.com/

# wrk
wrk -t4 -c100 -d30s https://example.com

# hey
hey -n 1000 -c 50 https://example.com
```

## 性能优化清单

### 代码层面
- [ ] 算法复杂度优化 (O(n²) → O(n log n))
- [ ] 避免不必要的循环
- [ ] 使用缓存 (内存缓存、Redis)
- [ ] 异步/并发处理
- [ ] 减少内存分配

### 数据库层面
- [ ] 添加合适索引
- [ ] 优化查询语句
- [ ] 分页查询避免全表扫描
- [ ] 读写分离
- [ ] 缓存热点数据

### 系统层面
- [ ] 调整系统参数
- [ ] 磁盘 I/O 优化
- [ ] 网络优化
- [ ] 负载均衡

## 文档

- Python profiling: https://docs.python.org/3/library/profile.html
- Node.js profiling: https://nodejs.org/en/docs/guides/simple-profiling/
- clinic.js: https://clinicjs.org/
- FlameGraph: https://www.brendangregg.com/flamegraphs.html
