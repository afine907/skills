# dbt 模式与最佳实践

## 项目结构

```
dbt_project/
├── dbt_project.yml          # 项目配置
├── profiles.yml             # 连接配置（~/.dbt/）
├── models/
│   ├── staging/             # 原始数据清洗
│   │   ├── stg_orders.sql
│   │   ├── stg_customers.sql
│   │   └── staging.yml      # schema 测试
│   ├── intermediate/        # 业务逻辑转换
│   │   ├── int_orders_enriched.sql
│   │   └── intermediate.yml
│   └── marts/               # 面向分析的聚合
│       ├── finance/
│       │   ├── fct_revenue.sql
│       │   └── finance.yml
│       └── marketing/
│           ├── dim_customers.sql
│           └── marketing.yml
├── seeds/                   # 静态数据（CSV）
│   └── country_codes.csv
├── macros/                  # 可复用 SQL 宏
│   ├── generate_schema_name.sql
│   └── incremental_merge.sql
├── snapshots/               # Type 2 SCD
│   └── scd_customers.sql
├── tests/                   # 自定义测试
│   └── assert_positive_revenue.sql
└── analyses/                # 临时分析查询
    └── data_quality_check.sql
```

## dbt_project.yml 配置

```yaml
name: my_project
version: "1.0.0"
config-version: 2

profile: my_profile

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  my_project:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: table
      +schema: intermediate
    marts:
      +materialized: table
      +schema: analytics
      finance:
        +tags: ["finance", "daily"]
      marketing:
        +tags: ["marketing", "weekly"]
```

## 物化策略

| 策略 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| `view` | Staging 层，轻量转换 | 始终最新，不占存储 | 查询慢，重复计算 |
| `table` | Marts 层，重计算 | 查询快 | 全量重建，占存储 |
| `incremental` | 大事实表 | 仅处理增量 | 逻辑复杂，需维护 |
| `ephemeral` | 辅助逻辑 | 不创建对象 | 嵌入 CTE，不可测试 |

### Incremental 模型

```sql
-- models/marts/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    {% if is_incremental() %}
    WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
    {% endif %}
),

final AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        amount,
        status,
        CURRENT_TIMESTAMP AS _loaded_at
    FROM orders
)

SELECT * FROM final
```

### 增量策略对比

| 策略 | 语法 | 适用场景 |
|------|------|----------|
| `merge` | `MERGE INTO ... USING ...` | 默认，支持更新+插入 |
| `delete+insert` | 先删后插 | 无 MERGE 的数据库 |
| `append` | 仅 INSERT | 不会更新的事件流 |
| `insert_overwrite` | 分区覆盖 | 按分区重算 |

## Schema 测试

```yaml
# models/staging/stg_orders.yml
version: 2

sources:
  - name: raw
    database: "{{ env_var('DBT_SOURCE_DB') }}"
    schema: raw_data
    tables:
      - name: orders
        description: "Raw orders from source system"
        columns:
          - name: id
            data_type: integer
          - name: customer_id
            data_type: integer
          - name: amount
            data_type: decimal
          - name: created_at
            data_type: timestamp

models:
  - name: stg_orders
    description: "Cleaned and standardized orders"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null

      - name: customer_id
        description: "Foreign key to customers"
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id

      - name: amount
        description: "Order amount in USD"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
              inclusive: true

      - name: status
        description: "Order status"
        tests:
          - accepted_values:
              values:
                - pending
                - processing
                - shipped
                - completed
                - cancelled
```

## 自定义宏

### 生成 Schema 名

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

### 增量合并宏

