# 安全扫描检查清单

本文档提供系统化的安全检查清单，供 `/security-scan` 技能执行代码安全扫描时参考。按 OWASP Top 10 和常见漏洞分类。

## 一、注入攻击 (Injection)

### SQL 注入

```python
# 危险：字符串拼接
query = f"SELECT * FROM users WHERE id = {user_id}"
query = "SELECT * FROM users WHERE id = '" + user_id + "'"

# 安全：参数化查询
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# 安全：ORM 查询
User.objects.filter(id=user_id)
```

**检查项**：
- [ ] 所有 SQL 查询使用参数化方式
- [ ] 动态表名/列名使用白名单校验
- [ ] LIKE 查询的通配符已转义
- [ ] ORDER BY 子句不直接拼接用户输入

### 命令注入

```python
# 危险：shell=True + 拼接
os.system(f"ping {user_input}")
subprocess.run(f"ls {user_input}", shell=True)

# 安全：列表参数
subprocess.run(["ping", "-c", "3", user_input])
subprocess.run(["ls", user_input])
```

**检查项**：
- [ ] `subprocess` 不使用 `shell=True`
- [ ] 用户输入不直接拼接到命令字符串
- [ ] 使用 `shlex.quote()` 转义必须拼接的参数

### XSS（跨站脚本）

```javascript
// 危险：直接插入 HTML
element.innerHTML = userInput;

// 安全：使用 textContent
element.textContent = userInput;

// 安全：使用框架的自动转义（React JSX）
return <div>{userInput}</div>;

// 危险：dangerouslySetInnerHTML
return <div dangerouslySetInnerHTML={{__html: userInput}} />;
```

**检查项**：
- [ ] 用户输入在 HTML 输出前已转义
- [ ] 不使用 `innerHTML`、`dangerouslySetInnerHTML`、`v-html`
- [ ] HTTP 响应头包含 `Content-Type: application/json`（API）
- [ ] CSP（Content-Security-Policy）已配置

### 路径遍历

```python
# 危险：直接拼接路径
file_path = os.path.join(base_dir, user_input)

# 安全：校验路径不越界
file_path = os.path.realpath(os.path.join(base_dir, user_input))
if not file_path.startswith(os.path.realpath(base_dir)):
    raise ValueError("Invalid path")
```

**检查项**：
- [ ] 文件路径参数已校验不包含 `..`
- [ ] 使用 `os.path.realpath()` 解析符号链接
- [ ] 文件名使用白名单字符集

---

## 二、认证与会话管理

### 密码安全

```python
# 危险：弱哈希
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# 危险：无盐值
hashed = hashlib.sha256(password.encode()).hexdigest()

# 安全：使用 bcrypt
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**检查项**：
- [ ] 密码使用 bcrypt/scrypt/argon2 哈希
- [ ] 不使用 MD5/SHA1 做密码哈希
- [ ] 哈希包含随机盐值
- [ ] 密码强度要求已实施（长度、复杂度）

### Token 安全

```python
# JWT 验证检查
import jwt

# 危险：不验证签名
payload = jwt.decode(token, options={"verify_signature": False})

# 安全：完整验证
payload = jwt.decode(
    token,
    key=SECRET_KEY,
    algorithms=["HS256"],
    issuer="my-app",
    audience="my-api",
    options={
        "verify_exp": True,
        "verify_iss": True,
        "verify_aud": True,
    }
)
```

**检查项**：
- [ ] JWT 验证签名、过期时间、issuer、audience
- [ ] Token 有过期时间，Refresh Token 有轮换机制
- [ ] Session ID 使用安全随机数生成
- [ ] 登录失败有速率限制

### 权限控制

```python
# 危险：只检查登录状态，不检查资源归属
@app.route("/orders/<order_id>")
@login_required
def get_order(order_id):
    return Order.query.get(order_id)  # 任何登录用户都能访问任何订单

# 安全：检查资源归属
@app.route("/orders/<order_id>")
@login_required
def get_order(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id  # 只能访问自己的订单
    ).first_or_404()
    return order
