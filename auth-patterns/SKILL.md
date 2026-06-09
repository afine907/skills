---
name: auth-patterns
description: |
  【认证授权】实现认证授权模式，包含 JWT、OAuth2、Session、RBAC/ABAC 权限模型、多因素认证。

  触发时机：
  - 用户要求"实现登录"、"JWT认证"、"OAuth2"
  - 需要设计权限系统
  - 需要实现多因素认证

  提供完整的认证授权实现方案。
category: development
user-invocable: false
---

# Auth Patterns — 认证授权模式

实现安全的认证授权系统，支持多种认证方式和权限模型。


## Goal

实现认证授权模式，包含 JWT、OAuth2、Session、RBAC/ABAC 权限模型、多因素认证

## Trigger

- 用户要求"实现登录"、"JWT认证"、"OAuth2"
  - 需要设计权限系统
  - 需要实现多因素认证

## 工作流程

### Step 1: 评估需求 (Assess)

分析系统安全需求：
- 用户类型（内部员工 / 外部用户 / 第三方服务）
- 合规要求（GDPR、等保、SOC2）
- 架构类型（单体 / 前后端分离 / 微服务）
- 是否需要第三方登录

### Step 2: 选择认证方式 (Choose Method)

根据需求应用决策表：

| 场景 | 推荐方式 | 原因 |
|------|----------|------|
| 前后端分离 + 微服务 | JWT | 无状态、可跨服务验证 |
| 传统 Web 应用 | Session | 可控、可即时撤销 |
| 需要第三方登录 | OAuth2 | 标准化协议 |
| 服务间调用 | API Key | 简单、可审计 |
| 内部管理后台（< 10 人） | Session | 简单够用，无需 OAuth2 复杂度 |

### Step 3: 设计 Token 结构 (Design Tokens)

- Access Token：短期（15 分钟），包含用户身份和权限
- Refresh Token：长期（7 天），仅用于刷新 Access Token
- 定义 Claims（用户 ID、角色、权限列表、过期时间）

### Step 4: 实现端点 (Implement Endpoints)

实现核心认证端点：
- `POST /auth/login` - 登录，返回 access_token + refresh_token
- `POST /auth/refresh` - 刷新 token
- `POST /auth/logout` - 登出，使 token 失效
- `POST /auth/mfa/verify` - MFA 验证（如需要）

### Step 5: 添加中间件 (Add Middleware)

- Token 验证中间件（解析 JWT / 查询 Session）
- 权限检查中间件（RBAC 角色校验 / ABAC 属性校验）
- 限流中间件（登录接口防暴力破解）

### Step 6: 安全加固 (Harden)

- 安全 Headers（CSP、HSTS、X-Content-Type-Options）
- CORS 配置（限制允许的源）
- 密码存储（bcrypt/argon2，不使用 MD5/SHA）
- 审计日志（记录所有认证事件）

### Step 7: 测试验证 (Test)

测试以下场景：
- 无效 token、过期 token、篡改 token
- 权限提升尝试（普通用户访问管理员接口）
- 并发登录、并发 token 刷新
- MFA 设备丢失的恢复流程

## 认证方式对比

| 方式 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| JWT | 前后端分离、微服务 | 无状态、可扩展 | 无法即时撤销 |
| Session | 传统 Web 应用 | 可控、可撤销 | 需要存储、跨域复杂 |
| OAuth2 | 第三方登录 | 标准化、安全 | 实现复杂 |
| API Key | 服务间调用 | 简单 | 功能有限 |

## JWT 认证实现

### Token 结构

```python
# Access Token (短期，15分钟)
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin",
  "permissions": ["read:users", "write:users"],
  "iat": 1704067200,
  "exp": 1704068100,
  "jti": "unique_token_id"
}

# Refresh Token (长期，7天)
{
  "sub": "user_id",
  "type": "refresh",
  "iat": 1704067200,
  "exp": 1704672000,
  "jti": "unique_token_id"
}
```

