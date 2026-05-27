---
name: python-service-creator
category: development
description: |
  Python 后端服务脚手架生成器。自然语言描述 → 完整 Python 项目目录。
  触发场景：用户要求"创建 FastAPI 服务"、"搭建 Python 后端"、"初始化 Flask 项目"、"生成 Python API"。
  关键词：fastapi, flask, django, python backend, python api, python service, uvicorn。
---

# Python Service — Python 后端服务脚手架生成

自然语言描述 → 完整 Python 项目目录（代码 + 配置 + Dockerfile），一次输出。

不适用：数据分析脚本（非服务）；已有项目的重构；纯前端。

## 工作流程

```
描述需求 → 选择框架 → 确认配置 → 生成项目 → 验证导入
```

### Step 1: 收集需求

从用户描述中提取：
- **服务名称**：用于目录名
- **框架偏好**：FastAPI（默认）/ Flask / Django
- **端口**：默认 8000
- **数据库**：PostgreSQL / MySQL / SQLite / 无
- **功能模块**：用户提到的业务实体

如果信息不足，询问 1-2 个关键问题，不要过度追问。

### Step 2: 选择框架

| 框架 | 适用场景 | 特点 |
|------|----------|------|
| **FastAPI** (默认) | 现代 API 服务 | 异步、自动文档、Pydantic 校验 |
| **Flask** | 轻量服务 | 简单灵活、扩展丰富 |

读取对应的模板文件：
- FastAPI → [references/fastapi-template.md](references/fastapi-template.md)
- Flask → [references/flask-template.md](references/flask-template.md)

### Step 3: 生成项目文件

标准目录布局（参考 [references/project-layout.md](references/project-layout.md)）：

```
<service-name>/
├── app/
│   ├── __init__.py
│   ├── main.py               # 入口：app 创建、lifespan、CORS
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # pydantic-settings 配置
│   ├── api/
│   │   ├── __init__.py
│   │   └── <entity>.py        # 路由
│   ├── models/
│   │   ├── __init__.py
│   │   └── <entity>.py        # SQLAlchemy 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── <entity>.py        # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── <entity>.py        # 业务逻辑
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_<entity>.py
├── alembic/                   # 数据库迁移（如需要数据库）
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md
```

**必生成文件**：
1. `app/main.py` — App 创建、路由注册、CORS、lifespan
2. `app/core/config.py` — pydantic-settings 配置类
3. `app/api/*.py` — 每个实体一个路由文件
4. `app/models/*.py` — SQLAlchemy 模型（如需要数据库）
5. `app/schemas/*.py` — Pydantic 请求/响应 schema
6. `app/services/*.py` — 业务逻辑层
7. `pyproject.toml` — 依赖和工具配置
8. `Dockerfile` — 多阶段构建（参考 [references/dockerfile-patterns.md](references/dockerfile-patterns.md)）
9. `.env.example` — 环境变量模板
10. `README.md` — 项目说明

### Step 4: 验证

生成完成后检查 Python 语法：
```bash
cd <service-name> && python -m py_compile app/main.py
```

报告生成结果。

## 输出格式

完成后输出：

```markdown
## 项目已生成

**服务**: <name>
**框架**: <fastapi/flask>
**端口**: <port>

### 文件结构
<tree>

### 启动方式

    # 安装依赖
    pip install -e .

    # 启动开发服务器
    uvicorn app.main:app --reload

### API 文档
- Swagger UI: http://localhost:<port>/docs
- ReDoc: http://localhost:<port>/redoc
```
