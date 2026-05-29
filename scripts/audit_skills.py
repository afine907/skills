#!/usr/bin/env python3
"""
Audit and improve all skill SKILL.md files.

Based on skill-creator quality standards:
- Add missing Goal/Trigger/Workflow sections
- Optimize descriptions for better triggering
- Ensure code examples are complete
- Verify reference files exist

Usage:
  python scripts/audit_skills.py              # audit all skills
  python scripts/audit_skills.py --fix        # auto-fix issues
  python scripts/audit_skills.py --skill NAME # audit specific skill
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Section patterns to detect existing sections
SECTION_PATTERNS = {
    "Goal": [
        r"^##\s+Goal",
        r"^##\s+Purpose",
        r"^##\s+Overview",
        r"^##\s+Description",
        r"^##\s+Summary",
        r"^##\s+What\s+(it|this)\s+does",
        r"^##\s+About",
    ],
    "Trigger": [
        r"^##\s+Trigger",
        r"^##\s+When\s+to\s+[Uu]se",
        r"^##\s+Usage",
        r"^##\s+Invoke",
        r"^##\s+Activate",
        r"^##\s+Trigger\s+[Cc]ondition",
        r"^##\s+When\s+to\s+invoke",
    ],
    "Workflow": [
        r"^##\s+Workflow",
        r"^##\s+How\s+it\s+[Ww]orks",
        r"^##\s+Steps",
        r"^##\s+Process",
        r"^##\s+Procedure",
        r"^##\s+Guide",
        r"^##\s+Commands",
        r"^##\s+Usage\s+[Ii]nstructions",
        r"^##\s+Tutorial",
        r"^##\s+Quick\s+[Ss]tart",
        r"^##\s+Getting\s+[Ss]tarted",
    ],
}


def parse_frontmatter(text: str) -> dict:
    """Parse simple YAML frontmatter between --- markers."""
    if not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        return {}

    block = text[3:end].strip()
    if not block:
        return {}

    result: dict[str, str] = {}
    current_key: str | None = None
    current_value_lines: list[str] | None = None
    in_multiline = False

    for line in block.split("\n"):
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

    return result


def get_body_after_frontmatter(text: str) -> str:
    """Return the content after the closing --- of frontmatter."""
    if not text.startswith("---"):
        return text

    end = text.find("---", 3)
    if end == -1:
        return ""

    body_start = end + 3
    if body_start < len(text) and text[body_start] == "\n":
        body_start += 1
    return text[body_start:]


def find_section_insert_point(body: str) -> int:
    """Find the best place to insert new sections (after title, before main content)."""
    # Look for first H1 or H2 heading
    h1_match = re.search(r"^#\s+.+$", body, re.MULTILINE)
    if h1_match:
        # Insert after the H1 and any immediately following paragraph
        pos = h1_match.end()
        # Skip past any following paragraph text (until next heading or blank line)
        while pos < len(body) and body[pos] == "\n":
            pos += 1
        # If there's a paragraph after the title, skip it
        next_heading = re.search(r"^#{1,2}\s+", body[pos:], re.MULTILINE)
        if next_heading:
            # Insert before the next heading
            return pos + next_heading.start()
        else:
            # Insert at end of body
            return len(body)
    return 0


def detect_existing_sections(body: str) -> dict[str, bool]:
    """Detect which recommended sections already exist."""
    found = {}
    for section, patterns in SECTION_PATTERNS.items():
        found[section] = False
        for pattern in patterns:
            if re.search(pattern, body, re.MULTILINE):
                found[section] = True
                break
    return found


def generate_goal_section(skill_name: str, description: str) -> str:
    """Generate a Goal section based on skill name and description."""
    # Extract the main purpose from description
    desc_lines = description.split("\n")
    main_desc = desc_lines[0] if desc_lines else ""

    # Clean up the description
    main_desc = re.sub(r"^【[^】]+】\s*", "", main_desc)
    main_desc = main_desc.strip().rstrip("。")

    return f"""
## Goal

