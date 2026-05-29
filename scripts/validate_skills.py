#!/usr/bin/env python3
"""
Validate all skill SKILL.md files.

Checks:
  - Required frontmatter fields (name, description, category)
  - name matches directory name
  - category is in the allowed list (with fuzzy typo detection)
  - description length is reasonable (10-200 chars)
  - SKILL.md has recommended sections (Title, Goal, Trigger conditions, Workflow)
  - SKILL.md is not empty beyond frontmatter
  - No duplicate skill names across directories
  - references/ directory contains at least 1 file if it exists
  - scripts/ has __init__.py if it contains .py files
  - No broken internal markdown links
  - file references point to existing files

Usage:
  python scripts/validate_skills.py            # normal output
  python scripts/validate_skills.py --verbose  # detailed output
  python scripts/validate_skills.py --fix      # auto-fix simple issues
"""

from __future__ import annotations

import argparse
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

# Common misspellings / near-misses of allowed categories
CATEGORY_TYPOS: dict[str, str] = {
    "developement": "development",
    "developmnt": "development",
    "devlopment": "development",
    "develpoment": "development",
    "qualty": "quality",
    "quailty": "quality",
    "qualiy": "quality",
    "souce-control": "source-control",
    "source_controll": "source-control",
    "sourcecontroll": "source-control",
    "sourc-control": "source-control",
    "soruce-control": "source-control",
    "opertions": "operations",
    "opreations": "operations",
    "opertaions": "operations",
    "opeartions": "operations",
    "produtivity": "productivity",
    "productvity": "productivity",
    "prodcutivity": "productivity",
    "produvtivity": "productivity",
    "reqirements": "requirements",
    "requiremnts": "requirements",
    "requrements": "requirements",
    "requierments": "requirements",
    "refrence": "reference",
    "referece": "reference",
    "refernce": "reference",
}

RECOMMENDED_SECTIONS = {
    "Title": [
        # Title is special: we check for the presence of an H1 heading
    ],
    "Goal": [
        "goal", "purpose", "overview", "description", "summary",
        "what it does", "what this does", "about",
    ],
    "Trigger": [
        "trigger", "when to use", "usage", "invoke", "activate",
        "trigger condition", "when to invoke",
    ],
    "Workflow": [
        "workflow", "how it works", "steps", "process", "procedure",
        "guide", "commands", "usage instructions", "tutorial",
        "quick start", "getting started",
    ],
}

SKIP_DIRS = {"wiki", ".github", ".claude", "scripts", ".git", "__pycache__"}

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)

# Severity levels
ERROR = "ERROR"
WARNING = "WARNING"
INFO = "INFO"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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

    # Skip past the closing --- and any immediate newline
    body_start = end + 3
    if body_start < len(text) and text[body_start] == "\n":
        body_start += 1
    return text[body_start:]


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def fuzzy_match_category(category: str) -> str | None:
    """Try to find the intended category for a misspelled input.

    Returns the corrected category name, or None if no close match found.
    """
    normalized = category.strip().lower().replace("_", "-")

    # Direct match after normalization
    if normalized in ALLOWED_CATEGORIES:
        return normalized

    # Check known typo map
    if normalized in CATEGORY_TYPOS:
        return CATEGORY_TYPOS[normalized]

    # Fuzzy match: if distance <= 2 to any allowed category, suggest it
    for allowed in ALLOWED_CATEGORIES:
        if levenshtein_distance(normalized, allowed) <= 2:
            return allowed

    return None


# ---------------------------------------------------------------------------
# Fix helpers
# ---------------------------------------------------------------------------


def fix_trailing_whitespace(text: str) -> tuple[str, bool]:
    """Remove trailing whitespace from each line. Returns (fixed_text, changed)."""
    fixed = "\n".join(line.rstrip() for line in text.split("\n"))
    return fixed, fixed != text


