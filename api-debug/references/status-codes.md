# HTTP 状态码速查

## 2xx 成功

| 状态码 | 说明 |
|--------|------|
| 200 OK | 请求成功 |
| 201 Created | 资源创建成功 |
| 202 Accepted | 请求已接受，处理中 |
| 204 No Content | 成功但无返回内容 |
| 206 Partial Content | 部分内容 (断点续传) |

## 3xx 重定向

| 状态码 | 说明 |
|--------|------|
| 301 Moved Permanently | 永久重定向 |
| 302 Found | 临时重定向 |
| 304 Not Modified | 未修改 (缓存有效) |
| 307 Temporary Redirect | 临时重定向 (保持方法) |
| 308 Permanent Redirect | 永久重定向 (保持方法) |

## 4xx 客户端错误

| 状态码 | 说明 |
|--------|------|
| 400 Bad Request | 请求格式错误 |
| 401 Unauthorized | 未认证 |
| 403 Forbidden | 无权限 |
| 404 Not Found | 资源不存在 |
| 405 Method Not Allowed | 方法不允许 |
| 409 Conflict | 资源冲突 |
| 422 Unprocessable Entity | 语义错误 |
| 429 Too Many Requests | 请求过多 |

## 5xx 服务端错误

| 状态码 | 说明 |
|--------|------|
| 500 Internal Server Error | 服务器内部错误 |
| 502 Bad Gateway | 网关错误 |
| 503 Service Unavailable | 服务不可用 |
| 504 Gateway Timeout | 网关超时 |
