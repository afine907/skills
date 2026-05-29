# Agent 可观测性系统设计方案

## 背景与问题陈述

**事故回顾：** 一个 Agent 工具调用进入无限循环，连续运行 11 天，累计消耗约 $40,000 后才被人工发现。

**根因分析：** 缺乏以下关键能力：
1. 无循环检测机制 — 相同工具以相同参数被反复调用，无人察觉
2. 无成本异常告警 — 单会话成本从正常的几美元飙升至数万美元，无任何阈值触发
3. 无会话时长限制 — Agent 会话可以无限期运行
4. 无工具调用审计 — 工具调用的频率、模式、成本未被追踪

**设计目标：** 确保任何类似的循环执行问题在 **5 分钟内** 被检测到，并自动触发断路器终止异常会话。

---

## 一、Agent 生命周期埋点模型

将 Agent 执行分解为 6 个可观测阶段，每个阶段独立埋点：

```
用户输入
  [1] 提示构建（组装系统提示 + 历史 + 用户输入）
  [2] LLM 推理（发送到模型、获取响应）
  [3] 决策解析（提取工具调用或最终回答）
  [4] 工具执行（调用工具、获取结果）
  [5] 结果整合（将工具结果反馈给 LLM 或返回用户）
  [6] 上下文管理（压缩、摘要、清理）
  循环 [2]-[5] 直到完成
```

每个阶段的失败模式不同，需要独立监控：

| 阶段 | 失败模式 | 本次事故关联 |
|------|---------|------------|
| 阶段 4: 工具执行 | 工具调用失败、无限循环 | **直接根因** — 工具循环调用 |
| 阶段 3: 决策解析 | 无法从循环中退出 | Agent 未识别到循环状态 |
| 阶段 5: 结果整合 | 结果未被正确消费 | 循环产生的结果未触发终止条件 |

---

## 二、决策追踪 Schema

每一步 Agent 执行生成一条结构化追踪记录，遵循以下 JSON Schema：

```json
{
  "trace_id": "uuid-v4",
  "session_id": "sess_abc123",
  "step_number": 1,
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
    "cached_tokens": 1200
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
    "error": null,
    "error_type": null,
    "retry_count": 0
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
  },
  "metadata": {
    "cost_cumulative_usd": 0.0825,
    "session_duration_seconds": 120,
    "loop_score": 0.0
  }
}
```

**针对本次事故的关键字段：**
- `decision.tool_name` + `decision.tool_params` — 用于循环检测的核心输入
- `metadata.cost_cumulative_usd` — 累计成本，用于成本飙升告警
- `metadata.loop_score` — 循环得分，由循环检测器实时计算
- `step_number` — 会话内步骤计数，用于会话时长控制

---

## 三、循环检测系统（核心防护）

### 3.1 多层循环检测算法

本次事故的直接原因是工具调用进入无限循环。需要实现三层检测：

**第一层：精确匹配检测（MTTD < 1 分钟）**

```
对最近 N 次工具调用（N=5）:
  if 存在连续 3+ 次调用具有:
    - 相同 tool_name
    - 相同 tool_params（JSON 深度比较）
  then:
    标记 "CONFIRMED_LOOP"
    立即触发断路器
    发送 Critical 告警
```

**第二层：语义相似度检测（MTTD < 2 分钟）**

```
对最近 N 次工具调用（N=10）:
  if 存在 5+ 次调用具有:
    - 相同 tool_name
    - tool_params 的语义相似度 > 0.85
  then:
    标记 "SEMANTIC_LOOP"
    触发断路器
    发送 Critical 告警
```

**第三层：行为模式检测（MTTD < 3 分钟）**

```
对整个会话:
  if 工具调用次数 > 50 且:
    - 冗余调用率 > 50%
    - 或 会话持续时间 > 30 分钟 且 无 text_response 输出
  then:
    标记 "BEHAVIORAL_LOOP"
    触发断路器
    发送 Critical 告警
```

### 3.2 断路器机制

