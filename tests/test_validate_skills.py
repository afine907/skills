#!/usr/bin/env python3
"""Tests for the validate_skills.py validation script."""

import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts directory to path so we can import validate_skills
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate_skills
from validate_skills import (
    ALLOWED_CATEGORIES,
    ERROR,
    WARNING,
    check_body_content,
    check_frontmatter,
    check_references,
    discover_skills,
    main,
    run_checks,
)
from utils import parse_frontmatter

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestParseFrontmatter:
    """Tests for the parse_frontmatter function."""

    def test_valid_frontmatter(self):
        text = textwrap.dedent("""\
            ---
            name: my-skill
            description: "A test skill."
            category: productivity
            ---
            # Content
        """)
        fm, _, _ = parse_frontmatter(text)
        assert fm["name"] == "my-skill"
        assert fm["description"] == "A test skill."
        assert fm["category"] == "productivity"

    def test_no_frontmatter(self):
        text = "# Just a heading\n\nSome content."
        fm, _, _ = parse_frontmatter(text)
        assert fm == {}

    def test_unclosed_frontmatter(self):
        # Use a string that has opening --- but no closing ---
        text = "---\nname: broken\nsome content without closing marker"
        fm, _, _ = parse_frontmatter(text)
        assert fm == {}

    def test_empty_frontmatter(self):
        text = "---\n---\n# Content"
        fm, _, _ = parse_frontmatter(text)
        assert fm == {}

    def test_multiline_value(self):
        text = textwrap.dedent("""\
            ---
            name: ml-skill
            description: |
              This is a long
              description that spans
              multiple lines.
            category: development
            ---
        """)
        fm, _, _ = parse_frontmatter(text)
        assert fm["name"] == "ml-skill"
        assert "multiple lines" in fm["description"]
        assert fm["category"] == "development"

    def test_quoted_values_stripped(self):
        text = textwrap.dedent("""\
            ---
            name: quoted
            description: 'Single quoted'
            category: "double quoted"
            ---
        """)
        fm, _, _ = parse_frontmatter(text)
        assert fm["description"] == "Single quoted"
        assert fm["category"] == "double quoted"

    def test_frontmatter_with_trailing_whitespace(self):
        # The parser handles trailing whitespace on key lines
        text = "---\nname: spaced  \ncategory: quality  \n---\n"
        fm, _, _ = parse_frontmatter(text)
        assert fm["name"] == "spaced"
        assert fm["category"] == "quality"


class TestCheckFrontmatter:
    """Tests for the check_frontmatter function."""

    def test_valid_skill(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_skills, "REPO_ROOT", tmp_path.parent)
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: my-skill
            description: "A valid skill for testing purposes."
            category: productivity
            ---
            # Content

            Some body text.
        """))
        issues = check_frontmatter(skill_dir)
        errors = [(s, m) for s, m in issues if s == ERROR]
        assert errors == []

    def test_missing_skill_md(self, tmp_path):
        skill_dir = tmp_path / "no-skill"
        skill_dir.mkdir()
        issues = check_frontmatter(skill_dir)
        assert len(issues) >= 1
        assert any(sev == ERROR and "does not exist" in msg for sev, msg in issues)

    def test_empty_skill_md(self, tmp_path):
        skill_dir = tmp_path / "empty-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("")
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "No valid frontmatter" in msg for sev, msg in issues)

    def test_no_frontmatter(self, tmp_path):
        skill_dir = tmp_path / "no-fm"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# No frontmatter here\n")
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "No valid frontmatter" in msg for sev, msg in issues)

    def test_missing_name_field(self, tmp_path):
        skill_dir = tmp_path / "missing-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            description: "Missing name field entirely."
            category: productivity
            ---
        """))
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "Missing 'name'" in msg for sev, msg in issues)

    def test_name_mismatch(self, tmp_path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: wrong-name
            description: "Name does not match the directory."
            category: productivity
            ---
        """))
        issues = check_frontmatter(skill_dir)
        assert any(
            sev == ERROR and "does not match directory name" in msg
            for sev, msg in issues
        )

    def test_missing_description(self, tmp_path):
        skill_dir = tmp_path / "no-desc"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: no-desc
            category: quality
            ---
        """))
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "Missing 'description'" in msg for sev, msg in issues)

    def test_missing_category(self, tmp_path):
        skill_dir = tmp_path / "no-cat"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: no-cat
            description: "Missing category field."
            ---
        """))
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "Missing 'category'" in msg for sev, msg in issues)

    def test_invalid_category(self, tmp_path):
        skill_dir = tmp_path / "bad-cat"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: bad-cat
            description: "Invalid category value."
            category: not-a-valid-category
            ---
        """))
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "is not valid" in msg for sev, msg in issues)

    def test_all_valid_categories_accepted(self, tmp_path, monkeypatch):
        """Verify that every category in ALLOWED_CATEGORIES is accepted."""
        monkeypatch.setattr(validate_skills, "REPO_ROOT", tmp_path.parent)
        for cat in ALLOWED_CATEGORIES:
            skill_dir = tmp_path / f"skill-{cat}"
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(textwrap.dedent(f"""\
                ---
                name: skill-{cat}
                description: "Testing that category {cat} is accepted."
                category: {cat}
                ---
            """))
            issues = check_frontmatter(skill_dir)
            errors = [(s, m) for s, m in issues if s == ERROR]
            assert errors == [], f"Category '{cat}' should be valid but got errors: {errors}"


