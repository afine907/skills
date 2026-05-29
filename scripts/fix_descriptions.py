#!/usr/bin/env python3
"""
Fix skills with descriptions that are too long.

Shortens descriptions to under 200 characters while preserving key information.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from utils import parse_frontmatter, discover_skill_dirs

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_DESC_LENGTH = 200


def shorten_description(desc: str) -> str:
    """Shorten a description to under 200 characters."""
    if len(desc) <= MAX_DESC_LENGTH:
        return desc

    # Try to extract just the first line (before trigger conditions)
    lines = desc.split("\n")
    first_line = lines[0].strip()

    # If first line is short enough, use it
    if len(first_line) <= MAX_DESC_LENGTH:
        return first_line

    # Try to find a good cutoff point
    # Look for Chinese sentence endings
    for i, char in enumerate(first_line):
        if char in "。！？" and i < MAX_DESC_LENGTH:
            return first_line[:i + 1]

    # Look for period
    for i, char in enumerate(first_line):
        if char == "." and i < MAX_DESC_LENGTH:
            # Check if it's not an abbreviation
            if i + 1 < len(first_line) and first_line[i + 1] == " ":
                return first_line[:i + 1]

    # Just truncate at word boundary
    truncated = first_line[:MAX_DESC_LENGTH - 3]
    last_space = truncated.rfind(" ")
    if last_space > MAX_DESC_LENGTH // 2:
        truncated = truncated[:last_space]
    return truncated + "..."


def fix_skill_description(skill_dir: Path) -> bool:
    """Fix a skill's description if it's too long."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    text = skill_md.read_text(encoding="utf-8")
    fm, fm_text, body = parse_frontmatter(text)

    if "description" not in fm:
        return False

    desc = fm["description"]
    if len(desc) <= MAX_DESC_LENGTH:
        return False

    # Shorten the description
    new_desc = shorten_description(desc)

    # Use string slicing to replace only within frontmatter, avoiding body matches
    fm_start = text.find("---\n")
    fm_end = text.find("---\n", fm_start + 4)
    if fm_start == -1 or fm_end == -1:
        return False

    old_fm = text[fm_start:fm_end + 4]
    new_fm = old_fm.replace(desc, new_desc, 1)
    new_text = text[:fm_start] + new_fm + text[fm_end + 4:]

    if new_text != text:
        skill_md.write_text(new_text, encoding="utf-8")
        print(f"Fixed {skill_dir.name}: {len(desc)} -> {len(new_desc)} chars")
        return True

    return False


def main():
    """Fix all skills with long descriptions."""
    fixed_count = 0

    for skill_dir in discover_skill_dirs(REPO_ROOT):
        if fix_skill_description(skill_dir):
            fixed_count += 1

    print(f"\nFixed {fixed_count} skills")


if __name__ == "__main__":
    main()
