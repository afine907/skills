---
name: git-branch
description: |
  【Git分支管理】智能分支管理策略，包含分支创建、合并、冲突解决、分支保护规则、Git Flow / Trunk-Based 工作流选择。

  触发时机：
  - 用户要求"创建分支"、"合并分支"、"解决冲突"
  - 需要选择合适的分支策略
  - 团队需要统一 Git 工作流

  提供策略建议和具体命令，不直接执行危险操作。
category: source-control
---

# Git Branch — Git 分支管理技能

提供智能分支管理策略、冲突解决和工作流选择。


## Goal

智能分支管理策略，包含分支创建、合并、冲突解决、分支保护规则、Git Flow / Trunk-Based 工作流选择

## Trigger

- 用户要求"创建分支"、"合并分支"、"解决冲突"
  - 需要选择合适的分支策略
  - 团队需要统一 Git 工作流

## Workflow

```
输入 → 处理 → 输出
```
## 分支策略选择

### Git Flow vs Trunk-Based

| 维度 | Git Flow | Trunk-Based |
|------|----------|-------------|
| 适用场景 | 版本发布周期长 | 持续部署 |
| 分支数量 | 多（main/develop/feature/release/hotfix） | 少（main + 短命 feature） |
| 合并频率 | 低（发布时合并） | 高（每天合并） |
| 团队规模 | 大团队、多版本并行 | 小团队、快速迭代 |
| 复杂度 | 高 | 低 |
| CI/CD | 发布时触发 | 每次提交触发 |

### 推荐选择

```
需要多版本并行维护？ ──是──▶ Git Flow
        │
        否
        ▼
需要持续部署？ ──是──▶ Trunk-Based
        │
        否
        ▼
小团队快速迭代？ ──是──▶ GitHub Flow（简化版 Git Flow）
        │
        否
        ▼
    Git Flow
```

## 分支命名规范

```
{type}/{ticket-id}-{short-description}
```

| Type | 用途 | 示例 |
|------|------|------|
| `feature` | 新功能 | `feature/PROJ-123-user-login` |
| `fix` | Bug 修复 | `fix/PROJ-456-login-crash` |
| `hotfix` | 紧急修复 | `hotfix/PROJ-789-security-patch` |
| `release` | 发布准备 | `release/v1.2.0` |
| `chore` | 杂务 | `chore/update-dependencies` |
| `docs` | 文档 | `docs/api-guide` |
| `refactor` | 重构 | `refactor/auth-module` |
| `test` | 测试 | `test/e2e-login` |

## 常用命令

### 分支操作

```bash
# 查看分支
git branch                    # 本地分支
git branch -r                 # 远程分支
git branch -a                 # 所有分支
git branch -vv                # 分支跟踪关系

# 创建分支
git checkout -b feature/PROJ-123-desc    # 创建并切换
git switch -c feature/PROJ-123-desc      # Git 2.23+ 语法

# 推送分支
git push -u origin feature/PROJ-123-desc  # 推送并设置跟踪

# 删除分支
git branch -d feature/old-branch          # 删除已合并分支
git branch -D feature/old-branch          # 强制删除
git push origin --delete feature/old-branch  # 删除远程分支
```

### 合并操作

```bash
# 合并分支（保留合并记录）
git checkout main
git merge feature/PROJ-123-desc

# 变基合并（线性历史）
git checkout feature/PROJ-123-desc
git rebase main
git checkout main
git merge feature/PROJ-123-desc

# 压缩合并（多个 commit 合为一个）
git checkout main
git merge --squash feature/PROJ-123-desc
git commit -m "feat: add user login (PROJ-123)"
```

### 合并策略选择

| 策略 | 命令 | 适用场景 |
|------|------|----------|
| 普通合并 | `git merge` | 保留完整历史 |
| 变基 | `git rebase` | 线性历史，个人分支 |
| 压缩合并 | `git merge --squash` | 功能分支合入主线 |

## 冲突解决

### 冲突类型

| 类型 | 标记 | 处理方式 |
|------|------|----------|
| 内容冲突 | `<<<<<<<` / `=======` / `>>>>>>>` | 手动编辑选择 |
| 删除冲突 | `deleted by us/them` | 决定保留还是删除 |
| 重命名冲突 | 两个分支重命名同一文件 | 选择最终名称 |

### 解决步骤

```bash
# 1. 查看冲突文件
git status

# 2. 编辑冲突文件，选择内容
# 删除标记行，保留正确内容

# 3. 标记为已解决
git add <conflicted-file>

# 4. 继续合并/rebase
git merge --continue    # 合并时
git rebase --continue   # 变基时

# 5. 或者放弃
git merge --abort       # 放弃合并
git rebase --abort      # 放弃变基
```

### 冲突预防

1. **频繁同步** — `git pull --rebase` 保持本地最新
2. **小步提交** — 每次只改一个功能点
3. **模块化** — 减少多人同时修改同一文件
4. **沟通协调** — 修改公共模块前通知团队

## 分支保护规则

### 推荐的 main 分支保护

```yaml
# GitHub Branch Protection
protection_rules:
  main:
    required_reviews: 2           # 至少 2 人 review
    dismiss_stale_reviews: true   # 新提交后重新 review
    require_status_checks: true   # 必须通过 CI
    enforce_admins: true          # 管理员也受限
    restrict_pushes: true         # 只能通过 PR 合入
    require_linear_history: true  # 要求线性历史
```

## 快速使用

```
# 选择分支策略
我们团队应该怎么选择 Git 分支策略？

# 创建功能分支
帮我创建一个用户登录功能的分支

# 解决合并冲突
帮我解决这个合并冲突：[粘贴冲突内容]

# 制定分支规范
帮我制定团队的 Git 分支命名规范

# 审查分支状态
检查当前分支状态，是否有未合并的分支
```

## 参考资料

- Git Flow 详解: [references/git-flow.md](references/git-flow.md)
- 冲突解决实战: [references/conflict-resolution.md](references/conflict-resolution.md)