def fix_missing_newline_at_eof(text: str) -> tuple[str, bool]:
    """Ensure file ends with exactly one newline. Returns (fixed_text, changed)."""
    if not text:
        return text, False
    stripped = text.rstrip("\n")
    fixed = stripped + "\n"
    return fixed, fixed != text


# ---------------------------------------------------------------------------
# Check functions -- each returns list of (severity, message) tuples
# ---------------------------------------------------------------------------


def check_frontmatter(
    skill_dir: Path, verbose: bool = False
) -> list[tuple[str, str]]:
    """Validate a single skill's SKILL.md frontmatter."""
    issues: list[tuple[str, str]] = []
    skill_name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        issues.append((ERROR, f"SKILL.md does not exist"))
        return issues

    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    if not fm:
        issues.append((ERROR, "No valid frontmatter found"))
        return issues

    # name field
    if "name" not in fm:
        issues.append((ERROR, "Missing 'name' field in frontmatter"))
    elif fm["name"] != skill_name:
        issues.append(
            (ERROR, f"name '{fm['name']}' does not match directory name '{skill_name}'")
        )

    # description field
    if "description" not in fm:
        issues.append((ERROR, "Missing 'description' field in frontmatter"))
    else:
        desc = fm["description"]
        if len(desc) < 10:
            issues.append(
                (WARNING, f"Description too short ({len(desc)} chars, minimum 10)")
            )
        elif len(desc) > 200:
            issues.append(
                (WARNING, f"Description too long ({len(desc)} chars, maximum 200)")
            )

    # category field
    if "category" not in fm:
        issues.append((ERROR, "Missing 'category' field in frontmatter"))
    elif fm["category"] not in ALLOWED_CATEGORIES:
        suggestion = fuzzy_match_category(fm["category"])
        if suggestion:
            issues.append(
                (
                    ERROR,
                    f"category '{fm['category']}' is not valid. "
                    f"Did you mean '{suggestion}'? "
                    f"Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}",
                )
            )
        else:
            issues.append(
                (
                    ERROR,
                    f"category '{fm['category']}' is not valid. "
                    f"Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}",
                )
            )

    return issues


