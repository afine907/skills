---
name: data-pipeline
description: |
  【数据管道】ETL 管道设计、Airflow/dbt 模式、数据验证、监控告警。

  触发时机：
  - 用户要求"设计数据管道"、"ETL流程"
  - 需要搭建 Airflow DAG
  - 数据转换和验证

  提供完整的数据管道设计方案。
category: development
---

# Data Pipeline — 数据管道设计与实现

ETL 管道设计 + Airflow DAG + dbt 转换 + 数据验证 + 监控告警，完整的数据工程方案。

不适用：实时流处理（用 Flink/Kafka Streams）；BI 报表制作；数据库运维操作（用 database-ops）。


## Goal

ETL 管道设计、Airflow/dbt 模式、数据验证、监控告警

## Trigger

- 用户要求"设计数据管道"、"ETL流程"
  - 需要搭建 Airflow DAG
  - 数据转换和验证

## 工作流程

```
收集需求 → 设计管道架构 → 选择工具 → 实现 ETL → 配置验证 → 设置监控 → 输出方案
```

### Step 1: 收集需求

从用户描述中提取：
- **数据源**: 数据库、API、文件（CSV/JSON/Parquet）、消息队列
- **目标存储**: 数据仓库（Snowflake/BigQuery/Redshift）、数据湖（S3/GCS）
- **数据量**: 日增量、全量大小
- **时效性**: 批处理（T+1）、近实时（分钟级）、实时（秒级）
- **转换逻辑**: 清洗、聚合、关联、特征工程
- **调度频率**: 每小时、每日、每周、事件驱动
- **已有技术栈**: Python/Spark/dbt/Airflow

如果信息不足，询问 1-2 个关键问题，不要过度追问。

### Step 2: 设计管道架构

根据需求选择架构模式：

**批处理架构（最常见）**：

```
数据源 → 提取(Extract) → 暂存区(Staging) → 转换(Transform) → 加载(Load) → 数据仓库
                                                              ↓
                                                         数据验证(GE)
```

**Lambda 架构**：

```
数据源 → 批处理层(Batch Layer) → 服务层 → 查询
     ↘ 速度层(Speed Layer)   ↗
```

**Kappa 架构（纯流式）**：

```
数据源 → Kafka → 流处理(Flink/Spark Streaming) → 服务层 → 查询
```

**Medallion 架构（湖仓一体）**：

```
原始数据 → Bronze(原始层) → Silver(清洗层) → Gold(聚合层)
```

### Step 3: Airflow DAG 实现

读取 [references/airflow-dag.md](references/airflow-dag.md) 获取 DAG 模板和最佳实践。

**基础 DAG 结构**：

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
}

with DAG(
    dag_id="etl_daily_pipeline",
    default_args=default_args,
    description="Daily ETL pipeline",
    schedule_interval="0 6 * * *",  # 每天 06:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "daily"],
) as dag:

    def extract(**context):
        """从数据源提取数据。"""
        hook = PostgresHook(postgres_conn_id="source_db")
        df = hook.get_pandas_df("SELECT * FROM orders WHERE date = '{{ ds }}'")
        df.to_parquet(f"/tmp/orders_{context['ds']}.parquet")
        return len(df)

    def transform(**context):
        """数据清洗和转换。"""
        import pandas as pd
        df = pd.read_parquet(f"/tmp/orders_{context['ds']}.parquet")

        # 清洗
        df = df.dropna(subset=["customer_id", "amount"])
        df["amount"] = df["amount"].clip(lower=0)

        # 转换
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["total_with_tax"] = df["amount"] * 1.1

        df.to_parquet(f"/tmp/orders_clean_{context['ds']}.parquet")
        return len(df)

    def validate(**context):
        """数据验证。"""
        import pandas as pd
        df = pd.read_parquet(f"/tmp/orders_clean_{context['ds']}.parquet")

        # 基本检查
        assert len(df) > 0, "Empty dataset after transformation"
        assert df["amount"].min() >= 0, "Negative amounts found"
        assert df["customer_id"].notna().all(), "Null customer_ids found"

        # 行数检查（不应比前一天少太多）
        prev_count = context["task_instance"].xcom_pull(task_ids="extract")
        if len(df) < prev_count * 0.5:
            raise ValueError(f"Row count dropped significantly: {prev_count} -> {len(df)}")

    def load(**context):
        """加载到数据仓库。"""
        import pandas as pd
        df = pd.read_parquet(f"/tmp/orders_clean_{context['ds']}.parquet")
        hook = PostgresHook(postgres_conn_id="warehouse_db")
        hook.insert_rows(
            table="fact_orders",
            rows=df.values.tolist(),
            target_fields=df.columns.tolist(),
        )

    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    validate_task = PythonOperator(task_id="validate", python_callable=validate)
    load_task = PythonOperator(task_id="load", python_callable=load)

    extract_task >> transform_task >> validate_task >> load_task
