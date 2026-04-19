# Skills

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-blue?logo=claude)](https://claude.ai/code)
[![Cursor](https://img.shields.io/badge/Cursor-Agent-purple?logo=cursor)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-Agent-teal?logo=windsurf)](https://codeium.com/windsurf)

**[English](README.md)**

让你的 AI 编码助手进化。

一套专业级提示词模板，覆盖从需求到上线的完整开发链路。

## ⚡ 30 秒上手

```bash
# 安装全部
npx skills add https://github.com/afine907/skills

# 安装单个
npx skills add https://github.com/afine907/skills --skill task-loom
```

然后在 Claude Code 里输入 `/task-loom` 或 `/commit`，开始使用。

## 🔥 核心能力

### [Task-Loom](task-loom/SKILL.md) — 10,000 行 PRD 秒变代码

```
/task-loom init my-project docs/prd.md
/task-loom audit    → 风险扫描，P0 问题提前暴露
/task-loom plan     → DAG 任务图，依赖一目了然
/task-loom execute  → 按依赖顺序生成代码
```

**适合**：新项目启动、大需求拆解、多人协作对齐

### [Commit](commit/SKILL.md) — 不用再想 commit message

```bash
git add .
/commit    → feat(auth): add JWT token refresh
```

自动分析 diff，生成 Conventional Commits 规范消息。

### 更多

| Skill | 一句话描述 |
|-------|----------|
| [Yan-Pai](yan-pai/SKILL.md) | 迭代式代码审查：审查 → 报告 → 修复 |
| [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md) | 对比两个 commit，变更一目了然 |
| [Explain-Code](explain-code/SKILL.md) | 代码结构 + 设计质量一键分析 |
| [Requirements-Analyzer](requirements-analyzer/SKILL.md) | 模糊需求 → 结构化文档 |
| [Technical-Article-Writer](technical-article-writer/SKILL.md) | 自动搜索 + 写技术文章 |

## 📁 项目结构

```
skills/
├── task-loom/        # 项目编排引擎
├── commit/           # Commit 生成器
├── commit-diff-analyzer/
├── explain-code/
├── requirements-analyzer/
└── technical-article-writer/
```

每个目录一个 `SKILL.md`，复制即用。

## 🤝 贡献

欢迎 PR。新建目录 + `SKILL.md` = 一个新 Skill。

## 📄 许可证

[MIT](LICENSE)