def check_body_content(skill_dir: Path) -> list[tuple[str, str]]:
    """Check that SKILL.md has meaningful content after frontmatter."""
    issues: list[tuple[str, str]] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return issues

    text = skill_md.read_text(encoding="utf-8")
    body = get_body_after_frontmatter(text)

    # Check body is not empty
    if not body.strip():
        issues.append((ERROR, "SKILL.md is empty beyond frontmatter"))
        return issues

    # Check for recommended sections
    headings: list[str] = []
    h1_count = 0
    for m in HEADING_RE.finditer(body):
        heading_text = m.group(1).strip()
        headings.append(heading_text.lower())
        if m.group(0).startswith("# "):
            h1_count += 1

    for section, synonyms in RECOMMENDED_SECTIONS.items():
        found = False

        if section == "Title":
            # Title is present if there's at least one H1 heading
            found = h1_count > 0
        else:
            # Check if any heading contains one of the synonyms
            for h in headings:
                if any(syn in h for syn in synonyms):
                    found = True
                    break

        if not found:
            issues.append(
                (WARNING, f"Missing recommended section: '{section}'")
            )

    return issues


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks from text to avoid false-positive link checks."""
    return re.sub(r"```[\s\S]*?```", "", text)


def check_references(skill_dir: Path) -> list[tuple[str, str]]:
    """Check that file references in SKILL.md point to existing files."""
    issues: list[tuple[str, str]] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return issues

    text = skill_md.read_text(encoding="utf-8")
    text = strip_code_blocks(text)

    for match in LINK_RE.finditer(text):
        link_text = match.group(1)
        link_path = match.group(2)

        # Skip external URLs and template placeholders
        if link_path.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if link_path in ("URL", "url", "path"):
            continue

        # Strip anchor fragments for file existence check
        file_part = link_path.split("#")[0]
        if not file_part:
            continue

        # Resolve relative to skill directory
        resolved = (skill_dir / file_part).resolve()

        # Verify it's under the repo root
        try:
            resolved.relative_to(REPO_ROOT)
        except ValueError:
            issues.append(
                (ERROR, f"Link '{link_path}' (text: '{link_text}') resolves outside repo")
            )
            continue

        if not resolved.exists():
            issues.append(
                (ERROR, f"Broken link '{link_path}' (text: '{link_text}') -> file not found")
            )

    return issues


def check_references_dir(skill_dir: Path) -> list[tuple[str, str]]:
    """Check that references/ directory contains at least 1 file if it exists."""
    issues: list[tuple[str, str]] = []
    refs_dir = skill_dir / "references"

    if refs_dir.is_dir():
        files = [f for f in refs_dir.iterdir() if f.is_file()]
        if not files:
            issues.append(
                (WARNING, "references/ directory exists but contains no files")
            )

    return issues


def check_scripts_init(skill_dir: Path) -> list[tuple[str, str]]:
    """Check that scripts/ has __init__.py if it contains .py files."""
    issues: list[tuple[str, str]] = []
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.is_dir():
        return issues

    py_files = [f for f in scripts_dir.iterdir() if f.is_file() and f.suffix == ".py"]
    init_file = scripts_dir / "__init__.py"

    if py_files and not init_file.exists():
        py_names = ", ".join(f.name for f in sorted(py_files))
        issues.append(
            (WARNING, f"scripts/ has .py files ({py_names}) but no __init__.py")
        )

    return issues


# ---------------------------------------------------------------------------
# Global checks (across all skills)
# ---------------------------------------------------------------------------


def check_duplicate_names(
    all_skills: dict[str, Path],
) -> dict[str, list[tuple[str, str]]]:
    """Check for duplicate skill names across directories."""
    issues_by_skill: dict[str, list[tuple[str, str]]] = {}

    # Build name -> list of dirs mapping
    name_to_dirs: dict[str, list[str]] = {}
    for skill_name, skill_dir in all_skills.items():
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        declared_name = fm.get("name", "")
        if declared_name:
            name_to_dirs.setdefault(declared_name, []).append(skill_name)

    for name, dirs in name_to_dirs.items():
        if len(dirs) > 1:
            dir_list = ", ".join(sorted(dirs))
            for d in dirs:
                issues_by_skill.setdefault(d, []).append(
                    (ERROR, f"Duplicate skill name '{name}' found in: {dir_list}")
                )

    return issues_by_skill


# ---------------------------------------------------------------------------
# Fix logic
# ---------------------------------------------------------------------------


def apply_fixes(skill_dir: Path, verbose: bool = False) -> list[str]:
    """Auto-fix simple issues in SKILL.md. Returns list of applied fixes."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []

    applied: list[str] = []
    text = skill_md.read_text(encoding="utf-8")
    original = text

    text, changed = fix_trailing_whitespace(text)
    if changed:
        applied.append("Removed trailing whitespace")

    text, changed = fix_missing_newline_at_eof(text)
    if changed:
        applied.append("Added missing newline at end of file")

    if text != original:
        skill_md.write_text(text, encoding="utf-8")

    return applied


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def discover_skills() -> dict[str, Path]:
    """Discover all skill directories in the repo."""
    skills: dict[str, Path] = {}
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        if entry.name in SKIP_DIRS:
            continue
        if entry.name.endswith("-workspace"):
            continue
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            skills[entry.name] = entry
    return skills


def run_checks(
    skills: dict[str, Path], verbose: bool = False
) -> dict[str, list[tuple[str, str]]]:
    """Run all checks on all skills. Returns skill_name -> list of (severity, message)."""
    results: dict[str, list[tuple[str, str]]] = {}

    for skill_name, skill_dir in sorted(skills.items()):
        issues: list[tuple[str, str]] = []
        issues.extend(check_frontmatter(skill_dir, verbose=verbose))
        issues.extend(check_body_content(skill_dir))
        issues.extend(check_references(skill_dir))
        issues.extend(check_references_dir(skill_dir))
        issues.extend(check_scripts_init(skill_dir))
        if issues:
            results[skill_name] = issues

    # Global checks
    dup_issues = check_duplicate_names(skills)
    for skill_name, dup_iss in dup_issues.items():
        results.setdefault(skill_name, []).extend(dup_iss)

    return results