### Python 实现

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await db.get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 登录接口
@router.post("/auth/login")
async def login(email: str, password: str):
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# 刷新 Token
@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    
    new_access_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_access_token, "token_type": "bearer"}
```

## ABAC 权限模型

基于属性的访问控制，通过用户属性、资源属性、环境属性动态计算权限。

### 核心概念

| 维度 | 属性示例 | 说明 |
|------|----------|------|
| 用户属性 | role, department, clearance_level | 用户的身份和资质 |
| 资源属性 | owner, classification, type | 资源的元数据 |
| 环境属性 | time, ip, device_type | 访问时的上下文 |

### Python 实现

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class ABACPolicy:
    name: str
    condition: Callable[[dict], bool]  # 返回 True 表示允许

class ABACEngine:
    def __init__(self):
        self.policies: list[ABACPolicy] = []
    
    def add_policy(self, policy: ABACPolicy):
        self.policies.append(policy)
    
    def evaluate(self, user: dict, resource: dict, environment: dict) -> bool:
        context = {
            "user": user,
            "resource": resource,
            "env": environment
        }
        # 所有策略都必须通过（AND 逻辑）
        return all(p.condition(context) for p in self.policies)

# 定义策略
def only_owner(context: dict) -> bool:
    return context["user"]["id"] == context["resource"]["owner"]

def business_hours(context: dict) -> bool:
    hour = context["env"]["hour"]
    return 9 <= hour <= 18

def high_clearance(context: dict) -> bool:
    return context["user"]["clearance_level"] >= context["resource"]["classification"]

# 使用
engine = ABACEngine()
engine.add_policy(ABACPolicy("only_owner", only_owner))
engine.add_policy(ABACPolicy("business_hours", business_hours))

allowed = engine.evaluate(
    user={"id": "u123", "clearance_level": 3},
    resource={"owner": "u123", "classification": 2},
    environment={"hour": 14}
)
```

### RBAC vs ABAC

| 维度 | RBAC | ABAC |
|------|------|------|
| 权限粒度 | 粗（角色级） | 细（属性级） |
| 实现复杂度 | 低 | 高 |
| 动态性 | 静态角色 | 动态计算 |
| 适用场景 | 通用权限控制 | 复杂业务规则 |

## RBAC 权限模型

### 数据模型

```sql
-- 用户表
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);

-- 角色表
CREATE TABLE roles (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 权限表
CREATE TABLE permissions (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT
);

-- 用户-角色关联
CREATE TABLE user_roles (
    user_id BIGINT REFERENCES users(id),
    role_id BIGINT REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- 角色-权限关联
CREATE TABLE role_permissions (
    role_id BIGINT REFERENCES roles(id),
    permission_id BIGINT REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
```

### 权限检查装饰器

```python
from functools import wraps
from fastapi import HTTPException

def require_permission(permission: str):
    """检查用户是否有指定权限"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            user_permissions = await get_user_permissions(current_user.id)
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """检查用户是否有指定角色"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            user_roles = await get_user_roles(current_user.id)
            if role not in user_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role required: {role}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用
@router.get("/admin/users")
@require_permission("read:users")
async def list_users(current_user = Depends(get_current_user)):
    return await db.get_all_users()

@router.delete("/admin/users/{user_id}")
@require_role("admin")
async def delete_user(user_id: str, current_user = Depends(get_current_user)):
    return await db.delete_user(user_id)
```

## OAuth2 实现

### PKCE Flow（推荐用于 SPA/Mobile）

PKCE（Proof Key for Code Exchange）是 OAuth2 的安全增强，适用于无后端的客户端。

```
流程:
1. 客户端生成 code_verifier（随机字符串）和 code_challenge（SHA256 哈希）
2. 授权请求带 code_challenge
3. 回调时带 code_verifier
4. 服务端验证 code_verifier 匹配 code_challenge
```

