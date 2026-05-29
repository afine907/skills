# LLM Agent Observability System: Infinite Loop Detection & Cost Control

## Executive Summary

This document defines a production-ready observability system designed to detect runaway agent tool calls (infinite loops, stuck retries, unbounded recursion) within **5 minutes** and prevent cost overruns. The system is motivated by a real incident where a tool call loop ran for 11 days and incurred $40,000 in charges before discovery.

---

## 1. Incident Analysis

### 1.1 Root Cause Pattern

The $40K incident followed a common failure pattern:

| Phase | What Happened | Why It Went Undetected |
|-------|---------------|----------------------|
| Trigger | A tool call received an unexpected response (error, empty result, or partial data) | No circuit breaker on retry logic |
| Amplification | The agent's retry/re-loop logic re-invoked the same tool with the same (or equivalent) arguments | No duplicate-call detection |
| Sustained | Each iteration consumed LLM tokens + tool execution resources | No per-task budget or time limit |
| Detection Gap | No alerting on cumulative cost, call count, or wall-clock duration for a single logical task | Monitoring was aggregate, not per-task |

### 1.2 Detection Requirements

| Metric | Target |
|--------|--------|
| Time to detect | ≤ 5 minutes from first anomalous call |
| False positive rate | < 1 per week per 1000 tasks |
| Coverage | All tool calls, all agent sessions |
| Cost ceiling enforcement | Hard kill at configurable threshold |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Runtime                            │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │ Agent    │───▶│ Tool Call    │───▶│ Tool Execution        │  │
│  │ Loop     │    │ Interceptor  │    │ (API, DB, Shell, etc) │  │
│  └──────────┘    └──────┬───────┘    └───────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│              ┌─────────────────────┐                            │
│              │  Local Emitter      │                            │
│              │  (structured logs)  │                            │
│              └─────────┬───────────┘                            │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                   Observability Pipeline                        │
│                                                                │
│  ┌────────────┐   ┌──────────────┐   ┌──────────────────────┐ │
│  │ Collector  │──▶│ Stream       │──▶│ Real-Time Detector   │ │
│  │ (sidecar)  │   │ Processor    │   │ (anomaly engine)     │ │
│  └────────────┘   └──────────────┘   └──────────┬───────────┘ │
│                                                  │              │
│                         ┌────────────────────────┼──────────┐  │
│                         ▼                        ▼          │  │
│              ┌──────────────┐        ┌───────────────────┐  │  │
│              │ Alert Router │        │ Dashboard / Viz   │  │  │
│              └──────┬───────┘        └───────────────────┘  │  │
│                     │                                       │  │
│        ┌────────────┼────────────┐                         │  │
│        ▼            ▼            ▼                         │  │
│   ┌─────────┐ ┌──────────┐ ┌──────────┐                   │  │
│   │ PagerDuty│ │ Slack    │ │ Auto-Kill│                   │  │
│   │ / OpsGenie│ │ Webhook │ │ Signal   │                   │  │
│   └─────────┘ └──────────┘ └──────────┘                   │  │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model: Tool Call Event Schema

