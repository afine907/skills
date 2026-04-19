# Skills

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-blue?logo=claude)](https://claude.ai/code)
[![Cursor](https://img.shields.io/badge/Cursor-Agent-purple?logo=cursor)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-Agent-teal?logo=windsurf)](https://codeium.com/windsurf)

**[中文文档](README_CN.md)**

Supercharge your AI coding assistant with professional-grade prompt templates covering the full development lifecycle.

## ⚡ Quick Start

```bash
# Install all
npx skills add https://github.com/afine907/skills

# Install single skill
npx skills add https://github.com/afine907/skills --skill task-loom
```

Then use `/task-loom` or `/commit` in Claude Code.

## 🔥 Core Skills

### [Task-Loom](task-loom/SKILL.md) — Turn 10,000-line PRDs into Code

```
/task-loom init my-project docs/prd.md
/task-loom audit    → Risk scan, catch P0 issues early
/task-loom plan     → DAG task graph, dependencies visualized
/task-loom execute  → Generate code in dependency order
```

**Best for**: New projects, large requirement breakdown, team alignment

### [Commit](commit/SKILL.md) — Never Write Commit Messages Again

```bash
git add .
/commit    → feat(auth): add JWT token refresh
```

Auto-analyzes diff and generates Conventional Commits messages.

### More Skills

| Skill | Description |
|-------|-------------|
| [Yan-Pai](yan-pai/SKILL.md) | Iterative code review → report → fix workflow |
| [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md) | Compare two commits, see changes at a glance |
| [Explain-Code](explain-code/SKILL.md) | Code structure + design quality analysis |
| [Requirements-Analyzer](requirements-analyzer/SKILL.md) | Vague requirements → structured docs |
| [Technical-Article-Writer](technical-article-writer/SKILL.md) | Auto-search + write tech articles |

## 📁 Project Structure

```
skills/
├── task-loom/        # Project orchestration engine
├── commit/           # Commit message generator
├── commit-diff-analyzer/
├── explain-code/
├── requirements-analyzer/
└── technical-article-writer/
```

Each directory has a `SKILL.md` — copy and use.

## 🤝 Contributing

PRs welcome. Create a directory + `SKILL.md` = a new skill.

## 📄 License

[MIT](LICENSE)
