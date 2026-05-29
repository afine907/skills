# Agent 统一监控仪表盘方案

## 1. 概述

本方案为 5 个生产环境 Agent 构建统一可观测性体系，覆盖基础设施健康、成本消耗、决策质量和安全审计四个维度。核心目标是让管理者在一个仪表盘上掌握全局健康状况，同时支持按 Agent 维度下钻排查。

### 设计原则

- **分层聚合**：全局概览 -> Agent 维度 -> 单会话追踪，逐层下钻
- **实时 + 趋势并重**：既有实时状态卡片，也有小时/天/周趋势
- **异常驱动**：正常状态静默，异常状态高亮，降低认知负荷
- **成本可视**：将 Token 消耗换算为美元，让非技术角色也能理解

---

## 2. Agent 生命周期模型

每个 Agent 执行被分解为 6 个可观测阶段，每阶段独立埋点：

```
用户输入
  [1] 提示构建  -- 组装系统提示 + 历史 + 用户输入
  [2] LLM 推理  -- 发送请求到模型、获取响应
  [3] 决策解析  -- 提取工具调用或最终回答
  [4] 工具执行  -- 调用工具、获取结果
  [5] 结果整合  -- 将工具结果反馈给 LLM 或返回用户
  [6] 上下文管理 -- 压缩、摘要、清理
  循环 [2]-[5] 直到完成
```

各阶段失败模式不同，需要独立监控：
- 阶段 1 失败 -> 提示拼接错误
- 阶段 2 失败 -> 模型超时/限流
- 阶段 3 失败 -> 响应解析错误
- 阶段 4 失败 -> 工具调用失败（最常见）
- 阶段 5 失败 -> 结果整合错误
- 阶段 6 失败 -> 上下文退化

---

## 3. 决策追踪 Schema

每条 Agent 执行步骤生成一条结构化追踪记录：

