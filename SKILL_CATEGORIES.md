# Skill Categories — SDLC Phase Map

All 67 skills organized by software development lifecycle phase. Find the right skill for where you are in the workflow.

```
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │ Requirements │───▶│ Architecture│───▶│ Development │
  │   (3 skills) │    │  (included) │    │ (25 skills) │
  └─────────────┘    └─────────────┘    └─────────────┘
                                              │
  ┌─────────────┐    ┌─────────────┐    ┌─────▼───────┐
  │ Maintenance  │◀───│ Operations  │◀───│   Quality   │
  │  (9 skills)  │    │ (11 skills) │    │  (9 skills) │
  └─────────────┘    └─────────────┘    └─────────────┘
        │
  ┌─────▼───────┐    ┌─────────────┐
  │Productivity  │    │  Reference  │
  │  (9 skills)  │    │  (5 skills) │
  └─────────────┘    └─────────────┘
```

---

## 📋 Phase 1: Requirements & Planning

> **When:** Starting a new project or feature. Turning vague ideas into structured plans.

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [requirements-analyzer](requirements-analyzer/SKILL.md) | Vague specs → structured PRD | Product handoffs, stakeholder meetings | `tech-spec`, `user-story` |
| [tech-spec](tech-spec/SKILL.md) | PRD → technical specification | Architecture decisions, API contracts | `requirements-analyzer`, `api-design` |
| [user-story](user-story/SKILL.md) | Write user stories with acceptance criteria | Sprint planning, backlog grooming | `requirements-analyzer`, `task-loom` |

---

## 🏗️ Phase 2: Architecture & Development

> **When:** Designing systems and writing code. The largest phase with 25 skills.

### Orchestration & Planning

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [task-loom](task-loom/SKILL.md) | PRD → DAG plan → code generation | Large features, new projects | `requirements-analyzer`, `test-generator` |
| [feature-flag](feature-flag/SKILL.md) | Feature flag system design | Gradual rollouts, A/B testing | `deploy-checklist`, `ci-workflow` |
| [monorepo-manager](monorepo-manager/SKILL.md) | Monorepo management | Multi-package repositories | `ci-workflow`, `task-loom` |

### API & Data

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [api-design](api-design/SKILL.md) | RESTful/GraphQL API design | New APIs, API refactoring | `tech-spec`, `api-mocking` |
| [api-mocking](api-mocking/SKILL.md) | Mock API service | Frontend dev, testing | `api-design`, `test-generator` |
| [graphql-design](graphql-design/SKILL.md) | GraphQL schema design | GraphQL APIs | `api-design`, `database-ops` |
| [database-ops](database-ops/SKILL.md) | Database operations | Schema design, queries, optimization | `data-pipeline`, `migration-helper` |
| [database-seeding](database-seeding/SKILL.md) | Seed data generation | Dev/test environments | `database-ops`, `test-generator` |
| [data-pipeline](data-pipeline/SKILL.md) | ETL pipeline design | Data processing, analytics | `database-ops`, `ci-workflow` |

### Authentication & Security

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [auth-patterns](auth-patterns/SKILL.md) | Auth/authz patterns | Login systems, permissions | `api-design`, `agent-security` |
| [agent-security](agent-security/SKILL.md) | AI Agent security framework | Agent permissions, injection defense | `auth-patterns`, `tool-use-patterns` |

### Service Scaffolding

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [python-service-creator](python-service-creator/SKILL.md) | Python service scaffolding | New Python backends | `database-ops`, `api-design` |
| [typescript-service-creator](typescript-service-creator/SKILL.md) | TypeScript backend scaffolding | New TS backends | `database-ops`, `api-design` |
| [go-service-creator](go-service-creator/SKILL.md) | Go service scaffolding | New Go backends | `database-ops`, `api-design` |
| [react-service-creator](react-service-creator/SKILL.md) | React project scaffolding | New React frontends | `api-mocking`, `vue-service-creator` |
| [vue-service-creator](vue-service-creator/SKILL.md) | Vue/Nuxt frontend scaffolding | New Vue frontends | `api-mocking`, `react-service-creator` |
| [mobile-service-creator](mobile-service-creator/SKILL.md) | Mobile app scaffolding | New mobile apps | `api-design`, `websocket-service` |
| [cli-tool-creator](cli-tool-creator/SKILL.md) | CLI tool development | New CLI tools | `python-service-creator`, `go-service-creator` |

