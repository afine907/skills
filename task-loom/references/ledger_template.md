# Ledger Template

Each task generates a ledger file upon completion, recording execution details and context information.

## File Naming

`ledgers/T_XXX.md`, where XXX is the three-digit task ID.

## Template Structure

```markdown
# Ledger: {{task_id}} - {{task_title}}

## Execution Info

| Field | Value |
|-------|-------|
| Task ID | {{task_id}} |
| Task Type | MODULE_IMPL / TEST / INTEGRATE |
| Execution Time | ISO-8601 timestamp |
| Status | COMPLETED / FAILED / PARTIAL |
| Duration | Estimated time (minutes) |
| Retry Count | 0-3 |

## Change Summary

### New Files

| File Path | Purpose | Lines |
|-----------|---------|-------|
| src/auth/login.ts | Login logic implementation | 150 |
| src/auth/middleware.ts | Authentication middleware | 80 |

### Modified Files

| File Path | Change Description | Lines Added | Lines Deleted |
|-----------|-------------------|-------------|---------------|
| src/app.ts | Add auth routes | 5 | 0 |
| src/types/index.ts | Export User type | 1 | 0 |

### Deleted Files

| File Path | Deletion Reason |
|-----------|-----------------|
| - | - |

## Implicit Decisions

Record technical decisions made that weren't explicitly stated in PRD:

1. **Decision Point**: JWT expiry time
   - **Choice**: 24 hours
   - **Rationale**: Not specified in PRD, per industry standard balancing security and UX
   - **Impact**: Users need to re-login once per day

2. **Decision Point**: Password hashing algorithm
   - **Choice**: bcrypt, cost=12
   - **Rationale**: Balance security and performance, cost=12 takes ~250ms
   - **Impact**: Login API response time increases by ~300ms

3. **Decision Point**: Login failure limit
   - **Choice**: 5 attempts / 15 minutes
   - **Rationale**: Prevent brute force while not affecting normal users
   - **Impact**: Requires Redis to store failure count

## Exported Interfaces

Interfaces and data structures for downstream tasks:

### Functions

```typescript
// src/auth/middleware.ts
export function authMiddleware(req, res, next): void
// Validates JWT token, mounts user info to req.user

// src/auth/login.ts
export async function login(email: string, password: string): Promise<LoginResult>
// User login, returns JWT token
```

### Types

```typescript
// src/types/auth.ts
export interface User {
  id: string;
  email: string;
  role: 'admin' | 'user';
}

export interface LoginResult {
  success: boolean;
  token?: string;
  error?: string;
}
```

### Constants

```typescript
// src/auth/constants.ts
export const JWT_EXPIRY = '24h';
export const MAX_LOGIN_ATTEMPTS = 5;
export const LOCKOUT_DURATION = 15 * 60 * 1000; // 15 minutes in ms
```

## Downstream Dependencies

Resources from this task that other tasks need:

| Dependent Task | Resource Needed | Use Case |
|----------------|-----------------|----------|
| T_002 | authMiddleware function | Protect payment API |
| T_002 | User type | Payment record user association |
| T_003 | login function | User login page |

## Pending Verification

- [ ] Unit test: login function normal flow
- [ ] Unit test: login function wrong password
- [ ] Unit test: authMiddleware valid token
- [ ] Unit test: authMiddleware invalid token
- [ ] Integration test: complete login flow

## Notes

Important notes for downstream task developers:

1. **Redis Dependency**: This module requires Redis service, ensure T_000 completed Redis config
2. **Environment Variables**: Requires JWT_SECRET environment variable
3. **Database Migration**: Requires users table, see migrations/001_create_users.sql

## Error Log

If failed, record failure reasons:

| Time | Error Type | Error Message | Resolution |
|------|------------|---------------|------------|
| - | - | - | - |
```

## Usage Notes

Ledger files are automatically generated and managed by Loom, primarily for:

1. **Context Transfer**: Downstream tasks read upstream ledgers to understand completed work
2. **Decision Traceability**: Record reasons and impacts of implicit decisions
3. **Debugging Aid**: Quickly locate change scope when issues arise
4. **Documentation Generation**: Can auto-generate changelogs from ledgers
