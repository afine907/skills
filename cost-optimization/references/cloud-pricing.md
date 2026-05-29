# 云平台定价参考与成本分析命令

## AWS 核心服务定价参考（us-east-1，按需）

### 计算 (EC2)

| 实例类型 | vCPU | 内存 | 按需价格/小时 | 用途 |
|----------|------|------|--------------|------|
| t3.micro | 2 | 1 GB | $0.0104 | 开发测试 |
| t3.small | 2 | 2 GB | $0.0208 | 轻量应用 |
| t3.medium | 2 | 4 GB | $0.0416 | 中小型服务 |
| t3.large | 2 | 8 GB | $0.0832 | 中型服务 |
| m6i.large | 2 | 8 GB | $0.0960 | 通用生产 |
| m6i.xlarge | 4 | 16 GB | $0.1920 | 通用生产 |
| c6i.large | 2 | 4 GB | $0.0850 | 计算密集 |
| r6i.large | 2 | 16 GB | $0.1260 | 内存密集 |
| g5.xlarge | 4 | 16 GB | $1.0060 | GPU 推理 |

### 存储 (S3)

| 存储类 | 每 GB/月 | 适用场景 |
|--------|---------|----------|
| Standard | $0.023 | 频繁访问 |
| Standard-IA | $0.0125 | 不频繁访问 |
| One Zone-IA | $0.01 | 不频繁，可重建数据 |
| Glacier Instant | $0.004 | 归档，毫秒检索 |
| Glacier Flexible | $0.0036 | 归档，分钟级检索 |
| Deep Archive | $0.00099 | 长期归档，小时级检索 |

### 数据库 (RDS)

| 引擎 | 实例 | vCPU | 内存 | 按需/小时 |
|------|------|------|------|----------|
| MySQL | db.t3.micro | 2 | 1 GB | $0.017 |
| MySQL | db.t3.medium | 2 | 4 GB | $0.068 |
| MySQL | db.r6g.large | 2 | 16 GB | $0.240 |
| PostgreSQL | db.t3.micro | 2 | 1 GB | $0.018 |
| PostgreSQL | db.r6g.large | 2 | 16 GB | $0.252 |

### 节省方案对比

| 方案 | 折扣 | 承诺 | 适用场景 |
|------|------|------|----------|
| Savings Plans (1yr) | ~30% | 1 年 | 稳定工作负载 |
| Savings Plans (3yr) | ~50% | 3 年 | 长期稳定 |
| Reserved Instances (1yr) | ~35% | 1 年 | 可预测实例使用 |
| Reserved Instances (3yr) | ~60% | 3 年 | 基础设施固定 |
| Spot Instances | ~60-90% | 无 | 容错批处理 |

## GCP 核心服务定价参考（us-central1）

### 计算 (Compute Engine)

| 机器类型 | vCPU | 内存 | 按需/小时 | 抢占式/小时 |
|----------|------|------|----------|------------|
| e2-micro | 0.25-2 | 1 GB | $0.00838 | $0.00251 |
| e2-small | 0.5-2 | 2 GB | $0.01675 | $0.00503 |
| e2-medium | 1-2 | 4 GB | $0.03351 | $0.01005 |
| e2-standard-2 | 2 | 8 GB | $0.06701 | $0.02010 |
| n2-standard-2 | 2 | 8 GB | $0.09711 | $0.02913 |

### GCP 节省方案

| 方案 | 折扣 | 说明 |
|------|------|------|
| Sustained Use | ~20-30% | 自动折扣，月运行 >25% |
| Committed Use (1yr) | ~37% | 1 年承诺 |
| Committed Use (3yr) | ~55% | 3 年承诺 |
| Preemptible/Spot | ~60-91% | 最长 24 小时（Spot 无限制） |

## Azure 核心服务定价参考（East US）

### 计算 (Virtual Machines)

| 系列 | vCPU | 内存 | 按需/小时 | 用途 |
|------|------|------|----------|------|
| B1s | 1 | 1 GB | $0.0104 | 开发测试 |
| B2s | 2 | 4 GB | $0.0416 | 轻量应用 |
| D2s_v5 | 2 | 8 GB | $0.0960 | 通用 |
| F2s_v2 | 2 | 4 GB | $0.0846 | 计算密集 |

### Azure 节省方案

| 方案 | 折扣 | 说明 |
|------|------|------|
| Reserved VM (1yr) | ~30-40% | 1 年预留 |
| Reserved VM (3yr) | ~50-60% | 3 年预留 |
| Spot VM | ~60-90% | 可被驱逐 |
| Azure Hybrid Benefit | ~40-50% | 已有 Windows/SQL 许可 |

## 成本分析命令速查

### AWS Cost Explorer CLI

```bash
# 月度总支出
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost

# 按服务分组
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# 按标签分组（需要先激活标签）
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=TAG,Key=Environment

# 预测下月费用
aws ce get-cost-forecast \
  --time-period Start=2024-02-01,End=2024-03-01 \
  --granularity MONTHLY \
  --metric UNBLENDED_COST

# 获取 Savings Plans 推荐
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT
```

### GCP Billing CLI

```bash
# 列出账单账户
gcloud billing accounts list

# 列出项目关联的账单
gcloud billing projects describe PROJECT_ID

# 导出账单到 BigQuery（一次性设置）
gcloud billing accounts export \
  --billing-account=BILLING_ACCOUNT_ID \
  --dataset-id=billing_dataset

# 查看预算
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID
```

### Azure Cost Management CLI

```bash
# 查看本月费用
az cost management query \
  --scope "/subscriptions/SUBSCRIPTION_ID" \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-aggregation '{"totalCost":{"name":"PreTaxCost","function":"Sum"}}'

# 按资源组分组
az cost management query \
  --scope "/subscriptions/SUBSCRIPTION_ID" \
  --type ActualCost \
  --timeframe MonthToDate \
  --dataset-aggregation '{"totalCost":{"name":"PreTagCost","function":"Sum"}}' \
  --dataset-grouping '[{"type":"Dimension","name":"ResourceGroupName"}]'

# 查看 Advisor 推荐
az advisor recommendation list \
  --category Cost \
  --query "[].{Resource:resourceMetadata.resourceId, Impact:impact, Description:shortDescription.problem}"
```