### Infrastructure & Patterns

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [caching-strategy](caching-strategy/SKILL.md) | Cache design | Performance optimization | `database-ops`, `microservice-patterns` |
| [microservice-patterns](microservice-patterns/SKILL.md) | Microservice architecture | Distributed systems | `api-design`, `websocket-service` |
| [websocket-service](websocket-service/SKILL.md) | WebSocket real-time communication | Real-time features | `microservice-patterns`, `api-design` |
| [code-migration](code-migration/SKILL.md) | Framework/language migration | Tech stack upgrades | `task-loom`, `test-generator` |
| [i18n-helper](i18n-helper/SKILL.md) | Internationalization | Multi-language support | `react-service-creator`, `vue-service-creator` |

### AI Agent Development

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [tool-use-patterns](tool-use-patterns/SKILL.md) | Defensive tool integration | Agent tool calling, function calling | `agent-eval`, `agent-security` |
| [prompt-cicd](prompt-cicd/SKILL.md) | Prompt lifecycle management | Prompt versioning, regression testing | `prompt-engineering`, `agent-eval` |
| [prompt-engineering](prompt-engineering/SKILL.md) | Prompt optimizer | Designing LLM prompts | `prompt-cicd`, `tool-use-patterns` |

---

## ✅ Phase 3: Quality & Testing

> **When:** Reviewing code, writing tests, and ensuring security before merge.

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [wo-yao-yan-pai](wo-yao-yan-pai/SKILL.md) | Iterative code review agent | After any coding task | `test-generator`, `code-review` |
| [code-review](code-review/SKILL.md) | Structured multi-dimension review | PR reviews, code audits | `wo-yao-yan-pai`, `explain-code` |
| [explain-code](explain-code/SKILL.md) | Code structure & design analysis | Onboarding, documentation | `code-review`, `doc-generator` |
| [test-generator](test-generator/SKILL.md) | Auto-generate pytest tests | Test coverage after coding | `wo-yao-yan-pai`, `python-testing` |
| [test-strategy](test-strategy/SKILL.md) | Test strategy design | Planning test approach | `test-generator`, `agent-eval` |
| [agent-eval](agent-eval/SKILL.md) | AI Agent output evaluation | Agent quality assurance | `tool-use-patterns`, `agent-security` |
| [agent-security](agent-security/SKILL.md) | Agent security review | Threat modeling, permissions | `auth-patterns`, `tool-use-patterns` |
| [security-scan](security-scan/SKILL.md) | Security vulnerability scanning | Pre-deploy security checks | `agent-security`, `deploy-checklist` |
| [accessibility-audit](accessibility-audit/SKILL.md) | Web accessibility audit | WCAG compliance | `react-service-creator`, `vue-service-creator` |

---

## 🔗 Phase 4: Version Control

> **When:** Committing code, creating PRs, managing branches and releases.

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [commit](commit/SKILL.md) | Conventional Commits from diff | Every git commit | `pr-description`, `changelog-generator` |
| [commit-diff-analyzer](commit-diff-analyzer/SKILL.md) | Compare two commits | Code review, debugging | `commit`, `code-review` |
| [pr-description](pr-description/SKILL.md) | PR description generator | Creating pull requests | `commit`, `changelog-generator` |
| [changelog-generator](changelog-generator/SKILL.md) | Git tags → changelog | Release prep | `pr-description`, `deploy-checklist` |
| [git-branch](git-branch/SKILL.md) | Git branch strategies | Branch management | `git-workflow`, `commit` |
| [git-workflow](git-workflow/SKILL.md) | Git workflow patterns | Team workflow design | `git-branch`, `ci-workflow` |

---

## 🚀 Phase 5: Deployment & Operations

> **When:** Deploying to production, monitoring systems, and responding to incidents.