```

**检查项**：
- [ ] 敏感操作前验证用户权限
- [ ] API 接口检查资源归属（防 IDOR）
- [ ] 管理接口有额外的权限验证
- [ ] 权限检查在业务逻辑之前执行

---

## 三、敏感数据处理

### 硬编码密钥检测模式

```regex
# 常见硬编码模式
password\s*=\s*["'][^"']+["']
api_key\s*=\s*["'][^"']+["']
secret\s*=\s*["'][^"']+["']
token\s*=\s*["'][^"']+["']
AWS_ACCESS_KEY_ID\s*=\s*["']AKIA[^"']+["']
PRIVATE_KEY\s*=\s*["']-----BEGIN
```

**检查项**：
- [ ] 代码中无硬编码密码、API Key、Secret
- [ ] 配置文件中的敏感值通过环境变量注入
- [ ] `.env` 文件在 `.gitignore` 中
- [ ] 历史提交中无泄露的密钥（如有需轮换）

### 日志脱敏

```python
# 危险：日志包含敏感信息
logger.info(f"User login: {email}, password: {password}")
logger.info(f"Processing payment: card={card_number}")

# 安全：脱敏处理
logger.info(f"User login: {mask_email(email)}")
logger.info(f"Processing payment: card={mask_card(card_number)}")

def mask_email(email):
    name, domain = email.split("@")
    return f"{name[0]}***@{domain}"

def mask_card(card):
    return f"****-****-****-{card[-4:]}"
```

**检查项**：
- [ ] 日志不包含密码、Token、密钥
- [ ] 日志不包含完整的身份证号、银行卡号
- [ ] 错误信息不暴露内部实现细节（堆栈、SQL、文件路径）
- [ ] 调试日志在生产环境关闭

### 传输安全

**检查项**：
- [ ] 所有外部通信使用 HTTPS
- [ ] 内部服务间通信使用 mTLS（微服务）
- [ ] 敏感数据不在 URL 参数中传递
- [ ] Cookie 设置 `Secure`、`HttpOnly`、`SameSite` 属性

---

## 四、安全配置

### HTTP 安全头

```nginx
# Nginx 安全头配置
add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

**检查项**：
- [ ] CSP（Content-Security-Policy）已配置
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options` 已设置（防 Clickjacking）
- [ ] `Strict-Transport-Security` 已启用
- [ ] `Referrer-Policy` 已配置

### CORS 配置

```python
# 危险：允许所有来源
CORS_ALLOW_ALL_ORIGINS = True
Access-Control-Allow-Origin: *

# 安全：白名单
CORS_ALLOWED_ORIGINS = [
    "https://myapp.com",
    "https://admin.myapp.com",
]
```

**检查项**：
- [ ] CORS 不使用 `*` 通配符
- [ ] 允许的来源使用白名单
- [ ] 不允许所有 HTTP 方法
- [ ] `Access-Control-Allow-Credentials` 配合具体来源使用

### 依赖安全

```bash
# Python
pip-audit
safety check

# Node.js
npm audit
npx snyk test

# Java
mvn org.owasp:dependency-check-maven:check

# Go
govulncheck ./...
```

**检查项**：
- [ ] 依赖文件无已知高危漏洞
- [ ] 依赖版本锁定（lock 文件已提交）
- [ ] 不使用已废弃的依赖
- [ ] 定期更新依赖

---

## 五、反序列化与输入验证

### 反序列化安全

```python
# 危险：pickle 反序列化不可信数据
import pickle
data = pickle.loads(untrusted_bytes)  # 可执行任意代码

# 安全：使用 JSON
import json
data = json.loads(untrusted_string)

# 安全：使用受限反序列化
from marshmallow import Schema, fields
schema = MySchema()
data = schema.load(untrusted_dict)
```

**检查项**：
- [ ] 不使用 `pickle`/`yaml.load()`/` unserialize()` 反序列化不可信数据
- [ ] 使用 JSON 或受限的反序列化库
- [ ] 反序列化后进行数据校验

### 输入验证

```python
# 危险：信任外部输入
age = int(request.args.get("age"))  # 可能不是数字

# 安全：校验 + 类型转换
from marshmallow import Schema, fields, validate

class UserInput(Schema):
    age = fields.Integer(required=True, validate=validate.Range(min=0, max=150))
    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(max=100))
```

**检查项**：
- [ ] 所有外部输入进行类型校验
- [ ] 字符串输入有长度限制
- [ ] 数值输入有范围限制
- [ ] 枚举值使用白名单校验

---

## 六、扫描优先级

| 优先级 | 类别 | 说明 |
|--------|------|------|
| P0 | SQL 注入、命令注入 | 可导致数据泄露或远程代码执行 |
| P0 | 硬编码密钥 | 可导致系统被直接入侵 |
| P0 | 认证绕过 | 可导致未授权访问 |
| P1 | XSS | 可导致用户数据泄露 |
| P1 | 权限缺失（IDOR） | 可导致越权访问 |
| P1 | 弱加密/哈希 | 可导致数据被破解 |
| P2 | 安全头缺失 | 增加攻击面 |
| P2 | CORS 过宽 | 增加 CSRF 风险 |
| P2 | 依赖漏洞 | 取决于漏洞严重程度 |
| P3 | 日志脱敏 | 合规要求 |
| P3 | 配置加固 | 纵深防御 |

---

## 七、误报排除

以下场景可能产生误报，需结合上下文判断：

1. **测试代码中的硬编码值** — 测试文件中的假密码/Key 通常不是问题
2. **文档/注释中的示例** — 示例代码中的占位符不是真实密钥
3. **哈希值字符串** — 已哈希的值（如 SHA256 输出）不是明文密码
4. **开发环境配置** — `.env.example` 中的示例值通常安全
5. **框架默认安全行为** — 某些框架已内置防护（如 Django 的 CSRF、SQL 参数化）
