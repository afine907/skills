---
name: commit
description: Analyze staged changes and generate semantic commit messages automatically. Reads git diff --staged, analyzes code changes, generates conventional commit messages following best practices, and executes git commit. Use when user wants to commit staged changes or asks to "commit", "create commit", "generate commit message". Commands: /commit, /commit -m "custom message", /commit --amend.
---

# Commit - Intelligent Git Commit Generator

## Overview

Commit is a smart git commit assistant that analyzes staged code changes and generates semantic, conventional commit messages automatically.

**Core Features**:
- **Automatic Analysis**: Analyzes staged changes using `git diff --staged`
- **Semantic Messages**: Generates conventional commit messages (feat/fix/refactor/docs/style/test/chore)
- **Scope Detection**: Identifies affected modules/components automatically
- **Multi-file Support**: Handles multiple files with unified commit message
- **Interactive Mode**: Allows user review and modification before commit

## Commands

| Command | Description |
|---------|-------------|
| `/commit` | Analyze staged changes and generate commit |
| `/commit -m "message"` | Commit with custom message (skips generation) |
| `/commit --amend` | Amend previous commit (use with caution) |
| `/commit --dry-run` | Preview commit message without committing |

## Workflow

### Step 1: Pre-flight Check

```bash
# Check if inside a git repository
git rev-parse --is-inside-work-tree

# Check for staged changes
git diff --staged --quiet
# If quiet (no output), no staged changes exist

# Get list of staged files
git diff --staged --name-only
```

**If no staged changes**:
- Check for unstaged changes: `git status`
- Prompt user: "No staged changes found. Would you like to stage changes first?"
- Optionally run: `git add -A` or `git add <files>`

### Step 2: Analyze Staged Changes

```bash
# Get detailed diff of staged changes
git diff --staged

# Get file statistics
git diff --staged --stat

# For large diffs, limit context
git diff --staged --unified=3
```

**Analysis Focus**:

1. **Change Type Detection**
   - New files → `feat` or initial commit
   - Modified files → Based on what changed
   - Deleted files → `refactor` or `chore`
   - Renamed files → `refactor` or `chore`

2. **Semantic Type Classification**
   - `feat`: New feature, new functionality
   - `fix`: Bug fix, error correction
   - `refactor`: Code restructuring without behavior change
   - `docs`: Documentation only changes
   - `style`: Formatting, missing semicolons, whitespace
   - `test`: Adding or modifying tests
   - `chore`: Build process, dependencies, tooling
   - `perf`: Performance improvements
   - `ci`: CI/CD configuration changes
   - `build`: Build system changes

3. **Scope Identification**
   - Extract module/component from file paths
   - Examples:
     - `src/auth/login.ts` → scope: `auth`
     - `components/Button.tsx` → scope: `Button`
     - `api/users/routes.ts` → scope: `api/users`

4. **Summary Generation**
   - Identify primary change (most impactful)
   - Summarize in imperative mood
   - Keep under 50 characters for title
   - Add body for complex changes

### Step 3: Generate Commit Message

**Conventional Commit Format**:
```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**Message Rules**:

1. **Title Line**
   - Format: `type(scope): subject`
   - Subject in imperative mood: "add" not "added" or "adds"
   - No period at the end
   - Max 50 characters for subject
   - Lowercase subject (unless proper noun)

2. **Body** (optional)
   - Separate from title with blank line
   - Explain WHAT and WHY, not HOW
   - Wrap at 72 characters
   - Use bullet points for multiple changes

3. **Footer** (optional)
   - Breaking changes: `BREAKING CHANGE: description`
   - Issue references: `Closes #123`, `Fixes #456`

**Examples**:

```bash
# Simple feature
feat(auth): add JWT token refresh mechanism

# Bug fix with body
fix(payment): handle duplicate callback correctly

Payment callback was processing duplicates due to missing idempotency
check. Added unique constraint on (order_id, callback_id).

Fixes #234

# Multiple changes with body
feat(api): add user profile endpoints

- Add GET /api/users/:id/profile endpoint
- Add PUT /api/users/:id/profile endpoint
- Add profile image upload support

# Breaking change
refactor(db)!: migrate from MySQL to PostgreSQL

BREAKING CHANGE: Database migration required. Run `npm run migrate`
before upgrading.

# Documentation
docs(readme): update installation instructions

# Refactoring
refactor(utils): extract date formatting utilities
```

### Step 4: Execute Commit

```bash
# Standard commit with generated message
git commit -m "$(cat <<'EOF'
type(scope): subject

optional body

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Alternative: use heredoc for multi-line
git commit -m "type(scope): subject" -m "optional body" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Post-commit Verification**:
```bash
# Verify commit was created
git log -1 --oneline

