---
name: python-testing
description: Python 测试框架速查，覆盖 pytest、unittest、mock、覆盖率测试和 CI 集成。
homepage: https://docs.pytest.org/
metadata: {"clawdbot":{"emoji":"🧪","requires":{"bins":["python","pytest"]}}}
---

# Python Testing

Python 测试框架核心用法，从基础到进阶。

## pytest 基础

### 安装和运行
```bash
# 安装
pip install pytest pytest-cov pytest-asyncio

# 运行所有测试
pytest

# 详细输出
pytest -v
pytest -vv  # 更详细

# 运行指定文件
pytest test_module.py

# 运行指定测试
pytest test_module.py::test_function
pytest test_module.py::TestClass::test_method

# 匹配测试名
pytest -k "login"
pytest -k "login or logout"

# 标记测试
pytest -m slow  # 运行标记为 slow 的测试

# 失败时停止
pytest -x
pytest --maxfail=3

# 并行执行
pip install pytest-xdist
pytest -n auto  # 自动并行
pytest -n 4     # 4 个进程

# 只运行失败的测试
pytest --lf
pytest --ff  # 先运行失败，再运行其他
```

### 测试发现
```bash
# 默认规则
# test_*.py 或 *_test.py
# Test* 类 (无 __init__)
# test_* 函数

# 指定目录
pytest tests/
pytest src/tests/

# 忽略目录
pytest --ignore=tests/integration
```

### 基本测试
```python
# test_basic.py

def test_addition():
    assert 1 + 1 == 2

def test_string_concat():
    assert "hello" + " world" == "hello world"

def test_list_contains():
    items = [1, 2, 3]
    assert 2 in items

# 失败信息
def test_custom_message():
    result = calculate()
    assert result == 42, f"Expected 42, got {result}"
```

### 测试类
```python
class TestUser:
    """用户相关测试"""

    def test_create(self):
        user = User(name="Alice")
        assert user.name == "Alice"

    def test_update(self):
        user = User(name="Alice")
        user.name = "Bob"
        assert user.name == "Bob"

class TestMath:
    @classmethod
    def setup_class(cls):
        """类级别 setup，所有测试前执行一次"""
        cls.calculator = Calculator()

    @classmethod
    def teardown_class(cls):
        """类级别 teardown"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.calculator.reset()

    def teardown_method(self):
        """每个测试方法后执行"""

    def test_add(self):
        assert self.calculator.add(1, 2) == 3
```

## 参数化测试

### 基本参数化
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected

# 多个参数
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 5, 10),
    (10, -5, 5),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### 参数组合
```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    # 会生成 6 个测试: (1,10), (1,20), (2,10)...
    assert multiply(x, y) == x * y

# 参数 ID
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("WORLD", "WORLD"),
], ids=["lowercase", "uppercase"])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

## Fixtures

### 基本 fixture
```python
import pytest

@pytest.fixture
def database():
    db = Database(":memory:")
    db.connect()
    yield db
    db.close()

def test_query(database):
    result = database.query("SELECT 1")
    assert result is not None

# fixture 依赖
@pytest.fixture
def user(database):
    return database.create_user(name="Alice")

def test_user_name(user):
    assert user.name == "Alice"
```

### fixture 作用域
```python
# function: 每个测试调用一次 (默认)
# class: 每个测试类调用一次
# module: 每个模块调用一次
# package: 每个包调用一次
# session: 整个测试会话调用一次

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.start()
    yield app
    app.stop()

@pytest.fixture(scope="session")
def docker_client():
    client = DockerClient()
    yield client
    client.close()
```

### conftest.py
```python
# tests/conftest.py - 共享 fixture

import pytest

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_header():
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}
```

## Mock 和 Patch

### unittest.mock
```python
from unittest.mock import Mock, patch, MagicMock

# Mock 对象
def test_mock():
    mock_db = Mock()
    mock_db.query.return_value = [{"id": 1}]
    mock_db.insert.return_value = 1

    result = mock_db.query("SELECT *")
    assert result == [{"id": 1}]
    mock_db.query.assert_called_once_with("SELECT *")

# patch 装饰器
@patch('module.Database')
def test_with_patch(MockDB):
    mock_db = MockDB.return_value
    mock_db.query.return_value = []

    service = Service()
    service.process()

    mock_db.query.assert_called()

# patch 上下文管理器
def test_with_context():
    with patch('module.get_user') as mock_get_user:
        mock_get_user.return_value = {"id": 1, "name": "Alice"}

        result = process_user(1)
        assert result == "Alice"
```

### pytest-mock
```python
# pip install pytest-mock

def test_with_mocker(mocker):
    # mock 函数
    mock_func = mocker.patch('module.function')
    mock_func.return_value = 42

    # mock 对象方法
    mock_method = mocker.patch.object(User, 'save')

    # spy (保留原实现)
    spy = mocker.spy(Calculator, 'add')

    # mock 异步函数
    async_mock = mocker.AsyncMock()
    async_mock.return_value = "result"
```

## 异步测试

### pytest-asyncio
```python
# pip install pytest-asyncio

import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == "expected"

@pytest.mark.asyncio
async def test_async_with_mock():
    with pytest.raises(ValueError):
        await async_function_that_raises()

# 异步 fixture
@pytest.fixture
async def async_client():
    client = await create_async_client()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    result = await async_client.get("/")
    assert result.status == 200
```

## 覆盖率

### pytest-cov
```bash
# 安装
pip install pytest-cov

# 运行覆盖率测试
pytest --cov=myapp
pytest --cov=myapp --cov-report=term-missing

# 生成 HTML 报告
pytest --cov=myapp --cov-report=html
open htmlcov/index.html

# 指定覆盖率阈值
pytest --cov=myapp --cov-fail-under=80
```

## 测试标记

### 自定义标记
```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)

@pytest.mark.integration
def test_database():
    pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_syntax():
    pass
```

### pytest.ini 配置
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    slow: marks tests as slow
    integration: integration tests
    unit: unit tests

addopts = -v --tb=short
```

## 测试异常

### 检查异常
```python
import pytest

def test_exception():
    with pytest.raises(ValueError):
        raise ValueError("error")

def test_exception_message():
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("specific error")

    assert str(exc_info.value) == "specific error"

def test_exception_match():
    with pytest.raises(ValueError, match="specific.*error"):
        raise ValueError("specific error message")
```

## 临时文件和目录

```python
import pytest

def test_temp_file(tmp_path):
    # tmp_path 是 pytest 提供的临时目录
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    assert test_file.read_text() == "content"

def test_temp_dir(tmp_path):
    dir_path = tmp_path / "subdir"
    dir_path.mkdir()

    assert dir_path.exists()
```

## 最佳实践

1. **命名规范**: test_*.py, test_function, TestClass
2. **单一职责**: 每个测试只验证一个行为
3. **独立性**: 测试之间互不依赖
4. **可重复**: 每次运行结果一致
5. **快速**: 使用 mock 加速，集成测试单独标记
6. **覆盖率**: 目标 80%+，关键路径 100%
7. **CI 集成**: 自动运行测试和覆盖率检查

## 文档

- pytest 文档: https://docs.pytest.org/
- unittest 文档: https://docs.python.org/3/library/unittest.html
- pytest-cov: https://pytest-cov.readthedocs.io/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
