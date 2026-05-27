# 数据库全品类选型指南

## 选型决策树

```
你的数据是什么模型？
├── 结构化关系数据 → OLTP?
│   ├── 单机/中小规模 → MySQL / PostgreSQL / SQLite
│   ├── 分布式/大规模 → TiDB / CockroachDB / OceanBase
│   └── 分析型负载 → Citus (PG扩展) / ClickHouse
├── 灵活文档 schema → MongoDB / CouchDB
├── 键值缓存 → Redis / Memcached / Dragonfly
├── 图关系 → Neo4j / NebulaGraph / ArangoDB
├── 时序数据 → TimescaleDB / InfluxDB / VictoriaMetrics
├── 全文搜索 → Elasticsearch / MeiliSearch / Typesense
├── 向量检索 → pgvector / Milvus / Qdrant
├── 分析/OLAP → ClickHouse / StarRocks / DuckDB
└── 消息/事件流 → Kafka / RabbitMQ / Pulsar
```

## 关系型数据库（OLTP）

### MySQL

- **定位**: 互联网轻量实用型数据库
- **适用**: Web 应用、电商、用户系统、读多写少
- **优势**: 生态最成熟、运维简单、云服务丰富（RDS）、读性能优异
- **劣势**: 复杂查询弱、JSON 支持基础、监控工具少、主从复制有延迟风险
- **数据量阈值**: 单表 < 5000 万行舒适区
- **版本推荐**: 8.0+（ICU 正则、窗口函数、CTE）

### PostgreSQL

- **定位**: 企业级全能数据库，开源版 Oracle
- **适用**: 复杂查询、GIS、JSON、强一致性、数据分析
- **优势**: 功能最全、SQL 标准兼容、扩展性强（pgvector/Citus/TimescaleDB）、MVCC 优秀
- **劣势**: 写性能略逊 MySQL、运维门槛稍高、内存占用较大
- **数据量阈值**: 单表 < 1 亿行舒适区
- **版本推荐**: 16+（并行 VACUUM 改进、增量备份；15+ 也兼容）

### MariaDB

- **定位**: MySQL 社区驱动替代
- **适用**: MySQL 兼容场景、开源优先
- **优势**: 完全兼容 MySQL、社区活跃、部分引擎性能更好（ColumnStore）
- **劣势**: 功能迭代可能滞后于 MySQL

### SQLite

- **定位**: 嵌入式零配置数据库
- **适用**: 单机应用、开发测试、移动端、桌面应用
- **优势**: 零配置、单文件、无服务端、ACID、读性能极好
- **劣势**: 无网络访问、并发写受限、无用户管理
- **数据量**: 适合 < 100GB

### TiDB

- **定位**: 分布式 NewSQL，MySQL 兼容
- **适用**: 大规模 OLTP+OLAP 混合、水平扩展
- **优势**: MySQL 协议兼容、自动分片、HTAP、强一致
- **劣势**: 最小部署 6+ 节点、单点查询延迟 2-5ms、运维复杂

### CockroachDB

- **定位**: 分布式 SQL，PostgreSQL 兼容
- **适用**: 全球多活、强一致、PostgreSQL 生态
- **优势**: 序列化隔离、自动分片、多区域部署
- **劣势**: 最小 3 节点、单点延迟 2-5ms、非 MySQL 兼容

### OceanBase

- **定位**: 金融级分布式数据库
- **适用**: 大规模分布式、金融强一致、多租户
- **优势**: 三副本强一致、MySQL 兼容、多租户、高压缩
- **劣势**: 运维复杂、社区版功能限制

## NoSQL — 文档型

### MongoDB

- **定位**: 灵活 schema 文档数据库
- **适用**: 内容管理、用户画像、日志、快速迭代
- **优势**: JSON 文档原生支持、水平扩展（分片）、聚合管道、Change Stream
- **劣势**: 无完整事务（4.0+ 副本集支持多文档事务，4.2+ 扩展到分片集群，推荐 6.0+）、内存占用大、JOIN 弱
- **数据模型**: `{"_id": ObjectId, "name": "xxx", "tags": ["a", "b"]}`

### CouchDB

- **定位**: 多主复制文档数据库
- **适用**: 离线优先应用、P2P 同步
- **优势**: HTTP API、MVCC、多主复制、冲突解决

## NoSQL — 键值型

### Redis

- **定位**: 内存高性能键值存储
- **适用**: 缓存、会话、排行榜、计数器、消息队列、分布式锁
- **优势**: 亚毫秒延迟、丰富数据结构（String/Hash/List/Set/ZSet/Stream）、持久化
- **劣势**: 内存限制、单线程（6.0+ 多线程 IO）、数据量受内存约束
- **数据量**: 适合 < 100GB 热数据

### Memcached

- **定位**: 简单分布式缓存
- **适用**: 纯 KV 缓存、多线程高并发
- **优势**: 多线程、简单高效、内存效率高
- **劣势**: 无持久化、无数据结构、最大 1MB value

### Dragonfly / KeyDB

- **定位**: Redis 高性能替代
- **适用**: 需要更大内存效率或多线程的 Redis 场景
- **优势**: 兼容 Redis 协议、多线程、更高吞吐

## NoSQL — 列族型

### Cassandra / ScyllaDB

- **定位**: 大规模分布式列存储
- **适用**: IoT、时序、日志、写密集、全球分布
- **优势**: 线性扩展、无单点故障、高写入吞吐
- **劣势**: 无 JOIN、查询模式受限（需按分区键查询）、最终一致
- **ScyllaDB**: C++ 重写，10x 性能提升，Cassandra 协议兼容

