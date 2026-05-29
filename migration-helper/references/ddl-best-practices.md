# DDL Migration Best Practices

## General Principles

1. **Every DDL change must be reversible** - Always write a down migration
2. **Test on production-like data** - Run against a copy of production data
3. **Use transactions where supported** - PostgreSQL DDL is transactional; MySQL is not
4. **Separate schema changes from data migrations** - Never in the same migration
5. **Deploy during low-traffic windows** - Even safe migrations have overhead

## Adding Columns

### Safe (PostgreSQL)

```sql
-- Safe: Adding a nullable column with no default
ALTER TABLE users ADD COLUMN nickname VARCHAR(100);

-- Safe: Adding with a non-volatile default (PG 11+)
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
```

### Dangerous

```sql
-- DANGEROUS: Adding NOT NULL without default (fails on existing rows)
ALTER TABLE users ADD COLUMN nickname VARCHAR(100) NOT NULL;

-- DANGEROUS: Adding volatile default locks table
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
```

### Safe Pattern for NOT NULL

```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN nickname VARCHAR(100);

-- Step 2: Backfill data (separate data migration)
UPDATE users SET nickname = name WHERE nickname IS NULL;

-- Step 3: Add NOT NULL constraint
ALTER TABLE users ALTER COLUMN nickname SET NOT NULL;
```

## Adding Indexes

### PostgreSQL (Concurrent)

```sql
-- Safe: Does not lock writes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Down migration
DROP INDEX CONCURRENTLY idx_users_email;
```

### MySQL

```sql
-- MySQL 8.0+ supports instant DDL for some operations
ALTER TABLE users ADD INDEX idx_users_email (email), ALGORITHM=INPLACE, LOCK=NONE;

-- For older MySQL, use pt-online-schema-change
-- pt-online-schema-change --alter "ADD INDEX idx_users_email (email)" D=mydb,t=users
```

## Renaming Columns

### Safe Pattern (Zero-Downtime)

```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(200);

-- Step 2: Copy data (data migration)
UPDATE users SET full_name = name;

-- Step 3: Deploy code that reads from both, writes to both
-- Step 4: Deploy code that reads from new only
-- Step 5: Drop old column
ALTER TABLE users DROP COLUMN name;
```

### Direct Rename (Downtime Required)

```sql
-- PostgreSQL
ALTER TABLE users RENAME COLUMN name TO full_name;

-- MySQL
ALTER TABLE users CHANGE COLUMN name full_name VARCHAR(200);
```

## Changing Column Types

### PostgreSQL (Safe)

```sql
-- Widening VARCHAR is safe
ALTER TABLE users ALTER COLUMN name TYPE VARCHAR(500);

-- Changing type requires caution
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN age_int INTEGER;

-- Step 2: Copy and convert
UPDATE users SET age_int = age::INTEGER;

-- Step 3: Drop old, rename new
ALTER TABLE users DROP COLUMN age;
ALTER TABLE users RENAME COLUMN age_int TO age;
```

### MySQL

```sql
-- Use ALGORITHM=INPLACE when possible
ALTER TABLE users MODIFY COLUMN name VARCHAR(500), ALGORITHM=INPLACE, LOCK=NONE;
```

## Foreign Keys

### Adding Foreign Keys

```sql
-- PostgreSQL (acquires ACCESS EXCLUSIVE lock)
-- Add index first to make FK validation fast
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);

-- Then add FK
ALTER TABLE orders
  ADD CONSTRAINT fk_orders_user
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE;
```

### Dropping Foreign Keys

```sql
-- PostgreSQL
ALTER TABLE orders DROP CONSTRAINT fk_orders_user;

-- MySQL
ALTER TABLE orders DROP FOREIGN KEY fk_orders_user;
```

## Table Operations

### Creating Tables

```sql
-- Always use IF NOT EXISTS for idempotency
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id BIGINT PRIMARY KEY,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Dropping Tables

```sql
-- Always use IF EXISTS
DROP TABLE IF EXISTS user_preferences;

-- Soft delete alternative: rename first
ALTER TABLE user_preferences RENAME TO _user_preferences_backup;
-- Wait confirmation period, then drop
DROP TABLE IF EXISTS _user_preferences_backup;
```

## Migration File Naming

```
YYYYMMDDHHMMSS_description.sql
20240115120000_add_users_table.sql
20240115120100_add_email_index.sql
20240115120200_add_nickname_column.sql
```

## Rollback Strategy

```sql
-- Always implement down migrations
-- Up: 20240115120000_add_nickname_column.sql
ALTER TABLE users ADD COLUMN nickname VARCHAR(100);

-- Down: 20240115120000_add_nickname_column_rollback.sql
ALTER TABLE users DROP COLUMN nickname;
```

## Checklist

- [ ] Migration is idempotent (can run multiple times safely)
- [ ] Down migration exists and works
- [ ] Indexes use CONCURRENTLY (PostgreSQL) or INPLACE (MySQL)
- [ ] NOT NULL columns have defaults or are backfilled first
- [ ] No data-destroying operations without explicit confirmation
- [ ] Tested on production-like data volume
- [ ] Migration runs in < 1 second for OLTP tables
- [ ] Foreign key additions have indexes on referencing columns