Every tool call emits a structured event. This is the foundation of all detection.

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-05-29T10:30:00.123Z",
  "session_id": "sess_abc123",
  "task_id": "task_xyz789",
  "agent_id": "agent_prod_01",
  "tool_name": "search_database",
  "tool_input_hash": "sha256:ab3f...",
  "tool_input_summary": "query=SELECT * FROM orders WHERE status='pending'",
  "tool_output_hash": "sha256:cd4e...",
  "tool_output_summary": "rows=0",
  "call_index_in_task": 47,
  "call_index_in_session": 312,
  "duration_ms": 1250,
  "status": "success|error|timeout",
  "error_message": null,
  "token_usage": {
    "input_tokens": 1500,
    "output_tokens": 200,
    "cached_tokens": 0
  },
  "cost_usd": 0.0042,
  "cumulative_task_cost_usd": 0.89,
  "cumulative_task_duration_s": 127,
  "parent_call_id": "uuid-of-previous-call",
  "retry_of_call_id": null
}
```

---

## 4. Detection Rules (Anomaly Engine)

The core of the system: a set of real-time detection rules evaluated on every incoming event.

### 4.1 Rule Definitions

#### Rule 1: Duplicate Tool Call Detector (Loop Detection)

**Purpose**: Detect the same tool being called with identical or near-identical inputs in rapid succession.

```python
class DuplicateCallDetector:
    """
    Fires when the same tool is called with the same input_hash
    more than N times within a rolling window.
    """
    THRESHOLD = 5           # max identical calls
    WINDOW_SECONDS = 300    # 5-minute rolling window

    def evaluate(self, event: ToolCallEvent, history: EventStore) -> Alert | None:
        recent_same = history.count_recent(
            session_id=event.session_id,
            tool_name=event.tool_name,
            tool_input_hash=event.tool_input_hash,
            window_seconds=self.WINDOW_SECONDS,
        )
        if recent_same >= self.THRESHOLD:
            return Alert(
                severity="critical",
                rule="duplicate_call_loop",
                message=(
                    f"Tool '{event.tool_name}' called {recent_same} times with "
                    f"identical input in {self.WINDOW_SECONDS}s. Likely infinite loop."
                ),
                event=event,
                action="auto_kill",
            )
        return None
```

#### Rule 2: Call Count Budget (Per-Task Limit)

**Purpose**: Hard cap on total tool calls per logical task.

```python
class TaskCallBudget:
    """
    Fires when a single task exceeds a configurable call count.
    """
    MAX_CALLS_PER_TASK = 100  # adjust per workload

    def evaluate(self, event: ToolCallEvent) -> Alert | None:
        if event.call_index_in_task > self.MAX_CALLS_PER_TASK:
            return Alert(
                severity="critical",
                rule="task_call_budget_exceeded",
                message=(
                    f"Task '{event.task_id}' has made {event.call_index_in_task} "
                    f"tool calls (limit: {self.MAX_CALLS_PER_TASK})."
                ),
                event=event,
                action="auto_kill",
            )
        return None
```

#### Rule 3: Cost Ceiling (Per-Task and Per-Session)

**Purpose**: Prevent runaway spending.

```python
class CostCeiling:
    """
    Fires when cumulative cost for a task or session exceeds threshold.
    """
    TASK_COST_LIMIT_USD = 10.0
    SESSION_COST_LIMIT_USD = 50.0

    def evaluate(self, event: ToolCallEvent) -> Alert | None:
        if event.cumulative_task_cost_usd > self.TASK_COST_LIMIT_USD:
            return Alert(
                severity="critical",
                rule="task_cost_exceeded",
                message=(
                    f"Task '{event.task_id}' cost ${event.cumulative_task_cost_usd:.2f} "
                    f"(limit: ${self.TASK_COST_LIMIT_USD:.2f})."
                ),
                event=event,
                action="auto_kill",
            )
        return None
```

#### Rule 4: Wall-Clock Duration Limit

**Purpose**: Detect tasks that run far longer than expected.

```python
class DurationLimit:
    """
    Fires when a task has been running longer than the allowed duration.
    """
    MAX_TASK_DURATION_S = 600  # 10 minutes

    def evaluate(self, event: ToolCallEvent) -> Alert | None:
        if event.cumulative_task_duration_s > self.MAX_TASK_DURATION_S:
            return Alert(
                severity="warning",
                rule="task_duration_exceeded",
                message=(
                    f"Task '{event.task_id}' has been running for "
                    f"{event.cumulative_task_duration_s}s (limit: {self.MAX_TASK_DURATION_S}s)."
                ),
                event=event,
                action="escalate",
            )
        return None
