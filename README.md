<p align="center">
  <a href="https://github.com/afine907/skills">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Claude_Code-%E2%9C%94%EF%B8%8F-fff?style=flat-square&logo=claude&logoColor=white&labelColor=1a1a2e">
      <img src="https://img.shields.io/badge/Claude_Code-%E2%9C%94%EF%B8%8F-blue?style=flat-square&logo=claude&labelColor=1a1a2e" />
    </picture>
  </a>
  <a href="https://github.com/afine907/skills">
    <img src="https://img.shields.io/badge/Cursor-%E2%9C%94%EF%B8%8F-purple?style=flat-square&logo=cursor&labelColor=1a1a2e" />
  </a>
  <a href="https://github.com/afine907/skills">
    <img src="https://img.shields.io/badge/Windsurf-%E2%9C%94%EF%B8%8F-teal?style=flat-square&logo=windsurf&labelColor=1a1a2e" />
  </a>
  <a href="https://github.com/afine907/skills">
    <img src="https://img.shields.io/badge/OpenClaw-%E2%9C%94%EF%B8%8F-orange?style=flat-square&logo=openclaw&labelColor=1a1a2e" />
  </a>
  <br>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/afine907/skills?style=flat-square&labelColor=1a1a2e&color=white" />
  </a>
  <a href="https://github.com/afine907/skills">
    <img src="https://img.shields.io/github/stars/afine907/skills?style=flat-square&labelColor=1a1a2e&color=yellow" />
  </a>
  <a href="https://github.com/afine907/skills/pulls">
    <img src="https://img.shields.io/github/issues-pr/afine907/skills?style=flat-square&labelColor=1a1a2e&color=white" />
  </a>
</p>

<br>

<h1 align="center">
  🎰 AI Skills<br>
  <sub><i>Professional-grade prompt templates for AI coding assistants</i></sub>
</h1>

<p align="center">
  <b>Code Review · Project Planning · Commit Messages · Technical Writing</b><br>
  From zero to production — prompt templates that make your AI actually productive.
</p>

<p align="center">
  <a href="README_CN.md">🇨🇳 中文版（玩梗更狠，推荐）</a>
</p>

<br>

---

## 🃏 Featured: Card Review Agent

> **"Deal me in."** Iterative code review that catches what humans miss.

<p align="center">
  <a href="wo-yao-yan-pai/SKILL.md">
    <img src="https://img.shields.io/badge/🃏_Card_Review-wo__yao__yan__pai-red?style=for-the-badge&labelColor=1a1a2e" />
  </a>
</p>

Think of it as your personal code auditor that runs autonomously:

```
     Code → 🔍 Multi-dim Review → 📊 Report → 🎯 Judgment
                                                   ↓
                                     ┌────────────┴────────────┐
                                     │                         │
                                 Needs Fix                Passes
                                     │                         │
                                     ▼                         ▼
                              🔧 Auto Fix                ✅ Ship It
                                     │                         │
                                     └────── 🔄 Repeat ────────┘
```

```bash
# After any coding task, just say:
wo-yao-yan-pai
# or in Chinese:
我要验牌

# The agent does the rest — review, report, fix, repeat.
# Fully autonomous, configurable iterations (default 2, max 5).
```

**What gets checked:**

| Dimension | What we look for |
|-----------|-----------------|
| 🏗️ Code Quality | Readability, naming, complexity, duplication |
| 🐛 Potential Bugs | Edge cases, null safety, concurrency, exception handling |
| ⚡ Performance | Algorithm complexity, memory leaks, unnecessary work |
| 🔒 Security | Input validation, injection risks, secrets handling |
| 📐 Best Practices | Design patterns, error handling, test coverage |

**Grading system:**
- 🏆 **High Roller** (90-100) — Code is production-ready, ship with confidence
- 🔧 **Needs Polish** (70-89) — Minor issues found, auto-fix applied
- 🧹 **Needs Work** (50-69) — Medium+ issues auto-repaired
- 🚨 **Critical** (0-49) — Significant refactoring needed

<details>
<summary><b>⚡ Quick Install</b></summary>

```bash
# One command, all skills
npx skills add https://github.com/afine907/skills

# Single skill
npx skills add https://github.com/afine907/skills --skill wo-yao-yan-pai
```

Then use it in Claude Code, Cursor, Windsurf, or any agent that supports `/commands`.
</details>

<br>

---

## 📦 The Full Deck

