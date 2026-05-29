---
name: cost-optimization
description: |
  【成本优化】云成本分析、AI Token 成本追踪、资源合理配置、预算告警。

  触发时机：
  - 用户要求"优化成本"、"降低云费用"
  - 需要分析 AI API 调用成本
  - 资源配置需要优化

  提供成本分析和优化建议。
category: operations
---

# Cost Optimization — 成本优化与资源分析

云成本分析 + AI Token 成本追踪 + 资源合理配置 + 预算告警，一站式成本优化方案。

不适用：本地开发环境资源管理；非云基础设施的物理服务器采购；财务审计与合规报告。


## Goal

云成本分析、AI Token 成本追踪、资源合理配置、预算告警

## Trigger

- 用户要求"优化成本"、"降低云费用"
  - 需要分析 AI API 调用成本
  - 资源配置需要优化

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
收集信息 → 成本分析 → 识别优化点 → 制定方案 → 配置告警 → 输出报告
```

### Step 1: 收集成本信息

从用户描述中提取：
- **云平台**: AWS / GCP / Azure / 阿里云 / 腾讯云
- **资源类型**: 计算（EC2/GCE/VM）、存储（S3/GCS/Blob）、数据库（RDS/Cloud SQL）、网络
- **AI 服务**: OpenAI / Anthropic / Azure OpenAI / 自建模型
- **当前月支出**: 预估或实际金额
- **业务规模**: 用户量、请求量、数据量
- **痛点**: 费用飙升、资源浪费、预算超支

如果信息不足，询问 1-2 个关键问题，不要过度追问。

### Step 2: 云成本分析

读取 [references/cloud-pricing.md](references/cloud-pricing.md) 获取各云平台定价参考和成本分析命令。

**AWS 成本分析**：

```bash
# 获取本月支出概览
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" "UsageQuantity" \
  --group-by Type=DIMENSION,Key=SERVICE

# 按服务查看每日支出趋势
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "30 days ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Elastic Compute Cloud - Compute"]}}'

# 查看未使用的资源
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "7 days ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=USAGE_TYPE

# 查看预留实例利用率
aws ce get-savings-plans-utilization \
  --time-period Start=$(date -d "30 days ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY
```

**GCP 成本分析**：

```bash
# 查看项目级费用
gcloud billing accounts list
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID

# 使用 BigQuery 分析账单
bq query --use_legacy_sql=false '
  SELECT
    service.description AS service,
    SUM(cost) AS total_cost,
    SUM(credits.amount) AS total_credits,
    SUM(cost) + SUM(IFNULL(credits.amount, 0)) AS net_cost
  FROM `project.dataset.gcp_billing_export_v1_*`
  WHERE _PARTITIONTIME >= "2024-01-01"
  GROUP BY service.description
  ORDER BY total_cost DESC
  LIMIT 20
'
```

**Azure 成本分析**：

```bash
# 查看订阅费用
az cost management query \
  --type "ActualCost" \
  --timeframe "MonthToDate" \
  --dataset-aggregation '{"totalCost":{"name":"PreTaxCost","function":"Sum"}}' \
  --dataset-grouping '[{"type":"Dimension","name":"ServiceName"}]'

# 查看资源使用情况
az resource list --query "[].{Name:name, Type:type, Location:location, Size:sku.name}" -o table
```

### Step 3: AI Token 成本追踪

读取 [references/token-tracking.md](references/token-tracking.md) 获取 Token 定价和追踪方案。

**OpenAI 成本分析**：

```python
import openai
from datetime import datetime, timedelta

# 获取用量数据（需要 admin API key）
# OpenAI 定价参考（2024）：
# GPT-4o:        $2.50/1M input,  $10.00/1M output
# GPT-4o-mini:   $0.15/1M input,  $0.60/1M output
# GPT-4-turbo:   $10.00/1M input, $30.00/1M output
# Claude 3.5 Sonnet: $3.00/1M input, $15.00/1M output
# Claude 3 Haiku:    $0.25/1M input, $1.25/1M output

# Token 成本计算
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = {
        "gpt-4o":        {"input": 2.50,  "output": 10.00},
        "gpt-4o-mini":   {"input": 0.15,  "output": 0.60},
        "gpt-4-turbo":   {"input": 10.00, "output": 30.00},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku":    {"input": 0.25, "output": 1.25},
    }
    if model not in pricing:
        raise ValueError(f"Unknown model: {model}")
    p = pricing[model]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000
```

**Anthropic API 用量追踪**：

```python
import anthropic

# 使用 response headers 追踪用量
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)

# 从 usage 对象获取 token 数
input_tokens = message.usage.input_tokens
output_tokens = message.usage.output_tokens
print(f"Input: {input_tokens}, Output: {output_tokens}")
```

**批量 Token 统计脚本**：

```python
import json
from collections import defaultdict
from pathlib import Path

def analyze_usage_logs(log_dir: str) -> dict:
    """分析 API 调用日志，按模型统计 Token 和成本。"""
    stats = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "cost": 0.0})

    for log_file in Path(log_dir).glob("*.jsonl"):
        with open(log_file) as f:
            for line in f:
                entry = json.loads(line)
                model = entry.get("model", "unknown")
                usage = entry.get("usage", {})
                stats[model]["calls"] += 1
                stats[model]["input"] += usage.get("input_tokens", 0)
                stats[model]["output"] += usage.get("output_tokens", 0)

    # 计算成本
    for model, data in stats.items():
        data["cost"] = calculate_cost(model, data["input"], data["output"])

    return dict(stats)
