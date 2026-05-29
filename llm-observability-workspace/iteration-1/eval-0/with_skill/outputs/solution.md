# 客服 Agent 长对话退化监控方案

## 问题诊断

客服 Agent 在 20+ 轮长对话中出现以下症状：

- **遗忘历史**：忘记用户之前提供的信息
- **重复提问**：询问用户已经回答过的问题
- **决策质量下降**：后期回复不如前期准确

根因分析指向 **上下文退化** —— 随着对话轮次增加，上下文窗口被填满，关键信息被淹没或压缩丢失。

---

## 1. Agent 生命周期追踪模型

客服 Agent 的执行流程分解为 6 个可观测阶段：

```
用户消息
  → [1] 提示构建（系统提示 + 对话历史 + 用户输入 + 工具描述）
  → [2] LLM 推理（调用模型生成回复或工具调用）
  → [3] 决策解析（判断是回复用户还是调用工具）
  → [4] 工具执行（查询订单、知识库、CRM 等）
  → [5] 结果整合（将工具结果整合进回复）
  → [6] 上下文管理（压缩旧消息、摘要长历史）
  → 循环 [2]-[5] 直到会话结束
```

每个阶段独立埋点，定位退化发生在哪个环节。

---

## 2. 决策追踪 Schema

每一步生成一条追踪记录：

```json
{
  "trace_id": "cs-session-20260529-abc123-step-15",
  "session_id": "cs-session-20260529-abc123",
  "step_number": 15,
  "timestamp": "2026-05-29T14:30:00Z",
  "input": {
    "context_tokens": 12800,
    "context_utilization": 0.64,
    "user_message": "我之前说的订单号是 12345，怎么还没查到？",
    "relevant_history_steps": [3, 7]
  },
  "llm_call": {
    "model": "claude-sonnet-4",
    "input_tokens": 12800,
    "output_tokens": 380,
    "latency_ms": 2100,
    "cost_usd": 0.019,
    "cached_tokens": 8200
  },
  "decision": {
    "type": "tool_call",
    "tool_name": "query_order",
    "tool_params": {"order_id": "12345"},
    "confidence": 0.85,
    "reasoning": "用户提到之前给过订单号，调用查询工具"
  },
  "tool_execution": {
    "latency_ms": 450,
    "success": true,
    "output_tokens": 200,
    "error": null
  },
  "output": {
    "type": "tool_result",
    "tokens": 200
  },
  "context_health": {
    "total_tokens_used": 32000,
    "window_utilization": 0.64,
    "compression_events": 1,
    "oldest_context_age_steps": 15
  },
  "metadata": {
    "agent_type": "customer_service",
    "customer_id": "cust-789",
    "topic": "order_inquiry"
  }
}
```

完整 JSON Schema：每条记录必须包含 `trace_id`, `session_id`, `step_number`, `timestamp`, `input`, `llm_call`, `decision`, `output` 字段。`context_health` 和 `tool_execution` 按需记录。

---

## 3. 上下文健康监控指标

这是解决"长对话退化"的核心监控层。

| 指标 | 定义 | 正常 | 警告 | 危险 | 检测方式 |
|------|------|------|------|------|---------|
| **上下文利用率** | 已用 Token / 窗口大小 | < 60% | 60-80% | > 80% | 每步计算 |
| **Token 预算** | 剩余可用 Token（扣除输出预留） | > 40% | 20-40% | < 20% | 每步计算 |
| **压缩事件频率** | 上下文压缩/摘要次数 | < 2 | 2-3 | > 3 | 计数器 |
| **引用新鲜度** | 被引用上下文的"年龄"（步数） | < 10 步 | 10-20 步 | > 20 步 | 追踪引用来源 |
| **连贯性分数** | 跨轮次回复一致性 | > 0.8 | 0.7-0.8 | < 0.7 | LLM-as-Judge 采样 |
| **任务漂移** | 当前目标与初始目标偏离度 | < 0.15 | 0.15-0.3 | > 0.3 | 语义相似度 |
| **重复提问率** | 重复询问已回答问题的比例 | 0% | > 5% | > 15% | NLI 检测 |

### 上下文退化检测逻辑