# Show the commit details
git show HEAD --stat
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMIT EXECUTION FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PRE-FLIGHT CHECK                                            │
│     ├─ Verify git repository                                    │
│     ├─ Check staged changes exist                               │
│     └─ If no staged changes: prompt user to stage               │
│                                                                 │
│  2. ANALYZE CHANGES                                             │
│     ├─ Run: git diff --staged                                   │
│     ├─ Identify changed files                                   │
│     ├─ Detect change types (new/modified/deleted)               │
│     └─ Analyze code patterns                                    │
│                                                                 │
│  3. GENERATE MESSAGE                                            │
│     ├─ Determine semantic type                                  │
│     ├─ Extract scope from file paths                            │
│     ├─ Write subject in imperative mood                         │
│     └─ Add body if needed for complex changes                   │
│                                                                 │
│  4. PREVIEW & CONFIRM                                           │
│     ├─ Display generated commit message                         │
│     ├─ Allow user to edit if needed                             │
│     └─ Get user approval                                        │
│                                                                 │
│  5. EXECUTE COMMIT                                              │
│     ├─ Run: git commit with generated message                   │
│     ├─ Add Co-Authored-By trailer                               │
│     └─ Verify commit success                                    │
│                                                                 │
│  6. POST-COMMIT                                                 │
│     ├─ Show commit hash and summary                             │
│     └─ Suggest push if ready                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Simple Feature Addition

**User runs**: `/commit`

**Staged changes**:
```diff
diff --git a/src/auth/login.ts b/src/auth/login.ts
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/auth/login.ts
@@ -0,0 +1,25 @@
+export function login(email: string, password: string) {
+  // Validate credentials
+  const user = await validateCredentials(email, password);
+  // Generate JWT token
+  return generateToken(user);
+}
```

**Generated commit**:
```
feat(auth): add user login function
```

### Example 2: Bug Fix with Context

**Staged changes**:
```diff
diff --git a/src/payment/callback.ts b/src/payment/callback.ts
index abc123..def456 100644
--- a/src/payment/callback.ts
+++ b/src/payment/callback.ts
@@ -45,6 +45,12 @@ async function handleCallback(data: CallbackData) {
+  // Check for duplicate callback
+  const existing = await findCallback(data.id);
+  if (existing) {
+    logger.warn('Duplicate callback detected', { id: data.id });
+    return { status: 'already_processed' };
+  }
+
   const order = await processPayment(data);
```

**Generated commit**:
```
fix(payment): add idempotency check for callbacks

Prevent duplicate payment processing by checking if callback
was already handled before processing.

Fixes #123
```

### Example 3: Multiple Files

**Staged files**:
- `src/api/users.ts` (modified)
- `src/api/users.test.ts` (modified)
- `src/types/user.ts` (modified)

**Generated commit**:
```
feat(api): add user profile update endpoints

- Add PUT /api/users/:id endpoint
- Add request validation
- Add unit tests for profile update
```

## Best Practices

### DO:
- ✅ Analyze ALL staged changes before generating message
- ✅ Use imperative mood for subject ("add" not "added")
- ✅ Keep subject under 50 characters
- ✅ Add body for complex changes
- ✅ Reference issues when applicable
- ✅ Use semantic commit types consistently
- ✅ Group related changes in one commit

### DON'T:
- ❌ Commit without staged changes
- ❌ Mix unrelated changes in one commit
- ❌ Use past tense in commit messages
- ❌ End subject with period
- ❌ Exceed 72 characters in body lines
- ❌ Include sensitive information
- ❌ Skip pre-commit hooks (unless explicitly requested)

## Edge Cases

### No Staged Changes

```bash
# Check unstaged changes
git status

# If unstaged changes exist:
echo "No staged changes found. Unstaged files:"
git diff --name-only
echo ""
echo "Would you like to stage all changes? (y/n)"
# If yes: git add -A
# If no: exit with instructions
```

### Empty Repository (Initial Commit)

```bash
# Detect initial commit
git rev-parse HEAD 2>/dev/null
# If fails, this is initial commit

# Initial commit message
git commit -m "chore: initial commit"
```

### Large Diff

```bash
# For large diffs (>500 lines), summarize
git diff --staged --stat
git diff --staged --unified=1

# Generate summary commit message
echo "Large change detected. Consider splitting into multiple commits."
```

### Merge Conflicts

```bash
# Check if resolving merge conflict
git status | grep "both modified"

# Merge commit message
git commit -m "merge: resolve conflicts in <files>"
# No need for detailed body - git handles merge commits
```

## Integration with Hooks

This skill respects git hooks:
- **pre-commit**: Runs automatically
- **commit-msg**: Runs automatically
- **If hooks fail**: Report error and suggest fixes

To bypass hooks (NOT RECOMMENDED):
```bash
git commit --no-verify
```

Only use `--no-verify` if explicitly requested by user.

## Configuration

Users can customize behavior via `.claude/settings.json`:

```json
{
  "commit": {
    "max_subject_length": 50,
    "max_body_width": 72,
    "always_add_co_author": true,
    "default_scope": null,
    "types": ["feat", "fix", "refactor", "docs", "style", "test", "chore"]
  }
}
```

## Summary

The `/commit` skill automates the commit workflow while ensuring high-quality, semantic commit messages that follow industry best practices. It analyzes staged changes, generates appropriate commit messages, and executes the commit with proper formatting.
