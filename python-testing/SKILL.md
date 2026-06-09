---
name: python-testing
description: |
  【Python测试】Python 测试完整指南：pytest、mock/patch、参数化、fixtures、异步测试、覆盖率。

  触发时机：
  - 用户要求"写测试"、"Python测试"、"pytest"
  - 需要 mock/patch 外部依赖
  - 需要参数化测试或 fixtures
  - 需要测试覆盖率报告

  提供完整的测试策略和代码示例。
category: reference
user-invocable: false
---

# Python Testing — Python 测试完整指南

从单元测试到集成测试的完整 Python 测试方法论。


## Goal

Python 测试完整指南：pytest、mock/patch、参数化、fixtures、异步测试、覆盖率

## Trigger

- 用户要求"写测试"、"Python测试"、"pytest"
  - 需要 mock/patch 外部依赖
  - 需要参数化测试或 fixtures
  - 需要测试覆盖率报告

## 工作流程

```
确定测试类型 → 编写测试用例 → Mock 外部依赖 → 运行测试 → 检查覆盖率
```

详见下方各测试主题的详细指南。

## 测试策略

### 测试金字塔

```
        /  E2E  \          少量，验证关键流程
       / 集成测试 \         中量，验证模块协作
      /  单元测试   \       大量，验证函数逻辑
```

### 测试分类

| 类型 | 标记 | 运行方式 | 速度 | 范围 |
|------|------|----------|------|------|
| 单元测试 | `@pytest.mark.unit` | `pytest -m unit` | 快 | 单个函数/类 |
| 集成测试 | `@pytest.mark.integration` | `pytest -m integration` | 中 | 多模块协作 |
| E2E 测试 | `@pytest.mark.e2e` | `pytest -m e2e` | 慢 | 完整流程 |
| 慢测试 | `@pytest.mark.slow` | `pytest -m "not slow"` | 慢 | 耗时操作 |

## pytest 核心

### 命令速查

```bash
# 运行测试
pytest                        # 运行所有测试
pytest -v                     # 详细输出
pytest -x                     # 失败时停止
pytest -k "login"             # 匹配测试名
pytest -m unit                # 按标记运行
pytest --tb=short             # 简短回溯
pytest --tb=long              # 详细回溯

# 并行执行
pytest -n 4                   # 4 个进程并行
pytest -n auto                # 自动检测 CPU 数

# 调试
pytest -s                     # 不捕获输出
pytest --pdb                  # 失败时进入调试器
pytest --lf                   # 只运行上次失败的测试
pytest -vv --tb=long          # 最详细输出

# 覆盖率
pytest --cov=myapp            # 显示覆盖率
pytest --cov=myapp --cov-report=html  # HTML 报告
pytest --cov=myapp --cov-report=term-missing  # 显示未覆盖行
```

### 断言

```python
# 基础断言
assert result == expected
assert response.status_code == 200
assert len(users) > 0

# 异常断言
import pytest
with pytest.raises(ValueError, match="invalid"):
    int("not-a-number")

# 近似浮点数
assert result == pytest.approx(3.14, rel=1e-2)

# 包含断言
assert "error" in response.text
assert user in user_list

# 类型断言
assert isinstance(result, dict)
assert all(isinstance(u, User) for u in users)
```

## Fixtures

### 基础 Fixture

```python
import pytest

@pytest.fixture
def user_data():
    return {"email": "test@example.com", "name": "Test User"}

@pytest.fixture
def database():
    db = Database(":memory:")
    db.connect()
    yield db
    db.disconnect()

def test_create_user(database, user_data):
    user = database.create_user(user_data)
    assert user.email == user_data["email"]
```

### Fixture 作用域

```python
@pytest.fixture(scope="session")
def db_connection():
    """整个测试会话只创建一次"""
    conn = create_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="module")
def app():
    """每个测试模块创建一次"""
    app = create_app(testing=True)
    yield app

@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    """每个测试函数创建一次（默认）"""
    return tmp_path / "test_data"
```

### Fixture 组合

```python
@pytest.fixture
def authenticated_client(client, user):
    """组合多个 fixture"""
    client.login(user)
    return client

@pytest.fixture
def sample_orders(user, products):
    """创建测试数据"""
    return [
        Order(user=user, product=p, quantity=2)
        for p in products[:3]
    ]
```

