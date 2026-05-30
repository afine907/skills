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
  <br>
  <img src="https://img.shields.io/badge/skills-67-blueviolet?style=flat-square&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/tests-704-brightgreen?style=flat-square&labelColor=1a1a2e" />
</p>

<br>

<h1 align="center">🎰 AI Skills</h1>

<p align="center">
  <b>67 prompt templates that make your AI agent actually productive.</b><br>
  From requirements to production — one <code>/skill-name</code> at a time.
</p>

<p align="center">
  <a href="README_CN.md">🇨🇳 中文版</a>
</p>

<br>

---

## What Is This?

A collection of reusable [skills](SKILL_CATEGORIES.md) (prompt templates) for AI coding agents. Each skill is a self-contained `SKILL.md` that turns vague instructions into structured, repeatable workflows.

**Works with:** Claude Code · Cursor · Windsurf · OpenClaw · Any agent supporting `/commands`

**Covers the full SDLC:** Requirements → Architecture → Development → Quality → Version Control → Deployment → Operations

<br>

---

## ⚡ Quick Install

```bash
# All skills at once
npx skills add https://github.com/afine907/skills

# Single skill
npx skills add https://github.com/afine907/skills --skill wo-yao-yan-pai
```

Then invoke in your agent: `/skill-name` or type the skill name directly.

<br>

---

## 📦 All 67 Skills

> See [SKILL_CATEGORIES.md](SKILL_CATEGORIES.md) for the full SDLC phase map with usage guidance and complementary skill suggestions.

### 📋 Requirements · 3 skills

| Skill | What it does |
|-------|-------------|
| **requirements-analyzer** | Vague specs → structured PRD |
| **tech-spec** | PRD → technical specification |
| **user-story** | User stories with acceptance criteria |

### 🏗️ Development · 25 skills

| Skill | What it does |
|-------|-------------|
| **task-loom** | PRD → DAG plan → code generation |
| **api-design** | RESTful/GraphQL API design |
| **api-mocking** | Mock API service for testing |
| **graphql-design** | GraphQL schema design |
| **database-ops** | Schema, queries, optimization |
| **database-seeding** | Seed data generation |
| **data-pipeline** | ETL pipeline design |
| **feature-flag** | Feature flag system |
| **go-service-creator** | Go service scaffolding |
| **microservice-patterns** | Distributed system architecture |
| **mobile-service-creator** | Mobile app scaffolding |
| **monorepo-manager** | Multi-package repo management |
| **python-service-creator** | Python service scaffolding |
| **prompt-cicd** | Prompt versioning & CI/CD |
| **react-service-creator** | React project scaffolding |
| **websocket-service** | Real-time WebSocket communication |
| **code-migration** | Framework/language migration |
| **i18n-helper** | Internationalization |
| **auth-patterns** | Authentication & authorization |
| **caching-strategy** | Cache design patterns |
| **cli-tool-creator** | CLI tool development |
| **tool-use-patterns** | Defensive tool integration for agents |
| **typescript-service-creator** | TypeScript backend scaffolding |
| **vue-service-creator** | Vue/Nuxt frontend scaffolding |

### ✅ Quality · 9 skills

| Skill | What it does |
|-------|-------------|
| **wo-yao-yan-pai** | 🃏 Iterative code review → auto-fix loop |
| **code-review** | Structured multi-dimension review |
| **explain-code** | Code structure & design analysis |
| **test-generator** | Auto-generate pytest tests |
| **test-strategy** | Test strategy design |
| **agent-eval** | AI Agent output evaluation |
| **agent-security** | Agent threat modeling & injection defense |
| **security-scan** | Security vulnerability scanning |
| **accessibility-audit** | WCAG accessibility audit |

### 🔗 Source Control · 6 skills

| Skill | What it does |
|-------|-------------|
| **commit** | Conventional Commits from git diff |
| **commit-diff-analyzer** | Compare two commits side-by-side |
| **pr-description** | Git diff → structured PR description |
| **changelog-generator** | Git tags → Keep a Changelog |
| **git-branch** | Branch strategy patterns |
| **git-workflow** | Git workflow patterns |

### 🚀 Operations · 11 skills

| Skill | What it does |
|-------|-------------|
| **ci-workflow** | NL → CI config (GitHub Actions / GitLab CI) |
| **remote-exec** | SSH command execution |
| **log-analyzer** | Structured log analysis & anomaly detection |
| **deploy-checklist** | Pre-deployment checklist |
| **cost-optimization** | Cloud cost analysis |
| **incident-response** | Incident response with RCA |
| **load-testing** | Load testing design |
| **migration-helper** | Database migration scripts |
| **k8s-cluster** | Kubernetes cluster management |
| **k8s-gen** | Kubernetes manifest generation |
| **llm-observability** | LLM/Agent monitoring & tracing |

### 🔧 Productivity · 8 skills

| Skill | What it does |
|-------|-------------|
| **shell-command** | NL → shell command with safety guardrails |
| **debug-helper** | 5-step structured debugging |
| **regex-buddy** | NL → regex + explanation + test cases |
| **prompt-engineering** | Task → optimized LLM prompt |
| **technical-article-writer** | Research & write tech articles |
| **doc-generator** | Auto-generate documentation |
| **meeting-notes** | Transcript → structured minutes |
| **self-improve** | Self-improvement feedback loop |

### 📚 Reference · 5 skills

| Skill | What it does |
|-------|-------------|
| **api-debug** | API debugging reference |
| **docker-essentials** | Docker reference |
| **linux-ops** | Linux operations reference |
| **performance-profiling** | Performance profiling reference |
| **python-testing** | Pytest patterns reference |

<br>

---

## 🃏 Featured: Card Review Agent

> **[wo-yao-yan-pai](wo-yao-yan-pai/SKILL.md)** — Iterative code review that catches what humans miss.

```bash
# After any coding task, just say:
wo-yao-yan-pai
# or in Chinese:
我要验牌
```

```
Code → 🔍 Review → 📊 Report → 🎯 Judgment
                                    │
                        ┌───────────┴───────────┐
                     Needs Fix               Passes
                        │                       │
                     🔧 Auto Fix            ✅ Ship It
                        │                       │
                        └──── 🔄 Repeat ────────┘
```

Reviews code quality, bugs, performance, security, and best practices. Grades from 🏆 High Roller (90-100) to 🚨 Critical (0-49). Auto-fixes issues and re-reviews until clean.

<br>

---

## 🧠 Why Use These?

1. **No more ad-hoc prompts** — "review this code" gives shallow answers. These templates are battle-tested.
2. **Consistent quality** — The same thorough analysis every time, regardless of model.
3. **Autonomous workflows** — Review → Fix → Re-review. No manual babysitting.
4. **Free & open** — MIT licensed, no subscription, no vendor lock-in.
5. **Portable** — Works with any agent that supports `/commands`.

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

See [SKILL_CATEGORIES.md](SKILL_CATEGORIES.md) for the category system and [CLAUDE.md](CLAUDE.md) for development conventions.

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
