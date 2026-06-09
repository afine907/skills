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
user-invocable: false
---

# Performance Profiling — 性能分析技能

系统性性能分析，从指标采集到瓶颈定位再到优化方案。


## Goal

系统性性能分析和优化，包含 CPU/内存/IO 分析、瓶颈定位、优化方案、监控指标

## Trigger

- 用户要求"性能分析"、"性能优化"、"分析瓶颈"
  - 系统响应慢需要定位原因
  - 需要建立性能监控

## 工作流程

1. **定义问题和症状** -- 明确性能问题表现：响应慢？CPU 高？内存泄漏？磁盘 IO 高？网络延迟大？确定影响范围（单个接口 / 全局 / 特定用户群）。收集用户报告的 P50/P95/P99 延迟数据作为基线。
2. **症状分类与工具选择** -- if CPU 使用率 > 70% -> Python: `cProfile` / `py-spy`；Node.js: `--prof` / clinic.js。if 内存持续增长 -> Python: `memory_profiler` / `tracemalloc`；Node.js: `--heapt-snapshot`。if 响应慢但 CPU 正常 -> 检查数据库慢查询（EXPLAIN ANALYZE）、网络延迟（mtr）、IO（iostat）。if 需要生产环境分析 -> 优先使用低开销工具（py-spy、perf）避免影响服务。
3. **采集基线指标** -- 运行诊断工具采集热点数据。对数据库使用 `EXPLAIN ANALYZE` 分析查询计划。生成火焰图（`py-spy record` / `perf`）进行可视化分析。记录当前的 P50/P95/P99、吞吐量、错误率作为优化前基线。
4. **定位瓶颈** -- 分析火焰图最宽的"平顶山"函数，确认 Self Time 最高的函数。检查数据库索引使用率和全表扫描。排查 N+1 查询、重复计算、内存泄漏。将瓶颈按影响程度排序（高/中/低）。
5. **实施优化** -- 优先处理影响最大的瓶颈。常见优化：添加缺失索引、缓存重复计算（`@lru_cache`）、使用生成器替代大列表、优化算法复杂度。每完成一个优化，重新运行测试确认效果。
6. **验证和迭代** -- 重新测量优化后的指标，与基线对比。if 改善 < 10% -> 尝试其他优化方向或确认瓶颈判断是否正确。if 出现新问题（如内存上升、错误率增加）-> 回退并分析。将优化后的结果记录为新基线，持续监控防止退化。

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

### 火焰图解读指南

**火焰图结构**：
- **X 轴**: 采样次数（宽度表示占用 CPU 时间的比例）
- **Y 轴**: 调用栈深度（底部是入口，顶部是当前执行函数）
- **颜色**: 随机分配，无特殊含义

**如何定位瓶颈**：

1. **找最宽的"平顶山"** — 这是 CPU 时间消耗最多的函数
2. **查看调用路径** — 从底部到顶部，看是什么调用链导致了这个函数
3. **区分应用代码和库代码** — 应用代码是优化重点
4. **关注 Self Time** — 函数自身消耗的时间（非子调用）

**常见模式**：

| 模式 | 现象 | 优化方向 |
|------|------|----------|
| 单一宽峰 | 某个函数占大部分 CPU | 优化该函数算法 |
| 锯齿状 | 多个函数交替执行 | 检查锁竞争或上下文切换 |
| 深调用栈 | 调用层级很深 | 考虑扁平化或缓存 |
| 浅而宽 | 循环密集 | 向量化或并行化 |

**Python 火焰图**：

```bash
# 使用 py-spy
py-spy record -o flamegraph.svg --pid 12345

# 或使用 Austin + flameprof
pip install austin
austin -o profile.austin python script.py

# 转换为火焰图
pip install flameprof
flameprof profile.austin > flamegraph.svg
```

## 压测工具

### k6（推荐）

```bash
# 安装
# macOS: brew install k6
# Linux: sudo snap install k6

# 基本压测
k6 run script.js

# 脚本示例
```

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // 30 秒内升到 20 用户
    { duration: '1m', target: 20 },   // 保持 20 用户 1 分钟
    { duration: '30s', target: 0 },   // 30 秒内降到 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% 请求 < 500ms
    http_req_failed: ['rate<0.01'],    // 错误率 < 1%
  },
};