```python
def detect_context_degradation(session):
    """每步执行，检测上下文退化信号"""

    alerts = []

    # 1. 窗口利用率检查
    utilization = session.current_step.context_health.window_utilization
    if utilization > 0.8:
        alerts.append(Alert("CONTEXT_HIGH_UTILIZATION", severity="warning"))
        trigger_context_compression(session)
    if utilization > 0.95:
        alerts.append(Alert("CONTEXT_OVERFLOW", severity="critical"))

    # 2. 引用新鲜度检查
    oldest_ref = session.current_step.context_health.oldest_context_age_steps
    if oldest_ref > 20:
        alerts.append(Alert("STALE_REFERENCE", severity="warning",
                            detail="引用了 20+ 步前的上下文，信息可能已压缩丢失"))

    # 3. 决策置信度下降检测
    recent_confidences = [s.decision.confidence for s in session.recent_steps(3)]
    if all(c is not None for c in recent_confidences):
        if is_monotonically_decreasing(recent_confidences):
            alerts.append(Alert("CONFIDENCE_DECLINE", severity="warning",
                                detail="连续 3 步决策置信度下降，可能正在退化"))
            inject_task_reminder(session)

    # 4. 重复提问检测
    current_question = extract_question(session.current_step.output)
    previous_questions = extract_all_questions(session.all_previous_outputs())
    if is_semantically_similar(current_question, previous_questions, threshold=0.85):
        alerts.append(Alert("REPEATED_QUESTION", severity="critical",
                            detail="Agent 重复提问用户已回答的问题"))

    # 5. 任务漂移检测
    initial_goal = session.steps[0].metadata.get("initial_goal_embedding")
    current_goal = embed(session.current_step.decision.reasoning)
    drift = 1 - cosine_similarity(initial_goal, current_goal)
    if drift > 0.3:
        alerts.append(Alert("TASK_DRIFT", severity="warning",
                            detail=f"任务漂移分数 {drift:.2f}，偏离初始目标"))

    return alerts
```

### 健康评分公式

```
health_score = (
    0.30 * context_utilization_score +    # < 80% = 1.0, > 95% = 0.0
    0.20 * reference_freshness_score +     # < 10步 = 1.0, > 30步 = 0.0
    0.20 * coherence_score +               # LLM-as-Judge 评分
    0.15 * no_repeated_question_score +    # 无重复提问 = 1.0
    0.15 * decision_confidence_score       # 决策置信度均值
)
```

| 健康分数 | 状态 | 自动响应 |
|---------|------|---------|
| > 0.8 | 健康 | 正常运行 |
| 0.6 - 0.8 | 亚健康 | 增加监控频率，记录趋势 |
| 0.4 - 0.6 | 警告 | 触发上下文压缩 + 重新注入任务目标 + 通知值班 |
| < 0.4 | 危险 | 建议终止会话 + 转人工 + 告警 |

---

## 4. 工具调用审计

客服 Agent 典型工具：查询订单、查询物流、查知识库、创建工单、转人工。每个工具调用独立审计。

| 审计维度 | 指标 | 告警阈值 |
|---------|------|---------|
| 调用频率 | 每会话工具调用总数 | > 50 次 |
| 错误率 | 失败调用 / 总调用 | > 10% |
| 参数验证失败率 | Schema 验证失败 / 总调用 | > 5% |
| 冗余调用率 | 相同参数重复调用 / 总调用 | > 15% |
| 延迟 P95 | 工具调用 95 分位延迟 | > 5 秒 |

### 循环检测

```python
def detect_tool_loop(recent_tool_calls, window=5):
    """检测 Agent 是否陷入工具调用循环"""
    if len(recent_tool_calls) < 3:
        return False

    last_n = recent_tool_calls[-window:]

    # 检测连续 3+ 次相同工具 + 相同参数
    for i in range(len(last_n) - 2):
        if (last_n[i].tool_name == last_n[i+1].tool_name == last_n[i+2].tool_name
            and last_n[i].tool_params == last_n[i+1].tool_params == last_n[i+2].tool_params):
            return True

    # 检测 A-B-A-B 振荡模式
    if len(last_n) >= 4:
        if (last_n[-1].tool_name == last_n[-3].tool_name
            and last_n[-2].tool_name == last_n[-4].tool_name):
            return True

    return False
```

循环检测触发后：立即执行断路器，停止工具调用，将问题摘要发给用户确认。

---

## 5. 告警配置

### Critical 告警（< 5 分钟响应）