### CI/CD & Deployment

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [ci-workflow](ci-workflow/SKILL.md) | NL → CI config | CI/CD pipeline setup | `deploy-checklist`, `git-workflow` |
| [deploy-checklist](deploy-checklist/SKILL.md) | Pre-deployment checklist | Every deployment | `ci-workflow`, `incident-response` |
| [k8s-gen](k8s-gen/SKILL.md) | K8s manifest generation | Kubernetes deployments | `k8s-cluster`, `ci-workflow` |
| [k8s-cluster](k8s-cluster/SKILL.md) | K8s cluster management | Cluster operations | `k8s-gen`, `remote-exec` |
| [migration-helper](migration-helper/SKILL.md) | Database migration scripts | Schema changes | `database-ops`, `deploy-checklist` |

### Monitoring & Incident Response

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [remote-exec](remote-exec/SKILL.md) | SSH command execution | Server operations | `log-analyzer`, `k8s-cluster` |
| [log-analyzer](log-analyzer/SKILL.md) | Structured log analysis | Error triage, debugging | `remote-exec`, `incident-response` |
| [incident-response](incident-response/SKILL.md) | Incident response with RCA | Production incidents | `log-analyzer`, `deploy-checklist` |
| [llm-observability](llm-observability/SKILL.md) | LLM/Agent observability | Agent monitoring, tracing | `agent-eval`, `log-analyzer` |
| [cost-optimization](cost-optimization/SKILL.md) | Cloud cost analysis | Cost reduction | `k8s-cluster`, `ci-workflow` |
| [load-testing](load-testing/SKILL.md) | Load testing design | Performance testing | `deploy-checklist`, `ci-workflow` |

---

## 🔧 Phase 6: Productivity & Daily Tools

> **When:** Everyday development tasks that don't fit neatly into one phase.

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [shell-command](shell-command/SKILL.md) | NL → shell command | Daily terminal one-liners | `debug-helper`, `remote-exec` |
| [debug-helper](debug-helper/SKILL.md) | 5-step structured debugging | Any error or bug | `log-analyzer`, `shell-command` |
| [regex-buddy](regex-buddy/SKILL.md) | NL → regex + explanation | Pattern matching | `shell-command`, `data-pipeline` |
| [technical-article-writer](technical-article-writer/SKILL.md) | Research & write tech articles | Documentation, blogs | `doc-generator`, `explain-code` |
| [doc-generator](doc-generator/SKILL.md) | Auto-generate documentation | API docs, READMEs | `explain-code`, `technical-article-writer` |
| [meeting-notes](meeting-notes/SKILL.md) | Meeting minutes generator | Team syncs, standups | `user-story`, `task-loom` |
| [self-improve](self-improve/SKILL.md) | Self-improvement feedback loop | Skill optimization | `agent-eval`, `prompt-engineering` |
| [symlink-maker](symlink-maker/SKILL.md) | Create symbolic links | File system management | `shell-command`, `monorepo-manager` |

---

## 📚 Phase 7: Reference Cards

> **When:** Quick lookups for common tools and technologies. Not workflows — cheat sheets.

| Skill | Description | When to Use | Pairs With |
|-------|-------------|-------------|------------|
| [api-debug](api-debug/SKILL.md) | API debugging reference | HTTP debugging | `api-design`, `debug-helper` |
| [docker-essentials](docker-essentials/SKILL.md) | Docker reference | Container operations | `k8s-gen`, `ci-workflow` |
| [linux-ops](linux-ops/SKILL.md) | Linux operations reference | System administration | `remote-exec`, `shell-command` |
| [performance-profiling](performance-profiling/SKILL.md) | Performance profiling reference | Performance analysis | `load-testing`, `debug-helper` |
| [python-testing](python-testing/SKILL.md) | Python testing reference | Pytest patterns | `test-generator`, `test-strategy` |

---

## Quick Reference: Skills by Count

| Phase | Category | Count |
|-------|----------|-------|
| 📋 Requirements | `requirements` | 3 |
| 🏗️ Development | `development` | 25 |
| ✅ Quality | `quality` | 9 |
| 🔗 Source Control | `source-control` | 6 |
| 🚀 Operations | `operations` | 11 |
| 🔧 Productivity | `productivity` | 8 |
| 📚 Reference | `reference` | 5 |
| **Total** | | **67** |
