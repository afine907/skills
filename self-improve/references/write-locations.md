# 写入位置指南

> 诊断完成后，根据根因选择正确的写入位置

## 写入位置判断

| 诊断结论 | 写入位置 |
|----------|----------|
| CLAUDE.md 缺规则 | 追加到项目 CLAUDE.md |
| rules 写得不好 | 修改/追加 项目/.claude/rules/xx.md |
| 没有记忆 | 写入 项目/.claude/rules/xx.md |
| skill 没覆盖 | 修改对应 skill |
| 代码设计问题 | 在代码中添加注释或修改逻辑 |

**判断标准**：
- 通用性规则（编码习惯、工具使用、项目约定）→ CLAUDE.md
- 专项规则（CI/CD、Git、测试、安全等）→ .claude/rules/对应文件
- 不确定时 → 默认 CLAUDE.md

## 文件命名规则

`.claude/rules/` 下的文件命名：

| 文件名 | 类别 | 建议 globs |
|--------|------|-----------|
| `ci-cd.md` | CI/CD 相关 | `[".github/workflows/*.yml", "Makefile", "Dockerfile*"]` |
| `code-review.md` | 代码审查相关 | `["**/*.py", "**/*.ts"]` |
| `testing.md` | 测试相关 | `["tests/**/*", "**/*_test.py"]` |
| `git.md` | Git 操作相关 | `[".gitignore", ".gitattributes"]` |
| `architecture.md` | 架构设计相关 | `["docs/**/*"]` |
| `performance.md` | 性能相关 | 无 globs（始终加载） |
| `security.md` | 安全相关 | `["**/auth/**/*"]` |
| `general.md` | 通用教训 | 无 globs（始终加载） |
| `frontend.md` | 前端相关 | `["apps/web/**/*.tsx", "apps/web/**/*.ts"]` |
| `backend.md` | 后端相关 | `["packages/*/src/**/*.py"]` |

## 格式要求

参考官方文档：https://code.claude.com/docs/zh-CN/memory#使用-clauderules-组织规则

```yaml
---
description: "规则描述"
globs: ["**/*.ts", "**/*.tsx"]
alwaysApply: false
---
```

## 重要：写入位置优先级

所有写入操作优先使用**当前项目目录**（如 `d:\Code\project\.claude\`），而非全局目录（`~/.claude/`）。
