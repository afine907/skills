"""Shared fixtures for skills repository tests."""

import shutil
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def tmp_skill_dir(tmp_path):
    """Create a temporary directory that looks like a skill directory.

    Returns a callable that takes a skill name and returns the directory path.
    The directory will be cleaned up after the test.
    """
    created_dirs = []

    def _make_skill(name: str) -> Path:
        skill_dir = tmp_path / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(skill_dir)
        return skill_dir

    yield _make_skill

    # Cleanup is handled by tmp_path fixture


@pytest.fixture
def valid_skill_md():
    """Return a valid SKILL.md content string."""
    return textwrap.dedent("""\
        ---
        name: test-skill
        description: "A test skill for unit testing."
        category: productivity
        ---

        # Test Skill

        A skill used for testing purposes.

        ## Usage

        Run the skill with `/test-skill`.
    """)


@pytest.fixture
def repo_root():
    """Return the repository root path."""
    return REPO_ROOT


@pytest.fixture
def all_skill_dirs():
    """Return a list of all skill directories in the repository.

    A skill directory is any directory (not in SKIP_DIRS) that contains a SKILL.md file.
    """
    from scripts.validate_skills import SKIP_DIRS

    skill_dirs = []
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name in SKIP_DIRS:
            continue
        if (entry / "SKILL.md").exists():
            skill_dirs.append(entry)
    return skill_dirs
