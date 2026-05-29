---
name: changelog-generator
category: source-control
description: |
  Analyze git tag/commit range and generate CHANGELOG.md in Keep a Changelog format.
---

# Changelog Generator — CHANGELOG.md 生成 Agent

git 标签/提交范围 → 按语义分组的 CHANGELOG.md。


## Goal

Analyze git tag/commit range and generate CHANGELOG.md in Keep a Changelog format.

## Trigger

- User says "生成 changelog"、"更新 CHANGELOG"、"generate changelog"
  - Before a release, needs to document changes since last tag
  - User provides a commit range

## 工作流程

```
获取标签 → 分析 commit 范围 → 语义分组 → 生成 CHANGELOG
```

## Step 1: 获取版本历史

```bash
# 查看所有标签（按版本排序）
git tag --sort=-version:refname

# 最近 N 个标签及其日期
git tag --sort=-version:refname --format="%(refname:short)|%(creatordate:short)" | head -10

# 查看指定范围内所有 commit
git log <from_tag>...<to_tag> --oneline

# 查看 commit 详情（提取 type 和 scope）
git log <from_tag>...<to_tag> --format="%s%n%b---"
```

**版本范围规则**：
- 如果用户指定了 `from_tag` 和 `to_tag`：用指定的
- 如果只指定 `to_tag`：取上一个标签作为 `from_tag`
- 如果只指定 `from_tag`：`to_tag` 用 HEAD
- 如果没有标签：从第一个 commit 开始

## Step 2: 语义分组

按 Conventional Commits 的 type 前缀分组：

| 分组标题 | 匹配 type | 说明 |
|----------|-----------|------|
| 🚀 Features | `feat` | 新功能 |
| 🐛 Bug Fixes | `fix` | 缺陷修复 |
| 🧹 Chores | `chore` | 构建/工具/依赖 |
| 📚 Documentation | `docs` | 文档变更 |
| ♻️ Refactor | `refactor` | 代码重构 |
| 🎨 Style | `style` | 格式调整 |
| ⚡ Performance | `perf` | 性能优化 |
| 🔒 Security | `security` | 安全修复 |
| ✅ Tests | `test` | 测试变更 |
| ⚙️ CI/CD | `ci` | CI 配置变更 |

**分组规则**：
- 无 type 前缀的 commit → 归入 "Other"
- `fix` 类型的 `fix(scope):` 按 scope 排序
- `feat` 类型的 `feat(scope):` 按 scope 排序
- Breaking Change 用 `⚠️ ` 前缀标注，在 changelog 顶部高亮

## Step 3: 生成 CHANGELOG.md

按 [Keep a Changelog](https://keepachangelog.com/) 格式输出：

```markdown
# Changelog

## [<new_version>] - <YYYY-MM-DD>

### ⚠️ Breaking Changes
- <breaking changes 列表>

### 🚀 Features
- <feat 列表>

### 🐛 Bug Fixes
- <fix 列表>

### ♻️ Refactor
- <refactor 列表>

### ⚡ Performance
- <perf 列表>

### 📚 Documentation
- <docs 列表>

### 🧹 Chores
- <chore 列表>

### ✅ Tests
- <test 列表>
```

### 版本号建议

基于 commit 内容自动建议版本号增量：

| 变更内容 | 版本增量 | 说明 |
|----------|----------|------|
| 包含 Breaking Change | MAJOR | `1.2.3` → `2.0.0` |
| 包含 feat | MINOR | `1.2.3` → `1.3.0` |
| 仅 fix/chore/refactor | PATCH | `1.2.3` → `1.2.4` |

### 输出规则

**DO**:
- ✅ 按语义分组，每组内按时间倒序
- ✅ 提取 commit body 中的额外上下文
- ✅ 版本号 + 发布日期
- ✅ 标注 Breaking Change
- ✅ 使用 Commitizen 风格的 emoji 前缀

**DON'T**:
- ❌ 直接罗列 commit message（已归组摘要）
- ❌ 包含 merge commit 信息
- ❌ 在分组中混入不相关的 type

## Step 4: 输出/写入文件

提供两个选项：

```
选项 1: 预览（直接显示生成的 changelog 内容）
选项 2: 追加到 CHANGELOG.md（如果文件存在则插入顶部，否则创建）
```

## Edge Cases

### 没有标签
```
仓库没有版本标签。建议先创建标签：git tag v0.1.0
将从头开始生成 changelog。
```

### 空范围（无新 commit）
```
指定范围内没有新 commit。
```

### 混杂的 commit 风格
部分 commit 没有遵循 Conventional Commits 格式时：
1. 按常规解析 `<type>: <description>` 格式
2. 无法解析的 commit 归入 "Other" 分组
3. 在分组内用 `- <commit_message> (<hash>)` 格式列出

### 非常大的 commit 范围（>200 commits）
```
commit 数量较多（>200），建议按 minor 版本分段生成。
只生成最近一个版本的 changelog。
```