```json
{
  "trace_id": "uuid",
  "session_id": "session-abc",
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
    "cost_usd": 0.0165,
    "cached_tokens": 800
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

聚合维度：按 Agent、按模型、按会话、按用户、按时间。

---

## 4. 指标体系

### 4.1 性能指标

| 指标名 | 定义 | 基准值 |
|--------|------|--------|
| `agent.latency.first_token` | 首次响应时间 | < 2 秒 |
| `agent.latency.total` | 会话总完成时间 | 任务相关 |
| `agent.latency.p50` | 50 分位延迟 | < 3 秒 |
| `agent.latency.p95` | 95 分位延迟 | < 10 秒 |
| `agent.latency.p99` | 99 分位延迟 | < 30 秒 |

### 4.2 成本指标

| 指标名 | 定义 | 基准值 |
|--------|------|--------|
| `agent.cost.per_session` | 每会话成本 | < $0.10 |
| `agent.cost.per_task` | 每任务成本 | 任务相关 |
| `agent.tokens.input` | 输入 Token 数 | 趋势监控 |
| `agent.tokens.output` | 输出 Token 数 | 趋势监控 |
| `agent.tokens.cache_hit_rate` | 缓存命中率 | > 50% |

### 4.3 质量指标

| 指标名 | 定义 | 基准值 |
|--------|------|--------|
| `agent.completion.success_rate` | 任务成功率 | > 90% |
| `agent.completion.steps_avg` | 平均步骤数 | 趋势监控 |
| `agent.hallucination.rate` | 幻觉率（采样） | < 5% |
| `agent.coherence.score` | 连贯性分数 | > 0.8 |
| `agent.decision.confidence` | 平均决策置信度 | > 0.8 |

### 4.4 工具指标

| 指标名 | 定义 | 基准值 |
|--------|------|--------|
| `agent.tools.call_count` | 工具调用次数 | 趋势监控 |
| `agent.tools.error_rate` | 工具错误率 | < 5% |
| `agent.tools.retry_rate` | 工具重试率 | < 10% |
| `agent.tools.redundant_rate` | 冗余调用率 | < 5% |
| `agent.tools.circuit_breaks` | 断路器触发次数 | 0 |

### 4.5 上下文健康指标

| 指标名 | 定义 | 基准值 |
|--------|------|--------|
| `agent.context.utilization` | 上下文利用率 | < 80% |
| `agent.context.budget_remaining` | 剩余 Token 预算 | > 20% |
| `agent.context.compression_count` | 压缩事件数 | < 3 |
| `agent.context.reference_age` | 引用新鲜度 | < 10 步 |
| `agent.context.drift_score` | 任务漂移分数 | < 0.3 |

### 4.6 安全指标

| 指标名 | 定义 | 基准值 |
|--------|------|--------|
| `agent.security.injection_attempts` | 注入攻击尝试 | 监控 |
| `agent.security.permission_denials` | 权限拒绝次数 | 监控 |
| `agent.security.sensitive_data_exposed` | 敏感数据泄露 | 0 |
| `agent.security.scope_violations` | 范围越权 | 0 |

---

## 5. 仪表盘设计

### 5.1 全局概览页（Level 1）

管理者日常查看的核心页面，一眼掌握 5 个 Agent 的整体状态。

#### 第一行：核心状态卡片（5 个）

| 卡片 | 数据来源 | 健康判断 |
|------|---------|---------|
| **总体健康度** | 加权综合评分 | 绿 > 0.8 / 黄 0.6-0.8 / 红 < 0.6 |
| **24h 总成本** | 5 个 Agent 成本求和 | 对比昨日同期 |
| **任务成功率** | 成功任务 / 总任务 | 绿 > 90% / 黄 80-90% / 红 < 80% |
| **平均延迟 P95** | 5 个 Agent P95 的加权平均 | 绿 < 10s / 黄 10-30s / 红 > 30s |
| **活跃告警数** | 告警系统 | 绿 0 / 黄 1-5 / 红 > 5 |

#### 第二行：Agent 健康矩阵

以表格形式展示 5 个 Agent 的并排对比：

| Agent | 状态 | 24h会话数 | 成功率 | 平均成本/会话 | P95延迟 | 活跃告警 |
|-------|------|----------|--------|--------------|---------|---------|
| Agent-A | 健康 | 1,240 | 94.2% | $0.08 | 3.2s | 0 |
| Agent-B | 警告 | 890 | 87.1% | $0.15 | 8.5s | 2 |
| Agent-C | 健康 | 2,100 | 96.8% | $0.05 | 2.1s | 0 |
| Agent-D | 危险 | 156 | 72.3% | $0.42 | 15.3s | 5 |
| Agent-E | 健康 | 560 | 91.5% | $0.11 | 4.8s | 1 |

状态颜色编码：绿色 = 健康、黄色 = 警告、红色 = 危险、灰色 = 无数据。

#### 第三行：趋势图（2 个）

**成本趋势（折线图）**
- X 轴：过去 7 天，每天一个数据点
- Y 轴：每日总成本（USD）
- 5 条线，每条代表一个 Agent
- 叠加一条虚线表示预算线

**任务成功率趋势（折线图）**
- X 轴：过去 7 天
- Y 轴：成功率百分比
- 5 条线，每条代表一个 Agent
- 红色区域标记 < 80% 的危险区

#### 第四行：告警汇总

按严重程度排序的告警列表，显示最近 24 小时的告警：

| 时间 | Agent | 告警 | 级别 | 状态 |
|------|-------|------|------|------|
| 10:32 | Agent-D | 工具错误率 > 30% | Critical | 处理中 |
| 10:28 | Agent-B | 单会话成本 > $1.00 | Warning | 待处理 |
| 09:15 | Agent-D | 循环执行检测 | Critical | 已确认 |
| 08:42 | Agent-E | P95 延迟 > 基线 2x | Warning | 已恢复 |

### 5.2 Agent 详情页（Level 2）

点击某个 Agent 进入详情页，展示该 Agent 的完整指标。

#### 顶部：Agent 状态摘要

- Agent 名称、模型、描述
- 当前状态指示灯
- 运行时长、总会话数

#### 第一行：核心指标卡片（6 个）

- 24h 会话数（对比昨日）
- 任务成功率（趋势箭头）
- 平均每会话成本
- 平均步骤数
- 上下文利用率中位数
- 工具错误率

#### 第二行：上下文健康面板

专门展示上下文健康指标，这是长任务 Agent 的头号风险：

- **上下文利用率分布直方图**：X 轴为利用率区间（0-20%, 20-40%, ..., 80-100%），Y 轴为会话数。红色标记 > 80% 的区间。
- **压缩事件趋势**：过去 24 小时每小时的压缩事件数。
- **引用新鲜度分布**：引用来源步骤年龄的分布。

#### 第三行：工具调用审计表

| 工具名 | 调用次数 | 成功率 | P95 延迟 | 冗余率 | 成本占比 |
|--------|---------|--------|---------|--------|---------|
| search_docs | 3,200 | 98.5% | 1.2s | 2.1% | 15% |
| write_file | 1,800 | 99.1% | 0.8s | 0.5% | 8% |
| api_call | 2,100 | 85.3% | 4.5s | 12.3% | 45% |
| db_query | 900 | 96.7% | 2.1s | 3.2% | 22% |

#### 第四行：质量指标趋势

- **决策置信度趋势**：过去 7 天的平均决策置信度
- **幻觉率趋势**：采样评估的幻觉率变化
- **连贯性分数趋势**：LLM-as-Judge 评分变化

### 5.3 单会话追踪页（Level 3）

选择特定 session_id，展示完整的决策链路。

#### 会话元信息

- Session ID、Agent、用户、开始时间、持续时长
- 总步骤数、总成本、最终状态

#### 决策时间线

垂直时间线展示每一步的执行：

```
Step 1 [10:30:00] 用户输入
  输入 Token: 320 | 上下文利用率: 5%
  决策: text_response (置信度: 0.95)
  LLM: claude-sonnet-4 | 延迟: 1.2s | 成本: $0.003