```

### Step 4: 资源合理配置（Right-Sizing）

**计算资源优化**：

```bash
# AWS: 查找低利用率 EC2 实例
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxxxx \
  --start-time $(date -d "14 days ago" -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 86400 \
  --statistics Average

# AWS: 查找未挂载的 EBS 卷
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query "Volumes[*].{ID:VolumeId,Size:Size,Type:VolumeType,Created:CreateTime}"

# AWS: 查找未关联的 Elastic IP
aws ec2 describe-addresses \
  --query "Addresses[?AssociationId==null].{IP:PublicIp,AllocId:AllocationId}"

# GCP: 查找闲置资源
gcloud compute instances list --filter="status=TERMINATED" --format="table(name,zone,machineType)"
gcloud compute disks list --filter="!users:*" --format="table(name,sizeGb,type,zone)"
```

**存储优化**：

```bash
# AWS S3: 分析存储类分布
aws s3api list-buckets --query "Buckets[].Name" --output text | while read bucket; do
  echo "=== $bucket ==="
  aws s3api get-bucket-analytics-configuration \
    --bucket "$bucket" --id full-analysis 2>/dev/null || echo "No analytics configured"
done

# AWS S3: 设置生命周期策略（自动降级存储类）
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "auto-tiering",
      "Status": "Enabled",
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"},
        {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
      ],
      "Expiration": {"Days": 730}
    }]
  }'
```

### Step 5: 预算告警配置

**AWS Budget**：

```bash
# 创建月度预算告警
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "Monthly-Cost-Budget",
    "BudgetLimit": {"Amount": "1000", "Unit": "USD"},
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "team@example.com"
    }]
  }]'
```

**GCP Budget**：

```bash
# 创建预算告警
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Monthly Budget" \
  --budget-amount=1000 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100 \
  --all-updates-rule-pubsub-topic=projects/PROJECT_ID/topics/budget-alerts
```

**Prometheus + Grafana 自建监控**：

```yaml
# prometheus.yml - 抓取云成本指标
scrape_configs:
  - job_name: 'aws-cost'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 6h

# 告警规则
groups:
  - name: cost_alerts
    rules:
      - alert: HighDailyCost
        expr: aws_daily_cost_total > 50
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "日成本超过 $50"
          description: "当前日成本: {{ $value }} USD"
```

### Step 6: 输出成本优化报告

完成后输出：

```markdown
## 成本优化报告

**分析周期**: <起止日期>
**当前月支出**: <金额>
**优化后预估**: <金额>（节省 <百分比>）

### 成本分布

| 类别 | 当前支出 | 占比 | 优化空间 |
|------|----------|------|----------|
| 计算 (EC2/VM) | $xxx | xx% | $xxx |
| 存储 (S3/EBS) | $xxx | xx% | $xxx |
| 数据库 (RDS) | $xxx | xx% | $xxx |
| AI API | $xxx | xx% | $xxx |
| 网络/CDN | $xxx | xx% | $xxx |

### AI Token 用量

| 模型 | 调用次数 | 输入 Token | 输出 Token | 成本 |
|------|----------|-----------|-----------|------|
| gpt-4o | xxx | xxx | $xxx |
| claude-sonnet | xxx | xxx | $xxx |

### 优化建议

1. **[高优先级]** <具体建议> — 预计节省 $xxx/月
2. **[中优先级]** <具体建议> — 预计节省 $xxx/月
3. **[低优先级]** <具体建议> — 预计节省 $xxx/月

### 已配置告警

- 月度预算: $xxx（80%/100% 阈值告警）
- 日成本异常: 偏离均值 50% 触发告警
```

## 成本优化清单

| 检查项 | 说明 | 优先级 |
|--------|------|--------|
| 闲置资源清理 | 未使用的 VM、EIP、EBS 卷、快照 | 高 |
| 实例 Right-Sizing | 根据 CPU/内存利用率调整实例规格 | 高 |
| 预留实例/Savings Plans | 稳定负载使用 RI 或 SP 节省 30-70% | 高 |
| Spot/抢占式实例 | 容错任务使用 Spot 节省 60-90% | 中 |
| 存储分层 | 冷数据迁移到低成本存储类 | 中 |
| 数据库优化 | 读写分离、连接池、查询优化 | 中 |
| AI 模型降级 | 非关键任务使用更便宜的模型 | 中 |
| 缓存优化 | 减少重复 API 调用和数据库查询 | 中 |
| 网络优化 | 使用 CDN、减少跨区域流量 | 低 |
| 自动扩缩容 | 配置 HPA/ASG 按需扩缩 | 低 |
| 账单分析自动化 | 定期生成成本报告 | 低 |

## 最佳实践

| 规则 | 说明 |
|------|------|
| **标签管理** | 所有资源必须打标签（team/env/project），便于成本归因 |
| **预算先行** | 新项目上线前配置预算告警 |
| **定期审查** | 每月审查成本报告，每季度评估资源利用率 |
| **AI 成本意识** | 在代码中记录每次 API 调用的 token 用量和成本 |
| **自动化治理** | 使用 AWS Config / GCP Organization Policy 约束资源创建 |
| **FinOps 文化** | 将成本意识融入开发流程，每个 PR 评估成本影响 |

## 快速使用

```
# 云成本分析
帮我分析 AWS 本月支出，找出最大的成本项

# AI Token 成本
分析过去一周的 OpenAI API 调用成本，按模型统计

# 资源优化
检查我的 EC2 实例，找出低利用率的可以降配的

# 预算告警
帮我配置 AWS 月度预算，80% 和 100% 时发邮件告警

# 综合优化
帮我做一个全面的成本优化审查，包括云资源和 AI API 调用
```
