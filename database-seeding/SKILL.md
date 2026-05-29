---
name: database-seeding
description: |
  【数据填充】设计和实现数据库种子数据(Seed Data)，包含测试数据生成、数据工厂、环境初始化、数据快照。

  触发时机：
  - 用户要求"生成测试数据"、"数据填充"、"数据库初始化"
  - 开发环境需要模拟数据
  - 演示环境需要展示数据

  支持多种数据库和数据生成策略。
category: development
---

# Database Seeding — 数据库填充技能

设计和实现数据库种子数据，支持开发、测试、演示环境。


## Goal

设计和实现数据库种子数据(Seed Data)，包含测试数据生成、数据工厂、环境初始化、数据快照

## Trigger

- 用户要求"生成测试数据"、"数据填充"、"数据库初始化"
  - 开发环境需要模拟数据
  - 演示环境需要展示数据

## 填充策略

| 策略 | 适用场景 | 特点 |
|------|----------|------|
| 固定数据 | 基础配置、字典表 | 不变、可预测 |
| 随机数据 | 测试、开发 | 大量、多样 |
| 真实数据 | 演示、验收 | 接近生产 |
| 快照恢复 | 测试隔离 | 快速重置 |

## Python + Faker 实现

### 数据工厂

```python
import factory
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('zh_CN')

class UserFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(fake.phone_number)
    avatar = factory.LazyFunction(fake.image_url)
    role = factory.LazyFunction(lambda: random.choice(['admin', 'user', 'guest']))
    status = factory.LazyFunction(lambda: random.choice(['active', 'inactive']))
    created_at = factory.LazyFunction(lambda: fake.date_time_between(start_date='-1y'))

class OrderFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.LazyFunction(lambda: random.randint(1, 100))
    product = factory.LazyFunction(lambda: random.choice(['商品A', '商品B', '商品C']))
    amount = factory.LazyFunction(lambda: round(random.uniform(10, 1000), 2))
    status = factory.LazyFunction(lambda: random.choice(['pending', 'paid', 'shipped', 'completed']))
    created_at = factory.LazyFunction(lambda: fake.date_time_between(start_date='-6m'))
```

### 种子脚本

```python
#!/usr/bin/env python
"""数据库种子数据脚本"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def seed_database():
    engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        # 1. 基础数据
        await seed_roles(session)
        await seed_permissions(session)
        
        # 2. 用户数据
        await seed_users(session, count=100)
        
        # 3. 业务数据
        await seed_orders(session, count=1000)
        
        await session.commit()
    
    print("✓ 数据库填充完成")

async def seed_roles(session):
    """填充角色数据"""
    roles = [
        {"name": "admin", "description": "管理员"},
        {"name": "user", "description": "普通用户"},
        {"name": "guest", "description": "访客"},
    ]
    for role in roles:
        await session.execute(
            "INSERT INTO roles (name, description) VALUES (:name, :description) ON CONFLICT DO NOTHING",
            role
        )

async def seed_users(session, count: int):
    """填充用户数据"""
    users = [UserFactory() for _ in range(count)]
    await session.run_sync(lambda s: s.bulk_insert_mappings(User, users))

async def seed_orders(session, count: int):
    """填充订单数据"""
    orders = [OrderFactory() for _ in range(count)]
    await session.run_sync(lambda s: s.bulk_insert_mappings(Order, orders))

if __name__ == "__main__":
    asyncio.run(seed_database())
```

### 环境区分

```python
# seed_config.py
import os

ENV = os.getenv("APP_ENV", "development")

SEED_CONFIG = {
    "development": {
        "users": 100,
        "orders": 1000,
        "products": 50,
    },
    "test": {
        "users": 10,
        "orders": 50,
        "products": 5,
    },
    "demo": {
        "users": 500,
        "orders": 5000,
        "products": 200,
    },
}

config = SEED_CONFIG[ENV]
```

## SQL 种子文件

### 结构化种子

```sql
-- seeds/001_roles.sql
INSERT INTO roles (name, description) VALUES
    ('admin', '管理员'),
    ('user', '普通用户'),
    ('guest', '访客')
ON CONFLICT (name) DO NOTHING;

-- seeds/002_permissions.sql
INSERT INTO permissions (name, resource, action) VALUES
    ('read:users', 'users', 'read'),
    ('write:users', 'users', 'write'),
    ('delete:users', 'users', 'delete'),
    ('read:orders', 'orders', 'read'),
    ('write:orders', 'orders', 'write')
ON CONFLICT (name) DO NOTHING;

-- seeds/003_admin_user.sql
INSERT INTO users (email, name, password_hash, role_id) VALUES
    ('admin@example.com', '管理员', '$2b$12$...', 
     (SELECT id FROM roles WHERE name = 'admin'))
ON CONFLICT (email) DO NOTHING;
```

## Alembic 种子 (Python)

```python
# alembic/versions/001_seed_data.py
"""seed data

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 插入基础数据
    op.execute("""
        INSERT INTO roles (name, description) VALUES
        ('admin', '管理员'),
        ('user', '普通用户')
        ON CONFLICT DO NOTHING
    """)

def downgrade():
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'user')")
```

## 数据快照

```python
# 创建快照
async def create_snapshot(engine, snapshot_name: str):
    """导出当前数据为快照"""
    async with engine.connect() as conn:
        tables = ['users', 'orders', 'products']
        snapshot = {}
        
        for table in tables:
            result = await conn.execute(f"SELECT * FROM {table}")
            snapshot[table] = [dict(row) for row in result]
        
        with open(f"snapshots/{snapshot_name}.json", 'w') as f:
            json.dump(snapshot, f, default=str)

# 恢复快照
async def restore_snapshot(engine, snapshot_name: str):
    """从快照恢复数据"""
    with open(f"snapshots/{snapshot_name}.json") as f:
        snapshot = json.load(f)
    
    async with engine.connect() as conn:
        for table, rows in snapshot.items():
            await conn.execute(f"DELETE FROM {table}")
            for row in rows:
                await conn.execute(
                    f"INSERT INTO {table} ({','.join(row.keys())}) VALUES ({','.join([':' + k for k in row.keys()])})",
                    row
                )
        await conn.commit()
```

## 测试数据隔离

```python
# pytest fixture
@pytest.fixture
async def seeded_db(db_session):
    """提供带种子数据的数据库会话"""
    # 填充测试数据
    users = [UserFactory() for _ in range(5)]
    orders = [OrderFactory(user_id=users[0]['id']) for _ in range(10)]
    
    for user in users:
        await db_session.execute(
            "INSERT INTO users (id, name, email) VALUES (:id, :name, :email)",
            user
        )
    
    for order in orders:
        await db_session.execute(
            "INSERT INTO orders (id, user_id, product, amount) VALUES (:id, :user_id, :product, :amount)",
            order
        )
    
    await db_session.commit()
    
    yield db_session
    
    # 测试后清理
    await db_session.execute("DELETE FROM orders")
    await db_session.execute("DELETE FROM users")
    await db_session.commit()
```

## 快速使用

```
# 生成测试数据
为用户表生成 1000 条测试数据

# 创建数据工厂
为订单系统创建数据工厂

# 设计种子方案
设计开发环境的数据库初始化方案

# 导出数据快照
导出当前数据库状态为快照
```

## 参考资料

- Faker 文档: [references/faker.md](references/faker.md)
- 工厂模式: [references/factory-pattern.md](references/factory-pattern.md)
