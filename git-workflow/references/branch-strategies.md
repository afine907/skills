# Branch Strategy Reference

## Git Flow

A structured branching model with long-lived branches for releases and development.

### Branch Types

| Branch | Lifetime | Purpose |
|---|---|---|
| `main` | Permanent | Production-ready code |
| `develop` | Permanent | Integration branch for next release |
| `feature/*` | Temporary | New features |
| `release/*` | Temporary | Release preparation |
| `hotfix/*` | Emergency | Production bug fixes |

### Workflow

```
main        ──●───────────────●─────────────────●──
              │               ^                 ^
              │               │                 │
hotfix/v1.0.1 │               │                 │
              │          ─────●                 │
              │                                  │
release/v1.1  │         ──●──────────●──────────┘
              │           ^          |
              │           │          v
develop    ──●─────●───●──●──────────●──
              │     ^   ^
              │     │   │
feature/x  ──●─●─●─┘   │
                        │
feature/y        ──●─●─●┘
```

### Commands

```bash
# Start a feature
git checkout develop
git checkout -b feature/user-auth

# Finish a feature (merge back to develop)
git checkout develop
git merge --no-ff feature/user-auth
git branch -d feature/user-auth

# Start a release
git checkout develop
git checkout -b release/v1.2.0

# Finish a release (merge to main AND develop)
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git checkout develop
git merge --no-ff release/v1.2.0
git branch -d release/v1.2.0

# Hotfix
git checkout main
git checkout -b hotfix/v1.1.1
# ... fix ...
git checkout main
git merge --no-ff hotfix/v1.1.1
git tag -a v1.1.1
git checkout develop
git merge --no-ff hotfix/v1.1.1
git branch -d hotfix/v1.1.1
```

### When to Use Git Flow

- Scheduled release cycles (e.g., monthly releases)
- Multiple versions supported in parallel
- Large teams with dedicated QA/release processes
- Projects that need strict release isolation

---

## Trunk-Based Development

A simpler model where all work integrates into a single main branch frequently.

### Branch Types

| Branch | Lifetime | Purpose |
|---|---|---|
| `main` | Permanent | Single source of truth |
| `feature/*` | Very short (hours to days) | Small, incremental changes |

### Core Principles

1. **Short-lived branches** -- features are merged within 1-2 days max
2. **Feature flags** -- incomplete work is hidden behind toggles, not branches
3. **Continuous integration** -- every commit to main is deployable
4. **Small commits** -- break work into small, reviewable chunks

### Workflow

```
main    ──●─────●─────●─────●─────●──
           ^     ^     ^     ^     ^
           │     │     │     │     │
           a     b     c     d     e     (all merged within hours/days)
```

### Commands

```bash
# Short-lived feature branch
git checkout main
git checkout -b feat/add-cache-header
# ... make changes ...
git push origin feat/add-cache-header
# Create PR, get review, merge within hours
git checkout main
git pull
git branch -d feat/add-cache-header

# Feature flag pattern (code lives in main, hidden by flag)
# src/features.ts
export const FEATURES = {
  NEW_DASHBOARD: process.env.FF_NEW_DASHBOARD === 'true',
};

# In component
if (FEATURES.NEW_DASHBOARD) {
  return <NewDashboard />;
}
return <OldDashboard />;
```

### When to Use Trunk-Based

- Continuous deployment / frequent releases
- Strong CI/CD pipeline with good test coverage
- Small to medium teams with high communication
- Products where fast iteration matters more than scheduled releases

---

## GitHub Flow

A simplified Git Flow variant popular on GitHub.

### Branch Types

| Branch | Lifetime | Purpose |
|---|---|---|
| `main` | Permanent | Deployable at all times |
| `feature/*` | Short | Any change (feature, fix, refactor) |

### Workflow

1. Branch from `main`
2. Make changes and push
3. Open a Pull Request
4. Review and discuss
5. Merge to `main` and deploy

```bash
git checkout -b improve-readme
# ... edit ...
git push origin improve-readme
# Open PR on GitHub, get review, merge
```

### When to Use GitHub Flow

- Web applications with continuous deployment
- Teams comfortable with PR-based workflow
- Simple projects that don't need release branches

---

## Choosing a Strategy

| Factor | Git Flow | Trunk-Based | GitHub Flow |
|---|---|---|---|
| Release cadence | Scheduled | Continuous | Continuous |
| Team size | Large | Small-Medium | Any |
| Branch complexity | High | Low | Low |
| CI/CD maturity needed | Medium | High | Medium |
| Version support | Multiple | Latest only | Latest only |
| Hotfix process | Formal | Feature flags | Direct to main |