```python
class AgentCircuitBreaker:
    """
    Agent 工具调用断路器。
    当检测到循环模式时，自动终止工具调用链。
    """

    # 断路器状态
    CLOSED = "closed"       # 正常运行
    OPEN = "open"           # 已触发，阻止所有工具调用
    HALF_OPEN = "half_open" # 允许一次试探性调用

    def __init__(self):
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.recovery_timeout_seconds = 300  # 5 分钟后尝试恢复

    def check_before_tool_call(self, session_id: str, tool_name: str, tool_params: dict) -> bool:
        """
        在每次工具调用前检查断路器状态。
        返回 True 允许调用，返回 False 阻止调用。
        """
        if self.state == self.OPEN:
            if self._should_attempt_recovery():
                self.state = self.HALF_OPEN
                return True  # 允许一次试探
            return False  # 阻止调用
        return True

    def record_loop_detected(self, session_id: str, loop_type: str, evidence: dict):
        """记录循环检测事件，触发断路器。"""
        self.state = self.OPEN
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        # 发送告警
        alert_service.send(
            level="CRITICAL",
            code="AGENT-CRIT-003",
            title="Agent Loop Detected",
            session_id=session_id,
            details={
                "loop_type": loop_type,
                "evidence": evidence,
                "action": "CIRCUIT_BREAKER_TRIGGERED"
            }
        )

        # 终止会话
        session_manager.terminate(session_id, reason=f"Loop detected: {loop_type}")
```

### 3.3 实现要点

```
循环检测器部署位置：Agent 执行引擎的核心循环内
                ┌──────────────────────────────────────┐
                │          Agent 执行引擎               │
                │                                      │
用户输入 ──→  │  [提示构建] → [LLM推理] → [决策解析]  │
                │       ↑                  │           │
                │       │            ┌─────▼─────┐    │
                │       │            │ 工具执行   │    │
                │       │            └─────┬─────┘    │
                │       │                  │           │
                │       │          ┌───────▼────────┐ │
                │       │          │  循环检测器     │ │ ← 在此处拦截
                │       │          │  (实时分析)     │ │
                │       │          └───────┬────────┘ │
                │       │                  │           │
                │       └── [结果整合] ←───┘           │
                └──────────────────────────────────────┘
```

**关键设计决策：**
- 循环检测器必须在工具执行**之前**运行，而非之后
- 检测基于滑动窗口，窗口大小为最近 10 次工具调用
- 参数比较使用 JSON canonical 化后精确匹配 + 语义相似度双轨制

---

## 四、成本追踪与告警

### 4.1 成本指标体系

| 指标 | 定义 | 告警阈值 | 说明 |
|------|------|---------|------|
| `agent.cost.per_session` | 单会话累计成本 | **$1.00 Warning, $5.00 Critical** | 本次事故：$40,000 未被检测 |
| `agent.cost.per_hour` | 小时级成本速率 | **$10.00/hour Warning** | 捕捉短时间内的爆发性消耗 |
| `agent.cost.per_step` | 单步成本 | **$0.10 Warning** | 异常大的单次调用 |
| `agent.cost.total_5m` | 5 分钟滚动窗口总成本 | **$50.00 Critical** | 跨会话的全局成本失控 |

### 4.2 成本告警规则

```yaml
# 核心防护告警 — 针对本次事故场景

alert: SessionCostCritical
code: AGENT-CRIT-005
condition: agent.cost.per_session > 5.0
for: 0s          # 立即触发，不等待
severity: critical
description: "单会话成本超过 $5.00，可能存在循环或异常"
runbook: |
  1. 立即检查该会话的工具调用模式
  2. 查看是否有循环检测告警同时触发
  3. 如果确认异常，终止会话
  4. 如果是正常的长对话任务，评估是否需要成本上限
notification:
  - pagerduty: immediate
  - slack: #agent-alerts
  - email: oncall@company.com

---

alert: CostRateSpike
code: AGENT-CRIT-006
condition: agent.cost.per_hour > 10.0
for: 2m
severity: critical
description: "小时级成本速率超过 $10.00/hour"
runbook: |
  1. 检查是否有多个会话同时出现高成本
  2. 排查是否是上游变更导致 token 消耗增加
  3. 评估是否需要全局限流

---

alert: GlobalCostSurge
code: AGENT-CRIT-007
condition: sum(agent.cost.total_5m) > 50.0
for: 0s
severity: critical
description: "5 分钟内全局 Agent 成本超过 $50.00"
runbook: |
  1. 立即检查所有活跃会话
  2. 识别成本最高的会话并优先排查
  3. 如果无法快速定位，触发全局暂停
```

