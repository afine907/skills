#!/usr/bin/env python3
"""
Tests for risk_scanner.py
"""

import json
import tempfile
import shutil
from pathlib import Path
import pytest

# Add scripts to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from risk_scanner import RiskScanner, Risk


class TestRiskScanner:
    """Test suite for RiskScanner"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project with manifest and PRD"""
        temp = tempfile.mkdtemp()
        project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        project_dir.mkdir(parents=True)

        # Create sample PRD with various risks
        prd_path = Path(temp) / "docs" / "prd.md"
        prd_path.parent.mkdir(parents=True)
        prd_path.write_text("""
# Test PRD

## Payment API

The payment callback handler processes incoming payment notifications.
Each callback should be processed within 5 seconds.

### User Authentication

GET /api/users/{id} returns user data.
Admin API endpoint for user management.

### Database Operations

SELECT * FROM users WHERE id = {userId}

### Configuration

password = "hardcoded_password_123"
apiKey = "sk_test_12345"

### Input Processing

The input value is processed directly.
For each user in users, call getUserOrders(user).

### TODO Items

TODO: Implement rate limiting
FIXME: Add proper error handling
""")

        manifest = {
            "schema_version": "1.0.0",
            "project_metadata": {
                "name": "test-project",
                "prd_files": [str(prd_path)]
            },
            "workflow": {
                "stage": "INIT"
            },
            "dag": {"nodes": []}
        }

        manifest_path = project_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        yield temp, prd_path
        shutil.rmtree(temp, ignore_errors=True)

    def test_scan_finds_risks(self, temp_project):
        """Test that scan finds risks in PRD"""
        temp, prd_path = temp_project

        scanner = RiskScanner("test-project")
        scanner.project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        scanner.manifest_path = scanner.project_dir / "manifest.json"
        scanner.manifest = json.loads(scanner.manifest_path.read_text())

        risks = scanner.scan()

        assert len(risks) > 0

    def test_risk_deduplication(self, temp_project):
        """Test that duplicate risks are removed"""
        temp, prd_path = temp_project

        scanner = RiskScanner("test-project")
        scanner.project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        scanner.manifest_path = scanner.project_dir / "manifest.json"
        scanner.manifest = json.loads(scanner.manifest_path.read_text())

        # Create multiple identical risks
        risk1 = Risk(
            id="RISK-001",
            severity="P2",
            risk_type="Documentation",
            title="Unfinished item",
            description="TODO found",
            location="file.md:10",
            suggestion="Complete it"
        )
        risk2 = Risk(
            id="RISK-002",
            severity="P2",
            risk_type="Documentation",
            title="Unfinished item",
            description="TODO found",
            location="file.md:10",
            suggestion="Complete it"
        )

        scanner.risks = [risk1, risk2]
        scanner._seen_risks.add(risk1.get_dedup_key())
        scanner._seen_risks.add(risk2.get_dedup_key())

        # Both should have same dedup key
        assert risk1.get_dedup_key() == risk2.get_dedup_key()

    def test_false_positive_detection(self, temp_project):
        """Test that false positives are filtered"""
        temp, prd_path = temp_project

        scanner = RiskScanner("test-project")
        scanner.project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        scanner.manifest_path = scanner.project_dir / "manifest.json"
        scanner.manifest = json.loads(scanner.manifest_path.read_text())

        # Content with false positive hint
        content = "This is an example password = 'test123' for documentation purposes"
        config = {
            "pattern": r"password\s*=\s*['\"]",
            "false_positive_hints": ["example", "documentation", "test"]
        }

        is_fp = scanner._is_false_positive(content, config, "password = 'test123'")
        assert is_fp is True

    def test_generate_markdown_report(self, temp_project):
        """Test Markdown report generation"""
        temp, prd_path = temp_project

        scanner = RiskScanner("test-project")
        scanner.project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        scanner.manifest_path = scanner.project_dir / "manifest.json"
        scanner.manifest = json.loads(scanner.manifest_path.read_text())

        scanner.scan()
        report = scanner.generate_report("markdown")

        assert "# Risk Audit Report" in report
        assert "## Overview" in report

    def test_generate_json_report(self, temp_project):
        """Test JSON report generation"""
        temp, prd_path = temp_project

        scanner = RiskScanner("test-project")
        scanner.project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        scanner.manifest_path = scanner.project_dir / "manifest.json"
        scanner.manifest = json.loads(scanner.manifest_path.read_text())

        scanner.scan()
        report = scanner.generate_report("json")

        # Should be valid JSON
        data = json.loads(report)
        assert "scan_time" in data
        assert "summary" in data
        assert "risks" in data

    def test_risk_severity_classification(self, temp_project):
        """Test that risks are classified by severity"""
        temp, prd_path = temp_project

        scanner = RiskScanner("test-project")
        scanner.project_dir = Path(temp) / ".claude" / "orchestra" / "test-project"
        scanner.manifest_path = scanner.project_dir / "manifest.json"
        scanner.manifest = json.loads(scanner.manifest_path.read_text())

        risks = scanner.scan()

        # Check that we have at least some risks with valid severities
        severities = {r.severity for r in risks}
        assert severities.issubset({"P0", "P1", "P2"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
