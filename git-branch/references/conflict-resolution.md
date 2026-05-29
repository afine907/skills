# Git Conflict Resolution Guide

## Understanding Conflicts

A conflict occurs when Git cannot automatically merge changes from two branches because they modified the same lines in the same file.

### Conflict Markers

```
<<<<<<< HEAD
// Your changes (current branch)
const timeout = 3000;
=======
// Their changes (incoming branch)
const timeout = 5000;
>>>>>>> feature/new-timeout
```

| Marker | Meaning |
|--------|---------|
| `<<<<<<< HEAD` | Start of your changes |
| `=======` | Separator between the two versions |
| `>>>>>>> branch-name` | End of incoming changes |

## Resolution Strategies

### 1. Accept Ours (Keep Current Branch)

```bash
git checkout --ours <file>
git add <file>
```

When to use: Your version is correct, theirs is outdated or wrong.

### 2. Accept Theirs (Take Incoming Changes)

```bash
git checkout --theirs <file>
git add <file>
```

When to use: Their version is the correct one, yours was experimental.

### 3. Manual Merge (Combine Both)

Edit the file to combine the best parts of both versions, then:

```bash
git add <file>
```

### 4. Use a Merge Tool

```bash
git mergetool
```

Popular tools: VS Code, IntelliJ, Beyond Compare, KDiff3, meld.

## Common Conflict Scenarios

### Import Statements

```python
<<<<<<< HEAD
from datetime import datetime, timedelta
from typing import List, Optional
=======
from datetime import datetime
from typing import Dict, List, Optional
>>>>>>> feature/new-module

# Resolution: combine unique imports
from datetime import datetime, timedelta
from typing import Dict, List, Optional
```

### Function Signatures

```typescript
<<<<<<< HEAD
async function fetchData(url: string, timeout?: number): Promise<Response> {
=======
async function fetchData(url: string, options?: RequestOptions): Promise<Response> {
>>>>>>> feature/options-refactor

// Resolution: use the newer API (options), add backward compatibility
async function fetchData(url: string, options?: RequestOptions | number): Promise<Response> {
  const opts = typeof options === 'number' ? { timeout: options } : options;
```

### Configuration Files

```json
// Don't try to merge config files manually - decide which is correct
// Then regenerate if needed (e.g., package-lock.json)

# For package-lock.json, regenerate:
git checkout --ours package-lock.json
npm install

# For other lock files, similar approach
```

### Deleted vs Modified

```
CONFLICT (modify/delete): file.js deleted in feature branch
and modified in HEAD.

# Keep the file:
git checkout HEAD -- file.js

# Accept deletion:
git rm file.js
```

## Preventing Conflicts

### Before Merging

```bash
# 1. Update your branch frequently
git fetch origin
git rebase origin/main   # or git merge origin/main

# 2. Check for potential conflicts before merging
git merge --no-commit --no-ff feature/branch
# Review, then:
git merge --abort        # if conflicts are too complex
# or resolve and:
git commit
```

### Merge vs Rebase

| Strategy | Pros | Cons |
|----------|------|------|
| `git merge` | Preserves history, non-destructive | Merge commits clutter history |
| `git rebase` | Clean linear history | Rewrites history, conflicts per commit |

```bash
# Merge: one conflict resolution for the whole branch
git checkout main
git merge feature/branch

# Rebase: resolve conflicts for each commit
git checkout feature/branch
git rebase main
```

### Rebase Conflict Workflow

```bash
# Start rebase
git rebase main

# Conflict occurs. Resolve:
# 1. Edit conflicted files
# 2. Stage resolved files
git add <file>

# 3. Continue rebase (don't commit manually)
git rebase --continue

# 4. If it gets too messy:
git rebase --abort
```

## Conflict Resolution for Specific Files

### Binary Files (Images, PDFs)

```bash
# Choose one version
git checkout --ours image.png    # keep yours
git checkout --theirs image.png  # take theirs
git add image.png
```

### Multiple Conflicts in One File

```bash
# Accept all ours:
git checkout --ours <file>

# Accept all theirs:
git checkout --theirs <file>

# Or use a tool to resolve one by one:
code <file>   # VS Code shows conflict UI
```

### Submodule Conflicts

```bash
# Update submodule to desired commit
cd submodule
git checkout <desired-commit>
cd ..
git add submodule
```

## Post-Resolution Checklist

```bash
# 1. Verify no conflict markers remain
grep -rn "<<<<<<< " . --include="*.ts" --include="*.py"
grep -rn ">>>>>>> " . --include="*.ts" --include="*.py"

# 2. Run tests
npm test  # or pytest, go test, etc.

# 3. Run linter
npm run lint

# 4. Stage all resolved files
git add .

# 5. Complete the merge/rebase
git commit   # for merge
git rebase --continue  # for rebase
```

## Undoing a Bad Merge

```bash
# If merge is complete but wrong:
git reset --hard HEAD~1    # undo the merge commit

# If merge is in progress:
git merge --abort

# If rebase is in progress:
git rebase --abort
```