| Skill | What it does | Best for |
|-------|-------------|----------|
| 🃏 **wo-yao-yan-pai** | Code review → report → auto-fix loop | Quality gate for AI-generated code |
| 🧵 **task-loom** | PRD → DAG plan → code generation | New projects, large features |
| ✍️ **commit** | Conventional Commits from git diff | Clean commit history |
| 🔍 **commit-diff-analyzer** | Compare two commits side-by-side | Code review, debugging |
| 🧠 **explain-code** | Structure + design quality analysis | Onboarding, documentation |
| 📋 **requirements-analyzer** | Vague specs → structured docs | Product handoffs |
| 📝 **technical-article-writer** | Research + write tech articles | Documentation, blogs |

<br>

---

## 🎯 Skills in Detail

### 🧵 [Task-Loom](task-loom/SKILL.md) — Turn Requirements into Code

```bash
/task-loom init my-project docs/prd.md
/task-loom audit     # Risk scan, catch P0 issues early
/task-loom plan      # DAG dependency graph
/task-loom execute   # Generate code in dependency order
```

**Why**: Large PRDs are hard for LLMs to handle in one pass. Task-Loom breaks them down, discovers dependencies, and generates code in optimal order. No context window overflows, no missed requirements.

### ✍️ [Commit](commit/SKILL.md) — Never Write a Commit Message Again

```bash
git add .
/commit   # → feat(auth): add JWT token refresh with refresh rotation
```

**Why**: Conventional Commits are a spec, not a suggestion. This agent analyzes your actual diff, understands the change type, and writes messages that pass semantic-release, changelog generators, and code review.

### 🔍 [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md)

```bash
# Compare any two commits
/commit-diff-analyzer <sha1> <sha2>
```

**Why**: "What changed between these two commits?" — the most common code review question. This gives you a structured, categorized answer.

### 🧠 [Explain-Code](explain-code/SKILL.md)

```bash
# Analyze a file or directory
/explain-code src/auth/
```

**Why**: Understanding unfamiliar code takes time. This agent analyzes structure, dependencies, design patterns, and generates a readable explanation.

### 📋 [Requirements-Analyzer](requirements-analyzer/SKILL.md)

```bash
# Transform vague requirements
/requirements-analyzer "Build a user auth system with SSO"
# → structured PRD with user stories, tech stack, API design
```

**Why**: The gap between "what we need" and "what we build" is where projects fail. This bridges it.

### 📝 [Technical-Article-Writer](technical-article-writer/SKILL.md)

```bash
/technical-article-writer "How to build a WebSocket server in Go"
```

**Why**: Writing takes time. This agent researches, outlines, writes, and formats. Great for docs, blogs, and READMEs.

<br>

---

## 📁 Project Structure

```
skills/
├── wo-yao-yan-pai/               # 🃏 Card Review Agent
├── task-loom/                    # 🧵 Project orchestration
├── commit/                       # ✍️ Commit messages
├── commit-diff-analyzer/         # 🔍 Diff analysis
├── explain-code/                 # 🧠 Code explanation
├── requirements-analyzer/        # 📋 Requirements → specs
└── technical-article-writer/     # 📝 Tech articles
```

Each skill directory contains:
- `SKILL.md` — The full prompt template, copy-paste ready
- `references/` — Detailed reference guides and checklists

<br>

---

## 🧠 Why Use These?

1. **No more ad-hoc prompts** — Stop writing "review this code" and getting shallow answers. These templates are battle-tested.
2. **Consistent quality** — The same thorough review every time, regardless of model or context length.
3. **Autonomous workflow** — Review → Fix → Re-review. No manual babysitting.
4. **Free & open** — No subscription, no API key needed beyond your LLM provider.
5. **Portable** — Works with Claude Code, Cursor, Windsurf, OpenClaw, and any agent that supports `/command` patterns.

<br>

---

## 🤝 Contributing

PRs welcome! Three rules:

1. **One skill = one directory** with a `SKILL.md`
2. **No external dependencies** — pure prompt templates only
3. **Keep it focused** — each skill does one thing well

```bash
skills/
└── your-skill-name/
    ├── SKILL.md          # Required
    └── references/       # Optional reference docs
```

<br>

---

## 🌟 Star History

<a href="https://www.star-history.com/#afine907/skills&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=afine907/skills&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=afine907/skills&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=afine907/skills&type=Date" width="600" />
 </picture>
</a>

<br>

---

<p align="center">
  <a href="https://github.com/afine907/skills/issues/new">🐛 Report Bug</a>
  ·
  <a href="https://github.com/afine907/skills/pulls">🔧 Submit PR</a>
  ·
  <a href="LICENSE">📄 MIT Licensed</a>
</p>

<p align="center">
  <sub>Built with 🎰 by <a href="https://github.com/afine907">afine907</a></sub>
</p>
