#!/usr/bin/env python3
"""
Fix skills with descriptions that are too long.

Shortens descriptions to under 200 characters while preserving key information.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_DESC_LENGTH = 200


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    """Parse frontmatter and return (fields, frontmatter_text, body)."""
    if not text.startswith("---"):
        return {}, "", text

    end = text.find("---", 3)
    if end == -1:
        return {}, "", text

    fm_text = text[3:end].strip()
    body = text[end + 3:].lstrip("\n")

    result = {}
    current_key = None
    current_value_lines = None
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

    if in_multiline and current_key and current_value_lines:
        result[current_key] = "\n".join(current_value_lines).strip()

    return result, fm_text, body


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

    # Rebuild the frontmatter
    new_fm_text = fm_text.replace(
        f"description: |",
        f"description: |"
    )

    # Replace the old description with the new one
    # Handle multiline description
    old_desc_block = desc
    new_desc_block = new_desc

    new_text = text.replace(old_desc_block, new_desc_block)

    if new_text != text:
        skill_md.write_text(new_text, encoding="utf-8")
        print(f"Fixed {skill_dir.name}: {len(desc)} -> {len(new_desc)} chars")
        return True

    return False


def main():
    """Fix all skills with long descriptions."""
    fixed_count = 0

    for skill_dir in sorted(REPO_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name in {"scripts", "tests", ".github", ".claude", "wiki"}:
            continue
        if skill_dir.name.endswith("-workspace"):
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue

        if fix_skill_description(skill_dir):
            fixed_count += 1

    print(f"\nFixed {fixed_count} skills")


if __name__ == "__main__":
    main()