export default function () {
  const res = http.get('http://localhost:3000/api/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Locust（Python）

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)  # 权重 3
    def index(self):
        self.client.get("/")

    @task(1)  # 权重 1
    def about(self):
        self.client.get("/about")

    def on_start(self):
        """用户启动时执行"""
        self.client.post("/login", json={
            "username": "test",
            "password": "pass"
        })
```

```bash
# 运行压测
locust -f locustfile.py --host=http://localhost:3000

# 无界面模式
locust -f locustfile.py --host=http://localhost:3000 \
  --headless -u 100 -r 10 --run-time 1m
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

## Edge Cases / 常见陷阱

| 场景 | 现象 | 诊断方法 | 解决方案 |
|------|------|----------|----------|
| Profiler 开销导致结果失真 | 优化后性能反而变差，或 profiling 期间服务变慢 | 对比 profiling 开启前后的响应时间；检查 profiler 的 CPU 开销 | 生产环境使用采样式 profiler（py-spy、perf）而非插入式（cProfile），避免在高峰期 profiling |
| 容器化环境无法安装 Profiler | `apt-get install` 失败或容器内无 perf 权限 | 检查容器是否基于 scratch/alpine 等精简镜像 | 使用 sidecar 模式运行 profiler，或使用 py-spy（纯 Python，无需系统权限），或在宿主机上 profiling |
| 火焰图结果模糊 | 无法确定瓶颈在哪，多个函数占用比例相近 | 检查 Self Time 是否分散在多个函数 | 聚焦应用代码（排除库代码），考虑是否有 I/O 等待未被捕获（需要结合 iostat/tcpdump 分析） |
| 内存泄漏难以复现 | 内存缓慢增长，但短时间内无法观测 | 使用 `tracemalloc` 追踪内存分配，对比两次快照 | 增加采样间隔和监控时间；使用 `objgraph` 分析对象引用链 |
| 优化收益递减 | 反复优化但 P99 无法进一步降低 | 确认是否已触及系统资源上限（CPU/网络/磁盘 IO） | 考虑架构层面优化（缓存、异步、水平扩展），而非继续代码级优化 |
| 数据库慢查询但索引已存在 | EXPLAIN 显示使用了索引，但查询仍然慢 | 检查是否为隐式类型转换、函数包裹索引列、或数据量变化导致索引失效 | 重新分析执行计划，检查 WHERE 条件是否匹配索引列类型，考虑添加覆盖索引 |
| 异步代码的阻塞点被忽略 | async 函数内部调用了同步阻塞代码 | 检查火焰图中事件循环阻塞的部分 | 将阻塞调用替换为 `asyncio.to_thread()` 或使用异步版本的库 |
| 跨语言性能问题定位困难 | Node.js 调用 Python/C++ 扩展时性能差 | 分别对各语言层进行 profiling | 使用语言特定工具分析各自热点，注意跨语言调用的序列化开销 |

## 不适用场景

| 场景 | 原因 | 建议使用 |
|------|------|----------|
| 负载测试 / 压力测试 | 本技能关注代码级性能分析，非系统级压力测试 | 使用 k6、Locust、JMeter 等负载测试工具（参见 [references/load-test.md](references/load-test.md)） |
| Java 应用性能分析 | 本技能不覆盖 JVM 生态 | 使用 JMH、async-profiler、VisualVM、JProfiler |
| Go 应用性能分析 | 本技能不覆盖 Go 生态 | 使用 `go tool pprof`、`go test -bench` |
| .NET 应用性能分析 | 本技能不覆盖 .NET 生态 | 使用 dotnet-trace、dotnet-counters、PerfView |
| 前端性能优化（浏览器端） | 本技能聚焦后端/系统级分析 | 使用 Lighthouse、Chrome DevTools Performance、Web Vitals |
| APM 全链路监控平台 | 本技能是单次分析工具，非持续监控平台 | 使用 Datadog、New Relic、SkyWalking、OpenTelemetry |
| 代码审查 / 架构评估 | 本技能不替代代码质量和架构审查 | 使用 code-review 或 explain-code 技能 |
| 安全审计 | 本技能不覆盖安全相关的性能问题（如 ReDoS） | 使用 security-scanning 技能 |

## 参考资料

- Python 分析: [references/python.md](references/python.md)
- Node.js 分析: [references/nodejs.md](references/nodejs.md)
- 数据库优化: [references/database.md](references/database.md)
- 系统性能: [references/system.md](references/system.md)
- Web 压测: [references/load-test.md](references/load-test.md)
