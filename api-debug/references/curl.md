# curl 完整用法

## 基本请求

```bash
# GET
curl https://api.example.com/users

# POST/PUT/DELETE
curl -X POST https://api.example.com/users
curl -X PUT https://api.example.com/users/1
curl -X DELETE https://api.example.com/users/1
```

## 请求头

```bash
curl -H "Content-Type: application/json" https://api.example.com
curl -H "Authorization: Bearer token" https://api.example.com
curl -H "Content-Type: application/json" -H "Authorization: Bearer token" https://api.example.com
```

## 请求体

```bash
# JSON
curl -X POST -H "Content-Type: application/json" -d '{"name":"Alice"}' https://api.example.com

# 从文件读取
curl -X POST -d @data.json https://api.example.com

# 表单
curl -X POST -d "name=Alice&age=25" https://api.example.com

# 文件上传
curl -X POST -F "file=@photo.jpg" -F "name=Alice" https://api.example.com/upload
```

## 认证

```bash
# Basic Auth
curl -u username:password https://api.example.com

# Bearer Token
curl -H "Authorization: Bearer token123" https://api.example.com

# API Key
curl -H "X-API-Key: your-api-key" https://api.example.com
```

## Cookie

```bash
# 发送 Cookie
curl -b "session=abc123" https://api.example.com

# 保存 Cookie
curl -c cookies.txt https://api.example.com/login

# 使用保存的 Cookie
curl -b cookies.txt https://api.example.com/profile
```

## 超时和重试

```bash
curl --connect-timeout 10 https://api.example.com
curl --max-time 30 https://api.example.com
curl --retry 3 https://api.example.com
curl --retry 3 --retry-delay 5 https://api.example.com
```

## SSL/TLS

```bash
# 忽略证书验证 (仅测试)
curl -k https://self-signed.badssl.com

# 指定证书
curl --cert client.pem --key key.pem https://api.example.com
```

## 重定向

```bash
curl -L https://example.com              # 跟随重定向
curl -L --max-redirs 5 https://example.com
```

## 代理

```bash
curl -x http://proxy:8080 https://api.example.com
curl --socks5 127.0.0.1:1080 https://api.example.com
```

## 响应处理

```bash
curl -i https://api.example.com           # 显示响应头
curl -I https://api.example.com           # 只显示响应头
curl -v https://api.example.com           # 详细输出
curl --trace-ascii - https://api.example.com  # 原始请求
curl -s https://api.example.com           # 静默模式
curl -o response.json https://api.example.com  # 保存响应
```
