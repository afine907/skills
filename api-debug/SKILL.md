---
name: api-debug
description: API 调试速查。当需要：(1) 使用 curl/httpie 发送请求 (2) 调试 HTTP 问题 (3) 查看状态码 (4) JSON 处理时使用。
---

# API Debug

API 调试命令和技巧速查。

## 快速参考

### curl 基础
```bash
curl https://api.example.com/users
curl -X POST -H "Content-Type: application/json" -d '{"name":"Alice"}' https://api.example.com
curl -H "Authorization: Bearer token" https://api.example.com
curl -u user:pass https://api.example.com
```

### 响应处理
```bash
curl -i https://api.example.com           # 显示响应头
curl -I https://api.example.com           # 只显示响应头
curl -v https://api.example.com           # 详细输出
curl -s https://api.example.com | jq      # 格式化 JSON
```

### httpie
```bash
http https://api.example.com/users
http POST https://api.example.com name=Alice age:=25
http -a user:pass https://api.example.com
```

## 详细参考

- **curl 完整用法**: [references/curl.md](references/curl.md) - 认证、Cookie、超时、SSL
- **httpie 用法**: [references/httpie.md](references/httpie.md) - 更友好的 HTTP 客户端
- **HTTP 状态码**: [references/status-codes.md](references/status-codes.md) - 常见状态码速查
- **jq 处理**: [references/jq.md](references/jq.md) - JSON 处理技巧

## 常见场景

### 认证
```bash
# Bearer Token
curl -H "Authorization: Bearer token123" https://api.example.com

# Basic Auth
curl -u username:password https://api.example.com

# API Key
curl -H "X-API-Key: your-api-key" https://api.example.com
```

### 文件上传
```bash
curl -X POST -F "file=@photo.jpg" https://api.example.com/upload
```

### 调试
```bash
curl -v https://api.example.com           # 详细输出
curl --trace-ascii - https://api.example.com  # 原始请求
```

## 文档

- curl: https://curl.se/docs/
- httpie: https://httpie.io/docs
- jq: https://stedolan.github.io/jq/manual/
