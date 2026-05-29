---
name: migration-helper
description: |
  【数据迁移】设计和执行数据迁移方案，包含迁移脚本生成、数据校验、回滚策略、灰度迁移计划。

  触发时机：
  - 数据库表结构变更需要迁移
  - 系统重构需要数据迁移
  - 数据库切换（MySQL→PostgreSQL）
  - 用户要求"数据迁移"、"表结构变更"

  支持 DDL 生成、数据迁移脚本、校验脚本。
category: operations
---

# Migration Helper — 数据迁移助手

设计安全的数据迁移方案，生成迁移脚本和校验逻辑。


## Goal

设计和执行数据迁移方案，包含迁移脚本生成、数据校验、回滚策略、灰度迁移计划

## Trigger

- 数据库表结构变更需要迁移
  - 系统重构需要数据迁移
  - 数据库切换（MySQL→PostgreSQL）
  - 用户要求"数据迁移"、"表结构变更"

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
变更分析 → 方案设计 → 脚本生成 → 校验逻辑 → 回滚方案 → 执行计划
```

## 迁移类型

| 类型 | 场景 | 风险 | 停机要求 |
|------|------|------|----------|
| DDL 变更 | 加字段、加索引 | 低 | 通常不需要 |
| 数据回填 | 填充新字段默认值 | 中 | 不需要 |
| 数据拆分 | 表拆分、分库分表 | 高 | 可能需要 |
| 数据合并 | 多表合并 | 高 | 可能需要 |
| 数据库切换 | MySQL→PostgreSQL | 极高 | 需要 |

## DDL 变更最佳实践

### 安全的 DDL 操作

```sql
-- ✅ 安全：加字段（带默认值）
ALTER TABLE users ADD COLUMN status TINYINT NOT NULL DEFAULT 0 
  COMMENT '用户状态: 0-正常, 1-禁用';

-- ✅ 安全：加索引（使用 CONCURRENTLY 避免锁表）
-- PostgreSQL
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
-- MySQL 8.0+
ALTER TABLE users ADD INDEX idx_users_email (email), ALGORITHM=INPLACE, LOCK=NONE;

-- ✅ 安全：加约束（先验证数据）
-- 1. 先检查是否有违反约束的数据
SELECT COUNT(*) FROM users WHERE email IS NULL;
-- 2. 修复违规数据
UPDATE users SET email = CONCAT('unknown_', id) WHERE email IS NULL;
-- 3. 再加约束
ALTER TABLE users MODIFY COLUMN email VARCHAR(255) NOT NULL;
```

### 危险的 DDL 操作

```sql
-- ❌ 危险：直接改列类型（可能丢数据）
ALTER TABLE users MODIFY COLUMN name VARCHAR(50);

-- ✅ 安全方式：
-- 1. 加新列
ALTER TABLE users ADD COLUMN name_new VARCHAR(50);
-- 2. 迁移数据
UPDATE users SET name_new = LEFT(name, 50);
-- 3. 切换列名
ALTER TABLE users DROP COLUMN name;
ALTER TABLE users CHANGE COLUMN name_new name VARCHAR(50);
```

## 迁移脚本模板

### 数据回填脚本

```sql
-- 迁移脚本: 回填 users 表的 full_name 字段
-- Author: {author}
-- Date: {date}
-- Ticket: {ticket}

-- Step 1: 验证前置条件
SELECT COUNT(*) as total_users FROM users;
-- 预期: {expected_count}

-- Step 2: 备份原数据
CREATE TABLE users_backup_{date} AS 
SELECT id, first_name, last_name FROM users;

-- Step 3: 执行回填（分批处理）
-- 每批处理 1000 条，避免长事务
DO $$
DECLARE
  batch_size INT := 1000;
  affected INT;
BEGIN
  LOOP
    UPDATE users 
    SET full_name = CONCAT(first_name, ' ', last_name)
    WHERE full_name IS NULL
    AND id IN (
      SELECT id FROM users 
      WHERE full_name IS NULL 
      LIMIT batch_size
    );
    GET DIAGNOSTICS affected = ROW_COUNT;
    EXIT WHEN affected = 0;
    PERFORM pg_sleep(0.1); -- 每批间隔 100ms
    RAISE NOTICE 'Updated % rows', affected;
  END LOOP;