```python
import hashlib
import secrets
from fastapi import Request

def generate_pkce_pair() -> tuple[str, str]:
    """生成 PKCE code_verifier 和 code_challenge"""
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    import base64
    code_challenge = base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode()
    return code_verifier, code_challenge

# 存储 code_verifier（到 session 或临时存储）
session["pkce_verifier"] = code_verifier

# 授权请求
authorize_url = (
    f"https://github.com/login/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)

# 回调时验证
async def oauth_callback(code: str, request: Request):
    code_verifier = session["pkce_verifier"]
    # 交换 token 时带上 code_verifier
    token = await exchange_code(code, code_verifier=code_verifier)
```

### GitHub 登录

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='github',
    client_id='your-client-id',
    client_secret='your-client-secret',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

@router.get("/auth/github/login")
async def github_login(request: Request):
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/auth/github/callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get('user', token=token)
    user_data = user_info.json()
    
    # 查找或创建用户
    user = await find_or_create_user(
        email=user_data['email'],
        name=user_data['login'],
        provider='github',
        provider_id=str(user_data['id'])
    )
    
    # 生成 JWT
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token}
```

## 多因素认证 (MFA)

### TOTP 实现

```python
import pyotp
import qrcode

def generate_mfa_secret(user_id: str) -> str:
    """生成 MFA 密钥"""
    secret = pyotp.random_base32()
    # 存储到数据库
    save_user_mfa_secret(user_id, secret)
    return secret

def generate_qr_code(secret: str, email: str) -> bytes:
    """生成二维码"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(email, issuer_name="YourApp")
    qr = qrcode.make(uri)
    return qr.tobytes()

def verify_mfa_code(secret: str, code: str) -> bool:
    """验证 MFA 代码"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

# 登录流程
@router.post("/auth/login")
async def login(email: str, password: str, mfa_code: str = None):
    user = await authenticate_user(email, password)
    
    if user.mfa_enabled:
        if not mfa_code:
            return {"requires_mfa": True, "temp_token": create_temp_token(user.id)}
        if not verify_mfa_code(user.mfa_secret, mfa_code):
            raise HTTPException(status_code=401, detail="Invalid MFA code")
    
    return create_tokens(user)
```

## 安全最佳实践

1. **密码存储**: 使用 bcrypt/argon2，不要用 MD5/SHA
2. **Token 过期**: Access Token 短期(15min)，Refresh Token 长期(7天)
3. **HTTPS**: 所有认证请求必须 HTTPS
4. **CORS**: 限制允许的源
5. **Rate Limiting**: 登录接口限流，防止暴力破解
6. **日志审计**: 记录所有认证事件

## Edge Cases

1. **Token 吊销（登出场景）**：JWT 无法即时撤销，需要维护一个 token 黑名单。在 Redis 中存储被吊销的 token ID（`jti`），TTL 与 token 过期时间一致。验证 token 时先检查黑名单。
2. **Refresh Token 轮换**：每次使用 refresh token 时，签发新的 refresh token 并使旧的失效。在 Redis 中记录有效的 refresh token jti，新 token 签发时删除旧记录。
3. **并发会话管理**：如果允许同一用户多设备登录，每个设备签发独立的 token 对。如果只允许单设备登录，新登录时使该用户所有旧 token 失效。
4. **时钟偏差（Clock Skew）**：多台服务器之间可能存在几秒的时钟偏差。在验证 token 过期时间时，增加 30 秒的缓冲：`if exp + 30 < now: reject`。
5. **MFA 设备丢失**：用户丢失 TOTP 设备时，需要提供恢复方案：(1) 预生成 10 个一次性恢复码，用户安全保存；(2) 通过邮件/短信验证身份后重置 MFA。
6. **OAuth2 提供方宕机**：第三方登录（GitHub/Google）不可用时，实现降级策略：(1) 显示"第三方登录暂时不可用"；(2) 保留邮箱密码登录作为备选；(3) 缓存用户基本信息避免频繁调用 OAuth2 API。
7. **CSRF 攻击防护**：使用 Session 认证时，所有状态变更请求需要 CSRF token。JWT 无状态认证天然免疫 CSRF（但需注意 XSS 防护）。在 cookie 中设置 `SameSite=Strict` 或 `Lax`。

## 输出模板

```markdown
# 认证授权设计文档