```

### Step 4: dbt 转换模式

读取 [references/dbt-patterns.md](references/dbt-patterns.md) 获取 dbt 模型模板。

**dbt 模型层次**：

```sql
-- models/staging/stg_orders.sql
-- 原始数据清洗，1:1 映射源表
{{ config(materialized='view') }}

SELECT
    id AS order_id,
    customer_id,
    amount,
    status,
    created_at AS order_date,
    _airbyte_extracted_at AS _loaded_at
FROM {{ source('raw', 'orders') }}
WHERE _airbyte_extracted_at >= '{{ var("start_date") }}'
```

```sql
-- models/intermediate/int_orders_enriched.sql
-- 中间层，业务逻辑转换
{{ config(materialized='table') }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

enriched AS (
    SELECT
        o.order_id,
        o.order_date,
        o.amount,
        o.status,
        c.customer_name,
        c.segment,
        c.region,
        o.amount * 0.1 AS tax_amount,
        o.amount * 1.1 AS total_amount
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
)

SELECT * FROM enriched
```

```sql
-- models/marts/fact_daily_sales.sql
-- 聚合层，面向分析
{{ config(
    materialized='incremental',
    unique_key='date_key',
    incremental_strategy='merge'
) }}

WITH daily_sales AS (
    SELECT
        order_date AS date_key,
        COUNT(DISTINCT order_id) AS order_count,
        COUNT(DISTINCT customer_name) AS customer_count,
        SUM(amount) AS gross_revenue,
        SUM(tax_amount) AS tax_revenue,
        SUM(total_amount) AS total_revenue,
        AVG(amount) AS avg_order_value
    FROM {{ ref('int_orders_enriched') }}
    {% if is_incremental() %}
    WHERE order_date > (SELECT MAX(date_key) FROM {{ this }})
    {% endif %}
    GROUP BY order_date
)

SELECT * FROM daily_sales
```

**dbt 测试配置**：

```yaml
# models/staging/stg_orders.yml
version: 2

models:
  - name: stg_orders
    description: "Cleaned orders from source system"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: customer_id
        description: "Customer reference"
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: amount
        description: "Order amount"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
```

### Step 5: Great Expectations 数据验证

```python
import great_expectations as gx

context = gx.get_context()

# 定义数据资产
datasource = context.sources.add_pandas("my_datasource")
data_asset = datasource.add_dataframe_asset(name="orders", dataframe=df)

# 定义期望
validator = context.get_validator(
    batch_request=data_asset.build_batch_request(),
    expectation_suite_name="orders_suite",
)

# 添加期望
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_not_be_null("customer_id")
validator.expect_column_values_to_be_between("amount", min_value=0, max_value=1000000)
validator.expect_column_values_to_be_in_set("status", ["pending", "completed", "cancelled"])
validator.expect_table_row_count_to_be_between(min_value=100, max_value=1000000)
validator.expect_column_values_to_be_unique("order_id")

# 保存并运行
validator.save_expectation_suite()
results = validator.validate()
```

### Step 6: 监控告警

**Airflow 告警配置**：

```python
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
from airflow.providers.email.operators.email import EmailOperator

def task_failure_callback(context):
    """任务失败时发送 Slack 通知。"""
    slack = SlackWebhookHook(slack_webhook_conn_id="slack_alerts")
    slack.send(text=f"""
:rotating_light: DAG Failed: {context['dag'].dag_id}
Task: {context['task_instance'].task_id}
Execution: {context['execution_date']}
Exception: {context['exception']}
    """)

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """SLA 超时告警。"""
    slack = SlackWebhookHook(slack_webhook_conn_id="slack_alerts")
    slack.send(text=f":warning: SLA Missed: {dag.dag_id} - Tasks: {task_list}")

# 在 DAG 中使用
with DAG(
    dag_id="monitored_pipeline",
    sla_miss_callback=sla_miss_callback,
    ...
) as dag:

    critical_task = PythonOperator(
        task_id="critical_step",
        python_callable=do_work,
        on_failure_callback=task_failure_callback,
        sla=timedelta(hours=2),  # 任务 SLA
    )
```

**数据质量监控查询**：

```sql
-- 数据新鲜度检查
SELECT
    table_name,
    MAX(updated_at) AS last_update,
    CURRENT_TIMESTAMP - MAX(updated_at) AS staleness
FROM metadata.data_freshness
GROUP BY table_name
HAVING CURRENT_TIMESTAMP - MAX(updated_at) > INTERVAL '2 hours';

-- 行数趋势异常检测
WITH daily_counts AS (
    SELECT
        date,
        table_name,
        row_count,
        LAG(row_count) OVER (PARTITION BY table_name ORDER BY date) AS prev_count
    FROM metadata.row_counts
)
SELECT *
FROM daily_counts
WHERE row_count < prev_count * 0.5  -- 行数下降超过 50%
   OR row_count > prev_count * 2;   -- 行数增长超过 100%
```

### Step 7: 输出方案

完成后输出：

```markdown
## 数据管道方案

**数据源**: <源系统>
**目标**: <数据仓库/数据湖>
**调度频率**: <频率>
**工具栈**: Airflow + dbt + Great Expectations

### 管道架构

<架构图和数据流>

### DAG 定义

<Airflow DAG 代码>

### 数据模型

<dbt 模型结构>

### 验证规则

<Great Expectations 配置>

### 监控告警

<告警规则和通知渠道>
```

## 管道设计最佳实践

| 规则 | 说明 |
|------|------|
| **幂等性** | 管道重跑不应产生重复数据 |
| **增量处理** | 优先增量加载，避免全量扫描 |
| **数据验证** | 每个阶段后验证数据质量 |
| **错误处理** | 失败任务自动重试，超时告警 |
| **可观测性** | 记录每步的行数、耗时、数据质量指标 |
| **文档化** | dbt model 自带文档，保持更新 |
| **版本控制** | DAG 和 dbt 模型纳入 Git 管理 |
| **环境隔离** | dev/staging/prod 环境配置分离 |
| **Schema 管理** | 使用 schema migration 工具管理表结构变更 |
| **资源限制** | DAG 设置 execution_timeout，避免资源泄漏 |

## 快速使用

```
# ETL 管道设计
帮我设计一个从 MySQL 到 Snowflake 的日增量同步管道

# Airflow DAG
创建一个 Airflow DAG，每天凌晨同步用户数据并做聚合

# dbt 模型
帮我设计 dbt 模型，从原始订单数据生成每日销售报表

# 数据验证
用 Great Expectations 验证订单数据的完整性

# 管道优化
我的 Airflow DAG 运行太慢，帮我分析瓶颈并优化

# 监控告警
给我的数据管道添加 SLA 监控和失败告警
```