```sql
-- macros/incremental_merge.sql
{% macro incremental_merge(source_model, target_table, unique_key) %}
    MERGE INTO {{ target_table }} AS target
    USING {{ source_model }} AS source
    ON target.{{ unique_key }} = source.{{ unique_key }}

    WHEN MATCHED THEN UPDATE SET
        {% for column in adapter.get_columns_in_relation(source_model) %}
            target.{{ column.name }} = source.{{ column.name }}{% if not loop.last %},{% endif %}
        {% endfor %}

    WHEN NOT MATCHED THEN INSERT (
        {% for column in adapter.get_columns_in_relation(source_model) %}
            {{ column.name }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ) VALUES (
        {% for column in adapter.get_columns_in_relation(source_model) %}
            source.{{ column.name }}{% if not loop.last %},{% endif %}
        {% endfor %}
    )
{% endmacro %}
```

### 数据质量检查宏

```sql
-- macros/tests/equality_with_tolerance.sql
{% test equality_with_tolerance(model, compare_model, compare_column, tolerance_percent=1) %}
    WITH source AS (
        SELECT SUM({{ compare_column }}) AS total
        FROM {{ model }}
    ),
    comparison AS (
        SELECT SUM({{ compare_column }}) AS total
        FROM {{ compare_model }}
    )
    SELECT *
    FROM source, comparison
    WHERE ABS(source.total - comparison.total) / comparison.total * 100 > {{ tolerance_percent }}
{% endtest %}
```

## Snapshots（SCD Type 2）

```sql
-- snapshots/scd_customers.sql
{% snapshot scd_customers %}

{{
    config(
        target_database='warehouse',
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
    )
}}

SELECT
    customer_id,
    customer_name,
    email,
    segment,
    region,
    updated_at
FROM {{ source('raw', 'customers') }}

{% endsnapshot %}
```

## 变量使用

```yaml
# dbt_project.yml
vars:
  start_date: "2024-01-01"
  lookback_days: 30
```

```sql
-- 在模型中使用
SELECT *
FROM orders
WHERE order_date >= '{{ var("start_date") }}'
  AND order_date >= CURRENT_DATE - INTERVAL '{{ var("lookback_days") }} days'
```

## Hooks

```yaml
# dbt_project.yml
models:
  my_project:
    +post-hook:
      - "GRANT SELECT ON {{ this }} TO ROLE analyst"
    marts:
      +pre-hook:
        - "ALTER WAREHOUSE {{ target.warehouse }} RESUME"
```

## dbt 命令速查

```bash
# 运行所有模型
dbt run

# 运行特定模型
dbt run --select stg_orders
dbt run --select +stg_orders          # 包含上游依赖
dbt run --select stg_orders+          # 包含下游依赖
dbt run --select staging.*            # staging 目录下所有
dbt run --select tag:finance          # 按标签选择

# 运行增量模型
dbt run --full-refresh                # 强制全量重建

# 测试
dbt test
dbt test --select stg_orders          # 测试特定模型
dbt test --select test_type:generic   # 通用测试
dbt test --select test_type:singular  # 自定义测试

# 文档
dbt docs generate
dbt docs serve

# 快照
dbt snapshot

# 调试
dbt debug                            # 检查连接
dbt compile                          # 编译不执行
dbt ls                               # 列出所有资源
```

## CI/CD 集成

```yaml
# .github/workflows/dbt-ci.yml
name: dbt CI
on:
  pull_request:
    paths:
      - "dbt_project/**"

jobs:
  dbt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dbt
        run: pip install dbt-postgres

      - name: Install packages
        run: dbt deps

      - name: Compile
        run: dbt compile --target ci

      - name: Run tests
        run: dbt test --target ci

      - name: Run models (CI schema)
        run: dbt run --target ci --full-refresh
```

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 增量模型数据丢失 | 检查 `is_incremental()` 条件和 `unique_key` |
| 循环依赖 | 重构模型，引入中间层打破循环 |
| 构建顺序错误 | 检查 `ref()` 依赖，使用 `--select` 验证 |
| 测试误报 | 调整测试阈值，添加 `severity: warn` |
| 性能问题 | 物化为 table，添加索引/分区，减少 JOIN |
| Schema 不同步 | 使用 `on_schema_change: sync_all_columns` |
