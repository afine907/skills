<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-%F0%9F%94%8D-blue?logo=claude&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Cursor-%E2%9C%A8-purple?logo=cursor&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Windsurf-%F0%9F%8C%8A-teal?logo=windsurf&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/OpenClaw-%F0%9F%A6%9E-orange?labelColor=1a1a2e" />
  <img src="https://img.shields.io/github/stars/afine907/skills?style=flat&labelColor=1a1a2e" />
</p>

<h1 align="center">🎰 AI Skills — Prompt Templates that Go Viral</h1>

<p align="center">
  <b>Supercharge your AI coding assistant with professional-grade prompt templates.</b><br>
  From code review to requirements, commit messages to tech articles — one command away.
</p>

<p align="center">
  <a href="README_CN.md">🇨🇳 中文</a>
</p>

<br>

---

<h2 align="center">🃏 FEATURED SKILL</h2>

<p align="center">
  <a href="wo-yao-yan-pai/SKILL.md">
    <img src="https://img.shields.io/badge/🔥_我要验牌-WO_YAO_YAN_PAI-red?style=for-the-badge&labelColor=1a1a2e" />
  </a>
</p>

<p align="center">
  <b>"赌侠" or "小瘪三"? Let the cards decide.</b><br>
  <i>Iterative Code Review → Report → Bug Fix · Autonomous quality gate for AI-generated code</i>
</p>

```bash
# After coding, just say:
我要验牌

# The Agent will:
# 🔍 Code Review → 📊 Report → 🎯 Judgment → 🔧 Fix → 🔄 Repeat

# If you're a "小瘪三", time to "擦皮鞋" 🧹
# If you're a "赌侠", you've earned your chips 🎉
```

<table align="center">
<tr>
  <td align="center"><b>🎯 Judgment</b></td>
  <td align="center"><b>🧹 Fix</b></td>
  <td align="center"><b>🔄 Iterate</b></td>
  <td align="center"><b>🏆 Pass</b></td>
</tr>
<tr>
  <td>Multi-dimension<br>code review</td>
  <td>Auto fix<br>medium+ issues</td>
  <td>Up to 5 rounds<br>of refinement</td>
  <td>Quality gates<br>enforced</td>
</tr>
</table>

<details>
<summary><b>⚡ Quick Install</b></summary>

```bash
# Install all skills
npx skills add https://github.com/afine907/skills

# Install single skill
npx skills add https://github.com/afine907/skills --skill wo-yao-yan-pai
```
</details>

<br>

---

<h2 align="center">🗂️ SKILL DECK</h2>

| Skill | What it does |
|-------|-------------|
| 🎰 **wo-yao-yan-pai** | Code Review → Report → Fix. The hero. |
| 🧵 **task-loom** | Turn 10,000-line PRDs into executable code plans |
| ✍️ **commit** | Never write commit messages again — auto Conventional Commits |
| 🔍 **commit-diff-analyzer** | Compare two commits, see everything that changed |
| 🧠 **explain-code** | Code structure + design quality at a glance |
| 📋 **requirements-analyzer** | From vague requirements to structured specs |
| 📝 **technical-article-writer** | Auto-search + write polished tech articles |

<br>

---

<h2 align="center">🎯 HOW THEY WORK</h2>

### 🧵 [Task-Loom](task-loom/SKILL.md) — Project Orchestration Engine

```
/task-loom init my-project docs/prd.md
/task-loom audit    → Risk scan, catch P0 issues early
/task-loom plan     → DAG task graph, dependencies visualized
/task-loom execute  → Generate code in dependency order
```

**Best for**: New projects, large requirement breakdown, team alignment

### ✍️ [Commit](commit/SKILL.md) — Commit Message Generator

```bash
git add .
/commit    → feat(auth): add JWT token refresh
```

Auto-analyzes diff and generates Conventional Commits messages.

<br>

---

<h2 align="center">📁 PROJECT STRUCTURE</h2>

```
skills/
├── wo-yao-yan-pai/          # 🃏 The hero — iterative code review
├── task-loom/               # Project orchestration engine
├── commit/                  # Commit message generator
├── commit-diff-analyzer/    # Diff between commits
├── explain-code/            # Code analysis
├── requirements-analyzer/   # Requirements → specs
└── technical-article-writer/# Tech article generator
```

Each directory contains a `SKILL.md` — copy and use in your AI coding assistant.

<br>

---

<p align="center">
  <a href="https://github.com/afine907/skills/issues">🐛 Report Bug</a>
  ·
  <a href="https://github.com/afine907/skills/pulls">🔧 Submit PR</a>
  ·
  <a href="LICENSE">📄 MIT License</a>
</p>

<p align="center">
  <sub>Made with 🎰 by <a href="https://github.com/afine907">afine907</a></sub>
</p>
