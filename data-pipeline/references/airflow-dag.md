# Airflow DAG 模板与最佳实践

## DAG 基础模板

### 标准批处理 DAG

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLCheckOperator, SQLValueCheckOperator
from airflow.utils.trigger_rule import TriggerRule

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email": ["alert@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=2),
    "sla": timedelta(hours=3),
}

with DAG(
    dag_id="example_etl_pipeline",
    default_args=default_args,
    description="Example ETL pipeline with best practices",
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    concurrency=4,
    tags=["etl", "example"],
    doc_md="""
    ## Example ETL Pipeline

    This DAG extracts data from source, transforms it, validates,
    and loads into the warehouse.

    ### Schedule
    - Runs daily at 06:00 UTC
    - SLA: 3 hours from execution start

    ### Dependencies
    - Source: PostgreSQL (source_db)
    - Target: Snowflake (warehouse)
    """,
) as dag:

    start = EmptyOperator(task_id="start")

    def extract_fn(**context):
        """Extract data from source."""
        ds = context["ds"]
        # ... extraction logic
        row_count = 0  # actual count
        context["task_instance"].xcom_push(key="row_count", value=row_count)
        return row_count

    def transform_fn(**context):
        """Transform extracted data."""
        row_count = context["task_instance"].xcom_pull(
            task_ids="extract", key="row_count"
        )
        # ... transformation logic

    def validate_fn(**context):
        """Validate transformed data."""
        # ... validation logic
        pass

    def load_fn(**context):
        """Load data into warehouse."""
        # ... load logic
        pass

    extract = PythonOperator(task_id="extract", python_callable=extract_fn)
    transform = PythonOperator(task_id="transform", python_callable=transform_fn)
    validate = PythonOperator(task_id="validate", python_callable=validate_fn)
    load = PythonOperator(task_id="load", python_callable=load_fn)

    row_count_check = SQLValueCheckOperator(
        task_id="row_count_check",
        conn_id="warehouse",
        sql="SELECT COUNT(*) FROM fact_orders WHERE date = '{{ ds }}'",
        pass_value=100,
        tolerance=0.5,
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_SUCCESS)

    start >> extract >> transform >> validate >> load >> row_count_check >> end
```

### 传感器模式（等待外部事件）

```python
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.sql import SqlSensor
from airflow.providers.http.sensors.http import HttpSensor

# 等待上游 DAG 完成
wait_for_upstream = ExternalTaskSensor(
    task_id="wait_for_upstream",
    external_dag_id="upstream_dag",
    external_task_id="end",
    allowed_states=["success"],
    failed_states=["failed"],
    timeout=3600,
    poke_interval=60,
)

# 等待文件到达
wait_for_file = FileSensor(
    task_id="wait_for_file",
    filepath="/data/incoming/orders_{{ ds }}.csv",
    timeout=3600,
    poke_interval=60,
)

# 等待数据就绪
wait_for_data = SqlSensor(
    task_id="wait_for_data",
    conn_id="source_db",
    sql="SELECT COUNT(*) FROM orders WHERE date = '{{ ds }}'",
    timeout=3600,
    poke_interval=300,
)
```

### 动态任务生成（TaskGroup）

```python
from airflow.utils.task_group import TaskGroup

def process_table(table_name: str, **context):
    """Process a single table."""
    pass

tables = ["users", "orders", "products", "inventory"]

with TaskGroup("process_tables") as process_group:
    for table in tables:
        PythonOperator(
            task_id=f"process_{table}",
            python_callable=process_table,
            op_kwargs={"table_name": table},
        )

# 在 DAG 中使用
start >> process_group >> end
```

### 分支逻辑

```python
def choose_branch(**context):
    """决定执行哪条路径。"""
    ds = context["ds"]
    # 检查数据量
    hook = PostgresHook(postgres_conn_id="source_db")
    count = hook.get_first("SELECT COUNT(*) FROM orders WHERE date = %s", parameters=(ds,))[0]

    if count > 10000:
        return "process_full"
    elif count > 0:
        return "process_incremental"
    else:
        return "skip_no_data"

branch = BranchPythonOperator(task_id="branch", python_callable=choose_branch)
process_full = PythonOperator(task_id="process_full", python_callable=full_process)
process_incremental = PythonOperator(task_id="process_incremental", python_callable=incremental_process)
skip = EmptyOperator(task_id="skip_no_data")
join = EmptyOperator(task_id="join", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

branch >> [process_full, process_incremental, skip] >> join
```

## Operator 速查表

| 场景 | Operator | 说明 |
|------|----------|------|
| Python 函数 | `PythonOperator` | 最灵活 |
| SQL 查询 | `SQLExecuteQueryOperator` | 执行 SQL |
| SQL 检查 | `SQLCheckOperator` | 条件检查 |
| 文件到 S3 | `LocalFilesystemToS3Operator` | 上传文件 |
| S3 到 Redshift | `S3ToRedshiftOperator` | 批量加载 |
| 大查询 | `BigQueryInsertJobOperator` | BQ 任务 |
| Spark | `SparkSubmitOperator` | Spark 作业 |
| dbt | `BashOperator` / `DbtRunOperator` | dbt 执行 |
| Docker | `DockerOperator` | 容器化任务 |
| Kubernetes | `KubernetesPodOperator` | K8s Pod |

## 连接管理

```python
# 通过 Airflow UI 或 CLI 配置连接
# 推荐使用环境变量或 Secrets Manager

# 环境变量方式
# AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql://user:pass@host:5432/db

# AWS Secrets Manager
# 在 airflow.cfg 中配置:
# [secrets]
# backend = airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend
# backend_kwargs = {"connections_prefix": "airflow/connections/"}
```

## DAG 调试技巧

```python
# 1. 使用 PythonOperator 打印调试信息
def debug_context(**context):
    print(f"DAG: {context['dag'].dag_id}")
    print(f"Execution Date: {context['ds']}")
    print(f"Task Instance: {context['task_instance']}")
    print(f"Params: {context['params']}")

# 2. 测试单个任务
# airflow tasks test etl_daily_pipeline extract 2024-01-15

# 3. 测试整个 DAG（不实际执行）
# airflow dags test etl_daily_pipeline 2024-01-15

# 4. 使用 XCom 传递数据
def push_data(**context):
    context["task_instance"].xcom_push(key="my_key", value={"data": [1, 2, 3]})

def pull_data(**context):
    data = context["task_instance"].xcom_pull(task_ids="push_data", key="my_key")
    print(f"Received: {data}")
```

## 性能优化

| 优化点 | 方法 |
|--------|------|
| 并行执行 | 使用 `ParallelExecutor` 或 `CeleryExecutor` |
| 减少 XCom | 大数据用文件/S3 传递，不走 XCom |
| 连接池 | 使用 `PooledPostgresHook` |
| 批量操作 | 使用 `insert_rows` 而非逐行插入 |
| 增量处理 | 避免全量扫描，使用时间分区 |
| 传感器模式 | 使用 `reschedule` 模式而非 `poke` |

```python
# reschedule 模式释放 Worker Slot
sensor = SqlSensor(
    task_id="wait_for_data",
    conn_id="source_db",
    sql="SELECT COUNT(*) FROM orders WHERE date = '{{ ds }}'",
    mode="reschedule",  # 释放 slot
    poke_interval=300,
)
```
