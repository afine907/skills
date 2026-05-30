# 工具权限映射模板

## 权限映射表

| 工具类别 | 工具示例 | 默认层级 | 理由 | 可配置 |
|---------|---------|---------|------|--------|
| **信息查询** | search, lookup, query | Tier 0 (自治) | 只读，无副作用 | 否 |
| **文件读取** | read_file, list_dir | Tier 0 (自治) | 只读 | 否 |
| **草稿创建** | create_draft, save_temp | Tier 1 (确认) | 可逆写入 | 是 |
| **数据更新** | update_record, edit_file | Tier 1 (确认) | 可逆写入 | 是 |
| **消息发送** | send_email, post_message | Tier 2 (审批) | 不可逆，影响外部 | 否 |
| **内容发布** | publish, deploy | Tier 2 (审批) | 不可逆，公开可见 | 否 |
| **数据删除** | delete_record, rm_file | Tier 2 (审批) | 不可逆 | 否 |
| **配置修改** | update_config, change_perm | Tier 2 (审批) | 影响系统行为 | 否 |
| **代码执行** | execute_code, run_script | Tier 3 (拒绝) | 安全风险极高 | 否 |
| **密钥访问** | read_secret, get_token | Tier 3 (拒绝) | 安全风险极高 | 否 |
| **权限修改** | grant_permission, add_role | Tier 3 (拒绝) | 安全风险极高 | 否 |

## 权限配置文件格式

```json
{
  "agent_id": "customer-support-agent",
  "version": "1.0",
  "default_tier": "deny",
  "permissions": {
    "search_faq": {
      "tier": 0,
      "reason": "只读查询FAQ"
    },
    "create_ticket": {
      "tier": 1,
      "reason": "创建工单，可取消",
      "confirmation_message": "将为您创建工单，确认？"
    },
    "send_email": {
      "tier": 2,
      "reason": "发送邮件不可逆",
      "approval_context": ["recipient", "subject", "body_preview"]
    },
    "execute_code": {
      "tier": 3,
      "reason": "安全风险，禁止自动执行"
    }
  },
  "rate_limits": {
    "max_tool_calls_per_session": 50,
    "max_tool_calls_per_minute": 10,
    "max_cost_per_session_usd": 1.0
  },
  "iam_role": "arn:aws:iam::123456789:role/customer-support-agent"
}
```

## 权限继承与组合

### 禁止权限堆叠

```
错误模式：
  Agent A 使用 Role-1（权限：read, write）
  Agent B 使用 Role-2（权限：read, execute）
  Agent C 使用 Role-1 + Role-2（权限：read, write, execute）← 权限爆炸

正确模式：
  每个 Agent 使用独立角色，权限不组合
  Agent A → Role-A（权限：read, write）
  Agent B → Role-B（权限：read, execute）
  Agent C → Role-C（权限：仅 Agent C 需要的权限）
```

### 权限变更流程

```
权限变更请求
  → 评估变更的影响范围
  → 确认最小权限原则
  → 更新权限配置文件
  → 运行安全测试
  → 部署到灰度环境
  → 验证后全量部署
```
