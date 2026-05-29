# HITL 门禁实现模式

## 模式 1：检查点门禁

**触发：** 每 N 步自动触发

```python
class CheckpointGate:
    def __init__(self, interval=5):
        self.step_count = 0
        self.interval = interval

    def check(self, step_result):
        self.step_count += 1
        if self.step_count % self.interval == 0:
            summary = self.build_summary()
            user_response = prompt_user(
                f"已完成 {self.step_count} 步。\n"
                f"当前状态：{summary}\n"
                f"继续执行？(yes/no/modify)"
            )
            if user_response == "no":
                return Action.STOP
            if user_response == "modify":
                return Action.ALLOW_MODIFY
        return Action.CONTINUE
```

**适用场景：** 长任务、多步骤工作流、需要用户确认方向的场景

## 模式 2：审批门禁

**触发：** Tier 1/2 操作前

```python
class ApprovalGate:
    def check(self, action: Action):
        tier = self.get_tier(action.tool)

        if tier == Tier.CONFIRM:
            # 简单确认：展示操作摘要
            return prompt_user(
                f"即将执行：{action.tool}\n"
                f"参数：{action.params}\n"
                f"确认？(yes/no)"
            )

        if tier == Tier.APPROVE:
            # 详细审批：展示完整上下文
            return prompt_user(
                f"⚠️ 不可逆操作\n"
                f"工具：{action.tool}\n"
                f"参数：{action.params}\n"
                f"影响范围：{action.impact_scope}\n"
                f"回滚方案：{action.rollback_plan}\n"
                f"批准？(approve/reject)"
            )
```

**适用场景：** 写入操作、发送消息、删除数据

## 模式 3：审查门禁

**触发：** 任务完成时

```python
class ReviewGate:
    def review(self, session: Session):
        # 展示所有操作记录
        report = {
            "total_steps": len(session.steps),
            "tools_used": session.get_tool_summary(),
            "total_cost": session.get_cost(),
            "operations": [
                {
                    "step": i,
                    "tool": step.tool,
                    "params": step.params,
                    "result": "success" if step.success else "failed",
                    "reversible": step.is_reversible
                }
                for i, step in enumerate(session.steps)
            ]
        }

        user_response = prompt_user(
            f"任务完成。操作摘要：\n"
            f"{format_report(report)}\n\n"
            f"确认提交？(approve/reject/undo_last)"
        )

        if user_response == "reject":
            session.rollback_all()
        if user_response == "undo_last":
            session.rollback_last()
```

**适用场景：** 高风险任务、需要事后审计的场景

## 模式 4：升级门禁

**触发：** Agent 置信度低时

```python
class EscalationGate:
    CONFIDENCE_THRESHOLD = 0.7

    def check(self, decision: Decision):
        if decision.confidence < self.CONFIDENCE_THRESHOLD:
            user_response = prompt_user(
                f"Agent 不确定如何处理：\n"
                f"情况：{decision.context}\n"
                f"选项：{decision.options}\n"
                f"Agent 倾向：{decision.preference} (置信度: {decision.confidence})\n\n"
                f"请选择：(1/2/3/custom)"
            )
            return user_response
        return decision.preference
```

**适用场景：** 不确定场景、模糊输入、多义性决策

## 模式 5：超时门禁

**触发：** 等待用户响应超时

```python
class TimeoutGate:
    TIMEOUT_SECONDS = 300  # 5 分钟

    def check(self, action: Action, timeout=TIMEOUT_SECONDS):
        tier = self.get_tier(action.tool)

        # 低风险操作：超时后自动执行
        if tier == Tier.CONFIRM:
            user_response = prompt_user_with_timeout(
                f"即将执行：{action.tool}，{timeout}秒后自动执行",
                timeout=timeout,
                default="yes"
            )
            return user_response

        # 高风险操作：超时后保持等待
        if tier == Tier.APPROVE:
            user_response = prompt_user_with_timeout(
                f"需要审批：{action.tool}，等待响应...",
                timeout=timeout,
                default="hold"
            )
            if user_response == "hold":
                return Action.HOLD  # 保持等待，不执行
            return user_response
```

## 门禁组合策略

```
Agent 执行流程:
  步骤 1-4: 自动执行（Tier 0 操作）
  步骤 5: 审批门禁（Tier 1 操作）
  步骤 6-9: 自动执行
  步骤 10: 检查点门禁（每 5 步）
  步骤 11: 升级门禁（置信度低）
  步骤 12: 审批门禁（Tier 2 操作）
  步骤 13-15: 自动执行
  完成: 审查门禁（展示所有操作记录）
```
