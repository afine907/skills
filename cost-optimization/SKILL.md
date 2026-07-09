---
name: cost-optimization
description: |
  【成本优化】云成本分析、AI Token 成本追踪、资源合理配置、预算告警。

  触发时机：
  - 用户要求"优化成本"、"降低云费用"
  - 需要分析 AI API 调用成本
  - 资源配置需要优化
category: operations
---

# Cost Optimization — 成本优化

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

云成本分析 + AI Token 成本追踪 + 资源优化。

## Workflow

1. **成本分析** — 收集各服务/AI API 的用量和费用
2. **识别热点** — 找出成本最高的服务/接口/模型
3. **制定策略** — 缓存、降级、模型切换、批量处理
4. **实施优化** — 代码层面和架构层面
5. **监控预算** — 设置告警阈值

## AI Token 成本追踪

```python
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TokenUsage:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float = field(default_factory=time.time)

class CostTracker:
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},        # per 1M tokens
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "deepseek-chat": {"input": 0.14, "output": 0.28},
    }

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

    def log_usage(self, usage: TokenUsage):
        """记录用量到数据库/日志"""
        print(f"[COST] {usage.model}: ${usage.cost_usd:.4f} ({usage.input_tokens}+{usage.output_tokens} tokens)")

    def daily_summary(self) -> dict:
        """每日成本汇总"""
        # SELECT model, SUM(cost_usd), COUNT(*) FROM token_usage GROUP BY model
        pass
```

## 成本优化策略

| 策略 | 场景 | 节省幅度 |
|------|------|----------|
| Prompt 缓存 | 相似请求 | 50-90% |
| 模型降级 | 简单任务用小模型 | 60-80% |
| 批量处理 | 非实时请求 | 30-50% |
| 结果缓存 | 重复查询 | 90%+ |
| Token 限制 | 控制输出长度 | 20-40% |

## 云资源优化

```bash
# 查看 AWS 费用分布

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
aws ce get-cost-and-usage --time-period Start=2026-01-01,End=2026-02-01 \
  --granularity MONTHLY --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# 查看闲置资源

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
aws ec2 describe-instances --filters "Name=instance-state-name,Values=stopped" \
  --query 'Reservations[].Instances[].[InstanceId,LaunchTime]'

# 设置预算告警

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
aws budgets create-budget --account-id 123456789 --budget '{
  "BudgetName": "monthly-limit",
  "BudgetLimit": {"Amount": "1000", "Unit": "USD"},
  "TimeUnit": "MONTHLY"
}'
```

## Example

```
用户: AI API 费用太高，每月 $500，需要优化

输出:
1. 分析: GPT-4o 占 70%，主要用于客服问答
2. 策略:
   - 客服问答降级到 GPT-4o-mini (节省 80%)
   - 相似问题加缓存 (节省 50%)
   - 设置每日 $20 预算告警
3. 预期: $500 → $100/月
```

## 参考

