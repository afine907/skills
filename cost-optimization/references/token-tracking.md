# AI Token 成本追踪与优化

## 主流模型定价参考（2024-2025）

### OpenAI 模型

| 模型 | 输入价格 ($/1M tokens) | 输出价格 ($/1M tokens) | 上下文窗口 | 适用场景 |
|------|----------------------|----------------------|-----------|----------|
| GPT-4o | $2.50 | $10.00 | 128K | 多模态，通用 |
| GPT-4o-mini | $0.15 | $0.60 | 128K | 轻量任务，高性价比 |
| GPT-4-turbo | $10.00 | $30.00 | 128K | 复杂推理 |
| GPT-4.1 | $2.00 | $8.00 | 1M | 长上下文 |
| GPT-4.1-mini | $0.40 | $1.60 | 1M | 长上下文高性价比 |
| GPT-4.1-nano | $0.10 | $0.40 | 1M | 极致性价比 |
| o1 | $15.00 | $60.00 | 200K | 复杂推理 |
| o3-mini | $1.10 | $4.40 | 200K | 推理高性价比 |

### Anthropic 模型

| 模型 | 输入价格 ($/1M tokens) | 输出价格 ($/1M tokens) | 上下文窗口 | 适用场景 |
|------|----------------------|----------------------|-----------|----------|
| Claude Opus 4 | $15.00 | $75.00 | 200K | 最强推理 |
| Claude Sonnet 4 | $3.00 | $15.00 | 200K | 均衡性能 |
| Claude 3.5 Sonnet | $3.00 | $15.00 | 200K | 通用 |
| Claude 3.5 Haiku | $0.80 | $4.00 | 200K | 快速轻量 |
| Claude 3 Haiku | $0.25 | $1.25 | 200K | 极致性价比 |

### Google 模型

| 模型 | 输入价格 ($/1M tokens) | 输出价格 ($/1M tokens) | 上下文窗口 |
|------|----------------------|----------------------|-----------|
| Gemini 2.5 Pro | $1.25-$2.50 | $10.00 | 1M |
| Gemini 2.0 Flash | $0.10 | $0.40 | 1M |
| Gemini 1.5 Pro | $1.25-$2.50 | $5.00-$10.00 | 2M |

## Token 追踪实现

### OpenAI SDK 用量追踪

```python
from openai import OpenAI

client = OpenAI()

def call_with_tracking(model: str, messages: list) -> dict:
    """带用量追踪的 API 调用。"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    usage = response.usage
    return {
        "model": model,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "response": response.choices[0].message.content,
    }
```

### Anthropic SDK 用量追踪

```python
import anthropic

client = anthropic.Anthropic()

def call_with_tracking(model: str, messages: list, system: str = "") -> dict:
    """带用量追踪的 API 调用。"""
    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    return {
        "model": model,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_read": getattr(response.usage, "cache_read_input_tokens", 0),
        "cache_creation": getattr(response.usage, "cache_creation_input_tokens", 0),
        "response": response.content[0].text,
    }
```

### 通用成本计算器

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelPricing:
    input_per_million: float   # $/1M input tokens
    output_per_million: float  # $/1M output tokens

# 定价表（保持更新）
PRICING = {
    "gpt-4o": ModelPricing(2.50, 10.00),
    "gpt-4o-mini": ModelPricing(0.15, 0.60),
    "gpt-4-turbo": ModelPricing(10.00, 30.00),
    "gpt-4.1": ModelPricing(2.00, 8.00),
    "gpt-4.1-mini": ModelPricing(0.40, 1.60),
    "claude-sonnet-4-20250514": ModelPricing(3.00, 15.00),
    "claude-opus-4-20250514": ModelPricing(15.00, 75.00),
    "claude-3-5-haiku-20241022": ModelPricing(0.80, 4.00),
    "claude-3-haiku-20240307": ModelPricing(0.25, 1.25),
    "gemini-2.5-pro": ModelPricing(1.25, 10.00),
    "gemini-2.0-flash": ModelPricing(0.10, 0.40),
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """计算单次 API 调用成本（美元）。"""
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}. Add pricing to PRICING dict.")
    p = PRICING[model]
    return (input_tokens * p.input_per_million + output_tokens * p.output_per_million) / 1_000_000

