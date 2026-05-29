---
name: api-debug
description: |
  【API调试】API 调试实战指南，包含请求构造、响应分析、问题定位、性能诊断、安全测试。

  触发时机：
  - 用户要求"调试API"、"测试接口"
  - API 返回异常需要排查
  - 需要构造复杂请求

  支持 curl/httpie/Postman/代码调试。
category: reference
---

# API Debug — API 调试实战指南

从请求构造到问题定位的完整 API 调试技能。


## Goal

API 调试实战指南，包含请求构造、响应分析、问题定位、性能诊断、安全测试

## Trigger

- 用户要求"调试API"、"测试接口"
  - API 返回异常需要排查
  - 需要构造复杂请求

## Workflow

```
输入 → 处理 → 输出
```
## 调试流程

```
问题描述 → 请求构造 → 发送请求 → 响应分析 → 问题定位 → 修复验证
```

## 请求构造

### curl 进阶用法

```bash
# 基础 GET
curl https://api.example.com/users

# POST JSON
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","email":"zhangsan@example.com"}'

# 带认证
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  https://api.example.com/users/me

# Basic Auth
curl -u username:password https://api.example.com/admin

# 带 Cookie
curl -b "session=abc123" https://api.example.com/dashboard

# 文件上传
curl -X POST https://api.example.com/upload \
  -F "file=@./photo.jpg" \
  -F "description=Profile photo"

# 下载文件
curl -O https://api.example.com/files/report.pdf

# 超时设置
curl --connect-timeout 5 --max-time 30 https://api.example.com

# 重试
curl --retry 3 --retry-delay 2 https://api.example.com

# 保存响应头
curl -D headers.txt https://api.example.com

# 跟随重定向
curl -L https://api.example.com/redirect

# 忽略 SSL 证书（调试用）
curl -k https://self-signed.example.com

# 详细调试
curl -v https://api.example.com 2>&1 | head -50
```

### httpie 更友好

```bash
# GET
http https://api.example.com/users

# POST（自动 JSON）
http POST https://api.example.com/users \
  name=张三 email=zhangsan@example.com

# 带认证
http -a username:password https://api.example.com/admin

# 带 Token
http https://api.example.com/users \
  Authorization:"Bearer token123"

# 上传文件
http --form POST https://api.example.com/upload \
  file@./photo.jpg

# 下载
http --download https://api.example.com/files/report.pdf

# 只看响应头
http --headers https://api.example.com

# 详细输出
http --verbose https://api.example.com
```

## 响应分析

### 状态码速查

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | 正常 |
| 201 | 已创建 | POST 成功 |
| 204 | 无内容 | DELETE 成功 |
| 301 | 永久重定向 | URL 变更 |
| 302 | 临时重定向 | 需要登录 |
| 400 | 请求错误 | 参数格式错 |
| 401 | 未认证 | Token 缺失/过期 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 未找到 | URL 错误或资源不存在 |
| 405 | 方法不允许 | GET/POST 用错 |
| 409 | 冲突 | 重复创建 |
| 422 | 不可处理 | 业务逻辑错误 |
| 429 | 请求过多 | 触发限流 |
| 500 | 服务器错误 | 后端 Bug |
| 502 | 网关错误 | 上游服务挂了 |
| 503 | 服务不可用 | 服务过载/维护 |

### 响应头分析

```bash
# 查看完整响应
curl -i https://api.example.com/users

# 重要响应头
Content-Type: application/json      # 响应格式
Cache-Control: max-age=3600         # 缓存策略
X-RateLimit-Remaining: 99           # 剩余请求次数
X-Request-Id: abc123                # 请求追踪 ID
Set-Cookie: session=xyz; HttpOnly   # Cookie 设置
```

### JSON 处理

```bash
# 格式化 JSON
curl -s https://api.example.com/users | jq .

# 提取特定字段
curl -s https://api.example.com/users | jq '.data[].name'

# 过滤
curl -s https://api.example.com/users | jq '.data[] | select(.age > 18)'

# 统计
curl -s https://api.example.com/users | jq '.data | length'

# 转为 CSV
curl -s https://api.example.com/users | jq -r '.data[] | [.id, .name, .email] | @csv'
```

## 常见问题排查

### 1. 认证问题 (401)

```bash
# 检查 Token 是否存在
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/me

# 解码 JWT
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq .

# 检查 Token 过期时间
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq '.exp | todate'

# 重新获取 Token
curl -X POST https://api.example.com/auth/login \
  -d '{"email":"user@example.com","password":"pass"}'
```

### 2. 权限问题 (403)

```bash
# 检查用户角色
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/me | jq '.role'

# 检查所需权限
# 查看 API 文档或后端代码
```

### 3. 参数问题 (400/422)

```bash
# 检查请求体
curl -v -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"","email":"invalid"}' 2>&1

# 查看详细错误
curl -s -X POST https://api.example.com/users \
  -d '{"name":"","email":"invalid"}' | jq '.error.details'
```

### 4. 网络问题

```bash
# DNS 解析
nslookup api.example.com
dig api.example.com

# 连接测试
telnet api.example.com 443

# 路由追踪
traceroute api.example.com

# SSL 证书检查
openssl s_client -connect api.example.com:443 -servername api.example.com
```

### 5. 性能问题

```bash
# 测量响应时间
curl -o /dev/null -s -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" https://api.example.com

# 多次测量取平均
for i in {1..10}; do
  curl -o /dev/null -s -w "%{time_total}\n" https://api.example.com
done | awk '{sum+=$1} END {print sum/NR}'
```

## 调试工具对比

| 工具 | 优势 | 适用场景 |
|------|------|----------|
| curl | 无处不在、脚本化 | 自动化测试、CI |
| httpie | 人性化输出 | 日常调试 |
| Postman | GUI、集合管理 | 团队协作、复杂场景 |
| Insomnia | 轻量、GraphQL 支持 | GraphQL 调试 |
| HTTPie Desktop | 现代 UI | 可视化调试 |

## 快速使用

```
# 调试 401 错误
我的 API 返回 401，帮我排查

# 构造复杂请求
帮我构造一个带文件上传和认证的 POST 请求

# 分析响应
这个 API 响应很慢，帮我分析原因

# 测试认证流程
帮我测试完整的登录-访问-刷新 Token 流程
```

## 参考资料

- curl 完整用法: [references/curl.md](references/curl.md)
- httpie 用法: [references/httpie.md](references/httpie.md)
- HTTP 状态码: [references/status-codes.md](references/status-codes.md)
- jq 处理: [references/jq.md](references/jq.md)