## 项目概览
- **系统类型**: {单体 / 前后端分离 / 微服务}
- **用户类型**: {内部员工 / 外部用户 / 混合}
- **合规要求**: {GDPR / 等保 / 无}

## 认证方案选择
- **认证方式**: {JWT / Session / OAuth2 / 混合}
- **选择理由**: {基于需求分析的理由}
- **是否需要 MFA**: {是 / 否}

## Token 设计
- **Access Token 有效期**: {15min / 30min / 自定义}
- **Refresh Token 有效期**: {7d / 30d / 自定义}
- **Token 存储位置**: {Cookie / LocalStorage / 内存}
- **Claims**: {user_id, role, permissions, ...}

## 权限模型
- **模型**: {RBAC / ABAC}
- **角色清单**: {admin, editor, viewer, ...}
- **权限粒度**: {模块级 / 接口级 / 字段级}

## 安全措施
- [ ] 密码使用 bcrypt/argon2 存储
- [ ] HTTPS 强制
- [ ] CORS 限制
- [ ] 登录限流（{n} 次/分钟）
- [ ] 审计日志记录
- [ ] CSRF 防护（如使用 Session）
```

**填写示例**（前后端分离 SaaS）：

```markdown
# 认证授权设计文档

## 项目概览
- **系统类型**: 前后端分离（React + FastAPI）
- **用户类型**: 外部用户（SaaS 客户）
- **合规要求**: GDPR

## 认证方案选择
- **认证方式**: JWT（Access + Refresh Token）
- **选择理由**: 前后端分离，需无状态认证，支持多实例部署
- **是否需要 MFA**: 是（可选，用户自行开启）

## Token 设计
- **Access Token 有效期**: 15 分钟
- **Refresh Token 有效期**: 7 天
- **Token 存储位置**: HttpOnly Cookie（防 XSS）
- **Claims**: sub, email, role, permissions, jti, exp, iat

## 权限模型
- **模型**: RBAC
- **角色清单**: super_admin, admin, editor, viewer
- **权限粒度**: 接口级（read:users, write:users, ...）

## 安全措施
- [x] 密码使用 bcrypt 存储
- [x] HTTPS 强制
- [x] CORS 限制（仅允许 *.example.com）
- [x] 登录限流（5 次/分钟）
- [x] 审计日志记录
- [x] CSRF 防护（SameSite=Lax）
```

## 不适用

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 需要即时 Token 撤销 | JWT 无法即时撤销 | 使用 Session 认证 |
| 内部管理后台 < 10 人 | OAuth2 带来不必要的复杂度 | Session + 简单角色 |
| 低风险只读公开应用 | MFA 增加用户摩擦，收益低 | 仅使用密码认证 |
| RBAC 不够用（复杂资源级权限） | 角色粒度过粗 | 升级为 ABAC 或 ReBAC |

**重定向**：
- 密码哈希存储：使用 bcrypt 或 argon2 库，不要自行实现哈希算法。
- API 限流：参考 rate-limiting 模式进行接口限流设计。

## 快速使用

```
# 实现 JWT 认证
实现基于 JWT 的用户认证系统

# 设计 RBAC 权限
设计角色权限管理系统

# 实现 OAuth2 登录
实现 GitHub/Google 第三方登录

# 添加 MFA
为系统添加多因素认证
```

## 参考资料

- JWT 最佳实践: [references/jwt-best-practices.md](references/jwt-best-practices.md)
- OAuth2 流程: [references/oauth2-flows.md](references/oauth2-flows.md)