```

#### Rule 5: Output Stagnation Detector

**Purpose**: Detect when repeated calls produce no new information (same output hash), indicating the agent is stuck.

```python
class OutputStagnationDetector:
    """
    Fires when N consecutive calls to any tool produce identical output hashes.
    """
    STAGNATION_THRESHOLD = 3

    def evaluate(self, event: ToolCallEvent, history: EventStore) -> Alert | None:
        recent_outputs = history.recent_output_hashes(
            session_id=event.session_id,
            task_id=event.task_id,
            count=self.STAGNATION_THRESHOLD,
        )
        if (len(recent_outputs) >= self.STAGNATION_THRESHOLD
                and len(set(recent_outputs)) == 1):
            return Alert(
                severity="warning",
                rule="output_stagnation",
                message=(
                    f"Last {self.STAGNATION_THRESHOLD} tool calls for task "
                    f"'{event.task_id}' produced identical outputs."
                ),
                event=event,
                action="escalate",
            )
        return None
```

#### Rule 6: Error Retry Spiral Detector

**Purpose**: Detect when an agent is retrying a failing tool call repeatedly.

```python
class ErrorRetrySpiralDetector:
    """
    Fires when the same tool call fails N times in a row.
    """
    MAX_CONSECUTIVE_ERRORS = 3

    def evaluate(self, event: ToolCallEvent, history: EventStore) -> Alert | None:
        if event.status != "error":
            return None
        consecutive_errors = history.count_consecutive_errors(
            session_id=event.session_id,
            tool_name=event.tool_name,
            tool_input_hash=event.tool_input_hash,
        )
        if consecutive_errors >= self.MAX_CONSECUTIVE_ERRORS:
            return Alert(
                severity="critical",
                rule="error_retry_spiral",
                message=(
                    f"Tool '{event.tool_name}' has failed {consecutive_errors} "
                    f"consecutive times with the same input."
                ),
                event=event,
                action="auto_kill",
            )
        return None
```

#### Rule 7: Token Rate Anomaly Detector

**Purpose**: Detect abnormally high token consumption rates (indicative of a tight loop making LLM calls).

```python
class TokenRateDetector:
    """
    Fires when token consumption rate exceeds a threshold over a rolling window.
    """
    MAX_TOKENS_PER_MINUTE = 100_000
    WINDOW_SECONDS = 60

    def evaluate(self, event: ToolCallEvent, history: EventStore) -> Alert | None:
        tokens_in_window = history.sum_tokens(
            session_id=event.session_id,
            window_seconds=self.WINDOW_SECONDS,
        )
        rate = tokens_in_window / (self.WINDOW_SECONDS / 60)
        if rate > self.MAX_TOKENS_PER_MINUTE:
            return Alert(
                severity="critical",
                rule="token_rate_anomaly",
                message=(
                    f"Session '{event.session_id}' consuming {rate:.0f} tokens/min "
                    f"(limit: {self.MAX_TOKENS_PER_MINUTE})."
                ),
                event=event,
                action="auto_kill",
            )
        return None
```

### 4.2 Rule Priority and Action Matrix

| Rule | Severity | Action | Response Time |
|------|----------|--------|---------------|
| Duplicate Call Loop | Critical | Auto-kill + page | Immediate |
| Task Call Budget | Critical | Auto-kill + page | Immediate |
| Cost Ceiling | Critical | Auto-kill + page | Immediate |
| Error Retry Spiral | Critical | Auto-kill + page | Immediate |
| Token Rate Anomaly | Critical | Auto-kill + page | Immediate |
| Duration Limit | Warning | Escalate + Slack | 5 min |
| Output Stagnation | Warning | Escalate + Slack | 5 min |

---

## 5. Enforcement Layer: Auto-Kill Mechanism

Detection without enforcement is useless. The system must be able to **stop** a runaway agent.

### 5.1 Kill Signal Architecture

```python
class AgentEnforcer:
    """
    Receives kill signals from the anomaly engine and terminates agent tasks.
    """

    def __init__(self, agent_runtime_client):
        self.client = agent_runtime_client

    def execute_kill(self, alert: Alert):
        """Immediately terminate the offending task/session."""
        # 1. Send kill signal to agent runtime
        self.client.terminate_task(
            task_id=alert.event.task_id,
            reason=alert.message,
        )

        # 2. Revoke API keys / tokens associated with this session
        self.client.revoke_session_credentials(
            session_id=alert.event.session_id,
        )

        # 3. Quarantine the task for post-mortem
        self.client.quarantine_task(
            task_id=alert.event.task_id,
            snapshot=True,
        )

        # 4. Log the kill action
        audit_log.record(
            action="auto_kill",
            alert=alert,
            timestamp=utcnow(),
        )