### 4.3 成本上限机制（硬防护）

```python
class CostGuard:
    """
    成本硬上限。当会话累计成本超过阈值时，强制终止。
    这是最后一道防线，即使循环检测器失效也能阻止灾难性消耗。
    """

    LIMITS = {
        "per_session": 10.0,       # 单会话 $10 上限
        "per_session_warning": 1.0, # $1 时发出警告
        "global_per_hour": 100.0,   # 全局每小时 $100 上限
    }

    def check_cost_before_step(self, session_id: str, cumulative_cost: float) -> bool:
        """在每步执行前检查成本。返回 True 允许继续。"""
        if cumulative_cost >= self.LIMITS["per_session"]:
            session_manager.terminate(
                session_id,
                reason=f"Cost limit reached: ${cumulative_cost:.2f} >= ${self.LIMITS['per_session']}"
            )
            alert_service.send(
                level="CRITICAL",
                code="AGENT-CRIT-008",
                title="Session Cost Limit Exceeded",
                session_id=session_id,
                details={"cumulative_cost": cumulative_cost}
            )
            return False

        if cumulative_cost >= self.LIMITS["per_session_warning"]:
            alert_service.send(
                level="WARNING",
                code="AGENT-WARN-001",
                title="Session Cost Approaching Limit",
                session_id=session_id,
                details={"cumulative_cost": cumulative_cost}
            )

        return True
```

---

## 五、会话生命周期管理

### 5.1 会话时长与步骤限制

```python
class SessionLifecycleManager:
    """
    会话生命周期管理器。
    防止会话无限期运行。
    """

    LIMITS = {
        "max_duration_seconds": 3600,    # 最大 1 小时
        "max_steps": 200,                # 最大 200 步
        "max_tool_calls": 100,           # 最大 100 次工具调用
        "max_idle_seconds": 600,         # 无进展 10 分钟自动终止
        "warning_duration_seconds": 1800, # 30 分钟时警告
        "warning_steps": 100,            # 100 步时警告
    }

    def check_session_health(self, session: Session) -> SessionAction:
        """每步执行前检查会话健康状态。"""

        # 检查时长
        duration = (datetime.utcnow() - session.start_time).total_seconds()
        if duration >= self.LIMITS["max_duration_seconds"]:
            return SessionAction.TERMINATE("Max duration exceeded")

        if duration >= self.LIMITS["warning_duration_seconds"]:
            alert_service.send(level="WARNING", code="AGENT-WARN-010",
                             title="Session duration approaching limit")

        # 检查步骤数
        if session.step_count >= self.LIMITS["max_steps"]:
            return SessionAction.TERMINATE("Max steps exceeded")

        if session.step_count >= self.LIMITS["warning_steps"]:
            alert_service.send(level="WARNING", code="AGENT-WARN-011",
                             title="Session step count approaching limit")

        # 检查工具调用数
        if session.tool_call_count >= self.LIMITS["max_tool_calls"]:
            return SessionAction.TERMINATE("Max tool calls exceeded")

        # 检查空闲时间
        idle_time = (datetime.utcnow() - session.last_meaningful_progress).total_seconds()
        if idle_time >= self.LIMITS["max_idle_seconds"]:
            return SessionAction.TERMINATE("Session idle too long")

        return SessionAction.CONTINUE()
```

### 5.2 会话限制阈值

