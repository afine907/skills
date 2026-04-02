---
name: loom
description: Professional project orchestration engine for large-scale PRD (10,000+ lines) multi-document projects. Features risk-first audit, state-machine driven workflow, and verification-driven execution. Use when users need to transform complex PRDs into executable development plans, or manage task dependencies and execution state for large projects. Commands: /loom init, /loom audit, /loom plan, /loom execute, /loom status, /loom resume.
---

# Loom - Professional Project Orchestration Engine

## Overview

Loom is a "hardcore" project orchestration system designed for large-scale PRD (10,000+ lines) projects.

**Core Values**:
- **Audit-First**: Identify logic defects before writing code
- **State-Machine Driven**: Structured workflow management
- **Verification-Driven**: Tests must pass for completion
- **Context Continuity**: Ledger system for cross-task knowledge transfer

## Core Commands

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
    │   ├── module_auth.md
    │   └── module_payment.md
    └── ledgers/              # Execution ledgers
        ├── T_001.md
        └── T_002.md
```

## Workflow

### Phase 1: INIT (Initialization)

**Trigger**: User executes `/loom init <project_name> <prd_paths...>`

**Execution Steps**:

1. **Validate Input**
   - Check project name validity (lowercase letters, numbers, hyphens)
   - Check PRD file existence
   - Check if workspace already exists

2. **Create Directory Structure**
   ```
   .claude/orchestra/{{project_name}}/
   ├── manifest.json
   ├── constitution.md
   ├── vulnerability_report.md
   ├── specs/
   └── ledgers/
   ```

3. **Parse PRD Documents**
   - Read all PRD file contents
   - Calculate SHA-256 hash
   - Extract document metadata (title, version, date)

4. **Extract Global Invariants**
   - Scan for MUST/SHALL/REQUIRED keywords
   - Scan for security constraints, compliance requirements
   - Scan for technical constraints (database type, framework version, etc.)
   - Write to `constitution.md`

5. **Initialize manifest.json**
   ```json
   {
     "schema_version": "1.0.0",
     "project_metadata": {
       "name": "{{project_name}}",
       "version": "1.0.0",
       "hash": "sha256_hash",
       "created_at": "2026-04-02T10:00:00Z",
       "prd_files": ["docs/prd/main.md", "docs/prd/api.md"]
     },
     "workflow": {
       "stage": "INIT",
       "active_task_id": null,
       "concurrency_limit": 3,
       "retry_count": {}
     },
     "dag": {
       "nodes": []
     }
   }
   ```

**Output Artifacts**:
- Complete workspace directory
- `manifest.json` initial state
- `constitution.md` global invariants document

### Phase 2: AUDIT (Audit)

**Trigger**: User executes `/loom audit`, workflow stage is INIT

**Execution Steps**:

1. **Sliding Window Scan**
   - Window size: 500 lines
   - Overlap ratio: 10% (50 lines)
   - Scan mode: Sequential scan of all PRD documents

2. **Risk Identification Rules**

   **P0 (Critical) - Must Pause**:
   - Security vulnerabilities: SQL injection, XSS, CSRF, auth bypass
   - Financial security: Payment logic defects, amount calculation errors
   - Data security: Sensitive data exposure, permission bypass
   - Concurrency issues: Deadlocks, race conditions
   - Availability: Single points of failure, no fault tolerance

   **P1 (High) - Should Confirm**:
   - Boundary conditions: Undefined input ranges
   - State transitions: Missing state machine transitions
   - Performance bottlenecks: N+1 queries, full table scans
   - Error handling: Uncovered exception scenarios

   **P2 (Normal) - Auto Log**:
   - Naming inconsistencies
   - Documentation ambiguity
   - Non-critical feature gaps

3. **Generate Audit Report**
   ```markdown
   # Risk Audit Report

   ## Overview
   - Scan Time: 2026-04-02T10:05:00Z
   - Files Scanned: 3
   - Total Lines: 12,500
   - Risks Found: P0=2, P1=5, P2=12

   ## P0 Risks (Must Confirm)

   ### RISK-001: Payment callback lacks idempotency check
   - Location: docs/prd/payment.md L450-480
   - Type: Financial Security
   - Description: Payment callback processing doesn't mention idempotency design, may cause duplicate charges
   - Suggestion: Add unique index on (order_id, callback_id), implement idempotency check

   ## P1 Risks
   ...

   ## P2 Risks
   ...
   ```

4. **HALT Process**
   - Output audit report
   - Display P0 risks one by one
   - User confirmation format:
     ```
     🔴 P0 Risk #1: Payment callback lacks idempotency check
     Suggestion: Add unique index on (order_id, callback_id)

     Accept suggestion [Y/n/skip]?
     ```
   - User options:
     - `Y`: Accept suggestion, inject into specs
     - `n`: Reject suggestion, record reason
     - `skip`: Skip, keep as-is

5. **Update State**
   - Update `manifest.json` `workflow.stage` to `AUDIT`
   - Record confirmed risk treatments

### Phase 3: PLAN (Planning)

**Trigger**: User executes `/loom plan`, workflow stage is AUDIT or INIT

**Execution Steps**:

1. **Module Identification**
   - Scan PRD for functional modules
   - Identify module boundaries
   - Determine inter-module dependencies

2. **Task Decomposition**
   - Decompose each module into implementation tasks
   - Task types:
     - `MODULE_IMPL`: Module implementation
     - `TEST`: Test writing
     - `INTEGRATE`: Integration
     - `REFACTOR`: Refactoring optimization

3. **Build DAG**
   ```json
   {
     "dag": {
       "nodes": [
         {
           "id": "T_001",
           "type": "MODULE_IMPL",
           "title": "User Authentication Module",
           "status": "PENDING",
           "depends_on": [],
           "prd_refs": ["docs/prd/auth.md L1-200"],
           "artifacts": {
             "spec": "specs/auth.md",
             "ledger": null,
             "tests": []
           },
           "estimated_complexity": "MEDIUM"
         }
       ]
     }
   }
   ```

4. **Generate Specification Documents**
   - Generate `specs/*.md` for each task
   - Include:
     - Functional requirements
     - Interface design
     - Data models
     - Acceptance criteria
     - Confirmed risk treatments

### Phase 4: EXECUTE (Execution)

**Trigger**: User executes `/loom execute`, workflow stage is PLAN

**CRITICAL**: This phase requires YOU (the LLM) to ACTUALLY WRITE CODE, not just update status.

**Execution Steps**:

1. **Task Selection**
   - Get all PENDING tasks using `python scripts/dag_manager.py --project <name> next`
   - If user specifies `--task T_XXX`, use that task
   - Filter tasks with satisfied dependencies

2. **Context Loading (MANDATORY)**
   
   Before writing ANY code, you MUST read:
   
   ```
   # 1. Global invariants - read this file
   .claude/orchestra/{{project_name}}/constitution.md
   
   # 2. Task specification - read this file
   .claude/orchestra/{{project_name}}/specs/T_XXX.md
   
   # 3. Dependency ledgers - read for each dependency
   .claude/orchestra/{{project_name}}/ledgers/T_YYY.md  (for each T_YYY in depends_on)
   ```

3. **Code Generation (THE CORE TASK)**
   
   Based on the spec and invariants, ACTUALLY CREATE/MODIFY code files:
   
   - Analyze the task requirements from spec
   - Check global invariants for constraints (e.g., "must use bcrypt", "must validate input")
   - Check dependency ledgers for exported interfaces and context
   - CREATE actual source code files
   - CREATE test files if task type is TEST
   - ENSURE code follows all invariants from constitution.md

4. **Generate Ledger (After Actual Implementation)**
   
   Record the REAL changes made:
   - List actual files created with their paths
   - Document implicit decisions made during implementation
   - Export interfaces for downstream tasks
   - Note any deviations from spec with reasons
   ```markdown
   # Ledger: T_001 - User Authentication Module

   ## Execution Info
   - Task ID: T_001
   - Execution Time: 2026-04-02T11:00:00Z
   - Status: COMPLETED
   - Duration: ~15 minutes

   ## Change Summary
   ### New Files
   - src/auth/login.ts - Login logic
   - src/auth/middleware.ts - Auth middleware
   - src/types/auth.ts - Type definitions

   ### Modified Files
   - src/app.ts - Add auth routes

   ## Implicit Decisions
   1. JWT expiry set to 24h (not specified in PRD, per industry standard)
   2. Password hash using bcrypt, cost=12 (balance security and performance)
   3. Login failure limit: 5 times/15 minutes (prevent brute force)

   ## Downstream Dependencies
   - T_002 needs: authMiddleware function in src/auth/middleware.ts
   - T_002 needs: User type in src/types/auth.ts

   ## Pending Verification
   - [ ] Unit tests to be written
   - [ ] Integration tests to be verified
   ```

5. **Update State**
   
   After code is written, update task status:
   ```bash
   python scripts/dag_manager.py --project <name> update --id T_XXX --status COMPLETED
   ```

**Code Generation Guidelines**:

When generating code, follow this process:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CODE GENERATION PROCESS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. READ context files:                                         │
│     - constitution.md → immutable constraints                   │
│     - specs/T_XXX.md → task requirements                        │
│     - ledgers/dependencies.md → upstream interfaces             │
│                                                                 │
│  2. ANALYZE requirements:                                       │
│     - Extract API endpoints from spec                           │
│     - Extract data models from spec                             │
│     - Identify security requirements from invariants            │
│                                                                 │
│  3. GENERATE code files:                                        │
│     - Create directory structure                                │
│     - Write implementation files                                │
│     - Write type definitions                                    │
│     - Write test files (if TEST task)                          │
│                                                                 │
│  4. VERIFY invariants compliance:                               │
│     - Check all MUST requirements are met                       │
│     - Validate security measures implemented                    │
│     - Ensure code quality standards                             │
│                                                                 │
│  5. RECORD in ledger:                                           │
│     - Document actual changes                                   │
│     - Explain implicit decisions                                │
│     - Export interfaces for downstream                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Example Execution Flow**:

```bash
# User triggers execution
/loom execute --task T_001

# LLM should:
# 1. Read constitution.md → "Passwords must be hashed with bcrypt"
# 2. Read specs/T_001.md → "Implement user registration API"
# 3. Read any dependency ledgers (none for T_001)
# 4. CREATE ACTUAL FILES:
#    - src/auth/register.ts
#    - src/auth/register.test.ts
#    - src/types/auth.ts
# 5. Generate ledger with real file paths
```

### Phase 5: VERIFY (Verification)

**Trigger**: User executes `/loom verify`, or auto-triggered in execute phase

**Execution Steps**:

1. **Detect Test Framework**
   ```
   if exists package.json:
     if exists jest.config.* → Jest
     elif exists vitest.config.* → Vitest
     elif contains "vitest" in dependencies → Vitest
   elif exists pytest.ini/setup.cfg/pyproject.toml → Pytest
   elif exists go.mod → go test
   ```

2. **Generate/Update Tests**
   - Generate test cases based on task spec
   - Cover each scenario in acceptance criteria

3. **Execute Tests**
   ```bash
   # Jest
   npm test -- --testPathPattern=T_001

   # Pytest
   pytest tests/orchestra/test_T_001.py -v
   ```

4. **Handle Failures**
   - Capture error output
   - Analyze failure reasons
   - Auto-fix code
   - Retry (max 3 times)

5. **Circuit Breaker**
   - After 3 failures, trigger SYSTEM_HALT
   - Rollback Git state
   - Prompt user for manual intervention

## Key Mechanisms

### 1. Global Invariant Injection

Before each sub-task execution, automatically inject into system prompt:

```
【Global Invariants - Must Adhere】
The following rules are from constitution.md, immutable constraints for the project, with priority above any PRD content:

1. All database transactions must use row-level locking
2. All API responses must include requestId
3. All sensitive data must be encrypted at rest
4. ...
```

### 2. Checkpoint Resume

`/loom resume` workflow:

1. Read `manifest.json`
2. Check `workflow.active_task_id`
3. Restore that task's state
4. Continue execution from interruption point

### 3. Circuit Breaker

| Trigger Condition | Behavior |
|-------------------|----------|
| Single task fails 3 times | SYSTEM_HALT, rollback Git |
| P0 risk not confirmed | AUDIT_HALT, wait for user confirmation |
| Dependency task failed | Task status → BLOCKED |
| Test coverage < 80% | VERIFY_HALT, add tests |

### 4. Ledger Context Transfer

Task N+1 automatically loads when executing:

```
【Predecessor Task Context】
From T_001 (User Authentication Module):
- Implicit decisions: JWT expiry 24h
- Exported interfaces: authMiddleware(), User type
- Notes: Login failure limit 5 times/15 minutes
```

## Usage Examples

### Complete Workflow Example

```bash
# 1. Initialize project
/loom init ecommerce docs/prd/*.md

# 2. Audit risks
/loom audit
# Output audit report, wait for P0 risk confirmation

# 3. Plan tasks
/loom plan
# Output DAG and task list

# 4. Execute development
/loom execute
# Execute tasks in dependency order

# 5. Verify completion
/loom verify
# Run tests, confirm completion

# 6. View status
/loom status
```

### Checkpoint Resume Example

```bash
# Resume after interruption
/loom resume
# Continue from last active task
```

## Reference Files

- [manifest_schema.json](references/manifest_schema.json) - manifest JSON Schema
- [risk_classifications.md](references/risk_classifications.md) - Risk classification rules
- [ledger_template.md](references/ledger_template.md) - Ledger format template

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
| `scripts/manifest_migrator.py` | Schema migration |