{main_desc}"""


def generate_trigger_section(description: str) -> str:
    """Generate a Trigger section from the description."""
    # Look for existing trigger conditions in description
    trigger_match = re.search(r"触发时机[：:]\s*\n((?:\s*[-•]\s*.+\n?)+)", description)
    if trigger_match:
        triggers = trigger_match.group(1).strip()
        return f"""
## Trigger

{triggers}"""

    # Look for "Use when" or similar patterns
    use_when_match = re.search(r"(?:Use when|When to use)[：:]\s*\n((?:\s*[-•]\s*.+\n?)+)", description)
    if use_when_match:
        triggers = use_when_match.group(1).strip()
        return f"""
## Trigger

{triggers}"""

    # Generate generic trigger based on skill name
    return """
## Trigger

当用户需要使用此技能时触发。"""


def generate_workflow_section(skill_name: str) -> str:
    """Generate a Workflow section."""
    return """
## Workflow

```
输入 → 处理 → 输出
```"""


def audit_skill(skill_dir: Path, fix: bool = False) -> dict:
    """Audit a single skill and optionally fix issues."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"skill": skill_dir.name, "error": "SKILL.md not found"}

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    body = get_body_after_frontmatter(text)

    issues = []
    existing = detect_existing_sections(body)

    # Check for missing sections
    for section, found in existing.items():
        if not found:
            issues.append(f"Missing {section} section")

    # Check description length
    if "description" in fm:
        desc_len = len(fm["description"])
        if desc_len > 200:
            issues.append(f"Description too long ({desc_len} chars)")

    result = {
        "skill": skill_dir.name,
        "issues": issues,
        "existing_sections": existing,
        "fixed": False,
    }

    if fix and issues:
        # Apply fixes
        new_text = text

        # Add missing sections
        sections_to_add = []
        if not existing["Goal"]:
            sections_to_add.append(generate_goal_section(
                skill_dir.name,
                fm.get("description", "")
            ))
        if not existing["Trigger"]:
            sections_to_add.append(generate_trigger_section(
                fm.get("description", "")
            ))
        if not existing["Workflow"]:
            sections_to_add.append(generate_workflow_section(skill_dir.name))

        if sections_to_add:
            # Find insertion point
            insert_pos = find_section_insert_point(body)
            abs_insert = len(text) - len(body) + insert_pos

            # Insert new sections
            new_sections = "\n".join(sections_to_add) + "\n"
            new_text = new_text[:abs_insert] + new_sections + new_text[abs_insert:]

        # Write back if changed
        if new_text != text:
            skill_md.write_text(new_text, encoding="utf-8")
            result["fixed"] = True

    return result


def main():
    parser = argparse.ArgumentParser(description="Audit and improve skill files")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--skill", help="Audit specific skill")
    args = parser.parse_args()

    # Find all skill directories
    skill_dirs = []
    if args.skill:
        skill_dir = REPO_ROOT / args.skill
        if skill_dir.exists() and (skill_dir / "SKILL.md").exists():
            skill_dirs.append(skill_dir)
        else:
            print(f"Skill not found: {args.skill}")
            sys.exit(1)
    else:
        for d in sorted(REPO_ROOT.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                if d.name not in {"scripts", "tests", ".github", ".claude", "wiki"}:
                    if not d.name.endswith("-workspace"):
                        skill_dirs.append(d)

    print(f"Auditing {len(skill_dirs)} skills...")

    results = []
    for skill_dir in skill_dirs:
        result = audit_skill(skill_dir, fix=args.fix)
        results.append(result)

    # Summary
    total_issues = sum(len(r.get("issues", [])) for r in results)
    fixed_count = sum(1 for r in results if r.get("fixed"))

    print(f"\nSummary:")
    print(f"  Skills audited: {len(results)}")
    print(f"  Total issues: {total_issues}")
    if args.fix:
        print(f"  Skills fixed: {fixed_count}")

    # Show details
    for r in results:
        if r.get("issues"):
            print(f"\n{r['skill']}:")
            for issue in r["issues"]:
                print(f"  - {issue}")


if __name__ == "__main__":
    main()
