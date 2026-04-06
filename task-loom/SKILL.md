---
name: task-loom
description: "Professional project orchestration engine for large-scale PRD (10,000+ lines) multi-document projects. Features risk-first audit, state-machine driven workflow, and verification-driven execution."
---

# Task-Loom - Project Orchestration Engine

Project orchestration system for large-scale PRD projects with audit-first, state-machine driven workflow.

## Core Commands

| Command | Phase | Description |
|---------|-------|-------------|
| `/task-loom init <project_name> <prd_paths...>` | INIT | Initialize project workspace |
| `/task-loom audit` | AUDIT | Scan PRD for risks, generate audit report |
| `/task-loom plan` | PLAN | Build DAG, decompose tasks |
| `/task-loom execute [--task T_XXX]` | EXECUTE | Execute tasks in dependency order |
| `/task-loom verify [--task T_XXX]` | VERIFY | Run tests, verify completion |
| `/task-loom status` | ANY | View current project status |
| `/task-loom resume` | ANY | Resume from checkpoint |

## Workspace Structure

```
.claude/orchestra/
└── {{project_name}}/
    ├── manifest.json         # State hub (SSoT)
    ├── constitution.md       # Global invariants
    ├── vulnerability_report.md # Risk audit report
    ├── specs/                # Technical specification docs
    └── ledgers/              # Execution ledgers
```

## Workflow Phases

### Phase 1: INIT

**Trigger**: `/task-loom init <project_name> <prd_paths...>`

**Steps**:
1. Validate project name and PRD file existence
2. Create directory structure under `.claude/orchestra/{{project_name}}/`
3. Parse PRD documents, calculate SHA-256 hash
4. Extract global invariants (MUST/SHALL/REQUIRED keywords, security constraints) → write to `constitution.md`
5. Initialize `manifest.json` with schema_version, project_metadata, workflow state, empty DAG

### Phase 2: AUDIT

**Trigger**: `/task-loom audit`, workflow stage is INIT

**Steps**:
1. Sliding window scan (500 lines, 10% overlap) of all PRD documents
2. Identify risks by classification:

   **P0 (Critical) - Must Pause**:
   - Security: SQL injection, XSS, CSRF, auth bypass
   - Financial: Payment logic defects, amount calculation errors
   - Data: Sensitive data exposure, permission bypass
   - Concurrency: Deadlocks, race conditions
   - Availability: Single points of failure

   **P1 (High) - Should Confirm**:
   - Boundary conditions, missing state transitions
   - Performance bottlenecks (N+1, full table scans)
   - Uncovered exception scenarios

   **P2 (Normal) - Auto Log**:
   - Naming inconsistencies, documentation ambiguity

3. Generate `vulnerability_report.md`
4. HALT for P0 risks - user must confirm each:
   ```
   🔴 P0 Risk #1: [description]
   Suggestion: [fix suggestion]
   Accept suggestion [Y/n/skip]?
   ```
5. Update `manifest.json` workflow.stage to AUDIT

### Phase 3: PLAN

**Trigger**: `/task-loom plan`, workflow stage is AUDIT or INIT

**Steps**:
1. Identify functional modules from PRD
2. Decompose into tasks (types: MODULE_IMPL, TEST, INTEGRATE, REFACTOR)
3. Build DAG with dependencies:
   ```json
   {
     "id": "T_001",
     "type": "MODULE_IMPL",
     "title": "User Authentication Module",
     "status": "PENDING",
     "depends_on": [],
     "prd_refs": ["docs/prd/auth.md L1-200"],
     "artifacts": {
       "spec": "specs/auth.md",
       "ledger": null
     }
   }
   ```
4. Generate `specs/*.md` for each task with requirements, interfaces, data models, acceptance criteria

### Phase 4: EXECUTE

**Trigger**: `/task-loom execute [--task T_XXX]`, workflow stage is PLAN

**CRITICAL**: You must ACTUALLY WRITE CODE, not just update status.

**Steps**:

1. **Task Selection**: Get PENDING tasks with satisfied dependencies
   ```bash
   python scripts/dag_manager.py --project <name> next
   ```

2. **Context Loading (MANDATORY)** - Read before writing ANY code:
   - `.claude/orchestra/{{project_name}}/constitution.md` - global invariants
   - `.claude/orchestra/{{project_name}}/specs/T_XXX.md` - task specification
   - `.claude/orchestra/{{project_name}}/ledgers/T_YYY.md` - for each dependency

3. **Code Generation**:
   - Analyze task requirements from spec
   - Check global invariants for constraints
   - Check dependency ledgers for exported interfaces
   - CREATE actual source code files
   - ENSURE code follows all invariants

4. **Generate Ledger** after implementation:
   ```markdown
   # Ledger: T_001 - User Authentication Module

   ## Execution Info
   - Task ID: T_001
   - Status: COMPLETED

   ## Change Summary
   ### New Files
   - src/auth/login.ts
   - src/auth/middleware.ts

   ## Implicit Decisions
   1. JWT expiry set to 24h (not specified in PRD)

   ## Downstream Dependencies
   - T_002 needs: authMiddleware function in src/auth/middleware.ts
   ```

5. **Update State**:
   ```bash
   python scripts/dag_manager.py --project <name> update --id T_XXX --status COMPLETED
   ```

### Phase 5: VERIFY

**Trigger**: `/task-loom verify`, or auto-triggered in execute phase

**Steps**:
1. Detect test framework (Jest/Vitest/Pytest/go test)
2. Generate/update tests based on task spec
3. Execute tests
4. Handle failures: auto-fix, retry (max 3 times)
5. Circuit breaker: After 3 failures, SYSTEM_HALT, rollback Git

## Key Mechanisms

### Global Invariant Injection

Before each task, inject into system prompt:
```
【Global Invariants - Must Adhere】
The following rules from constitution.md are immutable constraints:
1. All database transactions must use row-level locking
2. All API responses must include requestId
...
```

### Checkpoint Resume

`/task-loom resume`:
1. Read `manifest.json`
2. Check `workflow.active_task_id`
3. Restore task state, continue from interruption point

### Circuit Breaker

| Condition | Behavior |
|-----------|----------|
| Task fails 3 times | SYSTEM_HALT, rollback Git |
| P0 risk not confirmed | AUDIT_HALT |
| Dependency task failed | Task → BLOCKED |
| Test coverage < 80% | VERIFY_HALT |

### Ledger Context Transfer

Task N+1 loads predecessor context:
```
【Predecessor Task Context】
From T_001:
- Implicit decisions: JWT expiry 24h
- Exported interfaces: authMiddleware(), User type
```

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/init_workspace.py` | Initialize workspace |
| `scripts/dag_manager.py` | DAG state management |
| `scripts/risk_scanner.py` | PRD risk scanning |
| `scripts/spec_generator.py` | Generate task specifications |
| `scripts/ledger_generator.py` | Generate execution ledgers |
| `scripts/status_viewer.py` | Project status viewer |
| `scripts/resume_handler.py` | Checkpoint resume handler |

## Reference Files

- [risk_classifications.md](references/risk_classifications.md) - Risk classification rules
- [ledger_template.md](references/ledger_template.md) - Ledger format template
