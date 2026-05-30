# 上下文健康检测清单

## 检查项

### 1. 上下文窗口管理

- [ ] **窗口利用率** — 当前已用 Token / 最大窗口大小
  - 正常：< 60%
  - 警告：60-80%
  - 危险：> 80%
  - 临界：> 95%

- [ ] **Token 预算** — 估算剩余可用 Token（考虑输出 Token 预留）
  - 公式：remaining = window_size - used_tokens - output_reserve
  - output_reserve 通常为 20% 窗口大小

- [ ] **增长趋势** — 每步 Token 增长量
  - 正常：< 500 tokens/步
  - 警告：500-1000 tokens/步
  - 危险：> 1000 tokens/步

### 2. 压缩与摘要

- [ ] **压缩触发条件** — 何时触发上下文压缩
  - 利用率 > 70% 时考虑压缩
  - 利用率 > 80% 时必须压缩

- [ ] **压缩策略选择**
  - 滑动窗口：丢弃最旧的消息
  - 层次摘要：旧消息用摘要替代
  - 选择性保留：保留关键决策，丢弃探索过程

- [ ] **压缩质量** — 压缩后关键信息是否保留
  - 任务目标是否保留
  - 关键决策是否保留
  - 工具调用结果是否保留

### 3. 引用新鲜度

- [ ] **引用来源追踪** — 记录每步引用了哪些历史步骤
  - 被引用步骤的编号
  - 引用的类型（直接引用、间接依赖）

- [ ] **过时引用检测**
  - 被引用的上下文距今 > 20 步 → 标记为 "可能过时"
  - 被引用的上下文已被压缩/摘要 → 标记为 "引用已损失精度"

- [ ] **"Lost in the Middle" 效应**
  - 检查中间位置的信息是否被正确引用
  - 如果关键信息在上下文中间但未被引用 → 可能被忽略

### 4. 连贯性监控

- [ ] **跨轮次一致性**
  - Agent 是否与之前的陈述矛盾？
  - Agent 是否重复询问已回答的问题？

- [ ] **角色稳定性**
  - 语气、风格是否保持一致？
  - 知识水平是否保持稳定？

- [ ] **任务状态追踪**
  - Agent 是否记得当前正在做什么？
  - Agent 是否知道哪些子任务已完成？

### 5. 退化指标

- [ ] **决策置信度趋势**
  - 如果连续 3+ 步的决策置信度下降 → 可能正在退化

- [ ] **工具选择准确性趋势**
  - 如果后期步骤的工具选择错误率上升 → 上下文可能已腐化

- [ ] **输出质量趋势**
  - 如果后期输出的幻觉率上升 → 模型可能在腐化的上下文上运行

## 退化检测算法

```
function detect_degradation(session):
  scores = []

  for step in session.steps:
    score = compute_step_quality(step)
    scores.append(score)

  # 检查连续下降
  if last_3_scores_decreasing(scores):
    return "POSSIBLE_DEGRADATION"

  # 检查绝对值
  if scores[-1] < 0.5:
    return "QUALITY_DROP"

  # 检查突变
  if abs(scores[-1] - scores[-2]) > 0.3:
    return "SUDDEN_CHANGE"

  return "HEALTHY"
```

## 健康评分公式

```
health_score = (
    0.3 * context_utilization_score +  # < 80% = 1.0, > 95% = 0.0
    0.2 * reference_freshness_score +   # < 10步 = 1.0, > 30步 = 0.0
    0.2 * coherence_score +             # LLM-as-Judge 评分
    0.15 * compression_quality_score +  # 压缩后信息保留度
    0.15 * decision_confidence_score    # 决策置信度均值
)
```

## 响应策略

| 健康分数 | 状态 | 响应 |
|---------|------|------|
| > 0.8 | 健康 | 正常运行 |
| 0.6 - 0.8 | 亚健康 | 增加监控频率 |
| 0.4 - 0.6 | 警告 | 触发压缩 + 重新注入任务目标 |
| < 0.4 | 危险 | 终止会话 + 通知用户 |