### HBase

- **定位**: Hadoop 生态列存储
- **适用**: 大数据随机读写、与 Hadoop 集成
- **优势**: 强一致性、列族存储、与 HDFS 集成
- **劣势**: 运维复杂、不支持 SQL

## NoSQL — 图数据库

### Neo4j

- **定位**: 原生图数据库
- **适用**: 社交网络、推荐系统、知识图谱、欺诈检测
- **优势**: 原生图存储、Cypher 查询语言、ACID、可视化工具
- **劣势**: 单机为主（企业版集群）、大数据量性能下降

### NebulaGraph

- **定位**: 分布式图数据库
- **适用**: 大规模图数据、高性能遍历
- **优势**: 分布式架构、水平扩展、nGQL 语法

### ArangoDB

- **定位**: 多模型数据库（图+文档+KV）
- **适用**: 需要多种数据模型的场景
- **优势**: AQL 统一查询、灵活

## 时序数据库

### TimescaleDB

- **定位**: 时序 + 关系混合（PostgreSQL 扩展）
- **适用**: 监控、IoT、金融时序、需要 SQL 的时序场景
- **优势**: SQL 兼容、自动时间分区（Hypertable）、压缩、连续聚合
- **劣势**: 需要 PostgreSQL 基础

### InfluxDB

- **定位**: 专用时序数据库
- **适用**: DevOps 监控、指标收集
- **优势**: 高写入、InfluxQL/Flux、内置可视化
- **劣势**: 专用查询语言、非 SQL

### VictoriaMetrics

- **定位**: Prometheus 长期存储
- **适用**: 监控指标存储、替代 Thanos
- **优势**: 高压缩、PromQL 兼容、单机性能优秀

## 搜索引擎

### Elasticsearch

- **定位**: 分布式搜索和分析引擎
- **适用**: 全文搜索、日志分析（ELK）、APM、安全分析
- **优势**: 倒排索引、分布式、聚合分析、生态丰富
- **劣势**: 内存占用大、运维复杂、JSON DSL 学习曲线

### MeiliSearch

- **定位**: 轻量即时搜索引擎
- **适用**: 网站搜索、应用内搜索、即时搜索
- **优势**: 零配置、 typo 容错、毫秒级响应、REST API

## 向量数据库（AI/ML）

### pgvector

- **定位**: PostgreSQL 向量扩展
- **适用**: 已有 PG 的 RAG/语义搜索
- **优势**: SQL 兼容、无需额外基础设施、IVFFlat/HNSW 索引
- **劣势**: 大规模向量（>1亿）性能不如专用方案

### Milvus

- **定位**: 大规模向量检索引擎
- **适用**: 大规模 RAG、图像检索、推荐
- **优势**: 分布式、GPU 加速、支持十亿级向量
- **劣势**: 部署复杂、最小资源要求高

### Qdrant

- **定位**: 高性能向量搜索
- **适用**: RAG、语义搜索、多模态检索
- **优势**: Rust 编写、高性能、过滤+向量联合查询、简单 API

## 列式/分析型（OLAP）

### ClickHouse

- **定位**: 列式实时分析数据库
- **适用**: 日志分析、实时报表、用户行为分析
- **优势**: 列式存储、极快聚合（亿级秒查）、压缩率高
- **劣势**: 不支持 UPDATE/DELETE（异步合并）、无事务、不适合 OLTP 场景（不支持行级更新删除、无事务隔离），定位为 OLAP 分析引擎

### StarRocks

- **定位**: 实时分析、湖仓一体
- **适用**: 实时 BI、数据湖分析
- **优势**: 向量化引擎、CBO 优化器、MySQL 协议兼容

### DuckDB

- **定位**: 嵌入式分析数据库
- **适用**: 本地数据分析、Parquet/CSV 查询
- **优势**: 零配置、进程内运行、列式存储、Parquet 原生支持

## 消息/事件存储

### Apache Kafka

- **定位**: 分布式事件流平台
- **适用**: 事件驱动架构、数据管道、日志聚合
- **优势**: 高吞吐、持久化、Exactly-once 语义、流处理（Kafka Streams）
- **劣势**: 运维复杂、延迟高于内存队列

### RabbitMQ

- **定位**: 传统消息队列
- **适用**: 任务队列、RPC、复杂路由
- **优势**: AMQP 协议、灵活路由、多语言客户端

## 选型速查表

| 场景 | 首选 | 备选 |
|------|------|------|
| 电商订单/用户 | MySQL | PostgreSQL |
| 复杂报表/分析 | PostgreSQL | MySQL + ClickHouse |
| 内容管理/CMS | MongoDB | PostgreSQL (JSONB) |
| 缓存/会话 | Redis | Memcached |
| 社交关系 | Neo4j | PostgreSQL (递归 CTE) |
| IoT/时序 | TimescaleDB | InfluxDB / VictoriaMetrics |
| 全文搜索 | Elasticsearch | MeiliSearch |
| RAG/AI 向量 | pgvector | Qdrant / Milvus |
| 实时分析 | ClickHouse | StarRocks |
| 事件流 | Kafka | RabbitMQ / Pulsar |
| 分布式强一致 | TiDB | CockroachDB / OceanBase |
| 嵌入式/单机 | SQLite | DuckDB |
