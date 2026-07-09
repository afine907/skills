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
---

# Auth Patterns — 认证授权模式

实现安全的认证授权系统，支持多种认证方式和权限模型。


## Goal

实现认证授权模式，包含 JWT、OAuth2、Session、RBAC/ABAC 权限模型、多因素认证

## Trigger

- 用户要求"实现登录"、"JWT认证"、"OAuth2"
  - 需要设计权限系统
  - 需要实现多因素认证

## Workflow

1. **选择认证方式** — JWT / Session / OAuth2 / API Key
2. **设计权限模型** — RBAC / ABAC / 混合
3. **实现认证逻辑** — 登录、Token 签发/验证
4. **实现授权逻辑** — 权限校验、资源访问控制
5. **安全加固** — HTTPS、CORS、Rate Limiting

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
from datetime import datetime, timedelta
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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
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

## Example

```
用户: 实现 JWT 认证 + RBAC 权限控制

输出:
1. 设计 Token 结构 (access + refresh)
2. 实现登录接口 (签发 Token)
3. 实现 Token 验证中间件
4. 设计 RBAC 权限表 (user/role/permission)
5. 实现权限校验装饰器
```

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
