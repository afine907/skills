---
name: agent-security
description: |
  【Agent 安全】AI Agent 安全模式。覆盖 Prompt Injection 防御、权限分层设计、HITL 门禁、数据泄露防护和 Agent 威胁建模。

  触发时机：
  - 用户说"agent 安全"、"prompt injection"、"agent 权限"、"HITL"、"agent threat model"
  - 为 Agent 系统设计安全控制
  - 审查 Agent 代码中的安全漏洞
  - 实现权限分层和人机协作门禁

  不适用：通用代码安全审查（用 wo-yao-yan-pai）、Shell 命令安全（用 shell-command）、CI/CD 安全（用 ci-workflow）。
category: quality
---

# Agent Security — AI Agent 安全框架

AI Agent 专用的安全设计模式，应对 Agent 系统特有的威胁面。

> **核心洞察：** 拥有生产级权限的 AI Agent，从安全角度看是一个高权限进程。它可以被 Prompt Injection 操纵，执行非预期操作。这不是模型问题，是系统设计问题。

## 工作流程

```
威胁建模 → 分类权限 → 设计 HITL 门禁 → 实现防御 → 审计测试
```

## Step 1: Agent 威胁模型

Agent 系统面临 6 类特有威胁：

### 威胁分类

| 威胁 | 描述 | 风险等级 | 缓解措施 |
|------|------|---------|---------|
| **Prompt Injection（直接）** | 用户直接在输入中注入恶意指令 | Critical | 输入消毒 + 指令层级 |
| **Prompt Injection（间接）** | 通过工具返回的数据注入恶意指令 | Critical | 工具输出消毒 + 上下文隔离 |
| **工具滥用** | Agent 被操纵调用危险工具 | Critical | 权限分层 + HITL 门禁 |
| **数据泄露** | Agent 通过输出泄露敏感信息 | High | 输出过滤 + PII 检测 |
| **上下文投毒** | 通过对抗输入腐化 Agent 状态 | High | 上下文隔离 + 完整性校验 |
| **资源耗尽** | 无限循环或过度调用导致成本失控 | High | 断路器 + 成本上限 |

### 威胁分析模板

```
对每个 Agent 功能:
  1. 识别输入源（用户输入、工具返回、外部数据）
  2. 评估每个输入源的可信度
  3. 识别 Agent 可执行的操作（只读、写入、危险）
  4. 评估每个操作的爆炸半径
  5. 确定所需的安全控制级别
```

> 详细威胁目录见 [references/threat-catalog.md](references/threat-catalog.md)

## Step 2: 权限分层设计

基于操作风险的 4 级权限模型：

### 权限层级定义

| 层级 | 名称 | 定义 | 示例 | 控制方式 |
|------|------|------|------|---------|
| **Tier 0** | 自治 | 只读操作，无副作用 | 搜索、查询、读取文件 | 自动执行 |
| **Tier 1** | 确认 | 可逆的写入操作 | 创建分支、写临时文件、更新草稿 | 用户确认 |
| **Tier 2** | 审批 | 不可逆或高影响操作 | 发送邮件、发布内容、删除数据 | 显式审批 + 上下文展示 |
| **Tier 3** | 拒绝 | 危险操作，不应自动化 | 执行任意代码、修改权限、访问密钥 | 硬性拒绝 |

### 工具→权限映射

```json
{
  "search_api": {"tier": 0, "reason": "只读查询"},
  "create_draft": {"tier": 1, "reason": "可逆写入"},
  "send_email": {"tier": 2, "reason": "不可逆，影响外部"},
  "execute_code": {"tier": 3, "reason": "安全风险"},
  "read_file": {"tier": 0, "reason": "只读"},
  "delete_file": {"tier": 2, "reason": "不可逆"},
  "update_config": {"tier": 2, "reason": "影响系统行为"}
}
```

### 权限设计原则

1. **默认拒绝** — 未知工具默认 Tier 3（拒绝），除非明确配置
2. **最小权限** — 每个 Agent 只获得完成任务所需的最小权限集
3. **独立角色** — 每个 Agent 使用独立的 IAM 角色，权限不堆叠
4. **定期审计** — 定期审查权限使用情况，收回不再需要的权限

> 权限映射模板见 [references/permission-matrix.md](references/permission-matrix.md)

## Step 3: HITL 门禁设计

Human-in-the-Loop 门禁是 Agent 安全的最后防线。

### 门禁模式

| 模式 | 触发条件 | 用户体验 | 适用场景 |
|------|---------|---------|---------|
| **检查点门禁** | 每 N 步自动触发 | 展示摘要，用户确认继续 | 长任务 |
| **审批门禁** | Tier 1/2 操作前 | 展示操作详情，用户批准/拒绝 | 写入操作 |
| **审查门禁** | 任务完成时 | 展示所有操作记录，用户审查 | 高风险任务 |
| **升级门禁** | Agent 置信度低时 | 自动请求人工介入 | 不确定场景 |
| **超时门禁** | 等待用户响应超时 | 自动执行低风险操作 / 保持等待高风险 | 低延迟场景 |

