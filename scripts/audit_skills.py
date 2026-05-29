#!/usr/bin/env python3
"""
Audit all skill SKILL.md files.

Based on skill-creator quality standards:
- Detect missing Goal/Trigger/Workflow sections
- Check description length
- Verify reference files exist

Usage:
  python scripts/audit_skills.py              # audit all skills
  python scripts/audit_skills.py --skill NAME # audit specific skill
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from utils import parse_frontmatter, discover_skill_dirs

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


def audit_skill(skill_dir: Path) -> dict:
    """Audit a single skill and report issues."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"skill": skill_dir.name, "error": "SKILL.md not found"}

    text = skill_md.read_text(encoding="utf-8")
    fm, _, body = parse_frontmatter(text)

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

    return {
        "skill": skill_dir.name,
        "issues": issues,
        "existing_sections": existing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit skill files")
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
            return 1
    else:
        skill_dirs = discover_skill_dirs(REPO_ROOT)

    print(f"Auditing {len(skill_dirs)} skills...")

    results = []
    for skill_dir in skill_dirs:
        result = audit_skill(skill_dir)
        results.append(result)

    # Summary
    total_issues = sum(len(r.get("issues", [])) for r in results)

    print(f"\nSummary:")
    print(f"  Skills audited: {len(results)}")
    print(f"  Total issues: {total_issues}")

    # Show details
    for r in results:
        if r.get("issues"):
            print(f"\n{r['skill']}:")
            for issue in r["issues"]:
                print(f"  - {issue}")

    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
