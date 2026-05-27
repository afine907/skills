#!/usr/bin/env python3
"""
Cross-platform symlink/junction creator.

Usage:
    python create_link.py <source> <link_path>

On Windows, directories use junction (no admin needed).
Files use os.symlink (requires Developer Mode or admin).
macOS/Linux use os.symlink.
"""
import os
import platform
import subprocess
import sys


def create_link(source, link_path):
    source = os.path.abspath(source)
    link_path = os.path.abspath(link_path)

    if not os.path.exists(source):
        print(f"WARNING: Source does not exist: {source}")
        print("The link will be broken (dangling) until the source is created.")

    os.makedirs(os.path.dirname(link_path), exist_ok=True)

    if os.path.islink(link_path):
        os.remove(link_path)
    elif os.path.isdir(link_path):
        os.rmdir(link_path)
    elif os.path.isfile(link_path):
        os.remove(link_path)

    if platform.system() == "Windows" and os.path.isdir(source):
        subprocess.run(["cmd", "/c", "mklink", "/J", link_path, source], check=True)
    else:
        os.symlink(source, link_path)

    if os.path.islink(link_path):
        target = os.readlink(link_path)
        print(f"OK: {link_path} -> {target}")
    elif os.path.exists(link_path):
        print(f"OK: {link_path} (junction to {source})")
    else:
        print(f"FAILED: Link not created at {link_path}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_link.py <source> <link_path>")
        sys.exit(1)
    create_link(sys.argv[1], sys.argv[2])