```yaml
# AGENT-CRIT-001: 上下文溢出
alert: ContextWindowOverflow
condition: agent.context.utilization > 0.95
for: 1m
severity: critical
runbook:
  - 立即触发紧急上下文压缩
  - 如果持续溢出，终止会话并通知用户
  - 检查是否有异常的长对话

# AGENT-CRIT-002: 重复提问
alert: RepeatedQuestionDetected
condition: agent.coherence.repeated_question_rate > 0.15
for: 0s
severity: critical
runbook:
  - 检查上下文压缩是否丢失了关键信息
  - 注入已收集信息的摘要
  - 如果持续重复，转人工

# AGENT-CRIT-003: 循环执行
alert: AgentLoopDetected
condition: agent.tools.redundant_rate > 0.5 and agent.tools.call_count > 10
for: 1m
severity: critical
runbook:
  - 触发断路器，停止工具调用
  - 终止当前会话
  - 分析循环原因
```

### Warning 告警（< 30 分钟响应）

```yaml
# AGENT-WARN-001: 上下文利用率高
alert: ContextUtilizationHigh
condition: agent.context.utilization > 0.8
for: 5m
severity: warning
runbook:
  - 触发上下文压缩
  - 评估是否需要分段对话
  - 监控是否继续增长

# AGENT-WARN-002: 引用过时
alert: StaleContextReference
condition: agent.context.oldest_context_age_steps > 20
for: 5m
severity: warning
runbook:
  - 检查被引用的上下文是否已被压缩
  - 评估是否需要重新注入关键信息

# AGENT-WARN-003: 决策置信度下降
alert: ConfidenceDecline
condition: agent.decision.confidence declining over 3 consecutive steps
for: 0s
severity: warning
runbook:
  - 检查上下文健康状态
  - 重新注入任务目标
  - 记录退化样本用于离线分析

# AGENT-WARN-004: 任务漂移
alert: TaskDriftDetected
condition: agent.context.drift_score > 0.3
for: 5m
severity: warning
runbook:
  - 检查对话是否偏移话题
  - 重新注入初始任务目标
  - 如果是用户主动切换话题，降级为 Info

# AGENT-WARN-005: 成本飙升
alert: AgentCostSpike
condition: agent.cost.per_session > 1.0
for: 5m
severity: warning
runbook:
  - 检查是否有循环调用
  - 检查上下文大小是否异常增长
```

### 告警去重与聚合

- 同一会话的同类告警 5 分钟内去重
- 批量告警（如模型服务宕机导致大量会话报错）聚合为一条
- 每条告警附带 `session_id` 和 `trace_id`，支持快速定位

---

## 6. 仪表盘设计

### 第一行：概览指标卡片

| 卡片 | 指标 | 趋势 |
|------|------|------|
| 活跃会话数 | 当前正在运行的客服会话数 | 与昨日同期对比 |
| 任务完成率 | 成功解决用户问题的会话占比 | 过去 24 小时趋势 |
| 平均每会话成本 | 单个客服会话的总成本 | 过去 7 天趋势 |
| 平均响应延迟 | 从用户消息到 Agent 回复的时间 | P50/P95/P99 |

### 第二行：退化趋势图

- **上下文利用率分布**：直方图，X 轴为利用率区间（0-20%, 20-40%, ..., 80-100%），Y 轴为会话数。高亮 80% 以上的会话。
- **重复提问率趋势**：按小时统计，X 轴为时间，Y 轴为重复提问率。超过 5% 时标红。
- **决策置信度趋势**：按会话步骤数统计，观察是否随步骤增加而下降。

### 第三行：工具审计表

| 工具名 | 调用次数 | 成功率 | P95 延迟 | 冗余调用率 | 成本 |
|--------|---------|--------|---------|-----------|------|
| query_order | 1,234 | 98.5% | 320ms | 2.1% | $12.34 |
| query_knowledge | 890 | 95.2% | 1,200ms | 8.5% | $8.90 |
| create_ticket | 156 | 99.0% | 450ms | 0.5% | $1.56 |

### 第四行：异常事件列表

| 时间 | 会话 ID | 事件类型 | 严重程度 | 详情 |
|------|---------|---------|---------|------|
| 14:30 | cs-abc123 | REPEATED_QUESTION | Critical | 第 18 步重复询问用户手机号 |
| 14:25 | cs-def456 | CONTEXT_OVERFLOW | Critical | 上下文利用率达 97% |
| 14:20 | cs-ghi789 | TASK_DRIFT | Warning | 从退换货话题漂移到产品咨询 |

### 第五行：单会话追踪

选择特定 `session_id`，展示完整决策链路：

