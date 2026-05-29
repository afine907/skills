#!/usr/bin/env python3
"""Tests that ALL existing skills in the repository follow the required structure.

These tests run against the real skill directories to ensure ongoing compliance.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path so we can import validate_skills
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_skills import (
    ALLOWED_CATEGORIES,
    ERROR,
    SKIP_DIRS,
    WARNING,
    check_body_content,
    check_frontmatter,
    check_references,
    parse_frontmatter,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def discover_skill_dirs():
    """Discover all skill directories in the repository."""
    skill_dirs = []
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
            skill_dirs.append(entry)
    return skill_dirs


ALL_SKILL_DIRS = discover_skill_dirs()


class TestAllSkillsExist:
    """Verify that we have skills to test and they all have SKILL.md files."""

    def test_skills_discovered(self):
        """At least one skill directory should exist."""
        assert len(ALL_SKILL_DIRS) > 0, "No skill directories found in the repository"

    def test_all_skill_dirs_have_skill_md(self):
        """Every non-skipped directory that looks like a skill must have SKILL.md."""
        for skill_dir in ALL_SKILL_DIRS:
            skill_md = skill_dir / "SKILL.md"
            assert skill_md.exists(), f"{skill_dir.name} is missing SKILL.md"


@pytest.mark.parametrize("skill_dir", ALL_SKILL_DIRS, ids=lambda p: p.name)
class TestSkillFrontmatter:
    """Test that each skill's SKILL.md has valid frontmatter."""

    def test_has_frontmatter(self, skill_dir):
        """SKILL.md must have YAML frontmatter."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        assert fm, f"{skill_dir.name}/SKILL.md has no valid frontmatter"

    def test_has_name_field(self, skill_dir):
        """Frontmatter must include a 'name' field."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        assert "name" in fm, f"{skill_dir.name}/SKILL.md is missing 'name' in frontmatter"

    def test_name_matches_directory(self, skill_dir):
        """The 'name' field must match the directory name."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if "name" in fm:
            assert fm["name"] == skill_dir.name, (
                f"{skill_dir.name}/SKILL.md has name='{fm['name']}' "
                f"but directory is '{skill_dir.name}'"
            )

    def test_has_description_field(self, skill_dir):
        """Frontmatter must include a 'description' field."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        assert "description" in fm, (
            f"{skill_dir.name}/SKILL.md is missing 'description' in frontmatter"
        )

    def test_description_not_empty(self, skill_dir):
        """The 'description' field must not be empty."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if "description" in fm:
            assert fm["description"].strip(), (
                f"{skill_dir.name}/SKILL.md has empty 'description'"
            )

    def test_has_category_field(self, skill_dir):
        """Frontmatter must include a 'category' field."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        assert "category" in fm, (
            f"{skill_dir.name}/SKILL.md is missing 'category' in frontmatter"
        )

    def test_category_is_valid(self, skill_dir):
        """The 'category' must be one of the allowed values."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if "category" in fm:
            assert fm["category"] in ALLOWED_CATEGORIES, (
                f"{skill_dir.name}/SKILL.md has category='{fm['category']}' "
                f"which is not in {sorted(ALLOWED_CATEGORIES)}"
            )


@pytest.mark.parametrize("skill_dir", ALL_SKILL_DIRS, ids=lambda p: p.name)
class TestSkillReferences:
    """Test that file references in each skill's SKILL.md point to existing files."""

    def test_all_references_valid(self, skill_dir):
        """All [text](path) links must point to existing files."""
        issues = check_references(skill_dir)
        errors = [(s, m) for s, m in issues if s == ERROR]
        assert errors == [], (
            f"{skill_dir.name}/SKILL.md has broken references:\n"
            + "\n".join(f"  [{s}] {m}" for s, m in errors)
        )


@pytest.mark.parametrize("skill_dir", ALL_SKILL_DIRS, ids=lambda p: p.name)
class TestSkillContent:
    """Test that each skill's SKILL.md has meaningful content beyond frontmatter."""

    def test_has_content_after_frontmatter(self, skill_dir):
        """SKILL.md should have content after the frontmatter block."""
        issues = check_body_content(skill_dir)
        errors = [(s, m) for s, m in issues if s == ERROR]
        assert errors == [], (
            f"{skill_dir.name}/SKILL.md body issues:\n"
            + "\n".join(f"  [{s}] {m}" for s, m in errors)
        )

    def test_has_heading(self, skill_dir):
        """SKILL.md should contain at least one markdown heading."""
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        lines = text.split("\n")
        has_heading = any(line.strip().startswith("#") for line in lines)
        assert has_heading, (
            f"{skill_dir.name}/SKILL.md has no markdown headings"
        )
