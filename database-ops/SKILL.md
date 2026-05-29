---
name: database-ops
category: development
description: |
  数据库设计与运维全流程技能。自然语言描述 → 数据库选型 + 表结构设计 + 索引策略 + 迁移脚本 + 性能调优。
---

# Database Ops — 数据库设计与运维全流程

自然语言描述 → 完整数据库方案（选型 + DDL + 索引 + 迁移脚本 + 性能建议），一次输出。

不适用：已有数据库的运维操作（直连数据库执行）；纯 ORM 模型定义（非数据库设计）；数据备份恢复脚本。


## Goal

数据库设计与运维全流程技能。自然语言描述 → 数据库选型 + 表结构设计 + 索引策略 + 迁移脚本 + 性能调优

## Trigger

当用户需要使用此技能时触发。

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
描述需求 → 选择数据库 → 设计表结构 → 设计索引 → 生成迁移脚本 → 性能建议
```

### Step 1: 收集需求

从用户描述中提取：
- **业务场景**：电商、社交、SaaS、IoT、游戏、金融等
- **数据规模**：预估行数、增长速度
- **读写比例**：读多写少 / 写多读少 / 均衡
- **一致性要求**：强一致 / 最终一致
- **已有技术栈**：Go/Python/Java/Node.js、已有 ORM
- **业务实体**：用户提到的表/实体及其关系

如果信息不足，询问 1-2 个关键问题，不要过度追问。

### Step 2: 选择数据库

根据业务场景匹配数据库类型，读取 [references/database-comparison.md](references/database-comparison.md) 获取全品类选型指南。

**选型决策流**：
1. 确定数据模型 → 关系/文档/图/时序/向量
2. 确定访问模式 → OLTP/OLAP/搜索/缓存
3. 考虑规模、一致性、运维复杂度

| 数据模型 | 推荐数据库 |
|----------|-----------|
| 结构化关系数据 | MySQL / PostgreSQL |
| 灵活文档 schema | MongoDB |
| 缓存/会话/排行榜 | Redis |
| 社交关系/推荐 | Neo4j / NebulaGraph |
| 监控指标/时序 | TimescaleDB / VictoriaMetrics |
| 全文搜索/日志 | Elasticsearch / MeiliSearch |
| 向量检索/RAG | pgvector / Milvus / Qdrant |
| 实时分析/OLAP | ClickHouse / StarRocks |
| 事件流/消息 | Kafka / RabbitMQ |
| 分布式强一致 | TiDB / CockroachDB / OceanBase |
| 嵌入式/单机 | SQLite / DuckDB |

### Step 3: 设计表结构

读取 [references/schema-design.md](references/schema-design.md) 获取各数据库的表设计模式。

生成内容：
- DDL（CREATE TABLE）含字段类型、约束、默认值
- 字段命名规范（snake_case、有意义的名称）
- 必要字段：id、created_at、updated_at、is_deleted（软删除）
- 外键关系（如适用）
- 各数据库特有的数据类型选择

### Step 4: 设计索引

读取 [references/index-optimization.md](references/index-optimization.md) 获取索引策略。

根据查询模式生成：
- 主键索引
- 复合索引（按最左前缀原则排序）
- 覆盖索引（高频查询避免回表）
- 唯一索引
- 部分索引 / 条件索引（PostgreSQL）
- 全文索引（搜索场景）
- 向量索引（IVF/HNSW，AI 场景）

### Step 5: 生成迁移脚本

读取 [references/migration-patterns.md](references/migration-patterns.md) 获取迁移工具配置。

根据技术栈选择工具：
- Python → Alembic（FastAPI/Flask）或 Django migrations
- Go → golang-migrate 或 goose
- Java → Flyway 或 Liquibase
- Node.js → Prisma migrate 或 Knex

生成：
- 初始迁移脚本（V1__create_tables.sql）
- 回滚脚本（V1__rollback.sql）
- 种子数据脚本（如需要）

### Step 6: 性能建议

读取 [references/performance-tuning.md](references/performance-tuning.md) 获取调优指南。

根据表结构和查询模式输出：
- 连接池配置建议
- 慢查询排查方法
- 分库分表时机判断
- 该数据库特有的性能建议

## 输出格式

完成后输出：

```markdown
## 数据库方案已生成

**数据库**: <name>
**场景**: <业务场景>

### 数据库选型

<推荐理由和对比>

### 表结构（DDL）

    <CREATE TABLE 语句>

### 索引设计

    <CREATE INDEX 语句>

### 迁移脚本

<工具和脚本路径>

### 性能建议

<连接池、慢查询、扩缩建议>
```
