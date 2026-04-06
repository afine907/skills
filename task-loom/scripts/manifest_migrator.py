#!/usr/bin/env python3
"""
Loom Manifest Migrator

Handles schema version migrations for manifest.json files.

Usage:
    python manifest_migrator.py --project <name>
    python manifest_migrator.py --project <name> --backup
    python manifest_migrator.py --all
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple


# Migration registry: (from_version, to_version) -> migration_function
MIGRATIONS = {}


def migration(from_version: str, to_version: str):
    """Decorator to register migration functions"""
    def decorator(func):
        MIGRATIONS[(from_version, to_version)] = func
        return func
    return decorator


@migration("0.0.0", "1.0.0")
def migrate_0_0_0_to_1_0_0(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate from no schema version to 1.0.0

    Changes:
    - Add schema_version field
    - Ensure all required fields exist
    - Add default values for missing fields
    """
    manifest["schema_version"] = "1.0.0"

    # Ensure project_metadata structure
    if "project_metadata" not in manifest:
        manifest["project_metadata"] = {}

    project_metadata = manifest["project_metadata"]
    if "prd_files" not in project_metadata:
        project_metadata["prd_files"] = []

    # Ensure workflow structure
    if "workflow" not in manifest:
        manifest["workflow"] = {
            "stage": "INIT",
            "active_task_id": None,
            "concurrency_limit": 3,
            "retry_count": {}
        }

    workflow = manifest["workflow"]
    if "retry_count" not in workflow:
        workflow["retry_count"] = {}
    if "concurrency_limit" not in workflow:
        workflow["concurrency_limit"] = 3

    # Ensure dag structure
    if "dag" not in manifest:
        manifest["dag"] = {"nodes": []}

    dag = manifest["dag"]
    if "nodes" not in dag:
        dag["nodes"] = []

    # Ensure all task nodes have required fields
    for node in dag.get("nodes", []):
        if "artifacts" not in node:
            node["artifacts"] = {
                "spec": None,
                "ledger": None,
                "tests": []
            }
        if "prd_refs" not in node:
            node["prd_refs"] = []
        if "depends_on" not in node:
            node["depends_on"] = []

    # Ensure audit_results structure
    if manifest.get("audit_results") and "risks" in manifest["audit_results"]:
        for risk in manifest["audit_results"]["risks"]:
            if "status" not in risk:
                risk["status"] = "PENDING"

    return manifest


