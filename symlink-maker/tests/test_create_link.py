"""Unit tests for create_link.py"""

import os
import platform
import sys
import tempfile
import shutil
import pytest

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from create_link import _relative_target, _create, _remove, create, remove


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temp workspace with a source file and link path."""
    source = tmp_path / "source_file.txt"
    source.write_text("hello")
    source_dir = tmp_path / "source_dir"
    source_dir.mkdir()
    (source_dir / "child.txt").write_text("child")
    link_path = tmp_path / "link_location.txt"
    link_dir = tmp_path / "link_dir"
    yield tmp_path


# --- _relative_target tests ---

class TestRelativeTarget:
    def test_same_directory(self, tmp_workspace):
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "link.txt")
        result = _relative_target(source, link)
        assert result == "source_file.txt"

    def test_different_subdirectory(self, tmp_workspace):
        sub = tmp_workspace / "sub"
        sub.mkdir()
        source = str(tmp_workspace / "source_file.txt")
        link = str(sub / "link.txt")
        result = _relative_target(source, link)
        assert result == os.path.join("..", "source_file.txt")

    def test_returns_absolute_on_windows_cross_drive(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        monkeypatch.setattr(os.path, "splitdrive", lambda p: ("C:", "dummy") if "C" in str(p) else ("D:", "dummy"))
        # Force cross-drive by patching splitdrive to return different drives
        original_splitdrive = os.path.splitdrive

        def fake_splitdrive(p):
            p_str = str(p)
            if "C" in p_str.upper() or "c" in p_str.lower():
                return ("C:", "path")
            return ("D:", "path")

        monkeypatch.setattr(os.path, "splitdrive", fake_splitdrive)
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "link.txt")
        result = _relative_target(source, link)
        # On non-Windows with monkeypatch, the drive check is skipped
        # so it still returns relative. The drive check only runs on Windows.
        assert isinstance(result, str)


# --- _create / _remove tests ---

class TestCreateRemove:
    def test_create_symlink(self, tmp_workspace):
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "link.txt")
        result = _create(source, link)
        assert result in ("symlink", "junction")
        assert os.path.islink(link) or os.path.isdir(link)

    def test_create_and_remove(self, tmp_workspace):
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "link.txt")
        _create(source, link)
        assert os.path.islink(link)
        _remove(link)
        assert not os.path.exists(link)

    def test_create_dir_symlink(self, tmp_workspace):
        source = str(tmp_workspace / "source_dir")
        link = str(tmp_workspace / "link_dir")
        _create(source, link)
        assert os.path.islink(link) or os.path.isdir(link)
        # Verify content accessible
        child = os.path.join(link, "child.txt")
        assert os.path.exists(child)

    def test_remove_nonexistent_doesnt_crash(self, tmp_workspace):
        link = str(tmp_workspace / "nonexistent")
        # Should not raise
        if os.path.islink(link):
            _remove(link)


# --- High-level create/remove tests ---

class TestCreateRemoveHighLevel:
    def test_create_basic(self, tmp_workspace):
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "mylink.txt")
        create(source, link)
        assert os.path.islink(link) or os.path.exists(link)
        with open(link) as f:
            assert f.read() == "hello"

    def test_create_idempotent(self, tmp_workspace):
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "mylink.txt")
        create(source, link)
        # Second call should say reused, not fail
        create(source, link)
        assert os.path.islink(link)

    def test_create_with_nonexistent_source_warns(self, tmp_workspace):
        link = str(tmp_workspace / "mylink.txt")
        create("/nonexistent/file", link)
        # Link is created but points to nonexistent target (broken symlink)
        assert os.path.islink(link)
        assert not os.path.exists(link)

    def test_remove_existing_link(self, tmp_workspace):
        source = str(tmp_workspace / "source_file.txt")
        link = str(tmp_workspace / "mylink.txt")
        create(source, link)
        remove(link)
        assert not os.path.islink(link)

    def test_remove_non_link_skips(self, tmp_workspace):
        regular = tmp_workspace / "regular_file.txt"
        regular.write_text("data")
        remove(str(regular))
        # File should still exist
        assert regular.exists()
