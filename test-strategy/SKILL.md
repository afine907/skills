---
name: test-strategy
description: |
  【测试策略】为项目制定完整的测试策略，包含测试金字塔、测试范围、测试工具选型、覆盖率目标、CI集成方案。

  触发时机：
  - 用户要求"制定测试策略"、"测试方案"
  - 项目缺少测试需要规划
  - 需要建立测试体系

  输出可执行的测试计划和配置。
category: quality
---

# Test Strategy — 测试策略技能

为项目制定系统性测试策略，建立完整的测试体系。

## 测试金字塔

```
         ╱╲
        ╱  ╲        E2E 测试 (10%)
       ╱    ╲       - 关键业务流程
      ╱──────╲
     ╱        ╲     集成测试 (20%)
    ╱          ╲    - API 测试、数据库测试
   ╱────────────╲
  ╱              ╲  单元测试 (70%)
 ╱                ╲ - 函数、类、模块
╱──────────────────╲
```

## 测试类型与工具

| 测试类型 | 工具 | 目的 | 执行频率 |
|----------|------|------|----------|
| 单元测试 | pytest/Jest/Vitest | 验证函数逻辑 | 每次提交 |
| 集成测试 | pytest+DB/TestContainers | 验证模块交互 | 每次 PR |
| API 测试 | httpx/supertest | 验证接口行为 | 每次 PR |
| E2E 测试 | Playwright/Cypress | 验证用户流程 | 每日/发布前 |
| 性能测试 | k6/Locust | 验证性能指标 | 每周/发布前 |
| 安全测试 | bandit/Snyk | 检测安全漏洞 | 每周 |
| 视觉回归 | Percy/Chromatic | 检测 UI 变化 | 每次 PR |

## 测试策略模板

```markdown
# {项目名称} 测试策略

## 1. 测试目标

- 单元测试覆盖率: ≥ 80%
- 集成测试覆盖所有 API 端点
- E2E 测试覆盖核心业务流程
- 0 个 P0/P1 级别的 Bug 逃逸到生产

## 2. 测试范围

### 必须测试
- 所有业务逻辑函数
- 所有 API 端点
- 数据库 CRUD 操作
- 认证授权流程
- 支付相关功能

### 建议测试
- 工具函数
- 边界条件
- 错误处理路径

### 可选测试
- 第三方库封装
- 纯 UI 展示组件

## 3. 测试规范

### 命名规范
```
test_{功能}_{场景}_{期望结果}
```

示例:
```python
def test_create_user_with_valid_data_returns_201():
def test_create_user_with_duplicate_email_returns_409():
def test_login_with_wrong_password_returns_401():
```

### 测试结构 (AAA)
```python
def test_example():
    # Arrange - 准备测试数据
    user = {"email": "test@example.com", "name": "Test"}
    
    # Act - 执行被测试的操作
    response = client.post("/api/users", json=user)
    
    # Assert - 验证结果
    assert response.status_code == 201
    assert response.json()["email"] == user["email"]
```

### Mock 原则
- Mock 外部依赖（数据库、API、文件系统）
- 不 Mock 被测试的业务逻辑
- 集成测试使用真实依赖
- 使用 fixture 管理测试数据

## 4. 测试工具配置

### pytest 配置
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### conftest.py
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def client(db_session):
    app = create_app(db_session)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

## 5. CI 集成

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 6. 测试数据管理

### Fixture 模式
```python
@pytest.fixture
def sample_user():
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "SecurePass123!"
    }

@pytest.fixture
def authenticated_client(client, sample_user):
    client.post("/api/auth/register", json=sample_user)
    response = client.post("/api/auth/login", json={
        "email": sample_user["email"],
        "password": sample_user["password"]
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

## 7. 覆盖率报告

目标：
- 语句覆盖率 ≥ 80%
- 分支覆盖率 ≥ 70%
- 函数覆盖率 ≥ 90%

排除：
- 测试文件本身
- 配置文件
- 迁移脚本
- 类型定义
```

## 快速使用

```
# 制定测试策略
为这个项目制定测试策略

# 生成测试配置
生成 pytest 配置和 conftest.py

# 计算测试覆盖
分析当前项目的测试覆盖率，找出未覆盖的代码

# 审查测试质量
审查现有测试，找出薄弱环节
```

## 参考资料

- 测试最佳实践: [references/testing-best-practices.md](references/testing-best-practices.md)
- 测试数据管理: [references/test-data.md](references/test-data.md)