Step 2 [10:30:02] 工具调用
  输入 Token: 1,200 | 上下文利用率: 12%
  决策: tool_call -> search_documents (置信度: 0.92)
  工具: 成功 | 延迟: 0.8s
  LLM: claude-sonnet-4 | 延迟: 2.1s | 成本: $0.008

Step 3 [10:30:05] [WARNING] 上下文利用率 78%
  输入 Token: 8,500 | 上下文利用率: 78%
  决策: tool_call -> api_call (置信度: 0.65)
  工具: 失败 (timeout) | 延迟: 5.0s
  LLM: claude-sonnet-4 | 延迟: 3.2s | 成本: $0.015

Step 4 [10:30:13] [CRITICAL] 循环检测
  输入 Token: 9,200 | 上下文利用率: 85%
  决策: tool_call -> api_call (置信度: 0.58)
  [触发断路器]
```

#### 会话健康评分

```
健康分数 = 0.3 x 上下文利用率分 + 0.2 x 引用新鲜度分
         + 0.2 x 连贯性分 + 0.15 x 压缩质量分 + 0.15 x 决策置信度分

当前会话: 0.62 (警告)
  - 上下文利用率: 0.4 (危险，利用率 85%)
  - 引用新鲜度: 0.8 (正常)
  - 连贯性: 0.7 (警告)
  - 压缩质量: 0.6 (警告)
  - 决策置信度: 0.6 (警告)
```

---

## 6. 告警配置

### 6.1 Critical 告警（响应 < 5 分钟，电话 + 即时消息）

| 告警 ID | 名称 | 条件 | 响应 |
|---------|------|------|------|
| AGENT-CRIT-001 | 上下文溢出 | `agent.context.utilization > 0.95` 持续 1 分钟 | 紧急压缩或终止会话 |
| AGENT-CRIT-002 | 工具错误率飙升 | `agent.tools.error_rate > 0.3` 持续 2 分钟 | 检查工具服务、启用降级 |
| AGENT-CRIT-003 | 循环执行 | `agent.tools.redundant_rate > 0.5` 且 `call_count > 10` | 触发断路器、终止会话 |
| AGENT-CRIT-004 | 安全事件 | `agent.security.sensitive_data_exposed > 0` | 拦截输出、通知安全团队 |

### 6.2 Warning 告警（响应 < 30 分钟，即时消息）

| 告警 ID | 名称 | 条件 | 响应 |
|---------|------|------|------|
| AGENT-WARN-001 | 成本飙升 | `agent.cost.per_session > 1.0` | 检查循环、评估成本上限 |
| AGENT-WARN-002 | 延迟退化 | `agent.latency.p95 > 2x 基线` 持续 10 分钟 | 检查 LLM/工具延迟 |
| AGENT-WARN-003 | 上下文利用率高 | `agent.context.utilization > 0.8` 持续 5 分钟 | 触发压缩、监控增长 |
| AGENT-WARN-004 | Token 爆炸 | `agent.tokens.output > 50,000` | 检查输出长度限制 |
| AGENT-WARN-005 | 工具重试率高 | `agent.tools.retry_rate > 0.2` 持续 10 分钟 | 检查工具服务健康 |
| AGENT-WARN-006 | 任务漂移 | `agent.context.drift_score > 0.3` 持续 5 分钟 | 重新注入任务目标 |

### 6.3 Info 告警（响应 < 4 小时，邮件 + 仪表盘）

| 告警 ID | 名称 | 条件 | 响应 |
|---------|------|------|------|
| AGENT-INFO-001 | 缓存命中率低 | `agent.tokens.cache_hit_rate < 0.3` 持续 30 分钟 | 优化提示结构 |
| AGENT-INFO-002 | 注入尝试 | `agent.security.injection_attempts > 0` | 记录详情、验证防御 |

### 6.4 告警去重策略

- 同一会话的同类告警 5 分钟内去重
- 批量告警（如工具服务宕机）聚合为一条，附带受影响会话数
- 告警附带 `session_id` 和 `trace_id` 用于快速定位

---

## 7. MTTD 目标（Mean Time to Detect）

| 失败模式 | 目标 MTTD | 检测方式 |
|---------|----------|---------|
| 工具调用失败 | < 1 分钟 | 实时错误率告警 |
| 上下文退化 | < 5 分钟 | 上下文利用率趋势 |
| 循环执行 | < 2 分钟 | 连续调用检测 |
| 成本飙升 | < 5 分钟 | 成本阈值告警 |
| 幻觉输出 | < 1 小时 | 采样评估 + 人工审查 |

---

## 8. 上下文健康检测清单

### 8.1 窗口管理

- [ ] 窗口利用率 < 60% (正常) / 60-80% (警告) / > 80% (危险)
- [ ] Token 预算 > 20%（公式：remaining = window_size - used_tokens - output_reserve，output_reserve = 20% 窗口大小）
- [ ] 每步 Token 增长 < 500 tokens/步 (正常) / 500-1000 (警告) / > 1000 (危险)

### 8.2 压缩策略

- [ ] 利用率 > 70% 时考虑压缩
- [ ] 利用率 > 80% 时必须压缩
- [ ] 压缩后关键信息保留：任务目标、关键决策、工具调用结果

### 8.3 引用新鲜度

- [ ] 被引用上下文距今 < 10 步 (正常) / 10-20 步 (警告) / > 20 步 (标记过时)
- [ ] 检查 "Lost in the Middle" 效应

### 8.4 退化检测

```
function detect_degradation(session):
  scores = []
  for step in session.steps:
    score = compute_step_quality(step)
    scores.append(score)

  if last_3_scores_decreasing(scores):
    return "POSSIBLE_DEGRADATION"
  if scores[-1] < 0.5:
    return "QUALITY_DROP"
  if abs(scores[-1] - scores[-2]) > 0.3:
    return "SUDDEN_CHANGE"
  return "HEALTHY"