```

### 5.2 Graceful vs Hard Kill

| Scenario | Kill Type | Behavior |
|----------|-----------|----------|
| Cost ceiling approached (80%) | Graceful | Complete current call, then stop |
| Cost ceiling exceeded (100%) | Hard | Terminate mid-call, revoke credentials |
| Duplicate loop detected | Hard | Immediate termination |
| Duration exceeded | Graceful | Complete current call, then stop |

---

## 6. Alerting Configuration

### 6.1 Alert Routing

```yaml
# alerting-config.yaml
routes:
  - match:
      severity: critical
    receivers:
      - pagerduty-oncall
      - slack-incidents
      - auto-kill-executor
    repeat_interval: 1m

  - match:
      severity: warning
    receivers:
      - slack-agent-ops
    repeat_interval: 5m

receivers:
  pagerduty-oncall:
    type: pagerduty
    integration_key: ${PAGERDUTY_KEY}
    severity_mapping:
      critical: critical

  slack-incidents:
    type: slack
    webhook_url: ${SLACK_WEBHOOK_INCIDENTS}
    channel: "#agent-incidents"

  slack-agent-ops:
    type: slack
    webhook_url: ${SLACK_WEBHOOK_OPS}
    channel: "#agent-ops"

  auto-kill-executor:
    type: internal
    handler: AgentEnforcer.execute_kill
```

### 6.2 Alert Payload

```json
{
  "alert_name": "duplicate_call_loop",
  "severity": "critical",
  "timestamp": "2026-05-29T10:35:00Z",
  "message": "Tool 'search_database' called 7 times with identical input in 300s. Likely infinite loop.",
  "context": {
    "session_id": "sess_abc123",
    "task_id": "task_xyz789",
    "agent_id": "agent_prod_01",
    "tool_name": "search_database",
    "call_count": 7,
    "cumulative_cost_usd": 0.89,
    "duration_s": 127
  },
  "actions_taken": [
    "task_terminated",
    "session_credentials_revoked",
    "task_quarantined"
  ],
  "runbook_url": "https://runbooks.internal/agent-infinite-loop"
}
```

---

## 7. Dashboard Specification

### 7.1 Real-Time Dashboard Panels

| Panel | Visualization | Refresh | Purpose |
|-------|---------------|---------|---------|
| Active Sessions | Counter + sparkline | 5s | Current agent activity |
| Tool Calls/min | Time series | 10s | Detect sudden spikes |
| Cost (last 1h) | Gauge with thresholds | 30s | Budget tracking |
| Longest Running Task | Table (top 10) | 10s | Spot stuck tasks |
| Error Rate by Tool | Bar chart | 30s | Identify failing tools |
| Active Alerts | Alert list | 5s | Current incidents |
| Duplicate Call Detections | Counter + log | 10s | Loop detection hits |
| Token Consumption Rate | Time series | 10s | Anomaly visualization |

### 7.2 Key Queries (Prometheus/QL)

```promql
# Tool call rate per session
rate(tool_call_total{session_id="$session"}[1m])

# Cumulative cost per task
tool_call_cost_usd_total{task_id="$task"}

# Duplicate call detections (last 5 min)
sum(increase(duplicate_call_alert_total[5m]))

# Error rate by tool
rate(tool_call_errors_total[5m]) / rate(tool_call_total[5m])
```

---

## 8. Implementation: Instrumentation Layer

### 8.1 Tool Call Interceptor (Middleware)

This is the minimal code that must wrap every tool call in the agent runtime.

```python
import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class TaskContext:
    """Tracks state for the current logical task."""
    task_id: str
    session_id: str
    agent_id: str
    call_count: int = 0
    cumulative_cost_usd: float = 0.0
    start_time: float = field(default_factory=time.time)


