#!/usr/bin/env python3
"""
Cleanup placeholder sections injected by audit_skills.py.

Removes:
1. Placeholder '## Workflow' sections with '输入 → 处理 → 输出'
2. Duplicate Goal sections that copy from description
3. Generic trigger text ('当用户需要使用此技能时触发。')
"""

from __future__ import annotations

import re
from pathlib import Path

from utils import parse_frontmatter, discover_skill_dirs

REPO_ROOT = Path(__file__).resolve().parent.parent

PLACEHOLDER_WORKFLOW = "输入 → 处理 → 输出"
GENERIC_TRIGGER = "当用户需要使用此技能时触发。"


def remove_placeholder_workflow(text: str) -> str:
    """Remove placeholder Workflow section with '输入 → 处理 → 输出'."""
    # Pattern: ## Workflow section containing only the placeholder
    pattern = r"\n## Workflow\s*\n\n```\n输入 → 处理 → 输出\n```\n"
    return re.sub(pattern, "\n", text)


def remove_duplicate_goal(text: str, description: str) -> str:
    """Remove Goal section that duplicates the description."""
    # Find Goal section
    goal_match = re.search(r"\n## Goal\s*\n\n(.+?)(?=\n## |\Z)", text, re.DOTALL)
    if goal_match:
        goal_content = goal_match.group(1).strip()
        # Check if goal is just a copy of description (or part of it)
        desc_clean = description.strip().rstrip("。")
        goal_clean = goal_content.strip().rstrip("。")

        if goal_clean == desc_clean or desc_clean in goal_clean:
            # Remove the Goal section
            text = text[:goal_match.start()] + text[goal_match.end():]

    return text


def remove_generic_trigger(text: str) -> str:
    """Remove generic trigger text that provides no value."""
    # Pattern: ## Trigger section containing only generic text
    pattern = r"\n## Trigger\s*\n\n" + re.escape(GENERIC_TRIGGER) + r"\n"
    return re.sub(pattern, "\n", text)


def cleanup_skill(skill_dir: Path) -> dict:
    """Clean up a single skill's SKILL.md."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"skill": skill_dir.name, "changes": []}

    text = skill_md.read_text(encoding="utf-8")
    original = text
    changes = []

    # Parse frontmatter to get description
    fm, _, _ = parse_frontmatter(text)
    description = fm.get("description", "")

    # Remove placeholder workflow
    text = remove_placeholder_workflow(text)
    if text != original:
        changes.append("Removed placeholder workflow")

    # Remove duplicate goal (compare against current state, not original)
    snapshot = text
    text = remove_duplicate_goal(text, description)
    if text != snapshot:
        changes.append("Removed duplicate goal")

    # Remove generic trigger (compare against current state, not original)
    snapshot = text
    text = remove_generic_trigger(text)
    if text != snapshot:
        changes.append("Removed generic trigger")

    # Write back if changed
    if text != original:
        skill_md.write_text(text, encoding="utf-8")

    return {"skill": skill_dir.name, "changes": changes}


def main():
    """Clean up all skills."""
    total_fixed = 0
    total_changes = 0

    for skill_dir in discover_skill_dirs(REPO_ROOT):
        result = cleanup_skill(skill_dir)
        if result["changes"]:
            total_fixed += 1
            total_changes += len(result["changes"])
            print(f"Fixed {result['skill']}: {', '.join(result['changes'])}")

    print(f"\nTotal: {total_fixed} skills fixed, {total_changes} changes made")


if __name__ == "__main__":
    main()