class TestCheckReferences:
    """Tests for the check_references function."""

    def test_no_references(self, tmp_path):
        skill_dir = tmp_path / "no-refs"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: no-refs
            description: "No file references at all."
            category: productivity
            ---
            # No links here
        """))
        issues = check_references(skill_dir)
        assert issues == []

    def test_valid_reference(self, tmp_path, monkeypatch):
        # Point REPO_ROOT to tmp_path so relative paths resolve correctly
        monkeypatch.setattr(validate_skills, "REPO_ROOT", tmp_path)
        skill_dir = tmp_path / "good-refs"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: good-refs
            description: "All references point to existing files."
            category: productivity
            ---
            See [guide](references/guide.md) for details.
        """))
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "guide.md").write_text("# Guide")
        issues = check_references(skill_dir)
        assert issues == []

    def test_broken_reference(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_skills, "REPO_ROOT", tmp_path)
        skill_dir = tmp_path / "broken-refs"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: broken-refs
            description: "References a file that does not exist."
            category: development
            ---
            See [missing](references/nonexistent.md) for details.
        """))
        issues = check_references(skill_dir)
        assert any(
            sev == ERROR and "not found" in msg for sev, msg in issues
        )

    def test_external_urls_skipped(self, tmp_path):
        skill_dir = tmp_path / "ext-urls"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: ext-urls
            description: "External URLs should be skipped during checks."
            category: productivity
            ---
            - [GitHub](https://github.com)
            - [Docs](http://docs.example.com)
            - [Email](mailto:test@example.com)
        """))
        issues = check_references(skill_dir)
        assert issues == []

    def test_template_placeholders_skipped(self, tmp_path):
        skill_dir = tmp_path / "placeholders"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: placeholders
            description: "Template placeholders should be skipped."
            category: productivity
            ---
            - [URL](URL)
            - [path](path)
        """))
        issues = check_references(skill_dir)
        assert issues == []


class TestCheckBodyContent:
    """Tests for the check_body_content function."""

    def test_empty_body(self, tmp_path):
        skill_dir = tmp_path / "empty-body"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: empty-body
            description: "Has frontmatter but no body."
            category: productivity
            ---
        """))
        issues = check_body_content(skill_dir)
        assert any(sev == ERROR and "empty beyond frontmatter" in msg for sev, msg in issues)

    def test_valid_body(self, tmp_path):
        skill_dir = tmp_path / "good-body"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: good-body
            description: "Has meaningful content after frontmatter."
            category: productivity
            ---

            # Good Skill

            ## Goal

            This skill does something useful.

            ## Workflow

            Step 1: Do thing.
            Step 2: Do another thing.
        """))
        issues = check_body_content(skill_dir)
        errors = [(s, m) for s, m in issues if s == ERROR]
        assert errors == []


class TestMainFunction:
    """Tests for the main() entry point."""

    def test_main_returns_zero_on_valid_repo(self, tmp_path, monkeypatch):
        """main() returns 0 when all skills are valid."""
        skill_dir = tmp_path / "valid-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: valid-skill
            description: "A completely valid skill for testing."
            category: productivity
            ---

            # Valid Skill

            ## Goal

            Does something useful.

            ## Workflow

            Step 1: Run the skill.
        """))

        monkeypatch.setattr(validate_skills, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(sys, "argv", ["validate_skills.py"])

        exit_code = main()
        assert exit_code == 0

    def test_main_returns_one_on_invalid_repo(self, tmp_path, monkeypatch):
        """main() returns 1 when any skill has errors."""
        skill_dir = tmp_path / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: wrong-name
            description: "Name does not match directory."
            category: productivity
            ---
        """))

        monkeypatch.setattr(validate_skills, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(sys, "argv", ["validate_skills.py"])

        exit_code = main()
        assert exit_code == 1


class TestFixtureSkills:
    """Tests using the fixture skills in tests/fixtures/."""

    def test_good_skill_passes(self):
        skill_dir = FIXTURES_DIR / "good-skill"
        issues = check_frontmatter(skill_dir)
        errors = [(s, m) for s, m in issues if s == ERROR]
        assert errors == []

    def test_bad_no_frontmatter_fails(self):
        skill_dir = FIXTURES_DIR / "bad-no-frontmatter"
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "No valid frontmatter" in msg for sev, msg in issues)

    def test_bad_invalid_category_fails(self):
        skill_dir = FIXTURES_DIR / "bad-invalid-category"
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR and "is not valid" in msg for sev, msg in issues)

    def test_bad_name_mismatch_fails(self):
        skill_dir = FIXTURES_DIR / "bad-name-mismatch"
        issues = check_frontmatter(skill_dir)
        assert any(
            sev == ERROR and "does not match directory name" in msg
            for sev, msg in issues
        )

    def test_bad_empty_fails(self):
        skill_dir = FIXTURES_DIR / "bad-empty"
        issues = check_frontmatter(skill_dir)
        assert any(sev == ERROR for sev, _ in issues)

    def test_bad_broken_links_fails(self, monkeypatch):
        # Point REPO_ROOT to fixtures parent so links resolve within scope
        monkeypatch.setattr(validate_skills, "REPO_ROOT", FIXTURES_DIR.parent)
        skill_dir = FIXTURES_DIR / "bad-broken-links"
        issues = check_references(skill_dir)
        assert any(sev == ERROR and "not found" in msg for sev, msg in issues)