### conftest.py

```python
# tests/conftest.py
import pytest
from app import create_app
from app.models import db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    response = client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}
```

## Mock 和 Patch

### Mock 基础

```python
from unittest.mock import Mock, MagicMock, patch

# 创建 Mock
mock_db = Mock()
mock_db.query.return_value = [{"id": 1}]
mock_db.query.assert_called_once()

# 带属性的 MagicMock
mock_response = MagicMock()
mock_response.status_code = 200
mock_response.json.return_value = {"users": []}
```

### Patch 装饰器

```python
from unittest.mock import patch

@patch('app.services.email_service.send_email')
def test_user_registration(mock_send):
    register_user("test@example.com")
    mock_send.assert_called_once_with(
        to="test@example.com",
        subject="Welcome"
    )

@patch('app.models.db.session')
@patch('app.services.cache.get')
def test_with_multiple_mocks(mock_cache, mock_session):
    mock_cache.return_value = None
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    # test code
```

### Patch 上下文管理器

```python
def test_api_call():
    with patch('app.services.http_client') as mock_client:
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: {"data": "test"}
        )
        result = fetch_external_data()
        assert result["data"] == "test"
        mock_client.get.assert_called_once()
```

### Mock 返回值序列

```python
def test_retry_logic():
    mock_api = Mock()
    mock_api.call.side_effect = [
        ConnectionError("timeout"),
        ConnectionError("timeout"),
        {"status": "ok"}  # 第三次成功
    ]

    result = call_with_retry(mock_api, max_retries=3)
    assert result["status"] == "ok"
    assert mock_api.call.call_count == 3
```

### 属性 Mock

```python
@patch.object(UserService, 'find_by_email')
def test_login(mock_find):
    mock_find.return_value = User(
        email="test@example.com",
        password_hash=hash_password("correct")
    )
    result = login("test@example.com", "correct")
    assert result.success is True
```

## 参数化测试

### pytest.mark.parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("Python", "PYTHON"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
], ids=["positive", "zeros", "negative", "large"])
def test_addition(a, b, expected):
    assert add(a, b) == expected
```

### 多参数组合

```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [10, 20])
def test_combinations(x, y):
    # 生成 4 个测试：(1,10), (1,20), (2,10), (2,20)
    assert x + y > 0
```

### 动态参数化

```python
def test_cases_from_file():
    test_data = load_csv("test_cases.csv")
    return pytest.mark.parametrize(
        "input,expected",
        [(row.input, row.expected) for row in test_data]
    )
```

## 异步测试

### pytest-asyncio

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_timeout():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1.0)
```

### 异步 Mock

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_service():
    mock_client = AsyncMock()
    mock_client.fetch.return_value = {"data": "test"}

    service = DataService(mock_client)
    result = await service.get_data()
    assert result["data"] == "test"
    mock_client.fetch.assert_awaited_once()
```

### 异步 Fixture

```python
@pytest.fixture
async def async_db():
    db = AsyncDatabase()
    await db.connect()
    yield db
    await db.disconnect()

@pytest.mark.asyncio
async def test_async_query(async_db):
    result = await async_db.query("SELECT 1")
    assert result is not None
```

## 属性测试（Hypothesis）

### 基础用法

```python
from hypothesis import given, strategies as st

# 自动生成测试数据
@given(st.text())
def test_encode_decode_roundtrip(s):
    encoded = encode(s)
    decoded = decode(encoded)
    assert decoded == s

@given(st.lists(st.integers()))
def test_sort_is_idempotent(lst):
    # 排序两次结果相同
    assert sorted(sorted(lst)) == sorted(lst)

@given(st.integers(min_value=0, max_value=1000))
def test_addition_commutative(a, b):
    # 加法交换律
    assert a + b == b + a
```

### 复杂策略

```python
from hypothesis import given, strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

# 自定义策略
user_strategy = st.fixed_dictionaries({
    "email": st.emails(),
    "name": st.text(min_size=1, max_size=50),
    "age": st.integers(min_value=0, max_value=150),
    "role": st.sampled_from(["admin", "user", "guest"]),
})

@given(user_strategy)
def test_create_user(user):
    db_user = create_user(user)
    assert db_user.email == user["email"]

