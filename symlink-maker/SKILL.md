---
name: symlink-maker
description: Create symbolic links (symlinks) for files or directories.
category: productivity
---

# Symlink Maker

Cross-platform symlink creator (Windows/macOS/Linux).

## Usage

```bash
python <skill-dir>/scripts/create_link.py <source> <link_path>
python <skill-dir>/scripts/create_link.py --remove <link_path>
```

## Features

- **Relative paths**: Links use relative targets, survive directory moves
- **Windows auto-fallback**: Tries symlink first, auto-fallback to junction (no admin needed)
- **Idempotent**: Re-running skips if link is already correct

## Examples

```bash
# Link .opencode/rules to .claude/rules (shares same content)
python <skill-dir>/scripts/create_link.py ".claude/rules" ".opencode/rules"

# Remove the link
python <skill-dir>/scripts/create_link.py --remove ".opencode/rules"
```

## Platform Behavior

| Platform | Directory Link | File Link |
|----------|---------------|-----------|
| Windows (Developer Mode) | Symlink (relative) | Symlink (relative) |
| Windows (no Developer Mode) | Junction (absolute) | Symlink (fallback) |
| macOS/Linux | Symlink (relative) | Symlink (relative) |
