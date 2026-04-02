# Commit Skill

智能 Git Commit 生成器 - 分析暂存区变更并自动生成符合规范的 commit message。

## 快速开始

```bash
# 查看暂存区变更
git add <files>

# 使用技能生成 commit
/commit
```

## 功能特性

- ✅ 自动分析 `git diff --staged` 变更内容
- ✅ 生成语义化 Commit Message (feat/fix/refactor/docs/style/test/chore)
- ✅ 自动识别影响范围 (scope)
- ✅ 支持多文件变更聚合
- ✅ 遵循 Conventional Commits 规范
- ✅ 自动添加 Co-Authored-By 标注

## 命令

| 命令 | 说明 |
|------|------|
| `/commit` | 分析暂存变更并生成 commit |
| `/commit -m "msg"` | 使用自定义消息提交 |
| `/commit --amend` | 修改上一次提交 |
| `/commit --dry-run` | 预览 commit message（不提交） |

## 示例

### 新功能

```bash
/commit
# 生成: feat(auth): add JWT token refresh mechanism
```

### Bug 修复

```bash
/commit
# 生成: fix(payment): handle duplicate callback correctly
```

### 重构

```bash
/commit
# 生成: refactor(utils): extract date formatting utilities
```

## 工作流程

1. **预检查** - 确认是否在 git 仓库中，是否有暂存变更
2. **分析变更** - 运行 `git diff --staged` 分析代码变更
3. **生成消息** - 根据变更类型和范围生成 commit message
4. **执行提交** - 运行 `git commit` 完成提交

## 安装

此技能位于 `/d/Code/skills/commit` 目录，可直接通过 `/commit` 命令使用。
