# 索引策略

## 索引类型总览

| 索引类型 | MySQL | PostgreSQL | MongoDB | 适用场景 |
|----------|-------|-----------|---------|----------|
| B-Tree | 默认 | 默认 | 默认 | 等值+范围查询 |
| Hash | MEMORY 引擎 | HASH | Hash Index | 纯等值查询 |
| GIN | 不支持 | 支持 | 不支持 | JSONB/数组/全文搜索 |
| GiST | 不支持 | 支持 | 不支持 | 地理空间/范围/全文 |
| BRIN | 不支持 | 支持 | 不支持 | 物理顺序存储的大表 |
| 倒排索引 | FULLTEXT | TSVECTOR+GIN | Text Index | 全文搜索 |
| 向量索引 | 不支持 | IVFFlat/HNSW (pgvector) | 不支持 | 向量相似搜索 |
| 部分索引 | 不支持（8.0+ 有函数索引） | WHERE 条件 | 不支持 | 只索引部分行 |

## B-Tree 索引设计

### 最左前缀原则（复合索引）

复合索引 `(a, b, c)` 可以加速以下查询：

```sql
-- ✅ 能使用索引
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
WHERE a = 1 AND b > 2 AND b < 10
WHERE a = 1 ORDER BY b

-- ❌ 不能使用索引（跳过了 a）
WHERE b = 2
WHERE b = 2 AND c = 3
WHERE c = 3
```

### 字段排序规则

复合索引字段顺序应遵循：
1. **等值查询字段**放前面
2. **范围查询字段**放中间
3. **排序字段**放后面
4. **选择性高的字段**优先（区分度大）

```sql
-- 示例：查询 user_id=X AND status=Y ORDER BY created_at
-- 最优索引
CREATE INDEX idx_user_status_time ON orders (user_id, status, created_at);
```

### 覆盖索引

当索引包含查询需要的所有字段时，无需回表：

```sql
-- 查询只需要 username 和 email
SELECT username, email FROM users WHERE username = 'john';

-- 覆盖索引（包含这两个字段）
CREATE INDEX idx_users_username_email ON users (username, email);
-- EXPLAIN 显示 Using index（不回表）
```

### 唯一索引

```sql
-- MySQL
CREATE UNIQUE INDEX uk_email ON users (email);

-- PostgreSQL（支持部分唯一索引，软删除场景）
CREATE UNIQUE INDEX uk_users_email ON users (email) WHERE NOT is_deleted;
```

## MySQL 索引最佳实践

### 索引建议

```sql
-- 主键索引（InnoDB 聚簇索引）
PRIMARY KEY (id)

-- 查询条件索引
CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_orders_status ON orders (status);

-- 复合索引（覆盖查询）
CREATE INDEX idx_orders_user_status_time ON orders (user_id, status, created_at);

-- 前缀索引（长字符串节省空间）
CREATE INDEX idx_users_email_prefix ON users (email(20));

-- 函数索引（MySQL 8.0+）
CREATE INDEX idx_users_lower_email ON users ((LOWER(email)));
```

### 索引失效场景

```sql
-- ❌ 隐式类型转换
WHERE phone = 13800138000  -- phone 是 VARCHAR，应加引号

-- ❌ 对索引列使用函数
WHERE DATE(created_at) = '2025-01-01'
-- ✅ 改为范围查询
WHERE created_at >= '2025-01-01' AND created_at < '2025-01-02'

-- ❌ LIKE 以 % 开头
WHERE name LIKE '%john'
-- ✅ 改为全文索引或右模糊
WHERE name LIKE 'john%'

-- ❌ OR 连接不同索引列（可能全表扫描）
WHERE user_id = 1 OR status = 1
-- ✅ 改为 UNION
SELECT * FROM orders WHERE user_id = 1
UNION
SELECT * FROM orders WHERE status = 1 AND user_id != 1
```

## PostgreSQL 索引最佳实践

### 部分索引（Partial Index）

只索引满足条件的行，大幅减少索引体积：

