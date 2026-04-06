# Risk Classification Guide

## P0 Risks (Critical)

**Definition**: Must be resolved before development, otherwise may cause severe consequences

### Security Vulnerabilities

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| SQL Injection | String concatenation in SQL | "SELECT * FROM users WHERE id=" + userId |
| XSS | Unescaped user input | innerHTML = userInput |
| CSRF | Missing CSRF Token | Form submission without token validation |
| Auth Bypass | Skipped permission check | Admin routes without authentication |
| Sensitive Data Exposure | Plaintext storage/transmission | Password stored as plaintext |

### Financial Security

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| Missing Idempotency | Payment callback without deduplication | Duplicate callbacks cause duplicate charges |
| Amount Calculation Error | Floating-point calculation | 0.1 + 0.2 !== 0.3 |
| State Inconsistency | Missing transaction | Deduction succeeded but order status not updated |

### Concurrency Issues

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| Deadlock | Inconsistent resource acquisition order | A→B, B→A |
| Race Condition | Lock-free update | count = count + 1 |
| Data Loss | No version control | Overwriting others' changes |

## P1 Risks (High)

**Definition**: Should be confirmed, may cause functional defects or performance issues

### Boundary Conditions

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| Undefined Input Range | Missing parameter validation | age can be negative |
| Missing Null Check | No null check | user.address.city |
| Array Out of Bounds | No length check | items[0] direct access |

### State Transitions

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| Illegal State Transition | Missing state machine definition | PENDING → COMPLETED skipping PROCESSING |
| Missing Intermediate States | Only success/failure | No processing state |

### Performance Bottlenecks

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| N+1 Queries | Query inside loop | for user in users: getOrders(user) |
| Full Table Scan | Query without index | SELECT * FROM orders WHERE status = ? |
| Memory Leak | Unbounded cache growth | cache[key] = value without eviction policy |

## P2 Risks (Normal)

**Definition**: Log only, can be handled during development

### Documentation Quality

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| Naming Inconsistency | Multiple names for same concept | userId / user_id / uid |
| Vague Description | Missing specific details | "Should be fast" |
| Missing Details | Missing parameter description | API doc without response format |

### Non-critical Features

| Risk Type | Detection Pattern | Example |
|-----------|-------------------|---------|
| Missing Logging | No logging design | Critical operations without log records |
| Missing Monitoring | No metrics defined | Performance without monitoring |
| Missing Documentation | No usage instructions | New features without usage docs |

## Risk Scanning Patterns

```python
RISK_PATTERNS = {
    "P0": {
        "sql_injection": r"(SELECT|INSERT|UPDATE|DELETE)\s+.*\+.*",
        "plaintext_password": r"password\s*[=:]\s*['\"]",
        "missing_idempotency": r"callback|webhook(?!.*idempoten)",
        "race_condition": r"(increment|decrement|update)\s+\w+\s*(?!lock|transaction)",
    },
    "P1": {
        "missing_null_check": r"\.\w+\.\w+(?!\s*\?)",
        "missing_validation": r"param|input|request(?!.*valid)",
        "n_plus_one": r"for\s+\w+\s+in\s+\w+.*:\s*\w+\.\w+\(",
    },
    "P2": {
        "inconsistent_naming": r"(userId|user_id|uid)",
        "missing_docs": r"(TODO|FIXME|TBD)",
    }
}
```

## Processing Flow

```
P0 Risk → Pause execution → Display details → User confirmation → Inject into specs
P1 Risk → Log to report → Suggest confirmation → Can continue
P2 Risk → Auto log → Auto handle
```
