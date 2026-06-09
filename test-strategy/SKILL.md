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


## Goal

为项目制定完整的测试策略，包含测试金字塔、测试范围、测试工具选型、覆盖率目标、CI集成方案

## Trigger

- 用户要求"制定测试策略"、"测试方案"
  - 项目缺少测试需要规划
  - 需要建立测试体系

## 工作流程

```
项目评估 → 策略制定 → 工具选型 → 配置生成 → CI集成 → 监控调整
   │          │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼          ▼
 现状摸底    金字塔     决策表     配置文件   CI管道    覆盖率趋势
 指标采集    覆盖率     技术栈匹配  数据管理   门禁规则   策略迭代
 风险识别    优先级     团队适配   命名规范   报告集成
```

### Step 1: 项目评估（现状摸底）

向用户确认以下信息，并检查项目现有状态：

| 评估维度 | 具体指标 | 采集方式 |
|---------|---------|---------|
| 技术栈 | 语言、框架、数据库、前端/后端 | 读取 package.json / pyproject.toml / requirements.txt |
| 现有测试 | 测试文件数量、测试用例数 | 扫描 tests/ 目录，统计 test_*.py |
| 当前覆盖率 | 语句/分支/函数覆盖率 | 执行 pytest --cov（如有 pytest-cov） |
| CI 状态 | CI 平台、现有 CI 配置 | 检查 .github/workflows/ 或 .gitlab-ci.yml |
| 团队规模 | 开发人数、测试人数 | 询问用户 |
| 核心模块 | 关键业务路径 | 询问用户或分析代码结构 |
| 现有痛点 | 测试缺失、CI 慢、不稳定 | 询问用户 |

### Step 2: 策略制定
- 确定测试金字塔比例（根据项目类型调整，见决策表）
- 设定覆盖率目标（根据现状分级，见适应性目标表）
- 识别测试优先级（高风险模块优先）

### Step 3: 工具选型

根据技术栈使用以下决策表选择工具：

| 技术栈 | 单元测试 | 集成测试 | API 测试 | E2E 测试 | Mock 框架 |
|--------|---------|---------|---------|---------|----------|
| Python + FastAPI | pytest | pytest + TestContainers | httpx | Playwright | pytest-mock |
| Python + Django | pytest | pytest + pytest-django | DRF 测试客户端 | Playwright | unittest.mock |
| Python + Flask | pytest | pytest + Flask测试客户端 | httpx | Playwright | pytest-mock |
| Node.js + Express | Jest/Vitest | Supertest + Jest | Supertest | Playwright/Cypress | Jest mock |
| Node.js + NestJS | Jest | Jest + 内置测试 | Supertest | Playwright | Jest mock |
| Go + Gin/Echo | go test | go test + testcontainers | httptest | Playwright | gomock |
| Java + Spring | JUnit 5 | Spring Boot Test | MockMvc/RestAssured | Selenium/Playwright | Mockito |
| 前端 React | Vitest + Testing Library | — | — | Playwright/Cypress | MSW |
| 前端 Vue | Vitest + Vue Test Utils | — | — | Playwright/Cypress | MSW |
| 前端 Angular | Jest + Jasmine | — | — | Playwright/Cypress | HttpClientTestingModule |

### Step 4: 配置生成
- 生成测试配置文件（pytest.ini/conftest.py）
- 生成测试数据管理方案（Fixture模式）
- 生成命名规范和代码模板

### Step 5: CI集成
- 生成CI配置（GitHub Actions/GitLab CI）
- 配置覆盖率报告上传
- 设置质量门禁（覆盖率阈值、测试通过率）

### Step 6: 监控调整（反馈循环）
- IF 覆盖率低于目标 THEN: 生成未覆盖代码报告，建议补充测试的优先级
- IF CI 运行时间 > 10min THEN: 建议拆分测试套件（快速 vs 慢速）
- IF 测试不稳定（flaky tests）THEN: 识别不稳定测试，建议修复或标记
- 定期回顾：每月检查覆盖率趋势，调整目标

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

## 项目类型决策矩阵

根据项目特征选择测试金字塔比例和工具栈：