class ToolCallInterceptor:
    """
    Wraps every tool call with observability instrumentation.
    MUST be placed between the agent loop and actual tool execution.
    """

    def __init__(self, event_emitter, enforcer, config: dict = None):
        self.event_emitter = event_emitter
        self.enforcer = enforcer
        self.config = config or {}

    def intercept(
        self,
        tool_name: str,
        tool_fn: Callable,
        tool_input: Any,
        task_ctx: TaskContext,
    ) -> Any:
        """Execute a tool call with full instrumentation."""

        # Pre-call: check budgets BEFORE executing
        self._check_pre_call_limits(task_ctx)

        # Build event skeleton
        call_id = str(uuid.uuid4())
        input_hash = hashlib.sha256(str(tool_input).encode()).hexdigest()[:16]
        start = time.time()

        task_ctx.call_count += 1

        try:
            # Execute the actual tool
            result = tool_fn(tool_input)
            duration_ms = (time.time() - start) * 1000
            status = "success"

            # Estimate cost (replace with actual token counting)
            cost = self._estimate_cost(tool_name, tool_input, result)
            task_ctx.cumulative_cost_usd += cost

            # Build and emit event
            event = self._build_event(
                call_id=call_id,
                tool_name=tool_name,
                tool_input=tool_input,
                input_hash=input_hash,
                result=result,
                status=status,
                duration_ms=duration_ms,
                cost=cost,
                task_ctx=task_ctx,
            )
            self.event_emitter.emit(event)

            # Post-call: check for anomalies
            alerts = self._check_post_call_rules(event)
            for alert in alerts:
                self.enforcer.execute_kill(alert)

            return result

        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            event = self._build_event(
                call_id=call_id,
                tool_name=tool_name,
                tool_input=tool_input,
                input_hash=input_hash,
                result=None,
                status="error",
                duration_ms=duration_ms,
                cost=0.0,
                task_ctx=task_ctx,
                error_message=str(e),
            )
            self.event_emitter.emit(event)

            alerts = self._check_post_call_rules(event)
            for alert in alerts:
                self.enforcer.execute_kill(alert)

            raise

    def _check_pre_call_limits(self, task_ctx: TaskContext):
        """Hard limits checked BEFORE tool execution."""
        max_calls = self.config.get("max_calls_per_task", 100)
        if task_ctx.call_count >= max_calls:
            raise RuntimeError(
                f"Task {task_ctx.task_id} exceeded call budget ({max_calls}). "
                f"Refusing to execute more tool calls."
            )

        max_cost = self.config.get("max_task_cost_usd", 10.0)
        if task_ctx.cumulative_cost_usd >= max_cost:
            raise RuntimeError(
                f"Task {task_ctx.task_id} exceeded cost budget (${max_cost}). "
                f"Refusing to execute more tool calls."
            )

        max_duration = self.config.get("max_task_duration_s", 600)
        elapsed = time.time() - task_ctx.start_time
        if elapsed >= max_duration:
            raise RuntimeError(
                f"Task {task_ctx.task_id} exceeded time budget ({max_duration}s). "
                f"Refusing to execute more tool calls."
            )

    def _estimate_cost(self, tool_name, tool_input, result) -> float:
        """Estimate USD cost of this call. Replace with actual billing logic."""
        # Placeholder: $0.01 per call average
        return 0.01

    def _build_event(self, **kwargs) -> dict:
        """Build the structured event from call data."""
        ctx = kwargs["task_ctx"]
        return {
            "event_id": kwargs["call_id"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "session_id": ctx.session_id,
            "task_id": ctx.task_id,
            "agent_id": ctx.agent_id,
            "tool_name": kwargs["tool_name"],
            "tool_input_hash": kwargs["input_hash"],
            "tool_input_summary": str(kwargs["tool_input"])[:200],
            "tool_output_hash": hashlib.sha256(
                str(kwargs.get("result", "")).encode()
            ).hexdigest()[:16] if kwargs.get("result") else None,
            "tool_output_summary": str(kwargs.get("result", ""))[:200],
            "call_index_in_task": ctx.call_count,
            "duration_ms": kwargs["duration_ms"],
            "status": kwargs["status"],
            "error_message": kwargs.get("error_message"),
            "cost_usd": kwargs["cost"],
            "cumulative_task_cost_usd": ctx.cumulative_cost_usd,
            "cumulative_task_duration_s": time.time() - ctx.start_time,
        }

    def _check_post_call_rules(self, event: dict) -> list:
        """Evaluate all detection rules against the event. Returns list of alerts."""
        # This is where the rules from Section 4 are evaluated.
        # In production, this delegates to the anomaly engine.
        return []
```

### 8.2 Integration Example

```python
# How to wire the interceptor into an agent loop

from my_agent import AgentLoop, ToolRegistry

interceptor = ToolCallInterceptor(
    event_emitter=KafkaEmitter(brokers="kafka:9092", topic="tool-call-events"),
    enforcer=AgentEnforcer(runtime_client),
    config={
        "max_calls_per_task": 100,
        "max_task_cost_usd": 10.0,
        "max_task_duration_s": 600,
    },
)

# Wrap every tool with the interceptor
for tool_name, tool_fn in tool_registry.all():
    tool_registry.register(
        tool_name,
        lambda input, _fn=tool_fn, _name=tool_name: interceptor.intercept(
            tool_name=_name,
            tool_fn=_fn,
            tool_input=input,
            task_ctx=current_task_context,
        ),
    )
```

---

## 9. Stream Processing Pipeline

### 9.1 Technology Stack

| Component | Recommended Tool | Alternative |
|-----------|-----------------|-------------|
| Event transport | Apache Kafka | AWS Kinesis, Redis Streams |
| Stream processor | Apache Flink | Kafka Streams, Spark Streaming |
| Time-series store | Prometheus + Thanos | InfluxDB, TimescaleDB |
| Event store | ClickHouse | Elasticsearch, PostgreSQL |
| Alerting | Alertmanager + custom | Grafana Alerting |
| Dashboard | Grafana | Datadog, custom React |

### 9.2 Stream Processing Topology

```
tool-call-events (Kafka topic)
    │
    ├──▶ [Flink Job: Duplicate Detector]
    │       window: 5 min, keyed by (session, tool, input_hash)
    │       output: duplicate-call-alerts topic
    │
    ├──▶ [Flink Job: Cost Aggregator]
    │       window: unbounded, keyed by task_id
    │       output: cost-ceiling-alerts topic
    │
    ├──▶ [Flink Job: Duration Monitor]
    │       timer: per-task, keyed by task_id
    │       output: duration-alerts topic
    │
    ├──▶ [Flink Job: Error Spiral Detector]
    │       window: consecutive, keyed by (session, tool, input_hash)
    │       output: error-spiral-alerts topic
    │
    └──▶ [ClickHouse Sink]
            for historical analysis and dashboards

*-alerts topics ──▶ [Alert Router] ──▶ PagerDuty / Slack / Auto-Kill
```

---

## 10. Testing the System

### 10.1 Simulate an Infinite Loop

```python
def test_duplicate_loop_detection():
    """
    Simulate a tool being called with identical input 10 times in 60 seconds.
    Assert that the 5th call triggers a critical alert.
    """
    detector = DuplicateCallDetector()
    history = InMemoryEventStore()

    for i in range(10):
        event = make_event(
            session_id="test-session",
            tool_name="search_db",
            tool_input_hash="abc123",
            call_index_in_task=i + 1,
        )
        history.add(event)
        alert = detector.evaluate(event, history)

        if i < 4:
            assert alert is None, f"Should not alert on call {i+1}"
        else:
            assert alert is not None, f"Should alert on call {i+1}"
            assert alert.severity == "critical"
            assert alert.action == "auto_kill"


def test_cost_ceiling_enforcement():
    """
    Assert that a task is killed when cumulative cost exceeds the limit.
    """
    interceptor = ToolCallInterceptor(
        event_emitter=NullEmitter(),
        enforcer=MockEnforcer(),
        config={"max_task_cost_usd": 5.0},
    )
    ctx = TaskContext(task_id="t1", session_id="s1", agent_id="a1")
    ctx.cumulative_cost_usd = 5.01  # Already over limit

    with pytest.raises(RuntimeError, match="exceeded cost budget"):
        interceptor.intercept("noop_tool", lambda x: None, {}, ctx)
```

### 10.2 End-to-End Test Scenario

```bash
# Run the simulated runaway agent
python tests/simulate_runaway_agent.py --mode=loop --duration=60s

# Expected: alert fires within 5 minutes, agent is killed
# Verify:
#   1. Alert appears in PagerDuty/Slack within 5 min
#   2. Agent process is terminated
#   3. Session credentials are revoked
#   4. Task is quarantined with full call history
#   5. Dashboard shows the incident in real-time
```

---

## 11. Operational Runbook

### 11.1 When an Alert Fires

1. **Acknowledge** the alert in PagerDuty within 2 minutes.
2. **Verify** the auto-kill action was executed (check agent runtime logs).
3. **Inspect** the quarantined task in ClickHouse:
   ```sql
   SELECT * FROM tool_call_events
   WHERE task_id = 'task_xyz789'
   ORDER BY timestamp;
   ```
4. **Identify root cause**: Was it a logic bug, bad input, or infrastructure issue?
5. **File incident report** with timeline, root cause, and remediation steps.
6. **Adjust thresholds** if false positive, or add new rules if gap found.

### 11.2 Threshold Tuning Process

1. Run system in "observe only" mode for 2 weeks (alerts but no auto-kill).
2. Review all alerts: classify as true positive / false positive.
3. Adjust thresholds to achieve < 1 false positive per week per 1000 tasks.
4. Enable auto-kill for critical rules only.
5. Enable auto-kill for warning rules after 1 month of stable operation.

---

## 12. Cost Estimate for the Observability System

| Component | Monthly Cost (est.) |
|-----------|-------------------|
| Kafka (3 brokers) | $400 |
| Flink cluster (2 JM + 6 TM) | $800 |
| ClickHouse (3 nodes) | $600 |
| Prometheus + Grafana | $200 |
| PagerDuty | $150 |
| **Total** | **~$2,150/month** |

Compared to the $40K incident cost, this system pays for itself after preventing **one** incident every 18 months.

---

## 13. Rollout Plan

| Phase | Duration | Scope | Actions |
|-------|----------|-------|---------|
| Phase 1 | Week 1-2 | Instrument | Add ToolCallInterceptor to all agent runtimes. Emit events to Kafka. No alerting yet. |
| Phase 2 | Week 3-4 | Observe | Deploy anomaly engine in "log only" mode. Build dashboards. Validate data quality. |
| Phase 3 | Week 5-6 | Alert | Enable Slack alerts for all rules. Tune thresholds based on observed data. |
| Phase 4 | Week 7-8 | Enforce | Enable auto-kill for critical rules. Enable PagerDuty for critical alerts. |
| Phase 5 | Week 9+ | Harden | Add warning-level auto-kill. Expand to all environments. Conduct quarterly fire drills. |

---

## 14. Key Metrics to Track (SLIs)

| SLI | Target | Measurement |
|-----|--------|-------------|
| Detection latency | p99 < 5 min | Time from first anomalous call to alert |
| Kill latency | p99 < 30s | Time from alert to agent termination |
| False positive rate | < 1/week/1000 tasks | Human classification of alerts |
| Coverage | 100% of tool calls instrumented | Event completeness audit |
| System uptime | 99.9% | Observability pipeline availability |

---

## 15. Summary

This system prevents a recurrence of the $40K incident through four layers of defense:

1. **Pre-call hard limits** (call count, cost, duration) -- checked before every tool execution, fail-fast.
2. **Real-time duplicate detection** -- sliding window analysis catches loops within 5 minutes.
3. **Auto-kill enforcement** -- critical alerts automatically terminate runaway tasks and revoke credentials.
4. **Post-incident analysis** -- quarantined task history enables rapid root cause identification.

The total implementation effort is approximately 8 weeks for a small team, and the operational cost (~$2,150/month) is justified by the risk reduction against incidents costing tens of thousands of dollars per occurrence.
