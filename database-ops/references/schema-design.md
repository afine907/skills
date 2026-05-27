# 表设计模式

## 通用设计原则

### 字段命名规范

- 使用 snake_case：`user_name` 不是 `userName`
- 有意义的名称：`created_at` 不是 `ts` 或 `d`
- 布尔字段用 `is_`/`has_` 前缀：`is_deleted`、`has_permission`
- 避免保留字：`order`、`group`、`select`

### 必备字段

所有业务表都应包含：

```sql
id          BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 或 UUID/ULID
created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
is_deleted  TINYINT NOT NULL DEFAULT 0           -- 软删除标记
```

PostgreSQL 版本：
```sql
id          BIGSERIAL PRIMARY KEY,
created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
is_deleted  BOOLEAN NOT NULL DEFAULT FALSE
```

### 主键策略

| 方案 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| AUTO_INCREMENT | 简单、有序、索引友好 | 分布式需额外处理 | 单机 MySQL |
| BIGSERIAL | 同上 | 同上 | 单机 PostgreSQL |
| UUID v4 | 分布式友好、无冲突 | 无序（索引分裂）、占 16 字节 | 分布式系统 |
| ULID | 有序+唯一、可排序 | 占 16 字节 | 分布式+需要排序 |
| 雪花算法 | 有序、分布式、高性能 | 时钟回拨问题 | 分布式系统 |
| NanoID | 短小、URL 安全 | 随机 | 短链接、邀请码 |

## MySQL 表设计

### 字段类型选择

| 场景 | 推荐类型 | 避免 |
|------|----------|------|
| 整数 ID | BIGINT UNSIGNED | INT（21亿上限） |
| 短字符串 | VARCHAR(64/128/255) | CHAR（浪费空间） |
| 长文本 | TEXT / LONGTEXT | VARCHAR(10000) |
| 金额 | DECIMAL(10,2) | FLOAT/DOUBLE（精度丢失） |
| 时间 | TIMESTAMP / DATETIME | INT（无法利用时间函数） |
| 布尔 | TINYINT(1) | BOOLEAN（MySQL 无原生） |
| JSON | JSON | TEXT（无索引） |
| 枚举 | ENUM 或 TINYINT + 注释 | VARCHAR（无法约束） |

### MySQL DDL 模板

```sql
CREATE TABLE `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `email` VARCHAR(128) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1:active 2:inactive 3:banned',
  `profile` JSON DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_email` (`email`),
  UNIQUE KEY `uk_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## PostgreSQL 表设计

### 字段类型选择

| 场景 | 推荐类型 | 说明 |
|------|----------|------|
| 整数 ID | BIGSERIAL / BIGINT GENERATED ALWAYS AS IDENTITY | 推荐后者 |
| UUID | UUID DEFAULT gen_random_uuid() | PG 13+ 内置 |
| 文本 | TEXT | PG 的 TEXT 无性能差异 |
| JSON | JSONB | 支持索引、高效查询 |
| 数组 | TEXT[] / INT[] | 原生数组类型 |
| 枚举 | CREATE TYPE ... AS ENUM | 强类型 |
| 网络地址 | INET / CIDR | 原生支持 |
| 全文搜索 | TSVECTOR | 内置全文搜索 |
| 范围 | INT4RANGE / TSRANGE | 原生范围类型 |

### PostgreSQL DDL 模板

```sql
CREATE TABLE users (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  email VARCHAR(128) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  status SMALLINT NOT NULL DEFAULT 1,
  profile JSONB DEFAULT NULL,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX uk_users_email ON users (email) WHERE NOT is_deleted;
CREATE UNIQUE INDEX uk_users_username ON users (username) WHERE NOT is_deleted;

-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_timestamp();
```

## MongoDB 文档设计

### 文档模板

```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "status": "active",
  "profile": {
    "avatar": "url",
    "bio": "string"
  },
  "tags": ["string"],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 设计原则
- 嵌套优先于引用（数据一起查询时嵌套）
- 避免文档超过 16MB
- 为查询字段创建索引
- 使用 change stream 替代轮询

## Redis 数据结构设计

### 常用模式

```
# 缓存
SET user:{id} '{"name":"xxx"}' EX 3600

# 分布式锁
SET lock:order:{id} "uuid" NX EX 30

# 排行榜
ZADD leaderboard {score} {member}

# 计数器
INCR article:{id}:views

# 消息队列
XADD orders * user_id 123 product "phone"

# 布隆过滤器
BF.ADD filter:email "user@example.com"
```

## 各数据库 DDL 对比

| 特性 | MySQL | PostgreSQL | MongoDB |
|------|-------|-----------|---------|
| 自增主键 | AUTO_INCREMENT | GENERATED ALWAYS AS IDENTITY | ObjectId 自动 |
| JSON | JSON 类型 | JSONB（推荐，支持索引） | 原生文档 |
| 布尔 | TINYINT(1) | BOOLEAN | 无类型 |
| 枚举 | ENUM(...) | CREATE TYPE ... AS ENUM | 无 |
| 数组 | 不支持 | 原生数组 | 原生数组 |
| 全文搜索 | FULLTEXT INDEX | TSVECTOR + GIN | Text Index |
| 软删除 | is_deleted 字段 | 部分索引 WHERE NOT is_deleted | 无（直接删除） |
| 时区 | TIMESTAMP | TIMESTAMPTZ（推荐） | ISODate |
| 字符集 | utf8mb4 | UTF-8（默认） | UTF-8（默认） |
