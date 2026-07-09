---
name: data-pipeline
description: |
  【数据管道】ETL 管道设计、数据验证、监控告警。

  触发时机：
  - 用户要求"设计数据管道"、"ETL流程"
  - 需要搭建数据处理流水线
  - 数据需要清洗、转换、加载
category: development
---

# Data Pipeline — 数据管道

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

ETL 管道设计与实现，支持批处理和流处理。

## Workflow

1. **需求分析** — 数据源、目标、频率、SLA
2. **设计管道** — 提取 → 转换 → 加载 流程
3. **选择工具** — Airflow / dbt / Python 脚本
4. **实现逻辑** — 编写 DAG/脚本
5. **监控告警** — 失败重试、数据质量检查

## 管道模式

| 模式 | 适用场景 | 工具 |
|------|----------|------|
| 批处理 | 定时同步、报表 | Airflow, Cron |
| 流处理 | 实时数据、事件 | Kafka, Flink |
| CDC | 数据库同步 | Debezium, Maxwell |
| ETL | 数据仓库 | dbt, Spark |

## Airflow DAG 示例

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def extract(**context):
    """从数据源提取数据"""
    # SELECT * FROM source_table WHERE updated_at > last_sync
    return data

def transform(**context):
    """数据清洗和转换"""
    data = context['task_instance'].xcom_pull(task_ids='extract')
    # 清洗、去重、类型转换
    return cleaned_data

def load(**context):
    """加载到目标"""
    data = context['task_instance'].xcom_pull(task_ids='transform')
    # INSERT INTO target_table

with DAG('daily_etl', default_args=default_args,
         schedule_interval='0 2 * * *',  # 每天凌晨 2 点
         start_date=datetime(2026, 1, 1)) as dag:

    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)

    t1 >> t2 >> t3
```

## 数据验证

```python
import great_expectations as ge

def validate_data(df):
    """数据质量检查"""
    ge_df = ge.from_pandas(df)

    results = [
        ge_df.expect_column_values_to_not_be_null("id"),
        ge_df.expect_column_values_to_be_unique("id"),
        ge_df.expect_column_values_to_be_between("age", 0, 150),
        ge_df.expect_column_values_to_be_in_set("status", ["active", "inactive"]),
    ]

    failed = [r for r in results if not r["success"]]
    if failed:
        raise DataQualityError(f"验证失败: {failed}")
```

## Example

```
用户: 设计一个每日同步用户数据到数据仓库的管道

输出:
1. 数据源: MySQL users 表
2. 目标: PostgreSQL 数据仓库
3. 频率: 每天凌晨 2 点
4. 实现:
   - Airflow DAG: extract → transform → load
   - 增量同步: WHERE updated_at > last_sync
   - 数据验证: id 非空唯一、age 范围合理
   - 失败告警: 钉钉/邮件通知
```

## 参考

