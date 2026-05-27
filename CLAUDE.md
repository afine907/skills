# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Claude Code skills - reusable prompt templates that extend Claude's capabilities. Each skill is a self-contained module with a `SKILL.md` file that defines its behavior.

Each skill has a `category` field in its SKILL.md frontmatter. See individual `*/SKILL.md` for details.

| Category | Phase |
|----------|-------|
| `requirements` | Product & Requirements |
| `development` | Architecture & Coding |
| `quality` | Code Quality & Testing |
| `source-control` | Version Control |
| `operations` | Deploy & Operate |
| `productivity` | Cross-phase Tools |
| `reference` | Reference Cards |

## Creating Skills

### Structure

```
my-skill/           # kebab-case directory name
  SKILL.md          # Required
  scripts/          # Optional: CLI tools
  references/       # Optional: templates, schemas
```

### SKILL.md

Must start with YAML frontmatter (all fields required):

```yaml
---
name: my-skill                    # Must match directory name
description: One-line trigger description for Claude to decide when to invoke.
category: productivity            # requirements|development|quality|source-control|operations|productivity|reference
---
```

Body sections (recommended): Title → Goal → Trigger conditions → Workflow → Best practices → Edge cases.

### Validate locally

```bash
python scripts/validate_skills.py
```

Checks: frontmatter fields, name-directory match, category validity, `[text](path)` links point to existing files.

## Running Tests

```bash
# Run all tests
pytest task-loom/tests/ -v

# Run specific test file
pytest task-loom/tests/test_dag_manager.py -v

# Run single test
pytest task-loom/tests/test_dag_manager.py::TestDAGManager::test_add_task -v
```

