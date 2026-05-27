---
name: symlink-maker
description: Create symbolic links (symlinks) for files or directories. Cross-platform support for Windows, macOS, and Linux. Use when the user wants to create a symlink, shortcut, or symbolic link pointing to a file or directory, or asks to link/mirror/redirect a path to another location.
category: productivity
---

# Symlink Maker

Creates symbolic links for files or directories. Cross-platform (Windows/macOS/Linux).

## Usage

Run the bundled script:

```bash
python <skill-dir>/scripts/create_link.py "<source>" "<link_path>"
```

- **source**: what the link points TO
- **link_path**: where the link is created

## Examples

```bash
# File symlink
python <skill-dir>/scripts/create_link.py "D:/project/config.json" "C:/Users/me/Desktop/config.json"

# Directory symlink
python <skill-dir>/scripts/create_link.py "D:/shared/assets" "D:/my-project/assets"
```

## Notes

- If source doesn't exist, warns about broken symlink before creating
- On Windows directories, uses junction (no admin needed)
- Always verify the result after creation
