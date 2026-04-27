---
name: api-debug
description: API 调试工具速查，覆盖 curl、httpie、HTTP 状态码、请求调试技巧。
homepage: https://curl.se/
metadata: {"clawdbot":{"emoji":"🔌","requires":{"bins":["curl"]}}}
---

# API Debug

API 调试命令和技巧速查。

## curl 基础

### 基本请求
```bash
# GET 请求
curl https://api.example.com/users
curl -X GET https://api.example.com/users

# POST 请求
curl -X POST https://api.example.com/users

# 指定方法
curl -X PUT https://api.example.com/users/1
curl -X DELETE https://api.example.com/users/1
curl -X PATCH https://api.example.com/users/1
```

### 请求头
```bash
# 添加请求头
curl -H "Content-Type: application/json" https://api.example.com
curl -H "Authorization: Bearer token123" https://api.example.com

# 多个请求头
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer token123" \
     https://api.example.com
```

### 请求体
```bash
# JSON 数据
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","age":25}' \
  https://api.example.com/users

# 从文件读取
curl -X POST -d @data.json https://api.example.com/users

# 表单数据
curl -X POST \
  -d "name=Alice&age=25" \
  https://api.example.com/users

# multipart/form-data
curl -X POST \
  -F "file=@photo.jpg" \
  -F "name=Alice" \
  https://api.example.com/upload
```

### 响应处理
```bash
# 显示响应头
curl -i https://api.example.com

# 只显示响应头
curl -I https://api.example.com

# 显示详细过程 (调试用)
curl -v https://api.example.com

# 格式化 JSON 输出
curl -s https://api.example.com | jq
curl -s https://api.example.com | python -m json.tool

# 保存响应
curl -o response.json https://api.example.com
```

### 认证
```bash
# Basic Auth
curl -u username:password https://api.example.com

# Bearer Token
curl -H "Authorization: Bearer token123" https://api.example.com

# API Key
curl -H "X-API-Key: your-api-key" https://api.example.com
curl "https://api.example.com?api_key=your-api-key"
```

### Cookie
```bash
# 发送 Cookie
curl -b "session=abc123" https://api.example.com

# 保存 Cookie
curl -c cookies.txt https://api.example.com/login

# 使用保存的 Cookie
curl -b cookies.txt https://api.example.com/profile
```

### 超时和重试
```bash
# 连接超时
curl --connect-timeout 10 https://api.example.com

# 最大时间
curl --max-time 30 https://api.example.com

# 重试
curl --retry 3 https://api.example.com
curl --retry 3 --retry-delay 5 https://api.example.com
```

### SSL/TLS
```bash
# 忽略证书验证 (仅测试用)
curl -k https://self-signed.badssl.com

# 指定证书
curl --cert client.pem --key key.pem https://api.example.com
```

### 重定向
```bash
# 跟随重定向
curl -L https://example.com

# 限制重定向次数
curl -L --max-redirs 5 https://example.com
```

## httpie (更友好的 HTTP 客户端)

### 安装和基础
```bash
# 安装
pip install httpie

# GET 请求
http GET https://api.example.com/users
http https://api.example.com/users

# POST 请求
http POST https://api.example.com/users name=Alice age:=25

# 其他方法
http PUT https://api.example.com/users/1 name=Bob
http DELETE https://api.example.com/users/1
```

### 请求项语法
```bash
# 请求头: Header:Value
http https://api.example.com Authorization:Bearer\ token

# 查询参数: param==value
http https://api.example.com/users page==1 limit==20

# JSON 字段: field=value (字符串), field:=value (原生类型)
http POST https://api.example.com/users \
  name=Alice \
  age:=25 \
  active:=true

# 表单字段: field=value
http --form POST https://api.example.com/upload file@photo.jpg
```

### 认证
```bash
# Basic Auth
http -a user:pass https://api.example.com

# Bearer Token
http https://api.example.com Authorization:"Bearer token123"

# 使用 session (保存认证)
http --session=user -a user:pass https://api.example.com/login
http --session=user https://api.example.com/profile
```

### 输出控制
```bash
# 只显示响应头
http -h https://api.example.com

# 只显示响应体
http -b https://api.example.com

# 显示完整请求和响应
http -v https://api.example.com

# 下载文件
http --download https://example.com/file.zip
```

## HTTP 状态码速查

### 2xx 成功
| 状态码 | 说明 |
|--------|------|
| 200 OK | 请求成功 |
| 201 Created | 资源创建成功 |
| 202 Accepted | 请求已接受，处理中 |
| 204 No Content | 成功但无返回内容 |

### 4xx 客户端错误
| 状态码 | 说明 |
|--------|------|
| 400 Bad Request | 请求格式错误 |
| 401 Unauthorized | 未认证 |
| 403 Forbidden | 无权限 |
| 404 Not Found | 资源不存在 |
| 405 Method Not Allowed | 方法不允许 |
| 429 Too Many Requests | 请求过多 |

### 5xx 服务端错误
| 状态码 | 说明 |
|--------|------|
| 500 Internal Server Error | 服务器内部错误 |
| 502 Bad Gateway | 网关错误 |
| 503 Service Unavailable | 服务不可用 |
| 504 Gateway Timeout | 网关超时 |

## 调试技巧

### 查看完整请求
```bash
# curl 详细模式
curl -v https://api.example.com

# 查看原始请求
curl --trace-ascii - https://api.example.com

# httpie 详细模式
http -v https://api.example.com
```

### 测试响应时间
```bash
# curl 计时
curl -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s https://api.example.com
```

### 测试并发
```bash
# 使用 ab (Apache Bench)
ab -n 100 -c 10 https://api.example.com/

# 使用 wrk
wrk -t4 -c100 -d30s https://api.example.com
```

## jq JSON 处理

### 常用 jq 操作
```bash
# 格式化
curl -s https://api.example.com/users | jq

# 提取字段
curl -s https://api.example.com/users | jq '.name'

# 数组操作
curl -s https://api.example.com/users | jq '.[].name'

# 过滤
curl -s https://api.example.com/users | jq '.[] | select(.age > 25)'

# 排序
curl -s https://api.example.com/users | jq 'sort_by(.age)'
```

## 常见 API 测试场景

### REST API CRUD
```bash
# 创建 (POST)
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"Alice"}' https://api.example.com/users

# 读取 (GET)
curl https://api.example.com/users/1

# 更新 (PUT/PATCH)
curl -X PUT -H "Content-Type: application/json" \
  -d '{"name":"Bob"}' https://api.example.com/users/1

# 删除 (DELETE)
curl -X DELETE https://api.example.com/users/1
```

### 文件上传下载
```bash
# 上传文件
curl -X POST \
  -F "file=@photo.jpg" \
  https://api.example.com/upload

# 下载文件
curl -O https://example.com/file.zip

# 断点续传
curl -C - -O https://example.com/large-file.zip
```

## 最佳实践

1. **使用 -v/--trace 调试**：查看完整请求/响应
2. **格式化输出**：配合 jq 使用
3. **使用环境变量**：`curl -H "Authorization: Bearer $TOKEN"`
4. **注意敏感信息**：不要在命令行暴露密码
5. **检查 HTTPS**：生产环境不要用 -k

## 文档

- curl 文档: https://curl.se/docs/
- httpie 文档: https://httpie.io/docs
- jq 手册: https://stedolan.github.io/jq/manual/
