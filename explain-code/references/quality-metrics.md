# Code Quality Metrics Reference

## Complexity Metrics

### Cyclomatic Complexity

Measures the number of independent paths through code. Higher = harder to test and maintain.

| Complexity | Risk | Action |
|------------|------|--------|
| 1-10 | Low | Simple, easy to test |
| 11-20 | Moderate | Consider refactoring |
| 21-50 | High | Should refactor |
| 50+ | Very High | Must refactor |

```python
# Complexity = 1 (base) + 3 (if/elif/else) + 2 (for, if) = 6
def process_order(order):
    if order.is_valid():           # +1
        if order.is_premium():     # +1
            apply_discount(order)
        for item in order.items:   # +1
            if item.is_digital:    # +1
                send_download(item)
    elif order.is_pending():       # +1
        reminder(order)
    else:                          # +1
        cancel(order)
```

**How to reduce**: Extract methods, use strategy pattern, replace conditionals with polymorphism.

### Cognitive Complexity

Measures how hard code is to understand (by a human). Unlike cyclomatic complexity, it penalizes nesting.

```python
# High cognitive complexity (nesting + flow breaks)
def process(data):
    if data:                          # +1 (nesting = 1)
        for item in data:             # +1 (nesting = 2)
            if item.active:           # +1 (nesting = 3)
                if item.valid:        # +1 (nesting = 4)
                    result.append(item)

# Lower cognitive complexity (early returns, flat structure)
def process(data):
    if not data:
        return []

    result = []
    for item in data:
        if not item.active or not item.valid:
            continue
        result.append(item)
    return result
```

## Maintainability Metrics

### Maintainability Index

Composite metric (0-100) combining:
- Halstead volume (code length/vocabulary)
- Cyclomatic complexity
- Lines of code

| Score | Rating | Action |
|-------|--------|--------|
| 85-100 | Excellent | No action needed |
| 65-84 | Good | Monitor |
| 40-64 | Moderate | Consider refactoring |
| 0-39 | Difficult | Refactor urgently |

### Code Churn

Frequency of changes to a file. High churn in complex files indicates problems.

```
Churn = Number of commits modifying the file / Time period

High churn + High complexity = Hot spot (needs attention)
High churn + Low complexity = Active feature (normal)
Low churn + High complexity = Legacy risk
```

### Technical Debt Ratio

```
TD Ratio = (Remediation Cost) / (Total Development Cost) * 100%

Target: < 5%
Acceptable: 5-10%
Warning: 10-20%
Critical: > 20%
```

## Coverage Metrics

### Code Coverage

| Metric | What It Measures | Target |
|--------|------------------|--------|
| Line Coverage | % of lines executed | >= 80% |
| Branch Coverage | % of branches taken | >= 75% |
| Function Coverage | % of functions called | >= 90% |
| Condition Coverage | % of boolean sub-expressions | >= 70% |

```bash
# Python
pytest --cov=src --cov-report=html

# JavaScript
jest --coverage --coverageReporters=html

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### Mutation Testing

Measures test quality by introducing small code changes (mutations) and checking if tests catch them.

```
Mutation Score = Killed Mutants / Total Mutants * 100%

Target: >= 80%
```

```bash
# Python
mutmut run --paths-to-mutate=src/

# JavaScript
npx stryker run
```

## Size Metrics

### Lines of Code (LOC)

| File Size | Action |
|-----------|--------|
| < 100 lines | Good for most files |
| 100-300 lines | Acceptable |
| 300-500 lines | Consider splitting |
| 500+ lines | Likely needs refactoring |

### Method/Function Length

| Length | Action |
|--------|--------|
| < 20 lines | Ideal |
| 20-50 lines | Acceptable |
| 50-100 lines | Consider extracting |
| 100+ lines | Should be refactored |

### Parameters per Function

| Count | Action |
|-------|--------|
| 0-3 | Ideal |
| 4-5 | Consider options object |
| 6+ | Too many - refactor |

## Coupling Metrics

### Afferent Coupling (Ca)

Number of classes that depend on this class. High Ca = high impact of changes.

### Efferent Coupling (Ce)

Number of classes this class depends on. High Ce = fragile, hard to test.

### Instability

```
I = Ce / (Ca + Ce)

0 = Completely stable (many dependents, no dependencies)
1 = Completely unstable (no dependents, many dependencies)
```

### Coupling Goals

| Metric | Target | Warning |
|--------|--------|---------|
| Ca | Context-dependent | Sudden increases |
| Ce | < 7 | > 10 |
| I | 0.3-0.7 | Close to 0 or 1 |

## Duplication Metrics

### Code Duplication

```
Duplication = Duplicated Lines / Total Lines * 100%

Target: < 3%
Acceptable: 3-5%
Warning: 5-10%
Critical: > 10%
```

**Tools**: `jscpd`, `jscpd` (JS/TS), `pylint --duplicate-code` (Python), `sonar` (multi-language).

## Quality Gate Example (SonarQube)

```yaml
quality_gate:
  conditions:
    - metric: new_coverage
      operator: LESS_THAN
      value: 80
    - metric: new_duplicated_lines_density
      operator: GREATER_THAN
      value: 3
    - metric: new_major_violations
      operator: GREATER_THAN
      value: 0
    - metric: new_critical_violations
      operator: GREATER_THAN
      value: 0
```