```

### 8.5 健康评分公式

```
health_score = 0.3 x context_utilization_score
             + 0.2 x reference_freshness_score
             + 0.2 x coherence_score
             + 0.15 x compression_quality_score
             + 0.15 x decision_confidence_score
```

| 健康分数 | 状态 | 响应 |
|---------|------|------|
| > 0.8 | 健康 | 正常运行 |
| 0.6 - 0.8 | 亚健康 | 增加监控频率 |
| 0.4 - 0.6 | 警告 | 触发压缩 + 重新注入任务目标 |
| < 0.4 | 危险 | 终止会话 + 通知用户 |

---

## 9. 循环检测算法

```
对最近 N 次工具调用:
  if 存在连续 3+ 次相同工具 + 相同参数:
    标记 "疑似循环"
    触发断路器

审计维度:
  - 调用频率: 每会话工具调用总数（告警 > 50 次/会话）
  - 错误率: 失败调用 / 总调用（告警 > 10%）
  - 参数验证失败率: Schema 验证失败 / 总调用（告警 > 5%）
  - 冗余调用率: 相同参数重复调用 / 总调用（告警 > 15%）
  - 延迟 P95: 95 分位延迟（告警 > 5 秒）
  - 工具成本占比: 工具调用成本 / 总成本（告警 > 60%）
```

---

## 10. 技术实现建议

### 10.1 数据采集层

- 在 Agent 执行的每个阶段插入埋点，按追踪 Schema 记录 JSON
- 使用 OpenTelemetry SDK 作为基础，扩展 Agent 专用的 Span 属性
- 每条 trace 记录包含 `session_id` 和 `trace_id` 用于关联

### 10.2 数据存储层

- **时序数据库**（如 Prometheus / InfluxDB）：存储性能、成本、上下文健康等指标
- **日志存储**（如 Elasticsearch / ClickHouse）：存储完整的追踪记录，支持 session_id 查询
- **告警引擎**（如 Alertmanager / Grafana Alerting）：基于指标触发告警

### 10.3 可视化层

- 使用 Grafana 构建仪表盘
- 全局概览页：Dashboard 变量支持按 Agent 筛选
- Agent 详情页：Template Dashboard，复制 5 份分别配置
- 单会话追踪：基于日志查询的自定义面板

### 10.4 采样策略

高频 Agent 场景下追踪数据量巨大，建议：
- **全量采集**：错误、告警、异常会话
- **采样采集**：正常会话按 10% 采样
- **聚合预计算**：指标按 1 分钟粒度预聚合

---

## 11. 实施路线图

| 阶段 | 内容 | 时间 |
|------|------|------|
| Phase 1 | 追踪 Schema 实现 + 基础指标采集 | 第 1-2 周 |
| Phase 2 | 全局概览仪表盘 + Critical 告警 | 第 3 周 |
| Phase 3 | Agent 详情页 + 上下文健康监控 | 第 4 周 |
| Phase 4 | 单会话追踪 + 工具审计 + 循环检测 | 第 5 周 |
| Phase 5 | 采样策略优化 + 告警调优 | 第 6 周 |