| 限制项 | 软限制（警告） | 硬限制（强制终止） | 说明 |
|--------|--------------|------------------|------|
| 会话时长 | 30 分钟 | 1 小时 | 防止无限期运行 |
| 步骤数 | 100 步 | 200 步 | 防止无限循环 |
| 工具调用数 | 50 次 | 100 次 | 直接防护本次事故 |
| 空闲时间 | 5 分钟无进展警告 | 10 分钟无进展终止 | 防止卡死 |
| 单会话成本 | $1.00 | $10.00 | 成本硬上限 |

---

## 六、上下文健康监控

### 6.1 监控指标

| 指标 | 定义 | 警告阈值 | 危险阈值 |
|------|------|---------|---------|
| 上下文利用率 | 已用 Token / 窗口大小 | > 80% | > 95% |
| Token 预算 | 剩余可用 Token 估算 | < 20% | < 5% |
| 压缩事件频率 | 上下文压缩/摘要次数 | > 3 次/会话 | > 5 次/会话 |
| 引用新鲜度 | 被引用上下文的平均"年龄" | > 20 步 | > 30 步 |
| 任务漂移 | 当前目标与初始目标偏离度 | > 0.3 | > 0.5 |

### 6.2 上下文退化检测

```python
def detect_context_degradation(session: Session) -> DegradationReport:
    """检测上下文退化。每步执行后运行。"""

    report = DegradationReport()

    # 1. 利用率检查
    if session.context_utilization > 0.8:
        report.add_warning("Context utilization high", severity="warning")
        trigger_context_compression(session)

    # 2. 引用新鲜度检查
    if session.oldest_referenced_context_age > 20:
        report.add_warning("Referenced context may be stale", severity="warning")

    # 3. 决策置信度趋势
    recent_confidences = session.get_recent_confidence_scores(n=3)
    if len(recent_confidences) >= 3 and all(
        recent_confidences[i] > recent_confidences[i+1]
        for i in range(len(recent_confidences)-1)
    ):
        report.add_warning("Decision confidence declining — possible degradation",
                          severity="warning")
        report.recommend("Re-inject task objective into context")

    # 4. 健康评分
    health_score = compute_health_score(session)
    if health_score < 0.4:
        report.add_warning("Session health critical", severity="critical")
        report.recommend("Terminate session")

    return report


def compute_health_score(session: Session) -> float:
    """
    综合健康评分。
    权重：上下文利用率 30%、引用新鲜度 20%、连贯性 20%、压缩质量 15%、决策置信度 15%
    """
    return (
        0.30 * utilization_score(session.context_utilization) +
        0.20 * freshness_score(session.oldest_referenced_context_age) +
        0.20 * coherence_score(session) +
        0.15 * compression_quality_score(session) +
        0.15 * confidence_score(session.avg_decision_confidence)
    )
```

---

## 七、工具调用审计

### 7.1 审计维度

| 维度 | 指标 | 告警阈值 | 与本次事故的关系 |
|------|------|---------|----------------|
| 调用频率 | 每会话工具调用总次数 | > 50 次/会话 | 事故会话调用了数万次 |
| 错误率 | 失败调用 / 总调用 | > 10% | 需排查循环中的错误模式 |
| 参数验证失败率 | Schema 验证失败 / 总调用 | > 5% | — |
| 冗余调用率 | 相同参数重复调用 / 总调用 | > 15% | **事故核心指标** — 循环 = 100% 冗余 |
| 延迟 P95 | 95 分位延迟 | > 5 秒 | — |
| 工具成本占比 | 工具调用成本 / 总成本 | > 60% | 需排查工具调用是否异常消耗 |

### 7.2 工具调用指纹

