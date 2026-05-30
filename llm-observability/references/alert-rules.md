# Agent 告警规则模板

## 告警级别定义

| 级别 | 含义 | 响应时间 | 通知方式 |
|------|------|---------|---------|
| **Critical** | 服务不可用或数据损坏 | < 5 分钟 | 电话 + 即时消息 |
| **Warning** | 性能退化或异常行为 | < 30 分钟 | 即时消息 |
| **Info** | 需要关注但不紧急 | < 4 小时 | 邮件 + 仪表盘 |

## Critical 告警

### AGENT-CRIT-001: 上下文溢出
```yaml
alert: ContextWindowOverflow
condition: agent.context.utilization > 0.95
for: 1m
severity: critical
description: "Agent 上下文窗口利用率超过 95%，即将溢出"
runbook: |
  1. 检查是否有异常的长对话
  2. 触发紧急上下文压缩
  3. 如果持续溢出，终止会话并通知用户
```

### AGENT-CRIT-002: 工具错误率飙升
```yaml
alert: ToolErrorRateSpike
condition: rate(agent.tools.error_rate[5m]) > 0.3
for: 2m
severity: critical
description: "工具调用错误率超过 30%（5分钟窗口）"
runbook: |
  1. 检查工具服务健康状态
  2. 检查是否有认证过期
  3. 如果工具服务不可用，启用降级方案
  4. 通知工具服务负责人
```

### AGENT-CRIT-003: 循环执行检测
```yaml
alert: AgentLoopDetected
condition: agent.tools.redundant_rate > 0.5 and agent.tools.call_count > 10
for: 1m
severity: critical
description: "Agent 检测到循环执行：超过 50% 的工具调用是重复的"
runbook: |
  1. 触发断路器，停止工具调用
  2. 检查 Agent 是否陷入了推理循环
  3. 终止当前会话
  4. 分析循环原因（提示问题？工具返回不一致？）
```

### AGENT-CRIT-004: 安全事件
```yaml
alert: AgentSecurityViolation
condition: agent.security.sensitive_data_exposed > 0
for: 0s
severity: critical
description: "Agent 输出中检测到敏感数据泄露"
runbook: |
  1. 立即拦截输出
  2. 记录完整的输入-输出链路
  3. 通知安全团队
  4. 暂停该 Agent 实例
```

## Warning 告警

### AGENT-WARN-001: 成本飙升
```yaml
alert: AgentCostSpike
condition: agent.cost.per_session > 1.0
for: 5m
severity: warning
description: "单会话成本超过 $1.00"
runbook: |
  1. 检查会话详情，确认是否有异常
  2. 检查是否有循环调用
  3. 如果是正常的长对话，评估是否需要成本上限
```

### AGENT-WARN-002: 延迟退化
```yaml
alert: AgentLatencyDegradation
condition: agent.latency.p95 > 2 * baseline(agent.latency.p95[1h])
for: 10m
severity: warning
description: "P95 延迟超过基线的 2 倍"
runbook: |
  1. 检查 LLM 服务延迟
  2. 检查工具服务延迟
  3. 检查上下文大小是否异常增长
  4. 如果是 LLM 服务问题，考虑切换备用模型
```

### AGENT-WARN-003: 上下文利用率高
```yaml
alert: ContextUtilizationHigh
condition: agent.context.utilization > 0.8
for: 5m
severity: warning
description: "上下文利用率超过 80%"
runbook: |
  1. 检查是否需要触发上下文压缩
  2. 评估对话是否需要分段
  3. 监控是否继续增长
```

### AGENT-WARN-004: Token 爆炸
```yaml
alert: TokenExplosion
condition: agent.tokens.output > 50000
for: 0s
severity: warning
description: "单次 LLM 调用输出超过 50K tokens"
runbook: |
  1. 检查是否有异常的长输出
  2. 检查提示是否导致了冗长回复
  3. 考虑添加输出长度限制
```

### AGENT-WARN-005: 工具重试率高
```yaml
alert: ToolRetryRateHigh
condition: agent.tools.retry_rate > 0.2
for: 10m
severity: warning
description: "工具重试率超过 20%"
runbook: |
  1. 检查工具服务健康状态
  2. 检查网络稳定性
  3. 评估超时设置是否合理
```

### AGENT-WARN-006: 任务漂移
```yaml
alert: TaskDriftDetected
condition: agent.context.drift_score > 0.3
for: 5m
severity: warning
description: "Agent 任务漂移分数超过 0.3，可能偏离初始目标"
runbook: |
  1. 检查对话历史，确认是否发生话题偏移
  2. 评估是否需要重新注入任务目标
  3. 如果是用户主动切换话题，降级为 Info
```

## Info 告警

### AGENT-INFO-001: 缓存命中率低
```yaml
alert: CacheHitRateLow
condition: agent.tokens.cache_hit_rate < 0.3
for: 30m
severity: info
description: "提示缓存命中率低于 30%"
runbook: |
  1. 检查提示模板是否稳定
  2. 评估是否需要优化提示结构以提高缓存命中
```

### AGENT-INFO-002: 注入尝试
```yaml
alert: InjectionAttemptDetected
condition: agent.security.injection_attempts > 0
for: 0s
severity: info
description: "检测到 Prompt Injection 尝试"
runbook: |
  1. 记录注入尝试的详细内容
  2. 验证防御是否生效
  3. 如果防御失败，升级为 Critical
```

## 告警去重与聚合

- 同一会话的同类告警在 5 分钟内去重
- 批量告警（如工具服务宕机导致大量会话报错）聚合为一条
- 告警附带 session_id 和 trace_id，方便快速定位