def print_summary_table(
    skills: dict[str, Path],
    results: dict[str, list[tuple[str, str]]],
    verbose: bool = False,
) -> None:
    """Print a formatted summary table."""
    if not skills:
        print("No skills found.")
        return

    # Determine column widths
    name_width = max(len(n) for n in skills)
    name_width = max(name_width, len("Skill"))

    # Header
    header = f"{'Skill':<{name_width}}  {'Status':<8}  {'Errors':>6}  {'Warnings':>8}"
    separator = f"{'-' * name_width}  {'-' * 8}  {'-' * 6}  {'-' * 8}"

    print()
    print(header)
    print(separator)

    pass_count = 0
    fail_count = 0

    for skill_name in sorted(skills):
        issues = results.get(skill_name, [])
        errors = sum(1 for sev, _ in issues if sev == ERROR)
        warnings = sum(1 for sev, _ in issues if sev == WARNING)

        if errors > 0:
            status = "FAIL"
            fail_count += 1
        elif warnings > 0:
            status = "WARN"
            pass_count += 1
        else:
            status = "PASS"
            pass_count += 1

        print(
            f"{skill_name:<{name_width}}  {status:<8}  {errors:>6}  {warnings:>8}"
        )

        if verbose and issues:
            for sev, msg in issues:
                print(f"{'':>{name_width}}  [{sev}] {msg}")

    print(separator)
    total = len(skills)
    print(f"{'Total':<{name_width}}  {total:>8}  {pass_count:>6} pass  {fail_count} fail")
    print()


def print_detailed_results(
    results: dict[str, list[tuple[str, str]]],
) -> None:
    """Print detailed results for skills with issues."""
    if not results:
        return

    for skill_name in sorted(results):
        issues = results[skill_name]
        errors = sum(1 for sev, _ in issues if sev == ERROR)
        warnings = sum(1 for sev, _ in issues if sev == WARNING)
        print(f"--- {skill_name} ({errors} error(s), {warnings} warning(s)) ---")
        for sev, msg in issues:
            print(f"  [{sev}] {msg}")
        print()


def main() -> int:
    """Main entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Validate skill SKILL.md files in the repository."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed per-skill issues in the summary table.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix simple issues (trailing whitespace, missing newline at EOF).",
    )
    args = parser.parse_args()

    skills = discover_skills()

    # Apply fixes first if requested
    if args.fix:
        print("Applying auto-fixes...")
        for skill_name, skill_dir in sorted(skills.items()):
            fixes = apply_fixes(skill_dir, verbose=args.verbose)
            if fixes:
                print(f"  {skill_name}:")
                for fix in fixes:
                    print(f"    - {fix}")
        print()

    # Run all checks
    results = run_checks(skills, verbose=args.verbose)

    # Print summary table
    print(f"Skills found: {len(skills)}")
    print_summary_table(skills, results, verbose=args.verbose)

    # Print detailed results if there are issues
    if results and not args.verbose:
        print_detailed_results(results)

    # Final status
    total_errors = sum(
        sum(1 for sev, _ in issues if sev == ERROR)
        for issues in results.values()
    )
    total_warnings = sum(
        sum(1 for sev, _ in issues if sev == WARNING)
        for issues in results.values()
    )

    if total_errors == 0 and total_warnings == 0:
        print("All skills pass validation.")
        return 0
    elif total_errors == 0:
        print(f"PASSED with {total_warnings} warning(s).")
        return 0
    else:
        print(
            f"FAILED: {len(results)} skills with issues "
            f"({total_errors} error(s), {total_warnings} warning(s))"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
