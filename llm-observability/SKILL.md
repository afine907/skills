---
name: llm-observability
description: |
  【LLM 可观测性】为 AI Agent 系统设计可观测性方案。覆盖决策追踪、上下文健康监控、工具调用审计、成本追踪和异常告警。
category: operations
---

# LLM Observability — AI Agent 可观测性设计

为 AI Agent 系统设计可观测性方案，覆盖传统 APM 无法触及的 Agent 决策质量维度。

> **核心洞察：** 系统可以是基础设施健康的，同时完全错误。Agent 可以在幻觉的同时返回 200，在保持延迟阈值内的同时运行循环。传统监控不够。


## Goal

为 AI Agent 系统设计可观测性方案。覆盖决策追踪、上下文健康监控、工具调用审计、成本追踪和异常告警

## Trigger

- 用户说"agent 监控"、"LLM 可观测性"、"agent tracing"、"agent 日志"
  - 为 Agent 系统构建监控
  - 调试为什么 Agent 在长对话中退化
  - 需要了解生产环境中 Agent 的决策质量

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
识别 Agent 生命周期 → 定义追踪 Schema → 埋点决策点 → 配置仪表盘 → 配置告警
```

## Step 1: Agent 生命周期模型

将 Agent 执行分解为可观测的阶段：

```
用户输入
  → [1] 提示构建（组装系统提示 + 历史 + 用户输入）
  → [2] LLM 推理（发送到模型、获取响应）
  → [3] 决策解析（提取工具调用或最终回答）
  → [4] 工具执行（调用工具、获取结果）
  → [5] 结果整合（将工具结果反馈给 LLM 或返回用户）
  → [6] 上下文管理（压缩、摘要、清理）
  → 循环 [2]-[5] 直到完成
```

**每个阶段都需要独立埋点**，因为不同阶段的失败模式完全不同：
- 阶段 1 失败 → 提示拼接错误
- 阶段 2 失败 → 模型超时/限流
- 阶段 3 失败 → 响应解析错误
- 阶段 4 失败 → 工具调用失败（最常见的 Agent 失败模式）
- 阶段 5 失败 → 结果整合错误
- 阶段 6 失败 → 上下文退化

## Step 2: 决策追踪 Schema

每个 Agent 执行步骤生成一条追踪记录：

```json
{
  "trace_id": "唯一追踪ID",
  "session_id": "会话ID",
  "step_number": 3,
  "timestamp": "2026-05-29T10:30:00Z",
  "input": {
    "context_tokens": 4500,
    "context_utilization": 0.45,
    "relevant_history_steps": [1, 2]
  },
  "llm_call": {
    "model": "claude-sonnet-4",
    "input_tokens": 3200,
    "output_tokens": 450,
    "latency_ms": 1850,
    "cost_usd": 0.0165
  },
  "decision": {
    "type": "tool_call",
    "tool_name": "search_documents",
    "tool_params": {"query": "2024 Q3 report"},
    "confidence": 0.92
  },
  "tool_execution": {
    "latency_ms": 340,
    "success": true,
    "output_tokens": 1200,
    "error": null
  },
  "output": {
    "type": "tool_result",
    "tokens": 1200
  },
  "context_health": {
    "total_tokens_used": 8350,
    "window_utilization": 0.42,
    "compression_events": 0,
    "oldest_context_age_steps": 3
  }
}
```

> 完整 JSON Schema 见 [references/trace-schema.json](references/trace-schema.json)

## Step 3: 上下文健康指标

上下文退化是长任务 Agent 的头号杀手。需要持续监控以下指标：

| 指标 | 定义 | 告警阈值 | 检测方法 |
|------|------|---------|---------|
| **上下文利用率** | 已用 Token / 窗口大小 | > 80% 警告 | 每步计算 |
| **Token 预算追踪** | 剩余可用 Token 估算 | < 20% 警告 | 每步计算 |
| **压缩事件频率** | 上下文压缩/摘要的次数 | > 3 次/会话 警告 | 计数器 |
| **引用新鲜度** | 被引用的上下文的"年龄" | > 20 步 警告 | 追踪引用来源步骤 |
| **连贯性分数** | 跨轮次的一致性评估 | < 0.7 警告 | LLM-as-Judge 采样 |
| **任务漂移** | 当前目标与初始目标的偏离度 | > 0.3 警告 | 目标语义相似度 |

### 上下文退化检测

```
每步检查:
  if context_utilization > 0.8:
    触发压缩/摘要
    记录压缩事件

  if oldest_referenced_context > 20 steps:
    标记 "引用可能已过时"

  if 连续 3 步的决策置信度下降:
    标记 "可能正在退化"
    建议：重新注入任务目标