```sql
-- 只索引未删除的用户
CREATE INDEX uk_users_email ON users (email) WHERE NOT is_deleted;

-- 只索引活跃订单
CREATE INDEX idx_orders_active ON orders (created_at) WHERE status = 'active';
```

### GIN 索引（JSONB / 数组 / 全文）

```sql
-- JSONB 索引
CREATE INDEX idx_users_profile ON users USING GIN (profile);
-- 查询：WHERE profile @> '{"role": "admin"}'

-- 数组索引
CREATE INDEX idx_users_tags ON users USING GIN (tags);
-- 查询：WHERE tags @> ARRAY['vip']

-- 全文搜索索引
CREATE INDEX idx_users_search ON users USING GIN (
  to_tsvector('english', username || ' ' || email)
);
```

### GiST 索引（地理空间 / 范围）

```sql
-- 地理位置索引
CREATE INDEX idx_stores_location ON stores USING GiST (location);
-- 查询（<-> 返回欧几里得距离，单位取决于坐标系；推荐使用 ST_Distance 明确单位）：
-- SELECT * FROM stores WHERE ST_Distance(location, ST_MakePoint(116.4, 39.9)) < 1000;

-- 范围索引
CREATE INDEX idx_events_period ON events USING GiST (tsrange(start_time, end_time));
```

### BRIN 索引（大表低开销）

适合物理顺序插入的大表（日志、时序数据）：

```sql
-- 索引大小远小于 B-Tree，适合亿级大表
CREATE INDEX idx_logs_time ON logs USING BRIN (created_at);
```

## 全文搜索索引

### MySQL FULLTEXT

```sql
-- 建表时创建
CREATE TABLE articles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(200),
  content TEXT,
  FULLTEXT INDEX ft_content (title, content)
) ENGINE=InnoDB;

-- 查询
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST ('database optimization' IN BOOLEAN MODE);
```

### PostgreSQL TSVECTOR

```sql
-- 添加搜索向量列
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- 填充数据
UPDATE articles SET search_vector =
  to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- 创建 GIN 索引
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- 查询
SELECT * FROM articles WHERE search_vector @@ to_tsquery('english', 'database & optimization');
```

## 向量索引（pgvector）

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建带向量列的表
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT,
  embedding vector(1536)  -- OpenAI 维度
);

-- IVFFlat 索引（适合 < 100 万向量）
CREATE INDEX idx_docs_embedding ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- HNSW 索引（适合 > 100 万向量，构建慢但查询快）
CREATE INDEX idx_docs_embedding_hnsw ON documents USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- 相似搜索
SELECT content, embedding <=> '[0.1, 0.2, ...]' AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

## 索引运维

### 发现未使用索引

```sql
-- MySQL
SELECT * FROM sys.schema_unused_indexes;

-- PostgreSQL
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 发现重复/冗余索引

```sql
-- PostgreSQL
SELECT a.indexrelid::regclass AS index_a,
       b.indexrelid::regclass AS index_b
FROM pg_index a
JOIN pg_index b ON a.indrelid = b.indrelid
  AND a.indexrelid != b.indexrelid
  AND a.indkey::text LIKE b.indkey::text || '%'
WHERE a.indrelid::regclass::text NOT LIKE 'pg_%';
```

### 索引大小监控

```sql
-- MySQL
SELECT table_name, index_name, stat_value * @@innodb_page_size AS size_bytes
FROM mysql.innodb_index_stats
WHERE stat_name = 'size'
ORDER BY size_bytes DESC;

-- PostgreSQL
SELECT indexrelname AS index_name,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

## 索引设计检查清单

- [ ] 每个外键字段都有索引
- [ ] WHERE 条件字段有索引
- [ ] ORDER BY 字段在复合索引中
- [ ] 高频查询使用覆盖索引
- [ ] 复合索引遵循最左前缀
- [ ] 避免过多索引（写入性能影响）
- [ ] 定期清理未使用索引
- [ ] 大表考虑部分索引/BRIN
