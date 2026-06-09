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

## 工作流程

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 1. 分析Schema │───▶│ 2. 选择策略   │───▶│ 3. 处理依赖   │───▶│ 4. 生成数据   │───▶│ 5. 验证      │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

1. **分析 Schema** — 识别表结构、外键关系、数据量
2. **选择策略** — 固定数据 / 随机数据 / 真实数据 / 快照恢复
3. **处理依赖** — 按外键拓扑排序，先基础表后业务表
4. **生成数据** — Faker 工厂 / SQL 种子 / Alembic 迁移
5. **验证** — 数据完整性、外键约束、幂等性

## 填充策略

| 策略 | 适用场景 | 特点 |
|------|----------|------|
| 固定数据 | 基础配置、字典表 | 不变、可预测 |
| 随机数据 | 测试、开发 | 大量、多样 |
| 真实数据 | 演示、验收 | 接近生产 |
| 快照恢复 | 测试隔离 | 快速重置 |

### 策略选择决策流程

```
用户需求是什么？
    │
    ├── 需要每次一致的结果？ ──是──▶ 固定数据（字典表、配置、种子用户）
    │       │
    │       否
    │       ▼
    ├── 需要大量多样化数据？ ──是──▶ 随机数据（测试/开发环境）
    │       │                        工具选择见下方决策表
    │       否
    │       ▼
    ├── 需要接近生产的数据？ ──是──▶ 真实数据子集（演示/验收环境）
    │       │                        注意脱敏处理
    │       否
    │       ▼
    └── 需要快速重置数据库？ ──是──▶ 快照恢复（测试隔离）
```

### 工具选择决策表

| 数据库类型 | 数据量 | 环境 | 推荐工具 | 理由 |
|-----------|--------|------|----------|------|
| PostgreSQL | < 1万行 | 开发 | Faker + SQLAlchemy | Python 生态集成好 |
| PostgreSQL | 1-10万行 | 测试 | SQL 种子文件 | 执行速度快，可版本控制 |
| PostgreSQL | > 10万行 | 测试 | Alembic 迁移 + 批量插入 | 支持增量更新和回滚 |
| MySQL | < 1万行 | 开发 | Faker + SQLAlchemy | 同上 |
| MySQL | 1-10万行 | 测试 | SQL 种子文件 | 同上 |
| MySQL | > 10万行 | 测试 | CSV 导入 + LOAD DATA | 批量导入性能最优 |
| MongoDB | < 5万文档 | 开发 | Faker + Motor/PyMongo | 灵活的文档结构 |
| MongoDB | > 5万文档 | 测试 | JSON 种子 + mongoimport | 快速导入，支持快照 |
| SQLite | 任意 | 测试 | Python 直接操作 | 轻量，适合单元测试 |

### 环境配置决策表

| 环境 | 数据量级 | 数据敏感性 | 策略 | 工具 | 幂等性要求 |
|------|---------|-----------|------|------|-----------|
| 开发 (dev) | 100-1000行 | 可用 Faker 脱敏 | 随机数据 | Faker 工厂 | 必须（ON CONFLICT） |
| 测试 (test) | 10-100行 | 可用 Faker 脱敏 | 固定数据 | SQL 种子 | 必须（幂等执行） |
| 演示 (demo) | 1000-10000行 | 必须脱敏 | 随机 + 固定混合 | Faker + SQL | 推荐 |
| 预发布 (staging) | 生产子集 | 真实数据脱敏 | 真实数据子集 | pg_dump + 脱敏脚本 | 不要求 |
| CI/CD | 10-50行 | 可用 Faker 脱敏 | 固定数据 | SQL 种子 | 必须（每次重建） |

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

## 输出模板

### 完整种子方案模板

以下是一个完整的种子方案交付物示例，输入为一个用户-订单-产品三表 Schema。

**输入 — Schema 分析结果：**

```
表: users       (100行)  FK: role_id -> roles.id
表: roles       (3行)    无 FK（基础表）
表: products    (50行)   FK: category_id -> categories.id
表: categories  (10行)   无 FK（基础表）
表: orders      (1000行) FK: user_id -> users.id, product_id -> products.id
```

**输出 — 种子方案文档：**

```markdown
# 数据库种子方案

## 1. 策略选择
- roles / categories: 固定数据（字典表，不变）
- users: 随机数据（Faker 生成）
- products: 固定数据（业务需要预设商品）
- orders: 随机数据（关联 users + products）

## 2. 执行顺序（拓扑排序）
1. roles       (无依赖)
2. categories  (无依赖)
3. users       (依赖 roles)
4. products    (依赖 categories)
5. orders      (依赖 users + products)

## 3. 工具选择
- roles / categories / products: SQL 种子文件（固定数据）
- users / orders: Python Faker 工厂（随机数据）

## 4. 环境配置
| 环境 | users | orders | products |
|------|-------|--------|----------|
| dev  | 100   | 1000   | 50       |
| test | 10    | 50     | 5        |
| demo | 500   | 5000   | 200      |

## 5. 幂等性保证
- 所有 SQL 使用 ON CONFLICT DO NOTHING
- Python 脚本先检查数据是否存在
```

### 生成代码示例（接上述方案）

**roles + categories（SQL 固定种子）：**