| 项目类型 | 团队规模 | 风险等级 | 推荐金字塔比例 | 优先实施 |
|---------|---------|---------|---------------|---------|
| Web API | 1-5人 | 中 | 单元70%/集成25%/E2E 5% | 单元+API 测试 |
| Web API | 5-20人 | 高 | 单元60%/集成30%/E2E 10% | 全类型并行 |
| Web 前端 | 1-5人 | 低 | 单元50%/集成30%/E2E 20% | 组件测试+E2E |
| CLI 工具 | 1-5人 | 低 | 单元80%/集成15%/E2E 5% | 单元测试为主 |
| 库/SDK | 1-10人 | 中 | 单元75%/集成20%/E2E 5% | 单元+集成测试 |
| 微服务 | 5-20人 | 高 | 单元50%/集成35%/E2E 15% | 集成+契约测试 |
| 移动应用 | 3-10人 | 中 | 单元50%/集成20%/E2E 30% | E2E+快照测试 |
| 遗留系统 | 任意 | 高 | 单元40%/集成45%/E2E 15% | 集成测试优先 |

### 优先级排序（资源有限时）

| 优先级 | 测试类型 | 理由 | 预期 ROI |
|--------|---------|------|---------|
| P0 | 核心业务单元测试 | 成本低、速度快、防回归 | 极高 |
| P1 | API/接口集成测试 | 验证模块交互，发现集成问题 | 高 |
| P2 | 认证/支付 E2E 测试 | 覆盖关键用户路径 | 高 |
| P3 | 工具函数单元测试 | 覆盖率提升，但业务价值较低 | 中 |
| P4 | UI 组件测试 | 视觉回归，但维护成本高 | 中-低 |

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

### 适应性覆盖率目标

根据项目现状和成熟度选择目标级别：

| 级别 | 语句覆盖率 | 分支覆盖率 | 函数覆盖率 | 适用场景 |
|------|-----------|-----------|-----------|---------|
| 起步级 | ≥ 60% | ≥ 50% | ≥ 70% | 遗留项目从零开始 |
| 基础级 | ≥ 70% | ≥ 60% | ≥ 80% | 新项目初期 |
| 标准级 | ≥ 80% | ≥ 70% | ≥ 90% | 成熟项目（推荐默认） |
| 严格级 | ≥ 90% | ≥ 85% | ≥ 95% | 金融/医疗等高可靠性 |

### 增量覆盖率（遗留项目推荐）

对于遗留代码，设定增量覆盖率目标更实际：
- 新代码：语句 ≥ 80%，分支 ≥ 70%
- 修改代码：修改部分覆盖率 ≥ 90%
- 不强制存量代码覆盖率，但鼓励逐步提升

排除：
- 测试文件本身
- 配置文件
- 迁移脚本
- 类型定义
```

## Edge Cases

- 遗留代码无测试：从集成测试开始，逐步补充单元测试，不追求一步到位
- 新项目从零开始：先搭建测试框架和CI，再开发功能时同步写测试
- 前后端分离项目：前端用Vitest+Playwright，后端用pytest+TestContainers
- 微服务架构：每个服务独立测试策略，增加契约测试（Pact）
- 遗留代码覆盖率低：设定增量覆盖率目标（新代码≥80%），不强制存量

## 不适用

**范围边界：** 本技能制定测试策略和配置方案，不编写具体的测试用例、不执行测试、不进行性能或安全测试。输出为可执行的测试计划和配置，而非测试代码本身。

- 自动生成测试用例 → 使用 [test-generator](../test-generator/SKILL.md)
- 负载/性能测试 → 使用 [load-testing](../load-testing/SKILL.md)
- 安全测试 → 使用 [security-scan](../security-scan/SKILL.md)

### 适用场景矩阵

| 用户意图 | 推荐入口 | 输出物 |
|---------|----------|--------|
| 从零建立测试体系 | 全流程 Step 1-5 | 完整测试策略文档 + 配置 + CI |
| 改进现有测试 | Step 1 评估 + Step 6 监控 | 差距分析报告 + 改进建议 |
| 新项目规划测试 | Step 1-4 | 测试策略 + 工具配置 + CI 配置 |
| 审查测试质量 | Step 1 评估 | 测试覆盖率报告 + 薄弱环节清单 |
| 制定 CI 测试门禁 | Step 5 CI 集成 | CI 配置 + 质量门禁规则 |
| 选择测试工具 | Step 3 工具选型 | 工具对比表 + 推荐方案 |

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
