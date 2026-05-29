# API 错误码规范

## 错误响应格式

所有 API 错误必须遵循统一格式：

```json
{
  "error": {
    "code": "CATEGORY_SPECIFIC_ERROR",
    "message": "人类可读的错误描述",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  }
}
```

## HTTP 状态码与业务错误码映射

### 400 Bad Request — 参数错误

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `VALIDATION_ERROR` | 通用参数校验失败 | 必填字段缺失 |
| `VALIDATION_INVALID_FORMAT` | 格式错误 | 邮箱、手机号格式 |
| `VALIDATION_OUT_OF_RANGE` | 超出范围 | 数值超出 min/max |
| `VALIDATION_TOO_LONG` | 内容过长 | 超过 maxLength |
| `VALIDATION_TOO_SHORT` | 内容过短 | 低于 minLength |

### 401 Unauthorized — 认证错误

| 错误码 | 说明 |
|--------|------|
| `AUTH_MISSING_TOKEN` | 未提供 Token |
| `AUTH_INVALID_TOKEN` | Token 无效或已过期 |
| `AUTH_EXPIRED_TOKEN` | Token 已过期 |
| `AUTH_INVALID_CREDENTIALS` | 用户名或密码错误 |

### 403 Forbidden — 权限错误

| 错误码 | 说明 |
|--------|------|
| `FORBIDDEN_ACCESS` | 无权访问该资源 |
| `FORBIDDEN_ACTION` | 无权执行该操作 |
| `FORBIDDEN_ROLE` | 角色权限不足 |

### 404 Not Found — 资源不存在

| 错误码 | 说明 |
|--------|------|
| `NOT_FOUND` | 通用资源不存在 |
| `NOT_FOUND_USER` | 用户不存在 |
| `NOT_FOUND_ORDER` | 订单不存在 |
| `NOT_FOUND_RESOURCE` | 指定资源不存在 |

### 409 Conflict — 资源冲突

| 错误码 | 说明 |
|--------|------|
| `CONFLICT_DUPLICATE` | 资源已存在（如邮箱重复） |
| `CONFLICT_STATE` | 资源状态不允许该操作 |
| `CONFLICT_VERSION` | 版本冲突（乐观锁） |

### 422 Unprocessable Entity — 业务逻辑错误

| 错误码 | 说明 |
|--------|------|
| `BUSINESS_RULE_VIOLATION` | 违反业务规则 |
| `BUSINESS_INSUFFICIENT_BALANCE` | 余额不足 |
| `BUSINESS_QUOTA_EXCEEDED` | 配额超限 |
| `BUSINESS_DEPENDENCY_FAILED` | 依赖操作失败 |

### 429 Too Many Requests — 频率限制

| 错误码 | 说明 |
|--------|------|
| `RATE_LIMIT_EXCEEDED` | 请求频率超限 |
| `RATE_LIMIT_QUOTA` | 配额用尽 |

### 500 Internal Server Error — 服务器错误

| 错误码 | 说明 |
|--------|------|
| `INTERNAL_ERROR` | 通用服务器错误 |
| `INTERNAL_SERVICE_UNAVAILABLE` | 依赖服务不可用 |
| `INTERNAL_TIMEOUT` | 内部超时 |

## 设计原则

1. **错误码用 UPPER_SNAKE_CASE**
2. **错误码前缀表示类别**：VALIDATION_, AUTH_, FORBIDDEN_, NOT_FOUND_, CONFLICT_, BUSINESS_, RATE_LIMIT_, INTERNAL_
3. **message 字段面向用户**，可以展示给前端
4. **details 数组面向开发**，用于定位具体字段问题
5. **不要暴露内部实现细节**（如 SQL 错误、堆栈信息）