```python
def compute_tool_fingerprint(tool_name: str, tool_params: dict) -> str:
    """
    计算工具调用的唯一指纹。
    用于快速检测重复调用。
    """
    canonical_params = json.dumps(tool_params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(f"{tool_name}:{canonical_params}".encode()).hexdigest()[:16]


class ToolCallAuditor:
    """工具调用审计器。"""

    def __init__(self):
        self.recent_fingerprints: dict[str, list[str]] = {}  # session_id -> [fingerprints]

    def audit_tool_call(self, session_id: str, tool_name: str, tool_params: dict) -> AuditResult:
        """审计一次工具调用，返回审计结果。"""
        fingerprint = compute_tool_fingerprint(tool_name, tool_params)

        if session_id not in self.recent_fingerprints:
            self.recent_fingerprints[session_id] = []

        history = self.recent_fingerprints[session_id]
        history.append(fingerprint)

        # 保持滑动窗口大小
        if len(history) > 20:
            history.pop(0)

        # 检查连续重复
        if len(history) >= 3 and len(set(history[-3:])) == 1:
            return AuditResult(
                status="LOOP_DETECTED",
                evidence={
                    "consecutive_duplicates": 3,
                    "tool_name": tool_name,
                    "tool_params": tool_params,
                    "fingerprint": fingerprint
                }
            )

        # 检查高频重复（滑动窗口内）
        if len(history) >= 10:
            from collections import Counter
            counts = Counter(history)
            most_common_fp, most_common_count = counts.most_common(1)[0]
            if most_common_count / len(history) > 0.5:
                return AuditResult(
                    status="HIGH_REDUNDANCY",
                    evidence={
                        "redundancy_rate": most_common_count / len(history),
                        "tool_name": tool_name
                    }
                )

        return AuditResult(status="OK")
```

---

## 八、告警规则总表

### Critical 告警（需 5 分钟内响应）

| 告警代码 | 名称 | 条件 | 响应动作 |
|---------|------|------|---------|
| AGENT-CRIT-001 | 上下文溢出 | context_utilization > 95% | 立即压缩或终止 |
| AGENT-CRIT-002 | 工具错误率飙升 | error_rate > 30% (5分钟窗口) | 检查工具健康状态 |
| **AGENT-CRIT-003** | **循环执行检测** | **连续 3+ 次相同工具+参数** | **触发断路器，终止会话** |
| AGENT-CRIT-004 | 安全事件 | 敏感数据泄露检测 | 拦截输出，通知安全团队 |
| **AGENT-CRIT-005** | **会话成本超限** | **单会话成本 > $5.00** | **终止会话，通知 oncall** |
| **AGENT-CRIT-006** | **成本速率飙升** | **小时成本 > $10.00/hour** | **排查循环，评估限流** |
| **AGENT-CRIT-007** | **全局成本失控** | **5 分钟全局成本 > $50.00** | **全局暂停，紧急排查** |
| **AGENT-CRIT-008** | **会话成本硬上限** | **单会话成本 >= $10.00** | **强制终止** |

### Warning 告警（需 30 分钟内响应）

| 告警代码 | 名称 | 条件 | 响应动作 |
|---------|------|------|---------|
| AGENT-WARN-001 | 成本预警 | 单会话成本 > $1.00 | 检查会话详情 |
| AGENT-WARN-002 | 延迟退化 | P95 延迟 > 2 倍基线 | 检查模型/工具性能 |
| AGENT-WARN-003 | 上下文利用率高 | utilization > 80% | 触发压缩 |
| AGENT-WARN-004 | Token 爆炸 | 单次输出 > 50K tokens | 检查提示 |
| AGENT-WARN-005 | 工具重试率高 | retry_rate > 20% | 检查工具健康 |
| AGENT-WARN-006 | 任务漂移 | drift_score > 0.3 | 重新注入目标 |
| AGENT-WARN-010 | 会话时长预警 | duration > 30 分钟 | 检查会话状态 |
| AGENT-WARN-011 | 步骤数预警 | steps > 100 | 检查是否有循环 |

### Info 告警（4 小时内处理）

| 告警代码 | 名称 | 条件 |
|---------|------|------|
| AGENT-INFO-001 | 缓存命中率低 | cache_hit_rate < 30% |
| AGENT-INFO-002 | 注入尝试 | injection_attempts > 0 |

---

## 九、监控仪表盘设计

### 第一行：概览指标卡片

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│  活跃会话数      │  任务完成率      │  平均会话成本    │  P95 延迟       │
│     12          │    94.2%        │    $0.08        │    2.3s         │
│  ▲ +3 vs 1h ago │  ▼ -1.2%       │  ─ stable       │  ▲ +0.3s       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### 第二行：关键趋势图

