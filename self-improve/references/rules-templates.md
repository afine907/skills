# Rules 文件格式模板

> 写入 `.claude/rules/` 时使用这些模板
> 参考：https://code.claude.com/docs/zh-CN/memory#使用-clauderules-组织规则

## 通用规则（始终加载）

无 frontmatter 的规则会自动始终加载：

```markdown
# [类别名称]

> 自动积累的项目经验，Claude 每次会话会自动读取

### [标题]
- **错误**: 描述发生了什么
- **原因**: 根本原因分析
- **正确做法**: 标准操作流程
- **场景**: 适用条件
- **来源**: 日期

---
```

## 专项规则（懒加载）

使用 `globs` 和 `alwaysApply: false` 实现懒加载：

```yaml
---
description: "规则的简短描述，帮助 Claude 判断是否需要加载"
globs: ["**/*.tsx", "**/*.ts"]
alwaysApply: false
---

# [类别名称]

> 仅在操作匹配文件时加载

### [标题]
- **错误**: 描述发生了什么
- **原因**: 根本原因分析
- **正确做法**: 标准操作流程
- **场景**: 适用条件
- **来源**: 日期

---
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `description` | string | 推荐 | 自然语言描述，帮助 Claude 判断是否需要加载此规则 |
| `globs` | string[] | 可选 | glob 模式数组，匹配的文件会触发规则加载 |
| `alwaysApply` | boolean | 可选 | `true`=始终加载，`false`=仅匹配时加载（配合 globs 或 description） |

## Glob 模式示例

| 模式 | 匹配 |
|------|------|
| `**/*.ts` | 所有 TypeScript 文件 |
| `src/**` | src 下所有内容 |
| `*.test.{ts,js}` | 测试文件 |
| `!**/node_modules/**` | 排除 node_modules |
| `.github/workflows/*.yml` | GitHub Actions 配置 |

## 行为规则

| 配置 | 行为 |
|------|------|
| 无 frontmatter | 始终加载 |
| `alwaysApply: true` | 始终加载 |
| `alwaysApply: false` + `globs` | 文件匹配时加载 |
| `alwaysApply: false` + `description` | Claude 根据描述判断是否加载 |

## 常见错误

### ❌ 使用 `paths` 而不是 `globs`

```yaml
---
paths:
  - "**/*.ts"
---
```

**问题**：`paths` 不是标准字段，应使用 `globs`

### ✅ 正确格式

```yaml
---
globs: ["**/*.ts", "**/*.tsx"]
alwaysApply: false
---
```

## 文件命名建议

| 文件名 | 用途 | 建议 globs |
|--------|------|-----------|
| `ci-cd.md` | CI/CD 规则 | `[".github/workflows/*.yml", "Makefile", "Dockerfile*"]` |
| `frontend.md` | 前端规则 | `["apps/web/**/*.tsx", "apps/web/**/*.ts"]` |
| `backend.md` | 后端规则 | `["packages/*/src/**/*.py", "libs/*/src/**/*.py"]` |
| `testing.md` | 测试规则 | `["tests/**/*", "**/*_test.py"]` |
| `general.md` | 通用规则 | 无 globs（始终加载） |
