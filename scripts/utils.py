#!/usr/bin/env python3
"""Shared utilities for skill scripts."""

from __future__ import annotations

import re
from pathlib import Path

# Directories to skip when discovering skills
SKIP_DIRS = {"scripts", "tests", ".github", ".claude", "wiki", ".git", "__pycache__"}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, str]:
    """Parse YAML frontmatter between --- markers.

    Returns:
        (fields, frontmatter_text, body) where:
        - fields: dict of parsed key-value pairs
        - frontmatter_text: raw text between --- markers
        - body: content after the closing ---
    """
    if not text.startswith("---"):
        return {}, "", text

    end = text.find("---", 3)
    if end == -1:
        return {}, "", text

    fm_text = text[3:end].strip()
    body = text[end + 3:].lstrip("\n")

    result: dict[str, str] = {}
    current_key: str | None = None
    current_value_lines: list[str] | None = None
    in_multiline = False

    for line in fm_text.split("\n"):
        stripped = line.rstrip()

        if in_multiline:
            if stripped == "" or stripped.startswith(" ") or stripped.startswith("\t"):
                current_value_lines.append(stripped)
                continue
            else:
                result[current_key] = "\n".join(current_value_lines).strip()
                current_key = None
                current_value_lines = None
                in_multiline = False

        match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            if value == "|":
                in_multiline = True
                current_key = key
                current_value_lines = []
            else:
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                result[key] = value
            continue

    if in_multiline and current_key is not None and current_value_lines is not None:
        result[current_key] = "\n".join(current_value_lines).strip()

    return result, fm_text, body


def discover_skill_dirs(repo_root: Path) -> list[Path]:
    """Discover all skill directories in the repo.

    Returns sorted list of directories containing SKILL.md files,
    excluding infrastructure directories and workspace directories.
    """
    skill_dirs = []
    for d in sorted(repo_root.iterdir()):
        if not d.is_dir():
            continue
        if d.name in SKIP_DIRS:
            continue
        if d.name.endswith("-workspace"):
            continue
        if (d / "SKILL.md").exists():
            skill_dirs.append(d)
    return skill_dirs