```

> 详细检测清单见 [references/context-health-checklist.md](references/context-health-checklist.md)

## Step 4: 工具调用审计

工具调用是 Agent 最常见的失败点。需要独立审计每个工具调用：

### 审计维度

| 维度 | 指标 | 告警阈值 |
|------|------|---------|
| **调用频率** | 每会话的工具调用总次数 | > 50 次/会话 |
| **错误率** | 失败调用 / 总调用 | > 10% |
| **参数验证失败率** | Schema 验证失败 / 总调用 | > 5% |
| **冗余调用率** | 相同参数的重复调用 / 总调用 | > 15% |
| **延迟 P95** | 95 分位延迟 | > 5 秒 |
| **工具成本占比** | 工具调用成本 / 总成本 | > 60% |

### 循环检测

```
对最近 N 次工具调用:
  if 存在连续 3+ 次相同工具 + 相同参数:
    标记 "疑似循环"
    触发断路器
```

## Step 5: 告警配置

### Agent 专用告警规则

| 告警 | 条件 | 级别 | 响应 |
|------|------|------|------|
| **上下文溢出** | context_utilization > 90% | Critical | 立即压缩或终止 |
| **工具错误率飙升** | error_rate > 10% (5分钟窗口) | Critical | 检查工具健康状态 |
| **成本飙升** | 单会话成本 > $1.00 | Warning | 检查是否有循环 |
| **延迟退化** | P95 延迟 > 2 倍基线 | Warning | 检查模型/工具性能 |
| **循环检测** | 相同工具连续调用 3+ 次 | Critical | 触发断路器 |
| **Token 爆炸** | 单次调用 > 50K tokens | Warning | 检查上下文管理 |
| **MTTD 超标** | 故障检测时间 > 5 分钟 | Warning | 检查监控覆盖 |

> 预置告警规则模板见 [references/alert-rules.md](references/alert-rules.md)

## Step 6: 仪表盘模板

### Agent 监控仪表盘布局

**第一行：概览指标（4 个卡片）**
- 活跃会话数
- 平均任务完成率
- 平均每会话成本
- 平均响应延迟

**第二行：趋势图（2 个图表）**
- 工具调用成功率趋势（按小时）
- 上下文利用率分布（直方图）

**第三行：详情表（2 个表格）**
- 工具调用详情（工具名、调用次数、成功率、P95 延迟、成本）
- 异常事件列表（时间、类型、严重程度、详情）

**第四行：单会话追踪**
- 选择特定 session_id，展示完整的决策链路
- 每步显示：输入上下文、LLM 调用、决策、工具调用、输出
- 高亮异常步骤（错误、高延迟、循环）

## 快速使用

```
用户：我的客服 Agent 在长对话中越来越不靠谱，经常忘记之前的对话内容
助手：使用 /llm-observability 分析上下文健康、设置退化检测告警、追踪决策质量
```

## 边界情况

- **流式 Agent** — 需要在流式传输过程中捕获中间状态，不能等到完成后再记录
- **多 Agent 系统** — 每个 Agent 独立追踪，通过 session_id 关联跨 Agent 调用
- **有外部记忆的 Agent** — 外部记忆检索也需要埋点，追踪检索结果的相关性
- **高频 Agent** — 大量并发会话时，追踪数据量巨大，需要采样策略

## MTTD 目标

**Mean Time to Detect（平均检测时间）** 是衡量可观测性的核心指标：

| 失败模式 | 目标 MTTD | 检测方式 |
|---------|----------|---------|
| 工具调用失败 | < 1 分钟 | 实时错误率告警 |
| 上下文退化 | < 5 分钟 | 上下文利用率趋势 |
| 循环执行 | < 2 分钟 | 连续调用检测 |
| 成本飙升 | < 5 分钟 | 成本阈值告警 |
| 幻觉输出 | < 1 小时 | 采样评估 + 人工审查 |

## 与其他技能的协作

- `agent-eval` — 可观测性数据喂入评估，评估标准反向定义"观测什么"
- `log-analyzer` — 扩展服务器日志模式到 Agent 决策日志
- `tool-use-patterns` — 工具调用指标是可观测性的核心维度
- `task-loom` — 复用 Ledger 模式存储决策追踪
