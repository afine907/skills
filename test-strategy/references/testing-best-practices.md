# 测试最佳实践

## 测试金字塔原则

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

## AAA 模式 (Arrange-Act-Assert)

```python
def test_create_user_with_valid_data():
    # Arrange - 准备测试数据
    user_data = {"name": "张三", "email": "zhangsan@example.com"}
    
    # Act - 执行被测试的操作
    result = create_user(user_data)
    
    # Assert - 验证结果
    assert result.name == "张三"
    assert result.email == "zhangsan@example.com"
    assert result.id is not None
```

## 命名规范

### 函数命名
```
test_{功能}_{场景}_{期望结果}
```

示例：
```python
def test_create_user_with_valid_data_returns_user():
def test_create_user_with_duplicate_email_raises_error():
def test_login_with_wrong_password_returns_401():
```

### 类命名
```python
class TestUserService:
    def test_create_user(self):
        pass
    
    def test_get_user(self):
        pass
```

## 测试数据管理

### 使用 Fixtures
```python
@pytest.fixture
def sample_user():
    return {
        "name": "测试用户",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

@pytest.fixture
def authenticated_client(client, sample_user):
    """带认证的客户端"""
    response = client.post("/api/auth/register", json=sample_user)
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### 使用 Factories
```python
import factory

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.Faker('password')
```

## Mock 原则

### Mock 外部依赖，不 Mock 业务逻辑
```python
# ✅ 正确：Mock 外部 API
@patch('app.services.external_api.fetch_data')
def test_process_data(mock_fetch):
    mock_fetch.return_value = {"data": "test"}
    result = process_data()
    assert result.processed == True

# ❌ 错误：Mock 被测试的函数
@patch('app.services.process_data')
def test_workflow(mock_process):
    mock_process.return_value = True
    # 这样测试没有意义
```

### Mock 边界
```python
# 数据库操作 → Mock repository 层
# HTTP 请求 → Mock 响应
# 文件系统 → 使用 tmp_path
# 时间依赖 → 使用 freezegun
```

## 边界条件测试

```python
# 空值
def test_with_none_input():
    with pytest.raises(ValueError):
        process(None)

# 空集合
def test_with_empty_list():
    result = process([])
    assert result == []

# 极大值
def test_with_max_value():
    result = process(float('inf'))
    assert result is not None

# 极小值
def test_with_min_value():
    result = process(float('-inf'))
    assert result is not None

# 边界值
def test_at_boundary():
    result = process(0)  # 边界值
    assert result is not None
```

## 异常测试

```python
# 测试特定异常
def test_raises_value_error():
    with pytest.raises(ValueError, match="Invalid input"):
        validate_input("")

# 测试异常消息
def test_error_message():
    with pytest.raises(ValueError) as exc_info:
        process(-1)
    assert "negative" in str(exc_info.value)
```

## 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (0, 0),
    (1, 1),
    (-1, 1),
    (100, 100),
    (-100, 100),
])
def test_absolute_value(input, expected):
    assert abs(input) == expected
```

## 测试覆盖率

### 目标
- 语句覆盖率 ≥ 80%
- 分支覆盖率 ≥ 70%
- 函数覆盖率 ≥ 90%

### 排除项
- 测试文件本身
- 配置文件
- 迁移脚本
- 类型定义

## 测试隔离

### 每个测试独立
```python
# ✅ 正确：每个测试有自己的数据
def test_create_user():
    user = create_user({"name": "Test"})
    assert user.name == "Test"

# ❌ 错误：测试间共享状态
shared_user = None

def test_create_user():
    global shared_user
    shared_user = create_user({"name": "Test"})

def test_update_user():
    # 依赖上一个测试
    update_user(shared_user.id, {"name": "Updated"})
```

## 测试性能

### 快速测试
```python
# 单元测试应该 < 100ms
def test_fast():
    assert 1 + 1 == 2

# 集成测试可以 < 1s
@pytest.mark.integration
def test_with_db():
    # 数据库操作
    pass

# E2E 测试可以 < 10s
@pytest.mark.e2e
def test_full_workflow():
    # 完整流程
    pass
```

## 测试分类

```python
# pytest markers
@pytest.mark.unit
def test_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_e2e():
    pass

@pytest.mark.slow
def test_slow():
    pass
```

## CI 集成

```yaml
# GitHub Actions
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml --cov-fail-under=80
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```