### 门禁实现

```python
class HITLGate:
    def check(self, action: Action, context: Context) -> Decision:
        tier = self.get_permission_tier(action.tool)

        if tier == Tier.AUTONOMOUS:
            return Decision.ALLOW

        if tier == Tier.CONFIRM:
            return self.request_confirmation(action, context)

        if tier == Tier.APPROVE:
            return self.request_approval(action, context)

        if tier == Tier.DENY:
            return Decision.DENY

    def request_confirmation(self, action, context):
        # 展示操作摘要，等待用户确认
        summary = f"即将执行：{action.tool}({action.params})"
        user_response = prompt_user(summary)
        return Decision.ALLOW if user_response == "confirm" else Decision.DENY

    def request_approval(self, action, context):
        # 展示完整操作详情和上下文，等待用户审批
        details = format_action_details(action, context)
        user_response = prompt_user(details)
        return Decision.ALLOW if user_response == "approve" else Decision.DENY
```

> HITL 实现模式见 [references/hitl-patterns.md](references/hitl-patterns.md)

## Step 4: Prompt Injection 防御

### 防御层级

```
用户输入 → [层1] 输入消毒 → [层2] 指令层级 → [层3] 上下文隔离 → [层4] 输出验证 → 安全输出
```

**层 1：输入消毒**
- 检测已知的注入模式（"忽略之前的指令"、"你现在是..."）
- 对工具返回的数据做消毒（可能包含注入内容）
- 标记用户输入为不可信数据

**层 2：指令层级**
- 系统提示 > 工具定义 > 上下文 > 用户输入（可信度递减）
- 在系统提示中明确声明：用户输入中的指令不应被执行
- 使用分隔符清晰区分指令和数据

**层 3：上下文隔离**
- 用户输入和系统指令使用不同的消息角色
- 工具返回数据用特殊标签包裹
- 不同来源的数据不混合在同一上下文块中

**层 4：输出验证**
- 检查输出是否泄露了系统提示内容
- 检查输出是否包含用户未请求的敏感信息
- 检查输出是否试图执行未授权操作

> Prompt Injection 防御模式见 [references/injection-defenses.md](references/injection-defenses.md)

## Step 5: 数据保护模式

### PII 检测与过滤

```
对 Agent 的所有输出:
  if 检测到 PII（邮箱、电话、身份证号、银行卡号）:
    if 输出是面向用户的:
      脱敏处理（替换为 ***）
    if 输出是面向系统的:
      记录告警 + 阻止输出
```

### 数据流控制

```
数据分类:
  公开数据 → 可自由流动
  内部数据 → 仅限内部系统间流动
  敏感数据 → 需要审批才能流动
  机密数据 → 禁止通过 Agent 流动

对每次数据流动:
  1. 检查数据分类标签
  2. 检查目标是否在允许列表中
  3. 记录数据流动日志（审计用）
```

## Step 6: 安全审计清单

### 部署前安全审查

- [ ] **威胁建模** — 已识别所有输入源和操作的风险
- [ ] **权限分层** — 所有工具已分配到正确的权限层级
- [ ] **HITL 门禁** — Tier 1/2 操作已配置门禁
- [ ] **注入防御** — 4 层防御已实现
- [ ] **数据保护** — PII 检测已启用，数据流控制已配置
- [ ] **断路器** — 循环检测和成本上限已启用
- [ ] **日志审计** — 所有操作已记录，支持事后审查
- [ ] **回滚能力** — 关键操作支持回滚
- [ ] **最小权限** — Agent 使用最小权限 IAM 角色
- [ ] **红队测试** — 已用已知攻击模式测试

> 完整审计清单见 [references/audit-checklist.md](references/audit-checklist.md)

## 快速使用

```
用户：我正在构建一个能发送邮件和修改数据库的 Agent，需要确保安全
助手：使用 /agent-security 进行威胁建模、设计权限分层、配置 HITL 门禁、实现注入防御
```

## 边界情况

- **多租户 Agent** — 不同租户的数据需要严格隔离，Agent 不能跨租户访问
- **有文件系统访问权的 Agent** — 需要路径沙箱，防止路径穿越
- **能生成并执行代码的 Agent** — 最高风险，需要沙箱执行环境
- **长时间运行的 Agent** — 权限可能在运行期间发生变化，需要定期重新验证

## 与其他技能的协作

- `tool-use-patterns` — 安全是工具集成的关键维度
- `agent-eval` — 安全测试用例是评估的子集
- `shell-command` — 复用 safe/confirm/reject 分级模式
- `task-loom` — 复用风险分类（P0/P1/P2）到安全威胁
- `wo-yao-yan-pai` — 安全发现进入代码审查修复流程