```sql
-- seeds/001_roles.sql
INSERT INTO roles (name, description) VALUES
    ('admin', '管理员'),
    ('user', '普通用户'),
    ('guest', '访客')
ON CONFLICT (name) DO NOTHING;

-- seeds/002_categories.sql
INSERT INTO categories (name, sort_order) VALUES
    ('电子产品', 1), ('服装', 2), ('食品', 3)
ON CONFLICT (name) DO NOTHING;
```

**users + orders（Faker 工厂 + 种子脚本）：**

```python
import factory
from faker import Faker
import random

fake = Faker('zh_CN')

class UserFactory(factory.Factory):
    class Meta:
        model = dict
    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(fake.phone_number)
    role_id = factory.LazyFunction(lambda: random.choice([1, 2, 3]))
    created_at = factory.LazyFunction(lambda: fake.date_time_between(start_date='-1y'))

class OrderFactory(factory.Factory):
    class Meta:
        model = dict
    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.LazyFunction(lambda: random.randint(1, 100))
    product_id = factory.LazyFunction(lambda: random.randint(1, 50))
    amount = factory.LazyFunction(lambda: round(random.uniform(10, 1000), 2))
    status = factory.LazyFunction(lambda: random.choice(['pending', 'paid', 'shipped']))
    created_at = factory.LazyFunction(lambda: fake.date_time_between(start_date='-6m'))
```

**验证输出示例：**

```
[验证] roles:        3/3 ✓
[验证] categories:   3/3 ✓
[验证] users:        100/100 ✓ (外键检查通过)
[验证] products:     50/50 ✓ (外键检查通过)
[验证] orders:       1000/1000 ✓ (外键检查通过)
[验证] 幂等性:       重复执行 0 新增行 ✓
[验证] 数据类型:     无类型不匹配 ✓
总计: 1156 行，5 表，耗时 2.3s
```

## Edge Cases

- **循环外键依赖**
  - IF 检测到循环依赖 THEN: 1) 临时禁用外键约束 (`SET CONSTRAINTS ALL DEFERRED`)，2) 按反向依赖顺序插入，3) 重新启用约束并验证 (`CONSTRAINTS ALL IMMEDIATE`)
  - IF 无法打破循环 THEN: 使用 nullable FK 或关联表替代直接外键

- **大数据集（>10 万行）**
  - IF 数据量 > 10万 AND < 100万 THEN: 分批插入，每批 1000 行，使用事务提交
  - IF 数据量 > 100万 THEN: 每批 100 行，使用 COPY 命令或 LOAD DATA，禁用索引后重建
  - IF 需要生成 > 100万行 THEN: 使用批量 Faker 生成器，避免逐行调用

- **敏感数据**
  - IF 包含密码 THEN: 使用 bcrypt 哈希，绝不明文存储
  - IF 包含邮箱/手机号 THEN: 使用 Faker 生成（`fake.email()` / `fake.phone_number()`）
  - IF 演示环境 THEN: 所有 PII 字段必须脱敏，使用 `***` 占位或 Faker 替换

- **幂等性**
  - IF 可重复执行 THEN: 使用 `ON CONFLICT DO NOTHING` 或 `ON CONFLICT DO UPDATE`
  - IF 需要精确控制 THEN: 先 DELETE 再 INSERT，或使用 UPSERT 模式
  - IF 多环境共享种子 THEN: 使用版本化种子文件，避免跨环境冲突

- **数据类型不匹配**
  - IF 日期格式异常 THEN: 统一使用 ISO 8601 格式 (`YYYY-MM-DDTHH:MM:SS`)
  - IF JSON 字段类型不一致 THEN: 先序列化为字符串再插入
  - IF 枚举值超出范围 THEN: 先查询有效值列表，仅使用合法值

- **并发种子冲突**
  - IF 多个进程同时执行种子 THEN: 使用行级锁 (`SELECT ... FOR UPDATE`) 或分布式锁
  - IF CI 并行测试竞争同一数据库 THEN: 每个测试使用独立 schema 或独立数据库实例

- **Schema 迁移期间种子**
  - IF 种子依赖尚未创建的表 THEN: 先执行迁移，再执行种子
  - IF 种子脚本与迁移脚本版本不一致 THEN: 将种子嵌入迁移脚本的 upgrade() 中

## 不适用

**范围边界：** 本技能负责设计和执行开发/测试环境的种子数据方案，不负责生产数据迁移、实时数据同步或数据库备份恢复。

- 实时数据同步 → 使用 CDC 工具（Debezium、DMS）
- 生产环境数据导入 → 使用 ETL 管道（参考 data-pipeline）
- 数据库备份恢复 → 使用 pg_dump/mysqldump

### 适用场景矩阵

| 用户意图 | 推荐入口 | 示例 |
|---------|----------|------|
| 创建测试数据 | 工作流程 Step 1-5 | "为用户表生成 1000 条测试数据" |
| 设计种子方案 | 策略选择决策流程 | "设计开发环境的数据库初始化方案" |
| 数据工厂设计 | Python + Faker 实现 | "为订单系统创建数据工厂" |
| 环境数据配置 | 环境配置决策表 | "配置 test/demo/dev 三套环境数据" |
| 数据快照管理 | 数据快照代码 | "导出当前数据库状态为快照" |

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
