# Log Analyzer — 常见日志模式库

## 1. Nginx Access Log

```
# 默认 combined 格式
$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"

# 含响应时间（需自定义 log_format）
$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $request_time $upstream_response_time

# 示例
192.168.1.1 - - [10/May/2025:13:55:36 +0800] "GET /api/users HTTP/1.1" 200 1234 "-" "curl/7.68" 0.032 0.030
```

**关注点**:
- `$status` ≥ 500 → 服务端错误
- `$request_time` > 1s → 慢请求
- `$upstream_response_time` > `$request_time` → 上游超时

## 2. Nginx Error Log

```
# 格式
YYYY/MM/DD HH:MM:SS [level] PID#TID: *CID message
client: IP, server: HOST, request: "METHOD PATH PROTO", upstream: "URL", host: "HOST"

# 示例
2025/05/10 13:55:36 [error] 12345#0: *789 connect() failed (111: Connection refused) while connecting to upstream, client: 10.0.0.1, server: example.com, request: "GET /api/users HTTP/1.1", upstream: "http://127.0.0.1:8080/api/users", host: "example.com"
```

**关注点**:
- `[error]`, `[crit]`, `[alert]`, `[emerg]` 级别
- `connect() failed` → 上游服务不可用
- `upstream timed out` → 上游响应慢
- `no live upstreams` → 所有上游都挂了

## 3. JSON 结构化日志

```json
{"level":"error","time":"2025-05-10T13:55:36.123Z","msg":"failed to process request","request_id":"req_abc123","error":"connection refused","service":"user-svc","duration_ms":3012}
{"level":"warn","time":"2025-05-10T13:55:37.456Z","msg":"slow query detected","query":"SELECT * FROM orders","duration_ms":5200,"threshold_ms":1000}
{"level":"info","time":"2025-05-10T13:55:38.789Z","msg":"request completed","request_id":"req_abc123","status":200,"duration_ms":45}
```

**关注点**:
- `level` 字段分级
- `duration_ms` > 阈值 → 性能问题
- `error` 字段 → 错误类型聚合
- 同一 `request_id` 的多个日志可串联追踪

## 4. Java Stacktrace

```
2025-05-10 13:55:36,123 [http-nio-8080-exec-1] ERROR com.example.service.UserService - Failed to get user
java.sql.SQLTimeoutException: Timeout after 30000ms
    at com.zaxxer.hikari.pool.PoolBase.newConnection(PoolBase.java:354)
    at com.zaxxer.hikari.pool.HikariPool$1.call(HikariPool.java:270)
    at java.base/java.util.concurrent.FutureTask.run(FutureTask.java:264)
    at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1136)
    ... 5 common frames omitted
Caused by: com.mysql.cj.exceptions.CJCommunicationsException: Communications link failure
    at com.mysql.cj.protocol.a.NativeSocketConnection.connect(NativeSocketConnection.java:89)
    ... 12 more
```

**关注点**:
- 顶层异常类型 → `SQLTimeoutException`、`NullPointerException`、`OutOfMemoryError`
- `Caused by` → 根因链
- 关键包名 → `com.example` 业务异常 vs 第三方库异常
- 常见框架线程池 → `http-nio`, `scheduling-1`

## 5. System Log (syslog)

```
# 格式
<priority>timestamp hostname process[pid]: message

# 示例
<38>May 10 13:55:36 webserver kernel: [3746593.234] Out of memory: Kill process 12345 (java) score 327 or sacrifice child
<42>May 10 13:55:37 webserver sshd[23456]: Failed password for root from 10.0.0.1 port 22 ssh2
<38>May 10 13:55:38 webserver dockerd[789]: Container 3a4b5c6d7e8f crashed: exit code 137
```

**关注点**:
- `Out of memory` → OOM Killer 介入
- `Failed password` → 暴力破解尝试
- `crashed`, `exit code` → 容器/进程异常终止
- `disk`, `filesystem` → 磁盘相关

## 6. Python 应用日志

```
# 标准 logging 模块输出
2025-05-10 13:55:36,123 - myapp - ERROR - Failed to process webhook: HTTP 500
2025-05-10 13:55:37,456 - myapp - WARNING - Retry attempt 2/3 for order_456
2025-05-10 13:55:38,789 - myapp - INFO - Webhook processed: order_456
Traceback (most recent call last):
  File "/app/worker.py", line 42, in process_webhook
    response = requests.post(url, json=data, timeout=5)
  File "/app/.venv/lib/python3.11/site-packages/requests/api.py", line 60, in post
    return request("post", url, **kwargs)
requests.exceptions.ConnectionError: HTTPConnectionPool: Max retries exceeded
```

**关注点**:
- `ERROR` / `CRITICAL` 级别
- `Retry attempt` → 重试次数和最终成功率
- `Traceback` → 异常调用链
- `HTTP 500`, `ConnectionError`, `Timeout` → 外部依赖故障

## 7. 错误模式速查

| 日志片段 | 可能原因 | 建议操作 |
|----------|----------|----------|
| `connection refused` | 目标服务未启动或端口错误 | 检查服务状态和端口监听 |
| `connection timed out` | 网络不通或防火墙 | 检查网络连通性和安全组 |
| `too many open files` | 文件描述符耗尽 | 调整 ulimit 或检查连接泄漏 |
| `out of memory: Kill process` | 内存不足，OOM Killer | 增加内存或排查内存泄漏 |
| `no space left on device` | 磁盘已满 | 清理日志/临时文件 |
| `request timed out after` | 请求超时 | 优化响应速度或增加超时时间 |
| `failed with code 503` | 服务过载或正在重启 | 检查负载和部署状态 |
| `cannot assign requested address` | 端口耗尽（TIME_WAIT 过多） | 调整内核参数或使用连接池 |
| `SSL routines:WRONG_VERSION_NUMBER` | TLS 版本不匹配 | 检查服务端 TLS 配置 |
| `database is locked` | SQLite 并发写冲突 | 改用连接池或迁移到 PG/MySQL |