def format_cost_report(stats: dict) -> str:
    """格式化成本报告。"""
    lines = ["Model                Calls   Input TK    Output TK    Cost"]
    lines.append("-" * 65)
    total_cost = 0.0
    for model, data in sorted(stats.items(), key=lambda x: x[1]["cost"], reverse=True):
        cost = data["cost"]
        total_cost += cost
        lines.append(
            f"{model:<20} {data['calls']:>6} {data['input']:>10,} {data['output']:>10,}  ${cost:.4f}"
        )
    lines.append("-" * 65)
    lines.append(f"{'TOTAL':<20} {'':>6} {'':>10} {'':>10}  ${total_cost:.4f}")
    return "\n".join(lines)
```

## 成本优化策略

### 1. 模型降级策略

```python
def select_model(task_complexity: str, context_needed: bool = False) -> str:
    """根据任务复杂度选择最经济的模型。"""
    if task_complexity == "simple":
        return "gpt-4o-mini"            # $0.15/$0.60
    elif task_complexity == "medium":
        return "claude-3-5-haiku-20241022"  # $0.80/$4.00
    elif task_complexity == "complex" and context_needed:
        return "claude-sonnet-4-20250514"   # $3.00/$15.00
    else:
        return "gpt-4o"                 # $2.50/$10.00
```

### 2. Prompt 缓存（Anthropic）

```python
# Anthropic 支持 prompt caching，重复前缀不重复计费
# 缓存写入: 1.25x 基础价格
# 缓存读取: 0.1x 基础价格（节省 90%）

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "你是一个专业的代码审查助手...",  # 长 system prompt
            "cache_control": {"type": "ephemeral"},   # 启用缓存
        }
    ],
    messages=[{"role": "user", "content": "审查这段代码..."}],
)

# 检查缓存命中
cache_read = response.usage.cache_read_input_tokens  # 命中缓存的 token 数
```

### 3. 批处理优化（OpenAI Batch API）

```python
# OpenAI Batch API: 50% 折扣，24 小时内完成
# 适合非实时任务：数据标注、批量生成、评估

import json

# 准备 batch 文件
tasks = [
    {"custom_id": "task-1", "method": "POST", "url": "/v1/chat/completions",
     "body": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Summarize: ..."}], "max_tokens": 100}},
    # ... 更多任务
]

with open("batch_input.jsonl", "w") as f:
    for task in tasks:
        f.write(json.dumps(task) + "\n")

# 上传并创建 batch
batch_file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch = client.batches.create(input_file_id=batch_file.id, endpoint="/v1/chat/completions", completion_window="24h")
```

### 4. 输出长度控制

```python
# 精确控制 max_tokens 避免浪费
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "用一句话回答：Python 是什么？"}],
    max_tokens=50,  # 不要用默认的大值
)

# 使用 stop 序列提前终止
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "列出 3 个 Python 优点"}],
    max_tokens=200,
    stop=["\n\n"],  # 避免生成多余内容
)
```

### 5. 结构化输出减少 token

```python
import json

# 使用 JSON mode 减少冗余输出
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "以 JSON 格式回复"},
        {"role": "user", "content": "分析这段代码的复杂度"},
    ],
    response_format={"type": "json_object"},
)
```

## 成本监控日志格式

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123",
  "model": "gpt-4o",
  "user_id": "user_456",
  "project": "chatbot-v2",
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 300,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0
  },
  "cost_usd": 0.00675,
  "latency_ms": 2300,
  "task_type": "chat",
  "metadata": {
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": true
  }
}
```

## 成本异常检测

```python
import statistics
from datetime import datetime, timedelta

def detect_cost_anomaly(daily_costs: list[float], threshold: float = 2.0) -> list[dict]:
    """检测日成本异常（超过均值 N 个标准差）。"""
    if len(daily_costs) < 7:
        return []

    mean = statistics.mean(daily_costs)
    stdev = statistics.stdev(daily_costs)
    anomalies = []

    for i, cost in enumerate(daily_costs):
        if abs(cost - mean) > threshold * stdev:
            anomalies.append({
                "day": i,
                "cost": cost,
                "mean": mean,
                "deviation": (cost - mean) / stdev,
                "type": "spike" if cost > mean else "drop",
            })

    return anomalies
```
