# 测试数据管理指南

## 测试数据策略

| 策略 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| 硬编码数据 | 简单测试 | 直观、可控 | 维护成本高 |
| Fixtures | 共享数据 | 可复用 | 可能产生依赖 |
| Factories | 动态数据 | 灵活、多样 | 需要额外库 |
| 数据库种子 | 集成测试 | 真实数据 | 清理复杂 |
| 快照 | 回归测试 | 快速恢复 | 存储空间 |

## pytest Fixtures

### 基础 Fixture

```python
import pytest

@pytest.fixture
def sample_user():
    """提供测试用户数据"""
    return {
        "name": "张三",
        "email": "zhangsan@example.com",
        "password": "SecurePass123!"
    }

@pytest.fixture
def sample_order():
    """提供测试订单数据"""
    return {
        "product": "测试商品",
        "amount": 99.99,
        "quantity": 2
    }
```

### Fixture 作用域

```python
@pytest.fixture(scope="session")
def db_engine():
    """整个测试会话共享的数据库引擎"""
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """每个测试函数独立的数据库会话"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

### Fixture 组合

```python
@pytest.fixture
def user_repo(db_session):
    """用户仓库实例"""
    return UserRepository(db_session)

@pytest.fixture
def order_repo(db_session):
    """订单仓库实例"""
    return OrderRepository(db_session)

@pytest.fixture
def sample_user_in_db(user_repo, sample_user):
    """数据库中的测试用户"""
    return user_repo.create(sample_user)
```

## Factory 模式

### factory_boy (Python)

```python
import factory
from faker import Faker

fake = Faker('zh_CN')

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(fake.phone_number)
    created_at = factory.LazyFunction(fake.date_time_between)

class OrderFactory(factory.Factory):
    class Meta:
        model = Order
    
    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.SubFactory(UserFactory)
    product = factory.LazyFunction(lambda: fake.word())
    amount = factory.LazyFunction(lambda: round(random.uniform(10, 1000), 2))
    status = factory.LazyFunction(lambda: random.choice(['pending', 'paid', 'completed']))

# 使用
user = UserFactory()
users = UserFactory.build_batch(10)  # 批量创建
admin = UserFactory(role='admin')  # 覆盖字段
```

### Faker 常用 Provider

```python
from faker import Faker

fake = Faker('zh_CN')

# 个人信息
fake.name()          # 姓名
fake.email()         # 邮箱
fake.phone_number()  # 电话
fake.address()       # 地址
fake.company()       # 公司

# 文本
fake.text()          # 文本
fake.word()          # 单词
fake.sentence()      # 句子
fake.paragraph()     # 段落

# 数字
fake.random_int()    # 随机整数
fake.pydecimal()     # 小数

# 日期
fake.date()          # 日期
fake.date_time()     # 日期时间
fake.date_between()  # 指定范围日期

# 网络
fake.url()           # URL
fake.ipv4()          # IPv4
fake.ipv6()          # IPv6

# 文件
fake.file_name()     # 文件名
fake.mime_type()     # MIME 类型
```

## 测试数据清理

### 自动清理

```python
@pytest.fixture
def temp_dir():
    """提供临时目录，测试后自动清理"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def temp_file():
    """提供临时文件，测试后自动清理"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test data")
        yield f.name
    os.unlink(f.name)
```

### 数据库清理

```python
@pytest.fixture
def clean_db(db_session):
    """每个测试后清理数据库"""
    yield db_session
    
    # 清理所有表
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
```

## 测试数据文件

### JSON 测试数据

```json
{
  "users": [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
    {"id": 2, "name": "李四", "email": "lisi@example.com"}
  ],
  "orders": [
    {"id": 1, "user_id": 1, "product": "商品A", "amount": 99.99},
    {"id": 2, "user_id": 2, "product": "商品B", "amount": 199.99}
  ]
}
```

### 加载测试数据

```python
import json
from pathlib import Path

@pytest.fixture
def test_data():
    """加载测试数据文件"""
    data_file = Path(__file__).parent / "fixtures" / "test_data.json"
    with open(data_file) as f:
        return json.load(f)

@pytest.fixture
def users_data(test_data):
    return test_data["users"]

@pytest.fixture
def orders_data(test_data):
    return test_data["orders"]
```

## 测试数据隔离

### 每个测试独立数据

```python
def test_create_user():
    # 每个测试创建自己的数据
    user_data = {"name": "Test", "email": "test@example.com"}
    user = create_user(user_data)
    assert user.name == "Test"
```

### 使用事务回滚

```python
@pytest.fixture
def db_session():
    """每个测试在事务中执行，测试后回滚"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

## 测试数据生成脚本

```python
#!/usr/bin/env python
"""生成测试数据"""
import json
from faker import Faker

fake = Faker('zh_CN')

def generate_users(count=100):
    return [
        {
            "id": i + 1,
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
        }
        for i in range(count)
    ]

def generate_orders(users, count=500):
    return [
        {
            "id": i + 1,
            "user_id": fake.random_element(users)["id"],
            "product": fake.word(),
            "amount": round(fake.pyfloat(min_value=10, max_value=1000), 2),
            "status": fake.random_element(["pending", "paid", "completed"]),
        }
        for i in range(count)
    ]

if __name__ == "__main__":
    users = generate_users(100)
    orders = generate_orders(users, 500)
    
    data = {"users": users, "orders": orders}
    with open("test_data.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(users)} users and {len(orders)} orders")
```
