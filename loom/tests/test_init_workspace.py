#!/usr/bin/env python3
"""
Tests for init_workspace.py
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
import pytest

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from init_workspace import WorkspaceInitializer


class TestWorkspaceInitializer:
    """Test suite for WorkspaceInitializer"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def sample_prd(self, temp_dir):
        """Create a sample PRD file"""
        prd_path = Path(temp_dir) / "test_prd.md"
        prd_path.write_text("""# Test PRD

## Overview
This is a test PRD document.

## Requirements
- MUST: All users must be authenticated
- SHALL: Passwords must be hashed with bcrypt
- REQUIRED: All API responses must include requestId

## Security Constraints
- All database queries must use parameterized queries
- All sensitive data must be encrypted at rest
""")
        return prd_path

    def test_validate_project_name_valid(self):
        """Test valid project names"""
        initializer = WorkspaceInitializer.__new__(WorkspaceInitializer)

        assert initializer._validate_project_name("my-project") == "my-project"
        assert initializer._validate_project_name("test123") == "test123"
        assert initializer._validate_project_name("a1-b2-c3") == "a1-b2-c3"

    def test_validate_project_name_invalid(self):
        """Test invalid project names"""
        initializer = WorkspaceInitializer.__new__(WorkspaceInitializer)

        with pytest.raises(ValueError):
            initializer._validate_project_name("MyProject")  # Uppercase

        with pytest.raises(ValueError):
            initializer._validate_project_name("my_project")  # Underscore

        with pytest.raises(ValueError):
            initializer._validate_project_name("123project")  # Starts with number

        with pytest.raises(ValueError):
            initializer._validate_project_name("")  # Empty

    def test_extract_invariants(self, temp_dir, sample_prd):
        """Test invariants extraction from PRD"""
        # Create initializer with sample PRD
        initializer = WorkspaceInitializer("test-project", [str(sample_prd)])
        initializer.prd_files = [sample_prd]

        invariants = initializer._extract_invariants()

        assert len(invariants) > 0
        assert any("authenticated" in inv.lower() for inv in invariants)
        assert any("bcrypt" in inv.lower() for inv in invariants)

    def test_calculate_hash(self, temp_dir, sample_prd):
        """Test PRD hash calculation"""
        initializer = WorkspaceInitializer("test-project", [str(sample_prd)])
        initializer.prd_files = [sample_prd]

        hash1 = initializer._calculate_hash()
        hash2 = initializer._calculate_hash()

        assert len(hash1) == 64  # SHA-256 hex digest length
        assert hash1 == hash2  # Same content = same hash

    def test_create_manifest(self, temp_dir, sample_prd):
        """Test manifest creation"""
        # Change to temp directory
        os.chdir(temp_dir)

        initializer = WorkspaceInitializer("test-project", [str(sample_prd)])
        initializer.workspace_dir = Path(temp_dir) / ".claude" / "orchestra" / "test-project"
        initializer.prd_files = [sample_prd]

        initializer._create_directory_structure()
        manifest = initializer._create_manifest()

        assert manifest["project_metadata"]["name"] == "test-project"
        assert manifest["workflow"]["stage"] == "INIT"
        assert "schema_version" in manifest
        assert len(manifest["project_metadata"]["hash"]) == 64

    def test_force_overwrite(self, temp_dir, sample_prd):
        """Test --force flag for overwriting existing workspace"""
        os.chdir(temp_dir)

        # Create workspace first time
        initializer1 = WorkspaceInitializer("test-project", [str(sample_prd)], force=True)
        initializer1.workspace_dir = Path(temp_dir) / ".claude" / "orchestra" / "test-project"
        initializer1._create_directory_structure()
        initializer1._create_manifest()

        # Create again with force should succeed
        initializer2 = WorkspaceInitializer("test-project", [str(sample_prd)], force=True)
        initializer2.workspace_dir = initializer1.workspace_dir
        # Should not raise error
        assert initializer2.force is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