class ManifestMigrator:
    """Handles manifest.json schema migrations"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    CURRENT_VERSION = "1.0.0"

    def __init__(self, project_name: str = None):
        self.project_name = project_name
        if project_name:
            self.project_dir = self.ORCHESTRA_DIR / project_name
            self.manifest_path = self.project_dir / "manifest.json"

    def get_version(self, manifest: Dict[str, Any]) -> str:
        """Get schema version from manifest"""
        return manifest.get("schema_version", "0.0.0")

    def get_migration_path(self, from_version: str, to_version: str) -> List[Tuple[str, str]]:
        """
        Find the migration path from one version to another.

        Returns a list of (from, to) version pairs to apply.
        """
        if from_version == to_version:
            return []

        # Simple linear migration path
        # In the future, this could be a graph traversal
        path = []
        current = from_version

        # Find migrations from current version
        for (f, t), _ in MIGRATIONS.items():
            if f == current:
                path.append((f, t))
                current = t
                if current == to_version:
                    break

        return path

    def migrate(self, manifest: Dict[str, Any], target_version: str = None) -> Tuple[Dict[str, Any], List[str]]:
        """
        Migrate manifest to target version.

        Returns:
            Tuple of (migrated_manifest, list_of_applied_migrations)
        """
        target_version = target_version or self.CURRENT_VERSION
        current_version = self.get_version(manifest)
        applied = []

        if current_version == target_version:
            return manifest, applied

        migration_path = self.get_migration_path(current_version, target_version)

        for from_v, to_v in migration_path:
            migration_func = MIGRATIONS.get((from_v, to_v))
            if migration_func:
                manifest = migration_func(manifest)
                applied.append(f"{from_v} → {to_v}")

        return manifest, applied

    def backup_manifest(self) -> Path:
        """Create a backup of the current manifest"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = self.manifest_path.with_suffix(f".json.backup_{timestamp}")
        shutil.copy2(self.manifest_path, backup_path)
        return backup_path

    def migrate_project(self, backup: bool = False) -> Dict[str, Any]:
        """Migrate a single project's manifest"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"manifest.json not found for project '{self.project_name}'")

        manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        current_version = self.get_version(manifest)

        if current_version == self.CURRENT_VERSION:
            return {
                "project": self.project_name,
                "status": "already_current",
                "current_version": current_version,
                "message": f"Already at version {current_version}"
            }

        # Create backup if requested
        backup_path = None
        if backup:
            backup_path = self.backup_manifest()

        # Perform migration
        migrated_manifest, applied = self.migrate(manifest)

        # Save migrated manifest
        self.manifest_path.write_text(
            json.dumps(migrated_manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        return {
            "project": self.project_name,
            "status": "migrated",
            "from_version": current_version,
            "to_version": self.CURRENT_VERSION,
            "applied_migrations": applied,
            "backup_path": str(backup_path) if backup_path else None
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with their schema versions"""
        projects = []

        if not self.ORCHESTRA_DIR.exists():
            return projects

        for project_dir in self.ORCHESTRA_DIR.iterdir():
            if project_dir.is_dir():
                manifest_path = project_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                        version = self.get_version(manifest)
                        needs_migration = version != self.CURRENT_VERSION
                        projects.append({
                            "name": project_dir.name,
                            "version": version,
                            "needs_migration": needs_migration
                        })
                    except:
                        projects.append({
                            "name": project_dir.name,
                            "version": "ERROR",
                            "needs_migration": True
                        })

        return projects

    def migrate_all(self, backup: bool = False) -> List[Dict[str, Any]]:
        """Migrate all projects"""
        results = []
        for project in self.list_projects():
            if project["needs_migration"]:
                self.project_name = project["name"]
                self.project_dir = self.ORCHESTRA_DIR / project["name"]
                self.manifest_path = self.project_dir / "manifest.json"

                try:
                    result = self.migrate_project(backup=backup)
                except Exception as e:
                    result = {
                        "project": project["name"],
                        "status": "error",
                        "error": str(e)
                    }

                results.append(result)

        return results


def main():
    parser = argparse.ArgumentParser(description="Loom Manifest Migrator")
    parser.add_argument("--project", "-p", help="Project name to migrate")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Migrate all projects")
    parser.add_argument("--backup", "-b", action="store_true",
                        help="Create backup before migration")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List projects and their versions")

    args = parser.parse_args()

    migrator = ManifestMigrator()

    if args.list:
        projects = migrator.list_projects()
        print(f"\n{'='*60}")
        print("  LOOM PROJECTS - SCHEMA VERSIONS")
        print(f"{'='*60}\n")

        for p in projects:
            status = "✅" if not p["needs_migration"] else "⚠️ "
            print(f"  {status} {p['name']}: v{p['version']}")

            if p["needs_migration"]:
                print(f"      → Needs migration to v{migrator.CURRENT_VERSION}")

        print(f"\n{'='*60}\n")

    elif args.all:
        results = migrator.migrate_all(backup=args.backup)
        print(f"\n{'='*60}")
        print("  MIGRATION RESULTS")
        print(f"{'='*60}\n")

        for r in results:
            if r["status"] == "migrated":
                print(f"  ✅ {r['project']}: {r['from_version']} → {r['to_version']}")
                if r.get("backup_path"):
                    print(f"      Backup: {r['backup_path']}")
            elif r["status"] == "error":
                print(f"  ❌ {r['project']}: {r['error']}")

        print(f"\n{'='*60}\n")

    elif args.project:
        migrator = ManifestMigrator(args.project)
        result = migrator.migrate_project(backup=args.backup)

        if result["status"] == "already_current":
            print(f"✅ {result['message']}")
        elif result["status"] == "migrated":
            print(f"✅ Migrated {result['project']}: {result['from_version']} → {result['to_version']}")
            if result.get("backup_path"):
                print(f"   Backup: {result['backup_path']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
