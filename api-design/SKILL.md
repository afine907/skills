---
name: api-design
description: |
  【API设计】根据业务需求设计 RESTful/GraphQL API，输出 OpenAPI 规范文档。包含路由设计、请求/响应 Schema、错误码体系、版本策略。

  触发时机：
  - 用户要求"设计API"、"定义接口"、"写API文档"
  - 需要从数据库 Schema 推导 API 端点
  - 需要统一团队 API 规范

  不依赖外部工具，纯 prompt 模板驱动。
category: development
---

# API Design — API 设计技能

根据业务需求设计专业级 API，输出 OpenAPI 3.0 规范。


## Goal

根据业务需求设计 RESTful/GraphQL API，输出 OpenAPI 规范文档。包含路由设计、请求/响应 Schema、错误码体系、版本策略

## Trigger

- 用户要求"设计API"、"定义接口"、"写API文档"
  - 需要从数据库 Schema 推导 API 端点
  - 需要统一团队 API 规范

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
业务需求 → 资源识别 → 路由设计 → Schema 定义 → 错误码 → 输出规范
```

## Step 1: 资源识别

从需求中提取核心资源：

| 维度 | 分析内容 |
|------|----------|
| 名词提取 | 需求中的业务实体（用户、订单、商品...） |
| 关系映射 | 资源间的一对一、一对多、多对多关系 |
| 操作识别 | CRUD + 业务动作（下单、支付、审核...） |
| 权限模型 | 谁能对什么资源做什么操作 |

## Step 2: 路由设计

遵循 RESTful 规范：

```
GET    /api/v1/{resources}          # 列表查询
POST   /api/v1/{resources}          # 创建资源
GET    /api/v1/{resources}/{id}     # 获取详情
PUT    /api/v1/{resources}/{id}     # 全量更新
PATCH  /api/v1/{resources}/{id}     # 部分更新
DELETE /api/v1/{resources}/{id}     # 删除资源
```

**嵌套资源**：
```
GET    /api/v1/users/{id}/orders   # 用户的订单列表
```

**业务动作**：
```
POST   /api/v1/orders/{id}/submit  # 提交订单
POST   /api/v1/orders/{id}/cancel  # 取消订单
```

### 设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| 名词复数 | 资源用复数形式 | `/users` 不是 `/user` |
| 层级清晰 | 最多嵌套2层 | `/users/{id}/orders` ✓ |
| | | `/users/{id}/orders/{oid}/items/{iid}` ✗ |
| 小写连字符 | 多单词用连字符 | `/user-profiles` |
| 动词后置 | 业务动作用 POST + 动词 | `POST /orders/{id}/refund` |

## Step 3: 请求/响应 Schema

### 请求体设计

```yaml
CreateUserRequest:
  type: object
  required: [email, name]
  properties:
    email:
      type: string
      format: email
      description: 用户邮箱
    name:
      type: string
      minLength: 2
      maxLength: 50
      description: 用户昵称
    role:
      type: string
      enum: [admin, user, guest]
      default: user
```

### 响应体设计

**单个资源**：
```yaml
UserResponse:
  type: object
  properties:
    id:
      type: string
      format: uuid
    email:
      type: string
    name:
      type: string
    created_at:
      type: string
      format: date-time
```

**列表响应**（统一分页）：
```yaml
PaginatedResponse:
  type: object
  properties:
    data:
      type: array
      items: { $ref: '#/components/schemas/UserResponse' }
    pagination:
      type: object
      properties:
        page: { type: integer }
        page_size: { type: integer }
        total: { type: integer }
        total_pages: { type: integer }
```

### 错误响应（统一格式）：
```yaml
ErrorResponse:
  type: object
  properties:
    error:
      type: object
      properties:
        code: { type: string, example: "VALIDATION_ERROR" }
        message: { type: string, example: "邮箱格式不正确" }
        details:
          type: array
          items:
            type: object
            properties:
              field: { type: string }
              message: { type: string }
```

## Step 4: 错误码体系

| HTTP 状态码 | 业务错误码前缀 | 场景 |
|------------|--------------|------|
| 400 | VALIDATION_* | 参数校验失败 |
| 401 | AUTH_* | 未认证 |
| 403 | FORBIDDEN_* | 无权限 |
| 404 | NOT_FOUND_* | 资源不存在 |
| 409 | CONFLICT_* | 资源冲突（重复创建） |
| 422 | BUSINESS_* | 业务逻辑错误 |
| 429 | RATE_LIMIT_* | 请求频率限制 |
| 500 | INTERNAL_* | 服务器内部错误 |

## Step 5: 输出 OpenAPI 规范

输出完整的 `openapi.yaml`：

```yaml
openapi: 3.0.3
info:
  title: {项目名称} API
  version: 1.0.0
  description: {API 描述}
servers:
  - url: /api/v1
paths:
  /users:
    get:
      summary: 获取用户列表
      tags: [用户管理]
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: page_size
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedUserResponse'
components:
  schemas:
    ...（Schema 定义）
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
security:
  - bearerAuth: []
```

## 质量检查清单

输出前确认：
- [ ] 所有资源使用复数名词
- [ ] 统一的分页、排序、过滤参数
- [ ] 统一的错误响应格式
- [ ] 每个端点有清晰的 summary 和 description
- [ ] 请求/响应 Schema 完整定义
- [ ] 认证方式统一（Bearer Token / API Key）
- [ ] 版本策略明确（URL path / Header）
- [ ] 幂等性设计（PUT/DELETE 幂等，POST 非幂等）

## 快速使用

```
# 从需求设计 API
根据以下需求设计 API：[粘贴需求]

# 从数据库 Schema 推导 API
根据以下数据库表设计 RESTful API：[粘贴 DDL]

# 审查现有 API
审查以下 API 设计，指出问题：[粘贴 OpenAPI spec]

# 生成 API 文档
将以下接口说明转为 OpenAPI 规范：[粘贴接口文档]
```

## 参考资料

- OpenAPI 3.0 模板: [references/openapi-template.yaml](references/openapi-template.yaml)
- 错误码规范: [references/error-codes.md](references/error-codes.md)
