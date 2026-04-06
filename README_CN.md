# Skills

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skills-blue)](https://claude.ai/code)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI-Codex-green)](https://openai.com/codex)
[![Cursor](https://img.shields.io/badge/Cursor-Agent-purple)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-Agent-teal)](https://codeium.com/windsurf)

可复用的提示词模板集合，为 AI 编码 Agent 提供结构化能力扩展。

**[English](README.md)**

## 技能列表

| 技能 | 描述 | 用法 |
|------|------|------|
| [Task-Loom](task-loom/SKILL.md) | 项目编排引擎，专为大规模 PRD 项目设计 | `/task-loom init`, `/task-loom audit`, `/task-loom plan`, `/task-loom execute` |
| [Commit](commit/SKILL.md) | 智能 Git Commit 生成器，自动生成语义化提交消息 | `/commit`, `/commit --dry-run` |
| [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md) | 分析两个 git commit 之间的代码变更 | 提供两个 commit ID |
| [Explain-Code](explain-code/SKILL.md) | 分析代码功能、结构和设计质量 | 请求解释代码 |
| [Requirements-Analyzer](requirements-analyzer/SKILL.md) | 将模糊需求转化为结构化需求文档 | 提供需求点和用户旅程 |
| [Technical-Article-Writer](technical-article-writer/SKILL.md) | 使用网络搜索编写专业技术文章 | 请求编写技术文章 |

## 安装

```bash
# 安装所有技能
npx skills add https://github.com/afine907/skills

# 安装特定技能
npx skills add https://github.com/afine907/skills --skill task-loom
npx skills add https://github.com/afine907/skills --skill commit
```

## 许可证

[MIT License](LICENSE)