```
Step 1  [用户] "我要退货，订单号 12345"           ctx: 12%  conf: 0.95
Step 2  [工具] query_order(12345) → 成功           ctx: 18%  conf: 0.93
Step 3  [回复] "查到您的订单，是 3 天前购买的..."   ctx: 22%  conf: 0.91
...
Step 15 [工具] query_order(12345) → 成功           ctx: 64%  conf: 0.85  ⚠️ 冗余调用
Step 16 [回复] "请问您的订单号是多少？"             ctx: 66%  conf: 0.72  🔴 重复提问
```

高亮异常步骤（红色 = Critical，黄色 = Warning）。

---

## 7. 采样策略

生产环境中追踪数据量巨大，需要分层采样：

| 数据类型 | 采样率 | 理由 |
|---------|--------|------|
| 正常会话（健康分数 > 0.8） | 10% | 低价值，保留统计即可 |
| 警告会话（健康分数 0.6-0.8） | 50% | 需要足够样本分析退化模式 |
| 异常会话（健康分数 < 0.6） | 100% | 每条都要记录，用于根因分析 |
| 包含告警的步骤 | 100% | 告警必须完整保留 |
| 工具调用失败 | 100% | 失败样本全量保留 |

---

## 8. 针对"重复提问"的专项检测

这是用户反馈的核心痛点，需要专门的检测逻辑：

```python
def detect_repeated_questions(session):
    """检测 Agent 是否重复询问用户已回答的问题"""

    # 1. 提取所有用户回答过的信息
    collected_info = {}
    for step in session.steps:
        if step.decision.type == "text_response":
            # 提取 Agent 问了什么
            question = extract_question(step.output.text)
            if question:
                # 检查后续步骤中用户是否已回答
                answer_step = find_user_answer_after(session, step.step_number)
                if answer_step:
                    collected_info[question] = {
                        "answer": answer_step.input.user_message,
                        "step": step.step_number
                    }

    # 2. 检测当前回复是否重复提问
    current_output = session.current_step.output.text
    current_question = extract_question(current_output)

    if current_question:
        for prev_question, info in collected_info.items():
            similarity = semantic_similarity(current_question, prev_question)
            if similarity > 0.85:
                return RepeatedQuestionAlert(
                    current_step=session.current_step.step_number,
                    original_step=info["step"],
                    question=prev_question,
                    answer=info["answer"],
                    severity="critical"
                )

    return None


def inject_prevention_prompt(session):
    """在上下文中注入已收集信息的摘要，防止重复提问"""
    summary = "## 已从用户处收集的信息\n"
    for key, value in session.collected_info.items():
        summary += f"- {key}: {value}\n"
    summary += "\n请勿再次询问以上已收集的信息。\n"

    # 插入到系统提示或最近的上下文中
    session.inject_context(summary, position="system_append")
```

---

## 9. 防御性措施（预防退化）

监控发现问题后，需要自动化的防御措施：

### 9.1 智能上下文压缩

```python
def smart_context_compression(session):
    """保留关键信息，压缩低价值内容"""

    # 优先保留的内容（不压缩）
    preserve = []
    for msg in session.messages:
        # 保留系统提示
        if msg.role == "system":
            preserve.append(msg)
        # 保留用户的关键回答（包含事实信息）
        elif msg.role == "user" and contains_factual_info(msg.content):
            preserve.append(msg)
        # 保留工具调用的结果
        elif msg.role == "tool":
            preserve.append(msg)

    # 可压缩的内容
    compressible = [m for m in session.messages if m not in preserve]

    # 层次摘要：旧消息用摘要替代
    if len(compressible) > 10:
        summary = llm_summarize(compressible[:len(compressible)//2])
        session.replace_messages(compressible[:len(compressible)//2], summary)

    return session
```

### 9.2 任务目标定期重注入

每隔 N 步自动重注入任务目标和已收集信息：

```python
def maybe_reinject_context(session, interval=10):
    """每 interval 步重新注入关键上下文"""
    if session.step_number % interval == 0 and session.step_number > 0:
        reminder = f"""
## 当前任务状态
- 用户问题：{session.initial_query}
- 已收集信息：{session.collected_info_summary}
- 已完成步骤：{session.completed_actions}
- 待处理事项：{session.pending_actions}

请基于以上信息继续处理，不要重复已完成的步骤。
"""
        session.inject_context(reminder, position="before_last_user_message")
```

### 9.3 断路器机制

