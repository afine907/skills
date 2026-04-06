#!/usr/bin/env python3
"""
Task-Loom Workspace Initializer

Usage:
    python init_workspace.py <project_name> <prd_paths...>
    python init_workspace.py my-project docs/prd/*.md
    python init_workspace.py ecommerce docs/prd/main.md docs/prd/api.md --force

Arguments:
    project_name: Project name in kebab-case format
    prd_paths: PRD file paths (supports glob patterns)

Options:
    --force, -f: Overwrite existing workspace without prompting
"""

import argparse
import glob
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


# Schema version for manifest.json - increment when structure changes
MANIFEST_SCHEMA_VERSION = "1.0.0"


class WorkspaceInitializer:
    """Task-Loom Workspace Initializer"""

    ORCHESTRA_DIR = ".claude/orchestra"

    def __init__(self, project_name: str, prd_paths: List[str], force: bool = False):
        self.project_name = self._validate_project_name(project_name)
        self.prd_files = self._resolve_prd_paths(prd_paths)
        self.workspace_dir = Path(self.ORCHESTRA_DIR) / self.project_name
        self.force = force

    def _validate_project_name(self, name: str) -> str:
        """Validate project name format"""
        if not re.match(r'^[a-z][a-z0-9-]*$', name):
            raise ValueError(
                f"Invalid project name '{name}'. "
                "Must start with lowercase letter, contain only lowercase letters, "
                "numbers, and hyphens."
            )
        if len(name) > 64:
            raise ValueError(f"Project name too long. Max 64 characters.")
        return name

    def _resolve_prd_paths(self, patterns: List[str]) -> List[Path]:
        """Resolve PRD file paths (supports glob patterns)"""
        files = []
        base_dir = Path.cwd().resolve()

        for pattern in patterns:
            matched = glob.glob(pattern, recursive=True)
            if not matched:
                raise FileNotFoundError(f"No files found matching: {pattern}")

            for f in matched:
                file_path = Path(f).resolve()
                # Security: prevent path traversal
                try:
                    file_path.relative_to(base_dir)
                except ValueError:
                    raise ValueError(f"Path traversal detected: {file_path} is outside workspace")
                files.append(file_path)

        return sorted(set(files))

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of all PRD files"""
        hasher = hashlib.sha256()
        for file_path in self.prd_files:
            content = file_path.read_bytes()
            hasher.update(content)
            hasher.update(str(file_path).encode())  # Include file path in hash
        return hasher.hexdigest()

    def _extract_invariants(self) -> List[str]:
        """Extract global invariants from PRD documents"""
        invariants = []

        # Keyword patterns for different languages
        patterns = [
            # English patterns
            r'(?:MUST|SHALL|REQUIRED|MANDATORY)[：:\s]+([^\n]+)',
            r'(?:Security Constraint|SecurityRequirement)[：:\s]+([^\n]+)',
            r'(?:Compliance Requirement|Compliance)[：:\s]+([^\n]+)',
            r'(?:Technical Constraint|Tech Constraint)[：:\s]+([^\n]+)',
            r'(?:Non-negotiable|Invariant)[：:\s]+([^\n]+)',
            # Chinese patterns
            r'(?:必须|应当|一定要)[：:\s]+([^\n]+)',
            r'(?:安全约束|安全要求)[：:\s]+([^\n]+)',
            r'(?:合规要求|合规)[：:\s]+([^\n]+)',
            r'(?:技术限制|技术约束)[：:\s]+([^\n]+)',
        ]

        for file_path in self.prd_files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = file_path.read_text(encoding='utf-8-sig')

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                invariants.extend(matches)

        return list(set(invariants))  # Deduplicate

    def _create_directory_structure(self) -> None:
        """Create workspace directory structure"""
        subdirs = ['specs', 'ledgers']

        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        for subdir in subdirs:
            (self.workspace_dir / subdir).mkdir(exist_ok=True)

        print(f"✓ Created workspace directory: {self.workspace_dir}")

    def _create_manifest(self) -> Dict[str, Any]:
        """Create manifest.json with schema version"""
        manifest = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "project_metadata": {
                "name": self.project_name,
                "version": "1.0.0",
                "hash": self._calculate_hash(),
                "created_at": datetime.utcnow().isoformat() + "Z",
                "prd_files": [str(f) for f in self.prd_files]
            },
            "workflow": {
                "stage": "INIT",
                "active_task_id": None,
                "concurrency_limit": 3,
                "retry_count": {}
            },
            "dag": {
                "nodes": []
            },
            "audit_results": None
        }

        manifest_path = self.workspace_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

        print(f"✓ Created manifest.json (schema v{MANIFEST_SCHEMA_VERSION})")
        return manifest

    def _create_constitution(self, invariants: List[str]) -> None:
        """Create constitution.md with global invariants"""
        content = """# Global Invariants

The following rules are extracted from PRD documents as immutable constraints.
All tasks must adhere to these invariants throughout the project.

## Extraction Metadata

- Extracted At: {timestamp}
- Source Files: {files}
- Rules Count: {count}

## Invariant Rules

{rules}
""".format(
            timestamp=datetime.utcnow().isoformat() + "Z",
            files=", ".join(str(f) for f in self.prd_files),
            count=len(invariants),
            rules="\n".join(f"{i+1}. {inv}" for i, inv in enumerate(invariants))
            if invariants else "_No explicit global invariants detected_"
        )

        constitution_path = self.workspace_dir / "constitution.md"
        constitution_path.write_text(content, encoding='utf-8')

        print(f"✓ Created constitution.md ({len(invariants)} invariants)")

    def _create_empty_files(self) -> None:
        """Create empty placeholder files"""
        # vulnerability_report.md
        report_path = self.workspace_dir / "vulnerability_report.md"
        report_path.write_text("# Risk Audit Report\n\n_Waiting for audit phase_\n", encoding='utf-8')

        print(f"✓ Created vulnerability_report.md (placeholder)")

    def initialize(self) -> None:
        """Execute initialization process"""
        print(f"\n🚀 Initializing Task-Loom workspace: {self.project_name}")
        print(f"   PRD files: {len(self.prd_files)}")

        # Check if workspace already exists
        if self.workspace_dir.exists():
            if not self.force:
                print(f"\n❌ Error: Workspace '{self.project_name}' already exists.")
                print(f"   Use --force to overwrite, or choose a different project name.")
                sys.exit(1)
            print(f"   ⚠️  Overwriting existing workspace (--force)")

        # Execute initialization steps
        self._create_directory_structure()
        manifest = self._create_manifest()
        invariants = self._extract_invariants()
        self._create_constitution(invariants)
        self._create_empty_files()

        print(f"\n✅ Workspace initialized successfully!")
        print(f"\nNext steps:")
        print(f"  1. Run `/task-loom audit` to scan for risks")
        print(f"  2. Run `/task-loom plan` to create task DAG")
        print(f"  3. Run `/task-loom execute` to start development")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a Task-Loom workspace for project orchestration"
    )
    parser.add_argument(
        "project_name",
        help="Project name in kebab-case format (e.g., my-project)"
    )
    parser.add_argument(
        "prd_paths",
        nargs="+",
        help="Paths to PRD files (supports glob patterns)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing workspace without prompting"
    )

    args = parser.parse_args()

    try:
        initializer = WorkspaceInitializer(args.project_name, args.prd_paths, args.force)
        initializer.initialize()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
