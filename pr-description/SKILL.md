---
name: pr-description
category: source-control
description: |
  Analyze git diff and generate structured PR description. Integrates with GitHub CLI for PR creation.
  Use when:
  - User says "帮我写 PR 描述"、"提 PR"、"create PR"
  - User has pushed a branch and wants a PR description
  - User provides a git diff and wants it summarized

  Do NOT use: when user wants code review (use wo-yao-yan-pai) or commit messages (use commit).
---

# PR Description — Pull Request 描述生成 Agent

git diff + branch context → 结构化 PR 描述 → 可选通过 gh CLI 创建 PR。

## 工作流程

```
获取 diff → 分析变更 → 生成结构化描述 → 输出/创建 PR
```

## Step 1: 获取变更信息

```bash
# 获取当前分支名
git rev-parse --abbrev-ref HEAD

# 获取与目标分支的 diff（自动检测 main/master）
git diff origin/main...HEAD --stat
git diff origin/main...HEAD

# 如果 main 不存在则用 master
git diff origin/master...HEAD --stat
git diff origin/master...HEAD

# 获取近期提交信息
git log origin/main...HEAD --oneline
```

**如果参数中提供了特定分支**：用指定分支替代自动检测。

**如果不在 git 仓库或没有远程分支**：提示用户提供 diff 文本。

## Step 2: 分析变更

按以下维度分析：

### 变更分类

| 类型 | 特征 |
|------|------|
| 新功能 | 新增文件、新模块、新 API |
| Bug 修复 | 修复边界条件、异常处理、逻辑修正 |
| 重构 | 重命名、提取函数、调整结构 |
| 依赖更新 | package.json、requirements.txt 等 |
| 配置变更 | 配置文件、环境变量 |
| 文档/测试 | .md 文件、测试用例 |

### 变更影响分析

- **影响范围**：修改了哪些模块、API 接口是否变化
- **破坏性变更**：是否改接口签名、删字段、改配置格式
- **数据变更**：是否涉及数据库 schema、缓存 key 等

## Step 3: 生成 PR 描述

按以下模板输出：

```markdown
## Summary

<用 2-3 句话概括 PR 目的和变更要点>

## Changes

### <模块/功能 1>
- <具体变更，每点一行>
- ...

### <模块/功能 2>
- <具体变更>
- ...

## Breaking Changes

<如果有破坏性变更，列出迁移说明；如果没有则写 "None">

## Test Plan

- [ ] <验证步骤 1>
- [ ] <验证步骤 2>
- [ ] 现有测试通过：`<测试命令>`
```

### 编写规则

**DO**:
- ✅ 摘要简明扼要，让 reviewer 30 秒内理解 PR 目的
- ✅ Changes 按模块分组，而非按文件分组
- ✅ Test Plan 可执行，包含具体命令
- ✅ 标注 Breaking Change 及其迁移路径
- ✅ 如果 diff 有相关 issue 号，在 footer 引用

**DON'T**:
- ❌ 逐文件罗列（Changes 已按模块归组）
- ❌ 写 "fix bug" 这类模糊描述
- ❌ 遗漏 Test Plan
- ❌ 隐藏 Breaking Change

## Step 4: 创建 PR（可选）

如果用户确认且安装了 `gh` CLI：

```bash
# 先检查 gh CLI 和认证状态
gh --version && gh auth status

# 确保分支已推送到远程
git push -u origin HEAD

# 创建 PR
gh pr create --title "<短标题>" --body "<pr-body>"
```

**注意**：`git push` 必须在 `gh pr create` 之前执行，否则 GitHub 无法为不存在的远程分支创建 PR。

**提示用户确认后再执行创建操作**。

## Edge Cases

### 空 diff / 没有变更
```
当前分支相对目标分支没有变更。
请确保已提交更改并推送到远程。
```

### 首次提交 / 无目标分支
```
没有检测到 main/master 分支。是首次提交还是用的其他默认分支？
请指定目标分支。
```

### 超大 diff（>1000 行）
```
diff 较大，建议：
1. 考虑拆分为多个 PR 分别处理
2. 只生成 summary 和 changes 概览，不逐行描述
```

### 没有安装 gh CLI
提示用户安装或手动复制 PR 描述到 GitHub。

### gh CLI 未认证
```bash
gh auth login
# 认证完成后重新执行创建操作
```
