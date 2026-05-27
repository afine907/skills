# Python Service Project Layout

## 标准结构

```
<service>/
├── app/
│   ├── __init__.py
│   ├── main.py               # 入口
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py         # 配置（pydantic-settings）
│   ├── api/
│   │   ├── __init__.py
│   │   └── <entity>.py       # 路由
│   ├── models/
│   │   ├── __init__.py
│   │   └── <entity>.py       # ORM 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── <entity>.py       # Pydantic schema
│   └── services/
│       ├── __init__.py
│       └── <entity>.py       # 业务逻辑
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_<entity>.py
├── alembic/                   # 数据库迁移（如需要）
│   ├── versions/
│   └── env.py
├── alembic.ini
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md
```

## 分层原则

```
api (路由) → services (业务) → models (数据) → database
```

- **api**: 只做 HTTP 相关（参数解析、响应格式化）
- **services**: 纯业务逻辑，不依赖 HTTP 框架
- **models**: SQLAlchemy/ORM 模型定义
- **schemas**: Pydantic 请求/响应校验

## 依赖管理

推荐使用 `pyproject.toml`：

```toml
[project]
name = "my-service"
version = "0.1.0"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]
```
