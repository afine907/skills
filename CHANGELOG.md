# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added - 2026-05-29 (Phase 2: Gap Analysis Completion)

#### New Skills (6 skills added)

**Development (5 new)**
- `typescript-service-creator` - TypeScript backend scaffolding (Express/Hono/Fastify)
- `vue-service-creator` - Vue 3/Nuxt 3 frontend project scaffolding
- `mobile-service-creator` - React Native/Flutter mobile app scaffolding
- `data-pipeline` - ETL pipeline design (Airflow, dbt, Great Expectations)
- `code-migration` - Framework/language migration strategies (Python 2→3, JS→TS)

**Operations (1 new)**
- `cost-optimization` - Cloud cost analysis and AI token cost tracking

#### Improved Skills
- `python-testing` - Expanded from cheat sheet to comprehensive testing guide

#### Infrastructure
- `scripts/validate_skills.py` - Fixed link checker to skip links inside code blocks
- All 25 gap analysis skills now implemented (P0/P1/P2 complete)

### Statistics
- **Total Skills**: 67 (was 61, +10%)
- **Reference Files**: 90+ templates, guides, and cheat sheets
- **Validation**: 0 errors, 213 warnings

---

### Added - 2026-05-29 (Phase 1: Massive Expansion: 37 → 61 Skills)

#### New Skills (24 skills added)

**Requirements (2 new)**
- `tech-spec` - Technical specification design (architecture, modules, APIs, data models)
- `user-story` - User story writing with acceptance criteria and story point estimation

**Development (13 new)**
- `api-design` - RESTful/GraphQL API design with OpenAPI spec generation
- `api-mocking` - API mock service for parallel frontend/backend development
- `auth-patterns` - Authentication/authorization patterns (JWT, OAuth2, RBAC, MFA)
- `caching-strategy` - Cache design (Cache-Aside, Redis, invalidation strategies)
- `cli-tool-creator` - CLI tool development (Python Typer, Node.js Commander)
- `database-seeding` - Database seed data generation with factories
- `feature-flag` - Feature flag system for canary releases and A/B testing
- `graphql-design` - GraphQL schema design with DataLoader and Relay pagination
- `i18n-helper` - Internationalization (i18n) implementation
- `microservice-patterns` - Microservice architecture patterns (Saga, service discovery, circuit breaker)
- `monorepo-manager` - Monorepo project management (Turborepo, pnpm workspace)
- `react-service-creator` - React project scaffolding (Next.js/Vite, Zustand, Tailwind)
- `websocket-service` - WebSocket real-time communication service

**Quality (3 new)**
- `accessibility-audit` - Web accessibility (a11y) audit (WCAG 2.1, ARIA)
- `code-review` - Structured code review across multiple dimensions
- `security-scan` - Security vulnerability scanning (OWASP Top 10)
- `test-strategy` - Test strategy design (test pyramid, coverage targets)

**Operations (3 new)**
- `incident-response` - Incident response with RCA report generation
- `load-testing` - Load testing design and execution (K6, Locust)
- `migration-helper` - Database migration scripts and validation

**Productivity (1 new)**
- `doc-generator` - Auto-generate technical documentation from code

**Source Control (1 new)**
- `git-branch` - Git branch management strategies (Git Flow, Trunk-Based)

#### Improved Skills (3 skills rewritten)
- `explain-code` - Expanded from 6 lines to full workflow with multiple analysis dimensions
- `api-debug` - Expanded from 68 lines to comprehensive debugging guide
- `performance-profiling` - Expanded from 79 lines to full profiling methodology

#### Infrastructure
- `pyproject.toml` - Added project metadata and dependency management
- `tests/` - Added comprehensive test framework (535 tests)
  - `tests/test_validate_skills.py` - Unit tests for validation script
  - `tests/test_skill_structure.py` - Integration tests for all skills
  - `tests/conftest.py` - Shared test fixtures
  - `tests/fixtures/` - Example good/bad skill files
- `scripts/validate_skills.py` - Enhanced with 12 new checks
  - Recommended sections check
  - Description length validation
  - Duplicate skill name detection
  - Broken internal markdown link check
  - `--verbose` and `--fix` flags
  - Summary table output
- `GAP_ANALYSIS.md` - Comprehensive gap analysis with prioritized skill roadmap

### Statistics (Phase 1)
- **Total Skills**: 61 (was 37, +65%)
- **Categories**: 7 (requirements, development, quality, source-control, operations, productivity, reference)
- **Test Coverage**: 535 tests passing
- **Reference Files**: 80+ templates, guides, and cheat sheets

---

## [0.1.0] - 2026-05-28

### Added
- Initial release with 37 skills
- Core skills: task-loom, commit, wo-yao-yan-pai, explain-code
- Validation script (scripts/validate_skills.py)
- CI pipeline (.github/workflows/ci.yml)
- Documentation (README.md, README_CN.md, wiki/)