# 状态机测试
class ShoppingCart(RuleBasedStateMachine):
    @initialize()
    def setup(self):
        self.cart = ShoppingCart()

    @rule(item=st.sampled_from(["apple", "banana", "orange"]))
    def add_item(self, item):
        self.cart.add(item)

    @rule()
    def checkout(self):
        if self.cart.items:
            order = self.cart.checkout()
            assert order.total > 0

TestShoppingCart = ShoppingCart.TestCase
```

### 配置和标记

```python
from hypothesis import given, settings, HealthCheck

# 设置最大示例数
@given(st.integers())
@settings(max_examples=100)
def test_with_limited_examples(n):
    pass

# 忽略特定警告
@given(st.data())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_slow_operation(data):
    pass

# 标记为慢测试
@pytest.mark.slow
@given(st.lists(st.integers(), min_size=1))
def test_sort_performance(lst):
    result = sort_list(lst)
    assert result == sorted(lst)
```

## 集成测试（testcontainers）

### 基础用法

```python
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.mysql import MySqlContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:15-alpine") as pg:
        yield pg

@pytest.fixture(scope="session")
def redis():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis

def test_database_operations(postgres):
    # postgres.get_connection_url() 获取连接
    conn = postgres.get_connection_url()
    db = create_database(conn)
    
    # 测试数据库操作
    user = db.create_user({"email": "test@example.com"})
    assert user.id is not None

def test_with_redis(redis):
    client = redis.get_client()
    client.set("key", "value")
    assert client.get("key") == b"value"
```

### Docker Compose 测试

```python
import pytest
from testcontainers.compose import DockerCompose

@pytest.fixture(scope="session")
def services():
    with DockerCompose(
        ".",
        compose_file_name="docker-compose.test.yml",
        build=True
    ) as compose:
        yield compose

def test_api_with_services(services):
    # 等待服务就绪
    services.wait_for("http://localhost:3000/health")
    
    # 测试 API
    response = requests.get("http://localhost:3000/api/users")
    assert response.status_code == 200
```

### 测试数据工厂

```python
from faker import Faker
import factory

fake = Faker()

class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.LazyFunction(fake.email)
    name = factory.LazyFunction(fake.name)
    password = factory.LazyFunction(fake.password)
    
    @factory.lazy_attribute
    def password_hash(self):
        return hash_password(self.password)

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    items = factory.LazyFunction(
        lambda: [
            {"product_id": fake.random_int(), "quantity": fake.random_int(min=1, max=10)}
            for _ in range(fake.random_int(min=1, max=5))
        ]
    )

# 使用
def test_order_creation():
    order = OrderFactory()
    assert order.user is not None
    assert len(order.items) > 0
```

## 测试模式

### Given-When-Then

```python
def test_order_creation():
    # Given
    user = create_test_user()
    product = create_test_product(price=100)

    # When
    order = create_order(user, product, quantity=2)

    # Then
    assert order.total == 200
    assert order.status == "pending"
    assert order.user_id == user.id
```

### 测试工厂

```python
class UserFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {
            "email": f"user{cls._counter}@test.com",
            "name": f"Test User {cls._counter}",
            "role": "user",
        }
        return User(**{**defaults, **overrides})

    @classmethod
    def create_admin(cls, **overrides):
        return cls.create(role="admin", **overrides)

# 使用
def test_admin_access():
    admin = UserFactory.create_admin()
    assert admin.role == "admin"
```

### Snapshot 测试

```python
def test_api_response_format(snapshot):
    response = client.get("/api/users")
    snapshot.assert_match(response.json(), "users_response.json")
```

## 配置

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
addopts = -v --tb=short --strict-markers
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## 常用标记

```python
@pytest.mark.slow              # 标记慢测试
@pytest.mark.integration       # 集成测试
@pytest.mark.skip(reason="TODO")
@pytest.mark.skipif(sys.version_info < (3, 10))
@pytest.mark.xfail(reason="known bug")  # 预期失败
```

## 参考资料

- pytest 详解: [references/pytest.md](references/pytest.md)
- Mock 和 Patch: [references/mocking.md](references/mocking.md)
- Fixtures: [references/fixtures.md](references/fixtures.md)
- 异步测试: [references/async.md](references/async.md)
- 覆盖率: [references/coverage.md](references/coverage.md)
