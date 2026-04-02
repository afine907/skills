# Skills

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skills-blue)](https://claude.ai/code)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI-Codex-green)](https://openai.com/codex)
[![Cursor](https://img.shields.io/badge/Cursor-Agent-purple)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-Agent-teal)](https://codeium.com/windsurf)

可复用的提示词模板集合，为 AI 编码 Agent 提供结构化能力扩展。

## 技能列表

| 技能 | 描述 | 用法 |
|------|------|------|
| [Loom](loom/SKILL.md) | 项目编排引擎，专为大规模 PRD 项目设计 | `/loom init`, `/loom audit`, `/loom plan`, `/loom execute` |
| [Commit](commit/SKILL.md) | 智能 Git Commit 生成器，自动生成语义化提交消息 | `/commit`, `/commit --dry-run` |

## 安装

```bash
# 安装所有技能
npx skills add https://github.com/afine907/skills

# 安装特定技能
npx skills add https://github.com/afine907/skills --skill loom
npx skills add https://github.com/afine907/skills --skill commit
```

## 许可证

[MIT License](LICENSE)