```
┌──────────────────────────────────────┬──────────────────────────────────────┐
│  工具调用成功率趋势（按小时）          │  会话成本分布（直方图）               │
│                                      │                                      │
│  100%|    ╭──╮                       │  $0-1:    ████████████████ 85%       │
│   95%| ╭──╯  ╰──╮                   │  $1-5:    ████ 12%                   │
│   90%|─╯        ╰──                  │  $5-10:   █ 2%                      │
│      └──────────────                 │  $10+:    ▏ 1%  ← 告警区域          │
│      00  04  08  12  16  20  24      │                                      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

### 第三行：详情表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  工具调用详情                                                               │
│  工具名        │ 调用次数 │ 成功率  │ P95延迟 │ 成本    │ 冗余率  │ 状态    │
│  search_docs   │  1,234   │ 98.2%  │ 340ms  │ $12.50 │ 2.1%   │ 正常    │
│  code_exec     │    567   │ 91.3%  │ 1.2s   │ $45.20 │ 8.3%   │ 关注    │
│  web_fetch     │  8,901   │ 45.2%  │ 5.1s   │ $89.30 │ 78.5%  │ ⚠ 告警  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  异常事件列表                                                               │
│  时间          │ 类型        │ 严重程度 │ 会话ID      │ 详情                │
│  10:30:15      │ 循环检测     │ Critical │ sess_abc    │ web_fetch x3 重复  │
│  10:28:42      │ 成本预警     │ Warning  │ sess_def    │ $1.20 累计         │
│  10:25:00      │ 上下文溢出   │ Critical │ sess_ghi    │ utilization 96%   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 第四行：单会话追踪视图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  会话 sess_abc 完整决策链路                                                  │
│                                                                             │
│  Step 1  [OK]      用户输入 → LLM推理 → 决策: 调用 search_docs             │
│  Step 2  [OK]      工具结果 → LLM推理 → 决策: 调用 code_exec               │
│  Step 3  [OK]      工具结果 → LLM推理 → 决策: 调用 web_fetch               │
│  Step 4  [WARN]    工具结果 → LLM推理 → 决策: 调用 web_fetch (重复!)       │
│  Step 5  [ALERT]   工具结果 → LLM推理 → 决策: 调用 web_fetch (重复!!)      │
│  Step 6  [BREAK]   🔴 断路器触发 — 循环检测：连续 3 次相同调用              │
│                    → 会话终止，告警已发送                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 十、MTTD 保障分析

**目标：** 确保类似循环问题在 5 分钟内被检测到。

| 检测层 | 检测方式 | 预期 MTTD | 覆盖场景 |
|--------|---------|----------|---------|
| 第 1 层 | 连续 3 次相同调用精确匹配 | **< 1 分钟** | 精确循环（相同参数） |
| 第 2 层 | 10 次窗口内 > 50% 冗余率 | **< 2 分钟** | 近似循环（参数微变） |
| 第 3 层 | 会话级行为异常（步骤/时长/成本） | **< 5 分钟** | 所有类型的长时间异常 |
| 第 4 层 | 成本硬上限（$10/会话） | **成本封顶** | 兜底防护，无论何种原因 |

**本次事故的检测时间线模拟：**

假设循环以每 30 秒一次的频率运行（1 次 LLM 调用 + 1 次工具调用）：

```
T+0:00   循环开始
T+0:30   第 1 次重复调用 — 正常
T+1:00   第 2 次重复调用 — 正常
T+1:30   第 3 次重复调用 — 🚨 第 1 层检测触发！断路器激活，会话终止
```

**实际 MTTD：< 2 分钟**，远优于 5 分钟目标。

即使第 1 层失效（例如参数每次略有不同）：

```
T+0:00   循环开始（参数微变）
T+5:00   第 10 次调用，冗余率 > 50% — 🚨 第 2 层检测触发
```

**第 2 层 MTTD：< 5 分钟**，恰好满足目标。

最坏情况（所有检测层失效，仅依赖成本上限）：

```
假设每次调用成本 $0.02，每 30 秒一次：
$10 / $0.02 = 500 次调用
500 * 30s = 250 分钟 ≈ 4.2 小时
```

但此时还有 $1.00 预警线：

```
$1.00 / $0.02 = 50 次调用
50 * 30s = 25 分钟 → 告警发出
```

**结论：** 即使循环检测器完全失效，成本预警也能在 25 分钟内发出告警。而循环检测器本身能在 2 分钟内捕获精确循环。系统具备纵深防御能力。

---

## 十一、实施路线图

### Phase 1：紧急防护（1-2 天）

针对本次事故的直接修复：

1. 实现循环检测器（精确匹配 + 断路器）
2. 实现会话成本硬上限（$10/会话）
3. 实现会话时长/步骤数硬限制
4. 部署 AGENT-CRIT-003、005、008 告警

**验收标准：** 模拟循环场景，MTTD < 2 分钟。

### Phase 2：完整监控（1-2 周）

1. 实现完整的决策追踪 Schema 埋点
2. 部署工具调用审计器
3. 实现上下文健康监控
4. 部署监控仪表盘
5. 部署所有 Warning 和 Info 级别告警

**验收标准：** 仪表盘可实时展示所有关键指标，告警覆盖率 100%。

### Phase 3：高级能力（1-2 月）

1. 实现语义相似度循环检测
2. 实现任务漂移检测
3. 实现 LLM-as-Judge 连贯性评估
4. 实现跨会话的全局异常检测
5. 建立基线和异常检测模型

**验收标准：** 系统能检测语义层面的循环和退化。

---

## 十二、事故复盘检查清单

针对本次 $40,000 事故，系统已部署以下防护层：

| 防护层 | 机制 | 是否能阻止本次事故 | 预期 MTTD |
|--------|------|-------------------|----------|
| 循环检测（精确匹配） | 连续 3 次相同调用触发断路器 | **是** | < 2 分钟 |
| 循环检测（冗余率） | 50%+ 冗余率触发断路器 | **是** | < 5 分钟 |
| 会话工具调用上限 | 100 次工具调用后强制终止 | **是** | 取决于调用频率 |
| 会话成本硬上限 | $10 后强制终止 | **是** — 成本封顶 $10 | 成本封顶 |
| 成本预警 | $1 时发出警告 | **是** — 25 分钟内告警 | < 25 分钟 |
| 会话时长限制 | 1 小时后强制终止 | **是** — 最多 1 小时 | < 1 小时 |

**结论：** 即使只有最外层防护（成本硬上限），本次事故的损失也能从 $40,000 降低到 $10。而循环检测器能在 2 分钟内捕获问题，实现真正的"5 分钟内检测"目标。

---

## 附录 A：告警通知配置

```yaml
notification_channels:
  pagerduty:
    service_key: ${PAGERDUTY_SERVICE_KEY}
    severity_mapping:
      critical: trigger
      warning: acknowledge

  slack:
    webhook_url: ${SLACK_WEBHOOK_URL}
    channels:
      critical: "#agent-alerts-critical"
      warning: "#agent-alerts"
      info: "#agent-monitoring"

  email:
    smtp_host: ${SMTP_HOST}
    recipients:
      critical: ["oncall@company.com", "agent-team@company.com"]
      warning: ["agent-team@company.com"]
      info: ["agent-team@company.com"]

escalation_policy:
  critical:
    - immediate: pagerduty + slack
    - 5_minutes: phone_call
    - 15_minutes: escalate_to_manager
  warning:
    - immediate: slack
    - 30_minutes: email
```

## 附录 B：指标存储方案

```
数据流向：

Agent 执行引擎
  → 结构化日志（JSON Lines）
  → 日志收集器（Fluent Bit / Vector）
  → 时序数据库（InfluxDB / Prometheus）
  → 仪表盘（Grafana）

实时流：
  → 消息队列（Kafka / Redis Streams）
  → 循环检测器（实时消费）
  → 告警引擎
  → 通知服务

长期存储：
  → 对象存储（S3）
  → 用于事后分析和审计
```
