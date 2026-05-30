# Agent 专用指标目录

## 指标分类

### 1. 性能指标

| 指标名 | 定义 | 计算方式 | 基准值 |
|--------|------|---------|--------|
| `agent.latency.first_token` | 首次响应时间 | 从用户输入到首个输出的时间 | < 2 秒 |
| `agent.latency.total` | 总完成时间 | 从用户输入到最终输出的时间 | 任务相关 |
| `agent.latency.llm_call` | LLM 调用延迟 | 单次 LLM 调用的延迟 | < 3 秒 |
| `agent.latency.tool_call` | 工具调用延迟 | 单次工具调用的延迟 | < 2 秒 |
| `agent.latency.p50` | P50 延迟 | 50 分位延迟 | < 3 秒 |
| `agent.latency.p95` | P95 延迟 | 95 分位延迟 | < 10 秒 |
| `agent.latency.p99` | P99 延迟 | 99 分位延迟 | < 30 秒 |

### 2. 成本指标

| 指标名 | 定义 | 计算方式 | 基准值 |
|--------|------|---------|--------|
| `agent.cost.per_session` | 每会话成本 | 会话内所有 LLM + 工具调用成本之和 | < $0.10 |
| `agent.cost.per_step` | 每步骤成本 | 单步的 LLM 调用成本 | < $0.02 |
| `agent.cost.per_task` | 每任务成本 | 完成一个任务的总成本 | 任务相关 |
| `agent.tokens.input` | 输入 Token 数 | 每次 LLM 调用的输入 Token | 趋势监控 |
| `agent.tokens.output` | 输出 Token 数 | 每次 LLM 调用的输出 Token | 趋势监控 |
| `agent.tokens.cached` | 缓存命中 Token | 命中提示缓存的 Token 数 | 越高越好 |
| `agent.tokens.cache_hit_rate` | 缓存命中率 | cached_tokens / total_input_tokens | > 50% |

### 3. 质量指标

| 指标名 | 定义 | 计算方式 | 基准值 |
|--------|------|---------|--------|
| `agent.completion.success_rate` | 任务成功率 | 成功完成的任务 / 总任务 | > 90% |
| `agent.completion.steps_avg` | 平均步骤数 | 完成任务的平均步骤数 | 趋势监控 |
| `agent.hallucination.rate` | 幻觉率 | 含幻觉的输出 / 总输出（采样） | < 5% |
| `agent.coherence.score` | 连贯性分数 | LLM-as-Judge 评分（采样） | > 0.8 |
| `agent.decision.confidence` | 平均决策置信度 | 决策置信度均值 | > 0.8 |

### 4. 工具指标

| 指标名 | 定义 | 计算方式 | 基准值 |
|--------|------|---------|--------|
| `agent.tools.call_count` | 工具调用次数 | 每会话的工具调用总数 | 趋势监控 |
| `agent.tools.error_rate` | 工具错误率 | 失败调用 / 总调用 | < 5% |
| `agent.tools.retry_rate` | 工具重试率 | 触发重试的调用 / 总调用 | < 10% |
| `agent.tools.redundant_rate` | 冗余调用率 | 相同参数重复调用 / 总调用 | < 5% |
| `agent.tools.circuit_breaks` | 断路器触发次数 | 断路器打开的次数 | 0 |
| `agent.tools.latency.p95` | 工具 P95 延迟 | 工具调用的 95 分位延迟 | < 5 秒 |

### 5. 上下文健康指标

| 指标名 | 定义 | 计算方式 | 基准值 |
|--------|------|---------|--------|
| `agent.context.utilization` | 上下文利用率 | 已用 Token / 窗口大小 | < 80% |
| `agent.context.budget_remaining` | 剩余 Token 预算 | 估算剩余可用 Token | > 20% |
| `agent.context.compression_count` | 压缩事件数 | 上下文压缩/摘要的次数 | < 3 |
| `agent.context.reference_age` | 引用新鲜度 | 被引用上下文的平均"年龄" | < 10 步 |
| `agent.context.drift_score` | 任务漂移分数 | 当前目标与初始目标的语义距离 | < 0.3 |

### 6. 安全指标

| 指标名 | 定义 | 计算方式 | 基准值 |
|--------|------|---------|--------|
| `agent.security.injection_attempts` | 注入攻击尝试 | 检测到的 Prompt Injection 次数 | 监控 |
| `agent.security.permission_denials` | 权限拒绝次数 | 被 HITL 门禁阻止的操作数 | 监控 |
| `agent.security.sensitive_data_exposed` | 敏感数据泄露 | 输出中检测到的敏感信息数 | 0 |
| `agent.security.scope_violations` | 范围越权 | Agent 尝试超出权限的操作数 | 0 |

## 指标聚合维度

所有指标应支持按以下维度聚合：

- **按 Agent** — 区分不同类型的 Agent（客服、销售、运维）
- **按模型** — 区分不同 LLM（Claude、GPT、Gemini）
- **按会话** — 单会话级别的详细追踪
- **按用户** — 用户级别的成本和使用量
- **按时间** — 小时/天/周的趋势分析
