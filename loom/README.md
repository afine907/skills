# Loom - Professional Project Orchestration Engine

A "hardcore" project orchestration system designed for large-scale PRD (10,000+ lines) projects.

## Features

- **Audit-First**: Identify logic defects before writing code
- **State-Machine Driven**: Structured workflow management (INIT → AUDIT → PLAN → EXECUTE → VERIFY)
- **Verification-Driven**: Tests must pass for completion
- **Context Continuity**: Ledger system for cross-task knowledge transfer
- **Risk Classification**: P0/P1/P2 risk levels with automated scanning

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/loom-skill.git

# The skill can be used directly with Claude Code
# Place it in your .claude/skills/ directory
```

## Quick Start

```bash
# 1. Initialize a new project
python scripts/init_workspace.py my-project docs/prd/*.md

# 2. Scan for risks
python scripts/risk_scanner.py --project my-project --save

# 3. Build task DAG
python scripts/dag_manager.py --project my-project add --id T_001 --type MODULE_IMPL --title "Auth Module"

# 4. Generate specifications
python scripts/spec_generator.py --project my-project

# 5. View project status
python scripts/status_viewer.py --project my-project

# 6. Generate execution ledger after completing task
python scripts/ledger_generator.py --project my-project --task T_001 --status COMPLETED
```

## Commands

| Command | Phase | Description |
|---------|-------|-------------|
| `/loom init <project_name> <prd_paths...>` | INIT | Initialize project workspace |
| `/loom audit` | AUDIT | Scan PRD for risks, generate audit report |
| `/loom plan` | PLAN | Build DAG, decompose tasks |
| `/loom execute [--task T_XXX]` | EXECUTE | Execute tasks in dependency order |
| `/loom verify [--task T_XXX]` | VERIFY | Run tests, verify completion |
| `/loom status` | ANY | View current project status |
| `/loom resume` | ANY | Resume from checkpoint |

## Workspace Structure

```
.claude/orchestra/
└── {{project_name}}/
    ├── manifest.json         # State hub (SSoT)
    ├── constitution.md       # Global invariants
    ├── vulnerability_report.md # Risk audit report
    ├── specs/                # Technical specification docs
    │   └── T_001.md
    └── ledgers/              # Execution ledgers
        └── T_001.md
```

## Scripts

| Script | Description |
|--------|-------------|
| `init_workspace.py` | Initialize workspace |
| `dag_manager.py` | DAG state management |
| `risk_scanner.py` | PRD risk scanning |
| `spec_generator.py` | Generate task specifications |
| `ledger_generator.py` | Generate execution ledgers |
| `status_viewer.py` | Project status viewer |
| `resume_handler.py` | Checkpoint resume handler |
| `manifest_migrator.py` | Schema migration |

## Risk Classification

### P0 (Critical) - Must Confirm
- Security vulnerabilities: SQL injection, XSS, CSRF, auth bypass
- Financial security: Payment logic defects
- Data security: Sensitive data exposure

### P1 (High) - Should Review
- Boundary conditions
- State transitions
- Performance bottlenecks

### P2 (Normal) - Auto Log
- Naming inconsistencies
- Documentation ambiguity
- Non-critical feature gaps

## Development

```bash
# Run tests
cd loom
python -m pytest tests/ -v

# Or with specific test file
python tests/test_dag_manager.py
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## Author

Generated with Claude Code
