#!/usr/bin/env python3
"""
Cross-platform symlink creator.

Core idea from pnpm:
- Relative paths (survives directory moves)
- Windows: try symlink first, auto-fallback to junction (no admin needed)

Usage:
    python cross_platform_link.py <source> <link_path>
    python cross_platform_link.py --remove <link_path>
"""
import os
import platform
import subprocess
import sys


def _relative_target(source, link_path):
    """Relative path from link's parent to source. Absolute if cross-drive."""
    source = os.path.normpath(os.path.abspath(source))
    link_dir = os.path.normpath(os.path.abspath(os.path.dirname(link_path)))
    if platform.system() == "Windows":
        if os.path.splitdrive(source)[0] != os.path.splitdrive(link_dir)[0]:
            return source  # cross-drive: must be absolute
    try:
        return os.path.relpath(source, link_dir)
    except ValueError:
        return source


def _create(source, link_path):
    """Create symlink/junction. On Windows, try symlink first, fallback to junction."""
    rel = _relative_target(source, link_path)
    if platform.system() != "Windows":
        os.symlink(rel, link_path, target_is_directory=os.path.isdir(source))
        return "symlink"
    # Windows: probe symlink privilege
    try:
        os.symlink(rel, link_path, target_is_directory=os.path.isdir(source))
        return "symlink"
    except PermissionError:
        pass
    # Fallback: junction (no privilege needed)
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", link_path, os.path.abspath(source)],
        check=True, capture_output=True
    )
    return "junction"


def _remove(link_path):
    """Remove symlink/junction safely."""
    if platform.system() == "Windows":
        try: os.rmdir(link_path)
        except OSError: os.remove(link_path)
    else:
        os.remove(link_path)


def create(source, link_path):
    source = os.path.abspath(source)
    link_path = os.path.abspath(link_path)

    if not os.path.exists(source):
        print(f"WARNING: source does not exist: {source}")

    os.makedirs(os.path.dirname(link_path), exist_ok=True)

    # Idempotent: skip if already correct
    if os.path.islink(link_path):
        existing = os.path.normpath(os.path.join(os.path.dirname(link_path), os.readlink(link_path)))
        if existing == os.path.normpath(source):
            print(f"[reused] {link_path} (already correct)")
            return
        _remove(link_path)

    link_type = _create(source, link_path)
    try:
        target = os.path.relpath(source, os.path.dirname(link_path))
    except ValueError:
        target = source  # cross-drive fallback
    print(f"[created] {link_path} -> {target} ({link_type})")


def remove(link_path):
    link_path = os.path.abspath(link_path)
    if os.path.islink(link_path):
        target = os.readlink(link_path)
        _remove(link_path)
        print(f"[removed] {link_path} (was -> {target})")
    else:
        print(f"[skip] {link_path} is not a link")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print("Usage:")
        print("  python cross_platform_link.py <source> <link_path>")
        print("  python cross_platform_link.py --remove <link_path>")
        sys.exit(0)
    if sys.argv[1] == "--remove":
        remove(sys.argv[2])
    else:
        create(sys.argv[1], sys.argv[2])
