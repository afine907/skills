#!/usr/bin/env python3
"""
Validate all skill SKILL.md files for:
  - Required frontmatter fields (name, description, category)
  - name matches directory name
  - category is in the allowed list
  - file references point to existing files
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_CATEGORIES = {
    "requirements",
    "development",
    "quality",
    "source-control",
    "operations",
    "productivity",
    "reference",
}

SKIP_DIRS = {"wiki", ".github", ".claude", "scripts"}

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> dict:
    """Parse simple YAML frontmatter between --- markers."""
    if not text.startswith("---"):
        return {}

    # Find closing ---
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
                # End of multiline, flush it
                result[current_key] = "\n".join(current_value_lines).strip()
                current_key = None
                current_value_lines = None
                in_multiline = False
                # Fall through to handle this line as a new key

        # Check for new key-value pair
        match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            if value == "|":
                in_multiline = True
                current_key = key
                current_value_lines = []
            else:
                # Strip surrounding quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                result[key] = value
            continue

    # Flush any remaining multiline value
    if in_multiline and current_key is not None and current_value_lines is not None:
        result[current_key] = "\n".join(current_value_lines).strip()

    return result


def check_frontmatter(skill_dir: Path) -> list[str]:
    """Validate a single skill's SKILL.md frontmatter. Returns list of errors."""
    errors = []
    skill_name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        errors.append(f"  MISSING: {skill_md} does not exist")
        return errors

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    if not fm:
        errors.append(f"  ERROR: No valid frontmatter found in {skill_md}")
        return errors

    # name field
    if "name" not in fm:
        errors.append(f"  ERROR: Missing 'name' field in frontmatter")
    elif fm["name"] != skill_name:
        errors.append(
            f"  ERROR: name '{fm['name']}' does not match directory name '{skill_name}'"
        )

    # description field
    if "description" not in fm:
        errors.append(f"  ERROR: Missing 'description' field in frontmatter")

    # category field
    if "category" not in fm:
        errors.append(f"  ERROR: Missing 'category' field in frontmatter")
    elif fm["category"] not in ALLOWED_CATEGORIES:
        errors.append(
            f"  ERROR: category '{fm['category']}' is not valid. "
            f"Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}"
        )

    return errors


def check_references(skill_dir: Path) -> list[str]:
    """Check that file references in SKILL.md point to existing files."""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return errors

    text = skill_md.read_text(encoding="utf-8")

    for match in LINK_RE.finditer(text):
        link_text = match.group(1)
        link_path = match.group(2)

        # Skip external URLs and template placeholders
        if link_path.startswith(("http://", "https://", "mailto:")):
            continue
        if link_path in ("URL", "url", "path", "#"):
            continue

        # Resolve relative to skill directory (for relative paths starting without /)
        # or relative to repo root (for paths starting with ../ or similar)
        resolved = (skill_dir / link_path).resolve()

        # If the path doesn't start with the repo root, it might be referencing
        # something else in the repo via a path from root
        try:
            resolved.relative_to(REPO_ROOT)
        except ValueError:
            # Not under repo root, mark error
            errors.append(
                f"  REFERENCE: '{link_path}' (text: '{link_text}') resolves outside repo"
            )
            continue

        if not resolved.exists():
            errors.append(
                f"  REFERENCE: '{link_path}' (text: '{link_text}') → {resolved} does not exist"
            )

    return errors


def main() -> int:
    """Main entry point. Returns exit code."""
    all_errors: dict[str, list[str]] = {}
    skill_count = 0

    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name in SKIP_DIRS:
            continue

        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue

        skill_count += 1
        errors = []
        errors.extend(check_frontmatter(entry))
        errors.extend(check_references(entry))

        if errors:
            all_errors[entry.name] = errors

    # Summary header
    print(f"Skills found: {skill_count}")
    print()

    if not all_errors:
        print("All skills pass validation.")
        return 0

    for skill_name in sorted(all_errors.keys()):
        errors = all_errors[skill_name]
        print(f"--- {skill_name} ({len(errors)} issue(s)) ---")
        for err in errors:
            print(err)
        print()

    total_issues = sum(len(v) for v in all_errors.values())
    print(f"FAILED: {len(all_errors)} skills with issues ({total_issues} total issues)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
