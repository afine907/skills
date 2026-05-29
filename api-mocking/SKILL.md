---
name: api-mocking
description: |
  【API Mock】设计和实现 API Mock 服务，支持前后端并行开发、测试环境模拟、延迟/错误注入。

  触发时机：
  - 用户要求"Mock API"、"模拟接口"
  - 后端接口未就绪，前端需要开发
  - 测试需要模拟各种响应场景

  支持 Mock Server 搭建和代码级 Mock。
category: development
---

# API Mock — API Mock 技能

设计 Mock 服务，支持前后端并行开发和测试场景模拟。


## Goal

设计和实现 API Mock 服务，支持前后端并行开发、测试环境模拟、延迟/错误注入

## Trigger

- 用户要求"Mock API"、"模拟接口"
  - 后端接口未就绪，前端需要开发
  - 测试需要模拟各种响应场景

## Workflow

```
输入 → 处理 → 输出
```
## Mock 方案对比

| 方案 | 适用场景 | 优势 | 劣势 |
|------|----------|------|------|
| Mock Server | 前端独立开发 | 真实 HTTP 请求 | 需要维护服务 |
| 代码级 Mock | 单元测试 | 灵活、快速 | 不测试网络层 |
| API 网关 Mock | 微服务开发 | 无需改代码 | 配置复杂 |
| 录制回放 | 回归测试 | 真实数据 | 数据可能过期 |

## Mock Server 实现

### Python + FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
import time

app = FastAPI(title="Mock Server")

# Mock 数据
USERS_DB = [
    {"id": "1", "name": "张三", "email": "zhangsan@example.com"},
    {"id": "2", "name": "李四", "email": "lisi@example.com"},
    {"id": "3", "name": "王五", "email": "wangwu@example.com"},
]

# 配置
MOCK_DELAY = 0.1  # 模拟延迟
ERROR_RATE = 0.05  # 错误率

@app.middleware("http")
async def mock_delay(request, call_next):
    """模拟网络延迟"""
    await asyncio.sleep(MOCK_DELAY + random.uniform(0, 0.05))
    
    # 随机错误注入
    if random.random() < ERROR_RATE:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )
    
    return await call_next(request)

@app.get("/api/v1/users")
async def list_users(page: int = 1, page_size: int = 10):
    """获取用户列表"""
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "data": USERS_DB[start:end],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": len(USERS_DB),
            "total_pages": (len(USERS_DB) + page_size - 1) // page_size
        }
    }

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str):
    """获取用户详情"""
    user = next((u for u in USERS_DB if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": user}

@app.post("/api/v1/users")
async def create_user(user: dict):
    """创建用户"""
    new_user = {**user, "id": str(len(USERS_DB) + 1)}
    USERS_DB.append(new_user)
    return {"data": new_user}, 201
```

### Node.js + json-server

```bash
# 安装
npm install -g json-server

# db.json
{
  "users": [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
    {"id": 2, "name": "李四", "email": "lisi@example.com"}
  ],
  "posts": [
    {"id": 1, "title": "文章1", "userId": 1},
    {"id": 2, "title": "文章2", "userId": 2}
  ]
}

# 启动
json-server --watch db.json --port 3001
```

## 代码级 Mock

### Python pytest

```python
from unittest.mock import patch, MagicMock
import pytest

# Mock HTTP 请求
@patch('httpx.AsyncClient.get')
async def test_get_user(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"id": "1", "name": "张三"}
    }
    mock_get.return_value = mock_response
    
    result = await get_user("1")
    assert result["name"] == "张三"

# Mock 数据库
@patch('app.db.execute')
async def test_create_user(mock_execute):
    mock_execute.return_value = [{"id": 1}]
    
    result = await create_user({"name": "张三"})
    assert result["id"] == 1
```

### JavaScript MSW (Mock Service Worker)

```javascript
// mocks/handlers.js
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/users', () => {
    return HttpResponse.json({
      data: [
        { id: '1', name: '张三', email: 'zhangsan@example.com' },
        { id: '2', name: '李四', email: 'lisi@example.com' }
      ]
    });
  }),
  
  http.get('/api/v1/users/:id', ({ params }) => {
    const { id } = params;
    return HttpResponse.json({
      data: { id, name: '张三', email: 'zhangsan@example.com' }
    });
  }),
  
  http.post('/api/v1/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      data: { id: '3', ...body }
    }, { status: 201 });
  }),
];
```

## 场景 Mock

### 延迟模拟

```python
# 不同场景的延迟配置
SCENARIOS = {
    "fast": {"delay": 0.05, "description": "快速响应"},
    "normal": {"delay": 0.2, "description": "正常延迟"},
    "slow": {"delay": 2.0, "description": "慢响应"},
    "timeout": {"delay": 30, "description": "超时"},
}

@app.get("/api/v1/scenario/{scenario}")
async def scenario_endpoint(scenario: str):
    config = SCENARIOS.get(scenario)
    if not config:
        raise HTTPException(404, "Scenario not found")
    
    await asyncio.sleep(config["delay"])
    return {"scenario": scenario, "delay": config["delay"]}
```

### 错误模拟

```python
# 随机错误
@app.get("/api/v1/flaky")
async def flaky_endpoint():
    if random.random() < 0.3:  # 30% 错误率
        raise HTTPException(500, "Random error")
    return {"status": "ok"}

# 指定状态码
@app.get("/api/v1/status/{code}")
async def status_endpoint(code: int):
    raise HTTPException(code, f"Simulated {code} error")
```

### 数据生成

```python
from faker import Faker
import factory

fake = Faker('zh_CN')

class UserFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: str(n + 1))
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(fake.phone_number)
    avatar = factory.LazyFunction(fake.image_url)

# 生成测试数据
@app.get("/api/v1/users/generated")
async def generated_users(count: int = 10):
    return {"data": [UserFactory() for _ in range(count)]}
```

## OpenAPI Mock

### Prism Mock Server

```bash
# 安装
npm install -g @stoplight/prism-cli

# 从 OpenAPI 规范启动 Mock
prism mock openapi.yaml

# 支持动态响应
prism mock openapi.yaml --dynamic
```

## 快速使用

```
# 创建 Mock Server
为以下 API 创建 Mock 服务：[粘贴 API 文档]

# 生成测试数据
生成 100 条用户测试数据

# 模拟错误场景
模拟网络超时和服务不可用

# 前端 Mock 配置
配置 React 项目的 API Mock
```

## 参考资料

- MSW 文档: [references/msw.md](references/msw.md)
- 测试数据生成: [references/faker.md](references/faker.md)