```python
class AgentCircuitBreaker:
    def __init__(self):
        self.failure_count = 0
        self.redundant_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def check(self, step):
        # 检测工具调用循环
        if self._is_tool_loop(step):
            self.redundant_count += 1
            if self.redundant_count >= 3:
                self.state = "OPEN"
                raise CircuitBreakerOpen("检测到工具调用循环，断路器已打开")

        # 检测连续失败
        if step.tool_execution and not step.tool_execution.success:
            self.failure_count += 1
            if self.failure_count >= 5:
                self.state = "OPEN"
                raise CircuitBreakerOpen("连续工具调用失败过多")

        # 重置计数
        if step.tool_execution and step.tool_execution.success:
            self.failure_count = max(0, self.failure_count - 1)
            self.redundant_count = 0

    def _is_tool_loop(self, step):
        # 检测与最近步骤相同的工具调用
        recent = session.recent_tool_calls(3)
        return all(r.tool_name == step.decision.tool_name
                   and r.tool_params == step.decision.tool_params
                   for r in recent)
```

---

## 10. MTTD 目标（平均检测时间）

| 失败模式 | 目标 MTTD | 检测方式 |
|---------|----------|---------|
| 重复提问 | < 2 分钟 | NLI 语义相似度实时检测 |
| 上下文退化 | < 5 分钟 | 上下文利用率趋势 + 引用新鲜度 |
| 循环执行 | < 1 分钟 | 连续调用检测 + 断路器 |
| 任务漂移 | < 5 分钟 | 语义相似度监控 |
| 工具调用失败 | < 1 分钟 | 实时错误率告警 |
| 成本飙升 | < 5 分钟 | 成本阈值告警 |
| 幻觉输出 | < 1 小时 | 采样 LLM-as-Judge 评估 |

---

## 11. 实施路线图

### Phase 1: 基础追踪（1-2 周）

- 实现决策追踪 Schema 的数据采集
- 在每个 Agent 执行步骤记录 `trace_id`, `session_id`, `step_number`, `input`, `llm_call`, `decision`, `output`
- 接入日志存储（ELK / ClickHouse / 专用 tracing 后端）
- 建立基础仪表盘：活跃会话数、响应延迟、成本

### Phase 2: 上下文健康监控（2-3 周）

- 实现上下文利用率、引用新鲜度的实时计算
- 部署上下文退化检测算法
- 配置 AGENT-WARN-001（上下文利用率高）和 AGENT-WARN-002（引用过时）告警
- 建立上下文利用率分布直方图

### Phase 3: 重复提问检测（2-3 周）

- 实现 NLI-based 重复提问检测
- 部署已收集信息摘要注入机制
- 配置 AGENT-CRIT-002（重复提问）告警
- 建立重复提问率趋势图

### Phase 4: 防御性措施（3-4 周）

- 实现智能上下文压缩
- 部署任务目标定期重注入
- 实现工具调用断路器
- 配置 AGENT-CRIT-003（循环执行）告警

### Phase 5: 持续优化（持续）

- 基于告警数据调优阈值
- 分析退化模式，优化上下文压缩策略
- 定期审查 LLM-as-Judge 评估准确性
- 采样率动态调整

---

## 12. 技术栈建议

| 层 | 推荐 | 备选 |
|----|------|------|
| 追踪数据采集 | OpenTelemetry + 自定义 Span | LangSmith / Langfuse |
| 日志存储 | ClickHouse（高写入、列式查询） | Elasticsearch |
| 实时计算 | Flink / Kafka Streams | 自定义 Python 服务 |
| 仪表盘 | Grafana | Metabase / Superset |
| 告警 | Grafana Alerting / PagerDuty | Opsgenie |
| NLI 检测 | sentence-transformers + FAISS | OpenAI Embeddings |
| LLM-as-Judge | Claude Sonnet（采样评估） | GPT-4o-mini |

---

## 13. 关键指标看板速查

运营团队每天关注的核心指标：

| 指标 | 健康值 | 行动阈值 |
|------|--------|---------|
| 重复提问率 | 0% | > 5% 立即排查 |
| 上下文利用率 P95 | < 60% | > 80% 触发压缩优化 |
| 任务完成率 | > 90% | < 80% 启动专项优化 |
| 每会话成本 | < $0.10 | > $0.50 检查循环 |
| 长会话（20+ 轮）占比 | < 20% | > 40% 评估对话分流策略 |
| 健康分数均值 | > 0.8 | < 0.6 通知研发 |
