# Skills

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skills-blue)](https://claude.ai/code)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI-Codex-green)](https://openai.com/codex)
[![Cursor](https://img.shields.io/badge/Cursor-Agent-purple)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-Agent-teal)](https://codeium.com/windsurf)

A collection of reusable prompt templates that extend AI coding agents with structured capabilities.

**[中文文档](README_CN.md)**

## Skills

| Skill | Description | Usage |
|-------|-------------|-------|
| [Task-Loom](task-loom/SKILL.md) | Project orchestration engine for large-scale PRD projects | `/task-loom init`, `/task-loom audit`, `/task-loom plan`, `/task-loom execute` |
| [Commit](commit/SKILL.md) | Smart Git commit generator with semantic messages | `/commit`, `/commit --dry-run` |
| [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md) | Analyze code changes between two git commits | Provide two commit IDs |
| [Explain-Code](explain-code/SKILL.md) | Analyze code functionality, structure, and design quality | Ask to explain code |
| [Requirements-Analyzer](requirements-analyzer/SKILL.md) | Transform vague requirements into structured documents | Provide requirements and user journey |
| [Technical-Article-Writer](technical-article-writer/SKILL.md) | Write professional technical articles with web search | Request technical article |

## Installation

```bash
# Install all skills
npx skills add https://github.com/afine907/skills

# Install specific skill
npx skills add https://github.com/afine907/skills --skill task-loom
npx skills add https://github.com/afine907/skills --skill commit
```

## License

[MIT License](LICENSE)
