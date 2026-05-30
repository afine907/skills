# 验证机制

本文档介绍技能质量验证系统的工作原理。

## 概述

每次推送到 `master` 或提交 PR 时，GitHub Actions 会自动运行验证。本地也可以手动执行：

```bash
python scripts/validate_skills.py
```

## 检查项

验证脚本 (`scripts/validate_skills.py`) 对每个技能执行 13 项检查：

### Frontmatter 检查

| # | 检查项 | 级别 | 说明 |
|---|--------|------|------|
| 1 | 必填字段 | 错误 | `name`、`description`、`category` 必须存在 |
| 2 | name 匹配目录 | 错误 | `name` 必须与目录名完全一致 |
| 3 | 合法 category | 错误 | `category` 必须是 7 个合法值之一 |
| 4 | description 长度 | 错误 | 10-200 字符 |
| 5 | 无重名 | 错误 | 不允许两个技能同名 |

### 内容检查

| # | 检查项 | 级别 | 说明 |
|---|--------|------|------|
| 6 | 非空正文 | 错误 | SKILL.md 在 frontmatter 之后必须有内容 |
| 7 | 推荐章节 | 警告 | 应包含标题 (H1)、目标、触发条件、工作流程 |
| 8 | 链接有效 | 错误 | 所有 `[text](path)` 链接必须指向存在的文件 |

### 结构检查

| # | 检查项 | 级别 | 说明 |
|---|--------|------|------|
| 9 | references/ 非空 | 错误 | 如果存在 `references/` 目录，必须包含 ≥1 个文件 |
| 10 | scripts/ __init__.py | 警告 | 如果 `scripts/` 有 `.py` 文件，应有 `__init__.py` |
| 11 | 引用文件存在 | 错误 | SKILL.md 中引用的文件必须实际存在 |

### Category 拼写纠错

脚本内置了常见拼写错误的模糊匹配：

```
"developement" → "development"
"qualty"       → "quality"
"souce-control" → "source-control"
```

拼写错误时，提示信息会建议正确拼写。

## 本地运行

```bash
# 标准验证
python scripts/validate_skills.py

# 详细输出（显示所有检查项，不只失败项）
python scripts/validate_skills.py --verbose

# 自动修复简单问题（尾部空格、缺少 EOF 换行）
python scripts/validate_skills.py --fix
```

## CI 流水线

GitHub Actions 工作流 (`.github/workflows/ci.yml`) 在以下情况触发：
- 推送到 `master`
- 目标为 `master` 的 PR

**两个任务：**

1. **validate-skills** — 运行 `python scripts/validate_skills.py`
2. **run-tests** — 运行 `pytest task-loom/tests/ -v`

两个任务都必须通过，CI 才算成功。

## 常见错误修复

### "Missing required frontmatter field: name"

SKILL.md 缺少 `name` 字段：

```yaml
---
name: my-skill          # ← 添加这个
description: 做X的事情
category: productivity
---
```

### "name 'my-skill' does not match directory name 'my_skill'"

`name` 必须与目录名完全一致：

```
my-skill/SKILL.md  →  name: my-skill   ✅
my-skill/SKILL.md  →  name: my_skill   ❌
```

### "Invalid category: developement. Did you mean: development?"

检查拼写。合法的 category：
- `requirements`
- `development`
- `quality`
- `source-control`
- `operations`
- `productivity`
- `reference`

### "Broken link: references/guide.md"

SKILL.md 中的链接指向不存在的文件。要么：
- 在 `references/guide.md` 创建文件
- 修正链接指向正确路径

### "references/ directory is empty"

如果有 `references/` 目录，它必须至少包含一个文件。要么添加文件，要么删除目录。

## 添加新 Category

要添加新 category（如 `security`）：

1. 编辑 `scripts/validate_skills.py`
2. 添加到 `ALLOWED_CATEGORIES`：
   ```python
   ALLOWED_CATEGORIES = {
       "requirements",
       "development",
       "quality",
       "source-control",
       "operations",
       "productivity",
       "reference",
       "security",      # ← 新增
   }
   ```
3. 更新 `CLAUDE.md` 的 category 表
4. 更新 `SKILL_CATEGORIES.md` 的阶段映射
5. 运行验证确认通过

## 测试套件

`tests/` 目录包含验证脚本之外的额外测试：

| 文件 | 测试内容 |
|------|---------|
| `test_validate_skills.py` | 验证脚本本身的单元测试 |
| `test_skill_structure.py` | 对所有真实技能目录的参数化测试 |
| `fixtures/` | 测试夹具（good-skill、bad-broken-links 等） |

运行方式：
```bash
pytest tests/ -v
```
