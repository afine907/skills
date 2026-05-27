# 数据库迁移工具配置

## 工具选型

| 语言/框架 | 推荐工具 | 备选 |
|-----------|---------|------|
| Python (FastAPI/Flask) | Alembic | schema-benchmark |
| Python (Django) | Django migrations | — |
| Go | golang-migrate | goose |
| Java (Spring) | Flyway | Liquibase |
| Node.js (Prisma) | prisma migrate | Knex |
| Node.js (其他) | db-migrate | Knex |
| Ruby (Rails) | ActiveRecord migrations | — |
| Rust (SQLx) | SQLx migrate | — |
| 通用 | Bytebase | — |

## Alembic (Python/FastAPI/Flask)

### 初始化

```bash
pip install alembic
alembic init alembic
```

### alembic.ini 配置

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://your_user:your_password@localhost:5432/your_db  # 替换为实际值

[loggers]
keys = root,sqlalchemy,alembic
```

### env.py（异步配置）

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型以注册 metadata
from app.models import Base
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 创建迁移

```bash
# 自动生成迁移
alembic revision --autogenerate -m "add users table"

# 手动创建空迁移
alembic revision -m "add index"

# 执行迁移
alembic upgrade head

# 回滚一步
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>
```

### 迁移脚本模板

```python
"""add users table

Revision ID: abc123
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(64), nullable=False),
        sa.Column('email', sa.String(128), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, default=False),
    )
    op.create_index('uk_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('uk_users_email')
    op.drop_table('users')
```

## golang-migrate (Go)

### 安装

```bash
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest
```

### 目录结构

```
migrations/
├── 000001_create_users.up.sql
├── 000001_create_users.down.sql
├── 000002_add_orders.up.sql
└── 000002_add_orders.down.sql
```

### SQL 迁移文件

```sql
-- 000001_create_users.up.sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  email VARCHAR(128) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX uk_users_email ON users (email) WHERE NOT is_deleted;

-- 000001_create_users.down.sql
DROP TABLE IF EXISTS users;
```

### 执行迁移

```bash
# 执行所有待执行迁移
migrate -path ./migrations -database "postgres://user:pass@localhost:5432/mydb?sslmode=disable" up

# 回滚一步
migrate -path ./migrations -database "..." down 1

# 查看当前版本
migrate -path ./migrations -database "..." version

# 强制设置版本（跳过迁移）
migrate -path ./migrations -database "..." force <version>
```

## Flyway (Java/Spring)

### 配置（application.yml）

```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
    validate-on-migrate: true
    clean-disabled: true
    table: flyway_schema_history
    encoding: UTF-8
```

### 命名规范

```
V1__create_users_table.sql
V2__add_orders_table.sql
V3__add_index_on_email.sql
```

- `V` 前缀 + 版本号 + 双下划线 + 描述
- 版本号只递增，不回退
- 回滚脚本用 `U` 前缀（企业版）

### 最佳实践

- 禁用 `clean`（`clean-disabled: true`）
- 关闭 `out-of-order`
- 强制 `validate-on-migrate`
- Flyway 账号只授予 DDL 权限
- 一脚本一目的

## Prisma (Node.js)

### schema.prisma

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  orders    Order[]
}

model Order {
  id        Int      @id @default(autoincrement())
  userId    Int
  amount    Decimal  @db.Decimal(10, 2)
  status    String   @default("pending")
  createdAt DateTime @default(now())
  user      User     @relation(fields: [userId], references: [id])
}
```

### 迁移命令

```bash
# 修改 schema.prisma 后
npx prisma migrate dev --name add_orders_table  # 开发环境
npx prisma migrate deploy                       # 生产环境
npx prisma migrate reset                         # 重置数据库
npx prisma db seed                               # 执行种子数据
npx prisma studio                                # 可视化查看数据
```

## Django Migrations

### 创建迁移

```bash
python manage.py makemigrations          # 自动生成
python manage.py makemigrations -n name  # 指定名称
python manage.py migrate                 # 执行迁移
python manage.py migrate app_name 0003   # 回滚到指定版本
python manage.py showmigrations          # 查看迁移状态
python manage.py sqlmigrate app_name 0001  # 查看 SQL
```

### 自定义迁移

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.RunSQL(
            sql='CREATE INDEX idx_users_phone ON users (phone);',
            reverse_sql='DROP INDEX idx_users_phone;',
        ),
    ]
```

## 通用迁移规范

### 版本管理

- 使用递增版本号或时间戳
- 迁移脚本纳入版本控制
- 不修改已执行的迁移脚本
- 修复问题写新迁移

### 安全原则

- 生产环境禁止 `DROP TABLE`（只做 `is_deleted` 标记）
- DDL 变更前备份
- 大表变更使用 Online DDL（MySQL）或 `CREATE INDEX CONCURRENTLY`（PG，注意：不能在事务块内执行，使用时需确保迁移工具不包装在事务中）
- 回滚脚本与迁移脚本成对管理

### 团队协作

- 每次变更必须有对应迁移脚本
- 不允许直接手工改库
- CI/CD 中加入 migrate 验证
- 多人协作使用时间戳版本号避免冲突
