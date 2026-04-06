# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Claude Code skills - reusable prompt templates that extend Claude's capabilities. Each skill is a self-contained module with a `SKILL.md` file that defines its behavior.

## Skills

### Task-Loom (`/task-loom`)
A project orchestration engine for large-scale PRD (10,000+ lines) projects. Manages the full workflow from PRD analysis to code generation.

**Workflow phases**: INIT → AUDIT → PLAN → EXECUTE → VERIFY

**Key files**:
- `task-loom/SKILL.md` - Skill definition and workflow documentation
- `task-loom/scripts/` - Python utilities for DAG management, workspace init, risk scanning
- `task-loom/references/` - JSON schemas and templates

### Commit (`/commit`)
Analyzes staged git changes and generates semantic commit messages following Conventional Commits spec.

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
