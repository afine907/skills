---
name: commit-diff-analyzer
description: |
  Analyze code changes between two git commits with structured diff output. Trigger: user says "对比 commit"、"compare commits"、"查看两个提交的差异".
category: source-control
---

# Commit Diff Analyzer

## Goal

Analyze code changes between two git commits, presenting commit metadata, change summaries, and detailed diffs in a structured format for easy review.

## Trigger

- User says "对比 commit"、"compare commits"、"查看两个提交的差异"
- User provides two commit IDs and wants to see what changed

## 工作流程

### Step 1: 验证提交 (Validate)

检查两个 commit ID 是否存在：
```bash
git cat-file -t <commit-id>   # 返回 "commit" 表示有效
```
如果任一 commit 无效，报告错误并建议运行 `git log --oneline -20` 查看最近提交。

### Step 2: 确定时间顺序 (Determine Order)

比较两个提交的时间，确定哪个较旧、哪个较新：
```bash
git log -1 --format="%at" <commit-a>   # 获取时间戳
git log -1 --format="%at" <commit-b>
```
始终使用 `older..newer` 的顺序进行 diff。

### Step 3: 范围检查 (Scope Check)

先运行 `--stat` 了解变更规模，根据规模决定输出策略：

```bash
git diff --stat <older>..<newer>
```

**分支决策**：
- **<= 20 文件**：显示完整 diff
- **> 20 文件**：先显示统计摘要，询问用户是否需要过滤特定路径或查看特定文件的 diff

### Step 4: 收集元数据 (Collect Metadata)

获取两个提交的详细信息：
```bash
git log -1 --format="Hash: %H%nAuthor: %an <%ae>%nDate: %ad%nMessage: %s" <commit>
```

### Step 5: 分析变更 (Analyze)

执行完整 diff 并按文件类型分组：
```bash
# 完整 diff
git diff <older>..<newer>

# 仅文件列表（按状态分组）
git diff --name-status <older>..<newer>
```

将文件分为三类：Modified（修改）、Added（新增）、Deleted（删除）。

### Step 6: 汇总统计 (Summarize)

```bash
git diff --shortstat <older>..<newer>
```

### Step 7: 呈现结果 (Present)

使用下方输出模板组织所有信息。

## 决策表

### Diff 显示模式选择

| 场景 | 推荐模式 | 命令 | 原因 |
|------|----------|------|------|
| <= 20 文件变更 | 完整 diff | `git diff` | 内容可控，完整审查 |
| > 20 文件变更 | 统计摘要 | `git diff --stat` | 避免信息过载 |
| 只需知道改了哪些文件 | 文件名列表 | `git diff --name-only` | 快速概览 |
| 审查特定文件 | 路径过滤 | `git diff -- src/auth.js` | 聚焦关键文件 |

### Commit ID 格式解析

| 输入格式 | 示例 | 解析方式 |
|----------|------|----------|
| 完整 SHA | `abc123def456789...` | 直接使用 |
| 短 SHA（>=7位） | `abc123d` | git 自动解析 |
| 分支名 | `main`、`feature/login` | 解析为分支最新提交 |
| HEAD 引用 | `HEAD~3`、`HEAD^` | 相对于当前 HEAD 偏移 |
| 标签 | `v1.2.0` | 解析为标签指向的提交 |

### 输出格式选择

| 文件类型 | 显示方式 | 原因 |
|----------|----------|------|
| 代码文件（.js/.ts/.py） | 内行 diff（inline） | 需要审查具体代码改动 |
| 配置文件（.json/.yaml） | 内行 diff | 需要确认配置变更 |
| 二进制文件 | 仅显示"Binary files changed" | 无法展示内容差异 |
| 锁文件（package-lock.json） | 仅显示统计 | 内容不具可读性 |

## 关键命令

```bash
# 验证提交存在
git cat-file -t <commit-id>

# 获取完整提交信息
git log -1 --format="Hash: %H%nAuthor: %an%nDate: %ad%nMessage: %s%n" <commit-id>

# 时间顺序 diff (older..newer)
git diff <older-commit>..<newer-commit>

# Diff 统计
git diff --stat <older-commit>..<newer-commit>

# 文件名列表
git diff --name-only <older-commit>..<newer-commit>

# 文件名+状态
git diff --name-status <older-commit>..<newer-commit>
```

## Edge Cases

1. **Invalid commit IDs**：如果 `git cat-file -t` 返回错误，报告"commit ID 不存在"，并建议运行 `git log --oneline -20` 查看最近提交。
2. **Same commit**：如果两个 ID 解析为相同提交，通知用户"两个 commit ID 指向同一提交，无差异"。
3. **Non-git directory**：如果当前目录不是 git 仓库，报告错误"此技能仅适用于 git 仓库"。
4. **Reverse order**：自动检测时间顺序并调整 diff 方向，无需用户手动排序。
5. **Diff 过大（> 20 文件）**：先显示统计摘要，然后询问用户是否需要过滤路径：`git diff --stat older..newer -- src/`。
6. **Binary files in diff**：二进制文件无法显示行级 diff，报告"Binary files changed"并列出受影响的文件。
7. **Merge commits**：如果提交是 merge commit（有多个父提交），提示用户选择与哪个父提交比较：`git diff <merge-commit>^1..<merge-commit>` 或 `git diff <merge-commit>^2..<merge-commit>`。

## 输出模板

```markdown
## Commit 对比分析

### Commit A（较旧）
- **Hash**: {full-hash}
- **Author**: {author-name} <{author-email}>
- **Date**: {date}
- **Message**: {commit-message}

### Commit B（较新）
- **Hash**: {full-hash}
- **Author**: {author-name} <{author-email}>
- **Date**: {date}
- **Message**: {commit-message}

### 变更统计
- {n} files changed, {insertions} insertions(+), {deletions} deletions(-)

### 文件分类

| 状态 | 文件 | 变更行数 |
|------|------|----------|
| Modified | {file-path} | +{n} -{m} |
| Added | {file-path} | +{n} |
| Deleted | {file-path} | -{n} |

### 详细 Diff

#### {file-path}
\`\`\`diff
{diff-content}
\`\`\`
```

## Commit ID 格式

接受多种格式：
- Full SHA: `abc123def456...`
- Short SHA: `abc123d` (at least 7 chars)
- Branch names (if they point to commits)
- HEAD references like `HEAD~5`
- Tags like `v1.2.0`

## 不适用

| 场景 | 原因 | 推荐工具 |
|------|------|----------|
| 对比 PR 变更 | 应使用 PR 视图查看 | `gh pr diff <pr-number>` 或 GitHub PR 页面 |
| 可视化 diff 需求 | 需要图形化对比 | `git difftool` + Meld/Beyond Compare |
| 对比两个分支 | 应使用分支 diff 命令 | `git diff branch1..branch2` |
| 需要逐行溯源 | 应使用 blame 功能 | `git blame <file>` |
| 需要查看文件历史 | 应使用 log 功能 | `git log --follow -p <file>` |

**重定向**：
- PR 审查：使用 `gh pr diff` 或 GitHub/GitLab 的 PR Diff 视图。
- 可视化对比：使用 `git difftool` 配合外部 diff 工具。
