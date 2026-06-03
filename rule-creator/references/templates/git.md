---
paths: ["**/*"]
---

# Git Conventions

## Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding/fixing tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes

### Examples

```bash
# ✅ Good
git commit -m "feat(auth): add JWT token refresh"
git commit -m "fix(api): handle null response from user service"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(utils): extract date formatting to helper"

# ❌ Avoid
git commit -m "update code"
git commit -m "fixed stuff"
git commit -m "WIP"
```

### Scopes

Use the affected module or component:

```bash
feat(auth): ...
fix(api): ...
docs(readme): ...
refactor(utils): ...
```

## Branch Naming

Use descriptive names with type prefix:

```bash
# Feature branches
feat/user-authentication
feat/add-payment-processing

# Bug fixes
fix/login-redirect-bug
fix/null-pointer-exception

# Hotfixes
hotfix/critical-security-patch

# Release branches
release/v1.2.0
```

## Pull Requests

### Title
Follow commit message format:
```
feat(auth): implement OAuth2 login flow
```

### Description Template
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Related Issues
Closes #123
```

## Versioning

Follow Semantic Versioning (semver):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes (backward compatible)

```bash
# Tag releases
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

## Stashing

```bash
# Save work in progress
git stash push -m "WIP: user authentication"

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{1}
```

## Interactive Rebase

Clean up commits before merging:

```bash
# Interactive rebase last 3 commits
git rebase -i HEAD~3

# Squash commits
pick abc1234 feat: add user model
squash def5678 fix: user model tests
squash ghi9012 docs: update user docs
```