END $$;

-- Step 4: 验证结果
SELECT COUNT(*) as migrated 
FROM users WHERE full_name IS NOT NULL;
-- 预期: 等于 total_users

-- Step 5: 清理备份（确认无误后执行）
-- DROP TABLE users_backup_{date};
```

### Python 迁移脚本

```python
"""
数据迁移脚本: {描述}
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Migration:
    def __init__(self, db_session):
        self.db = db_session
        self.batch_size = 1000
    
    def up(self):
        """执行迁移"""
        logger.info(f"Starting migration: {self.__class__.__name__}")
        
        # 1. 验证前置条件
        self._verify_preconditions()
        
        # 2. 备份
        self._backup()
        
        # 3. 执行迁移
        self._migrate()
        
        # 4. 验证结果
        self._verify_result()
        
        logger.info("Migration completed successfully")
    
    def down(self):
        """回滚迁移"""
        logger.info(f"Rolling back migration: {self.__class__.__name__}")
        # 回滚逻辑
    
    def _verify_preconditions(self):
        """验证迁移前置条件"""
        count = self.db.execute("SELECT COUNT(*) FROM users").scalar()
        logger.info(f"Total records to migrate: {count}")
        assert count > 0, "No records to migrate"
    
    def _backup(self):
        """备份数据"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS users_backup AS 
            SELECT * FROM users
        """)
        logger.info("Backup created")
    
    def _migrate(self):
        """执行数据迁移"""
        offset = 0
        while True:
            result = self.db.execute("""
                UPDATE users 
                SET full_name = CONCAT(first_name, ' ', last_name)
                WHERE full_name IS NULL
                LIMIT :batch_size
            """, {"batch_size": self.batch_size})
            
            affected = result.rowcount
            offset += affected
            logger.info(f"Migrated {offset} records")
            
            if affected < self.batch_size:
                break
            
            import time
            time.sleep(0.1)  # 避免数据库过载
    
    def _verify_result(self):
        """验证迁移结果"""
        unmigrated = self.db.execute(
            "SELECT COUNT(*) FROM users WHERE full_name IS NULL"
        ).scalar()
        assert unmigrated == 0, f"{unmigrated} records not migrated"
        logger.info("Verification passed")
```

## 数据校验

### 校验脚本模板

```sql
-- 校验1: 记录数一致性
SELECT 
  source_count,
  target_count,
  source_count - target_count as diff
FROM (
  SELECT 
    (SELECT COUNT(*) FROM users) as source_count,
    (SELECT COUNT(*) FROM users_new) as target_count
) t
WHERE source_count != target_count;

-- 校验2: 抽样数据对比
SELECT 
  s.id,
  s.name as source_name,
  t.name as target_name,
  CASE WHEN s.name = t.name THEN 'OK' ELSE 'MISMATCH' END as status
FROM users s
JOIN users_new t ON s.id = t.id
ORDER BY RANDOM()
LIMIT 100;

-- 校验3: 数据完整性
SELECT 
  'NULL check' as check_type,
  COUNT(*) as failed_count
FROM users_new
WHERE required_field IS NULL
UNION ALL
SELECT 
  'duplicate check',
  COUNT(*) - COUNT(DISTINCT unique_field)
FROM users_new;
```

## 回滚策略

| 策略 | 适用场景 | 恢复时间 |
|------|----------|----------|
| 备份表回滚 | DDL 变更 | 分钟级 |
| 双写回滚 | 数据迁移 | 秒级 |
| 时间点恢复 | 重大变更 | 小时级 |
| 应用层回滚 | 新旧兼容 | 秒级 |

## 快速使用

```
# 生成 DDL 迁移
我需要给 users 表加一个 phone 字段，生成安全的迁移脚本

# 设计数据迁移方案
从旧系统迁移用户数据到新系统，设计迁移方案

# 生成校验脚本
为这个迁移生成数据校验脚本：[粘贴迁移逻辑]

# 审查迁移脚本
审查以下迁移脚本的安全性：[粘贴脚本]
```

## 参考资料

- DDL 最佳实践: [references/ddl-best-practices.md](references/ddl-best-practices.md)
- 分批迁移策略: [references/batch-migration.md](references/batch-migration.md)
