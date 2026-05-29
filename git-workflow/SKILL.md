---
name: git-workflow
description: |
  【Git工作流】一键完成 Git 工作流：分支→暂存→commit→push→PR。
  触发时机：用户说"帮我提PR"、"提交代码"、"git flow"。
  智能判断 git 状态，自动执行需要的步骤。
category: source-control
---

# Git Workflow — 一键 Git 工作流

自动化 Git 工作流：分支 → 暂存 → commit → push → PR。

## Goal

一键完成 Git 工作流：智能判断状态 → 创建分支 → 暂存 → commit → push → PR。

## Trigger

用户说出以下任一关键词时触发：
- 帮我提 PR、提交代码、推一下
- 创建分支然后提交、git flow
- 提交并推送、一键提交
- 发 PR、开 PR

## 工作流程

```
智能判断 git 状态 → 执行需要的步骤 → 完成
```

### Step 1: 智能判断当前状态

```bash
# 检查是否在 git 仓库
git rev-parse --is-inside-work-tree

# 获取当前分支
git rev-parse --abbrev-ref HEAD

# 检查工作区状态
git status --porcelain

# 检查暂存区
git diff --staged --name-only

# 检查未提交的变更
git diff --name-only

# 检查是否有未推送的 commit
git log origin/main..HEAD --oneline 2>/dev/null || git log origin/master..HEAD --oneline 2>/dev/null
```

**根据状态决定执行步骤**：

| 当前状态 | 执行步骤 |
|----------|----------|
| 在 main/master 分支，有未暂存变更 | 1. 创建分支 → 2. 暂存 → 3. commit → 4. push → 5. PR |
| 在 feature 分支，有未暂存变更 | 2. 暂存 → 3. commit → 4. push → 5. PR |
| 在 feature 分支，有未提交 commit | 4. push → 5. PR |
| 在 main/master 分支，无变更 | 1. 创建分支（等用户描述需求） |
| 已推送，无新 commit | 无操作，提示"已是最新的" |

### Step 2: 创建/切换分支（如需要）

**分支命名规则**（Conventional Commits 前缀）：

| 需求类型 | 前缀 | 示例 |
|----------|------|------|
| 新功能 | `feat/` | `feat/user-auth` |
| Bug 修复 | `fix/` | `fix/login-error` |
| 重构 | `refactor/` | `refactor/api-layer` |
| 文档 | `docs/` | `docs/api-guide` |
| 测试 | `test/` | `test/auth-cases` |
| 构建/CI | `chore/` | `chore/ci-config` |

**自动推断逻辑**：
- 用户描述中包含"修复"、"bug"、"fix" → `fix/xxx`
- 用户描述中包含"新增"、"添加"、"feat" → `feat/xxx`
- 其他情况 → 根据变更内容推断

**执行命令**：
```bash
# 创建并切换到新分支
git checkout -b <type>/<short-description>

# 或者切换到已存在的分支
git checkout <branch-name>
```

**分支名清理规则**：
- 只保留字母、数字、连字符
- 长度 ≤ 40 字符
- 全小写
- 连字符代替空格和特殊字符

### Step 3: 暂存文件（如需要）

```bash
# 检查是否有未暂存的变更
git status --porcelain

# 如果有变更，询问用户或自动暂存
# 选项 A: 暂存所有变更
git add .

# 选项 B: 暂存特定文件（根据变更内容智能推荐）
git add <file1> <file2> ...
```

**智能暂存策略**：
- 如果用户明确说"提交所有" → `git add .`
- 如果变更涉及多个不相关模块 → 提示用户确认
- 如果只有少量相关文件 → 自动暂存

### Step 4: 生成 Commit（复用 /commit 技能）

调用 `/commit` 技能生成语义化 commit message：

```bash
# 分析暂存的变更
git diff --staged
git diff --staged --stat

# 生成 commit message（Conventional Commits 格式）
# <type>(<scope>): <subject>
```

**commit message 规范**：
- 祈使语气："add" 不是 "added"
- 主题不超过 50 字符
- 不以句号结尾
- 复杂变更添加 body 说明

### Step 5: 推送到远程（如需要）

```bash
# 首次推送新分支
git push -u origin <branch-name>

# 后续推送
git push origin <branch-name>
```

### Step 6: 创建 PR（复用 /pr-description 技能）

调用 `/pr-description` 技能生成 PR 描述并创建 PR：

```bash
# 检查 gh CLI
gh --version && gh auth status

# 生成 PR 描述（自动分析 diff）
# 创建 PR
gh pr create --title "<title>" --body "<body>"
```

**PR 标题格式**：
```
<type>(<scope>): <简短描述>
```

**PR 描述模板**：
```markdown
## Summary
<2-3 句话概括 PR 目的>

## Changes
### <模块 1>
- <具体变更>

## Breaking Changes
<如有>

## Test Plan
- [ ] <验证步骤>
```

## 输出格式

执行完成后，输出执行摘要：

```markdown
## Git 工作流完成

**分支**: `feat/user-auth` (从 main 创建)
**Commit**: `feat(auth): add JWT authentication` (abc1234)
**PR**: #42 - feat(auth): add JWT authentication
**链接**: https://github.com/user/repo/pull/42
```

## 边界情况

### 没有变更
```
当前没有待提交的变更。
请先修改文件，然后告诉我你想提交什么。
```

### 分支已存在
```
分支 feat/xxx 已存在，已切换到该分支。
```

### push 失败（远程有新 commit）
```
远程分支有新 commit，需要先拉取：
git pull --rebase origin <branch>
```

### gh CLI 未安装
```
未检测到 gh CLI。
PR 描述已生成，请手动复制到 GitHub 创建 PR。
```

### PR 创建失败
```
PR 创建失败，可能是：
1. 分支已存在 PR
2. 远程仓库权限不足
请检查 gh auth status 或手动创建。
```

## 最佳实践

**DO**:
- ✅ 智能判断当前状态，只执行必要的步骤
- ✅ 复用 /commit 和 /pr-description 技能
- ✅ 分支命名遵循 Conventional Commits 规范
- ✅ PR 描述清晰，包含变更摘要和测试计划
- ✅ 每步执行后验证结果

**DON'T**:
- ❌ 在 main/master 分支直接提交
- ❌ 跳过暂存直接 commit
- ❌ 强制 push（除非用户明确要求）
- ❌ 忽略 pre-commit hooks
