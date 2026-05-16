# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Claude Code skills - reusable prompt templates that extend Claude's capabilities. Each skill is a self-contained module with a `SKILL.md` file that defines its behavior.

Skills are categorized by SDLC phase via the `category` field in SKILL.md frontmatter:

| Category | Phase | Skills |
|----------|-------|--------|
| `requirements` | Product & Requirements | requirements-analyzer |
| `development` | Architecture & Coding | task-loom |
| `quality` | Code Quality & Testing | wo-yao-yan-pai, explain-code, test-generator |
| `source-control` | Version Control | commit, commit-diff-analyzer, pr-description, changelog-generator |
| `operations` | Deploy & Operate | ci-workflow, remote-exec, log-analyzer, deploy-checklist |
| `productivity` | Cross-phase Tools | technical-article-writer, shell-command, debug-helper, regex-buddy, prompt-engineering, meeting-notes |
| `reference` | Reference Cards (type: reference) | api-debug, docker-essentials, linux-ops, performance-profiling, python-testing |

## Skills

### Task-Loom (`/task-loom`, category: development)
A project orchestration engine for large-scale PRD (10,000+ lines) projects. Manages the full workflow from PRD analysis to code generation.

**Workflow phases**: INIT → AUDIT → PLAN → EXECUTE → VERIFY

**Key files**:
- `task-loom/SKILL.md` - Skill definition and workflow documentation
- `task-loom/scripts/` - Python utilities for DAG management, workspace init, risk scanning
- `task-loom/references/` - JSON schemas and templates

### Commit (`/commit`, category: source-control)
Analyzes staged git changes and generates semantic commit messages following Conventional Commits spec.

### Test-Generator (`/test-generator`, category: quality)
Auto-generates pytest test suites from source code analysis. Covers normal paths, edge cases, and error scenarios. Pairs with wo-yao-yan-pai for review-then-test workflow.

### Log-Analyzer (`/log-analyzer`, category: operations)
Parses and analyzes server logs (Nginx, JSON, syslog, stacktraces). Detects anomaly patterns, error bursts, and performance degradation. Pairs with remote-exec for fetch-then-analyze workflow.

### CI-Workflow (`/ci-workflow`, category: operations)
Natural language → CI configuration (GitHub Actions / GitLab CI) generator. Maps user descriptions to YAML pipeline configs with platform detection, per-section explanation, and built-in security audit. Covers build/test, Docker push, deploy, release, lint, and security scanning. Pattern library in [references/patterns.md](ci-workflow/references/patterns.md).

### Shell-Command (`/shell-command`, category: productivity)
Natural language → shell command translator. Maps user descriptions to bash commands with safety level classification (safe / confirm / reject). Covers file ops, process management, network, Docker, Git and more. Reference patterns in [references/common-patterns.md](shell-command/references/common-patterns.md).

### Debug-Helper (`/debug-helper`, category: productivity)
Structured debugging with a fixed 5-step analysis pipeline: locate → context → hypothesis → verify → fix. Handles Python/Node.js/Go exceptions, HTTP errors, system errors, stack traces, and test failures. Error pattern library in [references/patterns.md](debug-helper/references/patterns.md).

### Regex-Buddy (`/regex-buddy`, category: productivity)
Natural language → regex + explanation + test cases in one shot. Outputs structured JSON with per-token explanation, test cases, edge cases, and alternatives. Regex cheat-sheet in [references/cheat-sheet.md](regex-buddy/references/cheat-sheet.md).

### PR-Description (`/pr-description`, category: source-control)
Analyzes git diff (branch-level, not staged) and generates structured PR descriptions with summary, changes grouped by module, breaking changes, and test plan. Optionally creates the PR via `gh pr create`. See [pr-description/SKILL.md](pr-description/SKILL.md).

### Changelog-Generator (`/changelog-generator`, category: source-control)
Reads git tag/commit ranges and generates CHANGELOG.md following Keep a Changelog format. Groups commits by semantic type (feat, fix, refactor, etc.), detects breaking changes, and suggests version bumps. See [changelog-generator/SKILL.md](changelog-generator/SKILL.md).

### Deploy-Checklist (`/deploy-checklist`, category: operations)
Generates pre-deployment checklists tailored to project type (web backend, frontend, mobile, microservice, etc.) and detected changes (DB migration, config update, dependency change). Covers backup, monitoring, rollback, and post-deploy verification. See [deploy-checklist/SKILL.md](deploy-checklist/SKILL.md).

### Prompt-Engineering (`/prompt-engineering`, category: productivity)
Transforms task descriptions into optimized LLM prompts. Supports multiple structural templates (classification, generation, chain-of-thought, code generation) with persona design, output control, and defensive prompt techniques. Dogfooding: useful for creating skills in this repo. See [prompt-engineering/SKILL.md](prompt-engineering/SKILL.md).

### Meeting-Notes (`/meeting-notes`, category: productivity)
Converts meeting transcripts or rough notes into structured meeting minutes. Extracts discussion points, decisions, and action items with owners. Handles voice-to-text cleanup, technical discussion deep-dives, and minimal-input fallback. See [meeting-notes/SKILL.md](meeting-notes/SKILL.md).

## Running Tests

```bash
# Run all tests
pytest task-loom/tests/ -v

# Run specific test file
pytest task-loom/tests/test_dag_manager.py -v

# Run single test
pytest task-loom/tests/test_dag_manager.py::TestDAGManager::test_add_task -v
```

## Task-Loom Script Usage

The Python scripts in `task-loom/scripts/` are CLI tools used by the skill:

```bash
# Initialize workspace
python task-loom/scripts/init_workspace.py <project_name> <prd_paths...>

# DAG management
python task-loom/scripts/dag_manager.py --project <name> add --id T_001 --type MODULE_IMPL --title "Task"
python task-loom/scripts/dag_manager.py --project <name> update --id T_001 --status COMPLETED
python task-loom/scripts/dag_manager.py --project <name> next

# Risk scanning
python task-loom/scripts/risk_scanner.py --project <name>
```

## Architecture Notes

### Manifest Structure
The `manifest.json` is the single source of truth (SSoT) for project state:
- `workflow.stage` - Current phase (INIT/AUDIT/PLAN/EXECUTE/VERIFY)
- `workflow.active_task_id` - Currently executing task
- `dag.nodes` - Task definitions with dependencies

### Task Dependency Graph
Tasks form a DAG where edges represent dependencies. The `DAGManager` class handles:
- Cycle detection when adding tasks
- Dependency satisfaction checking
- Task state transitions (PENDING → IN_PROGRESS → COMPLETED/FAILED)

### Workspace Location
All generated files go to `.claude/orchestra/<project_name>/`:
- `manifest.json` - State hub
- `constitution.md` - Global invariants extracted from PRD
- `specs/` - Task specifications
- `ledgers/` - Execution records
