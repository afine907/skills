#!/usr/bin/env python3
"""
Loom DAG Manager

Usage:
    # Add a task
    python dag_manager.py add --project <name> --id T_001 --type MODULE_IMPL --title "Auth Module"

    # Remove a task
    python dag_manager.py remove --project <name> --id T_001

    # Update status
    python dag_manager.py update --project <name> --id T_001 --status COMPLETED

    # Get next task
    python dag_manager.py next --project <name>

    # Check dependencies
    python dag_manager.py check --project <name> --id T_001
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class TaskType(str, Enum):
    MODULE_IMPL = "MODULE_IMPL"
    AUDIT = "AUDIT"
    TEST = "TEST"
    INTEGRATE = "INTEGRATE"
    REFACTOR = "REFACTOR"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class DAGManager:
    """DAG State Manager"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    def __init__(self, project_name: str):
        self.project_dir = self.ORCHESTRA_DIR / project_name
        self.manifest_path = self.project_dir / "manifest.json"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found. Run init first.")

        self.manifest = self._load_manifest()

    def _detect_cycle(self, task_id: str, visited: set = None, rec_stack: set = None) -> bool:
        """
        Detect if adding a task would create a cycle in the DAG.
        Uses DFS to detect cycles in the dependency graph.

        Args:
            task_id: The task ID to check
            visited: Set of visited nodes
            rec_stack: Set of nodes in current recursion stack

        Returns:
            True if a cycle is detected, False otherwise
        """
        if visited is None:
            visited = set()
        if rec_stack is None:
            rec_stack = set()

        visited.add(task_id)
        rec_stack.add(task_id)

        task = self._get_task(task_id)
        for dep_id in task.get('depends_on', []):
            if dep_id not in visited:
                if self._detect_cycle(dep_id, visited, rec_stack):
                    return True
            elif dep_id in rec_stack:
                return True

        rec_stack.remove(task_id)
        return False

    def _would_create_cycle(self, task_id: str, depends_on: List[str]) -> bool:
        """
        Check if adding dependencies would create a cycle.
        This simulates adding the dependencies before actually adding them.

        Args:
            task_id: The new task ID
            depends_on: List of dependency task IDs

        Returns:
            True if adding these dependencies would create a cycle
        """
        # Temporarily add the task with dependencies to check for cycles
        existing_ids = [n['id'] for n in self.manifest['dag']['nodes']]

        # Build a temporary graph including the new task
        temp_task = {
            'id': task_id,
            'depends_on': depends_on or [],
            'status': 'PENDING'
        }

        # Check if any of the new dependencies point back to the new task
        # This would happen if an existing task depends on the new task
        for node in self.manifest['dag']['nodes']:
            if task_id in node.get('depends_on', []):
                # The new task is already a dependency of an existing task
                # Check if we're adding a dependency on that existing task
                for dep_id in (depends_on or []):
                    if self._check_reaches(node['id'], dep_id, set()):
                        return True

        return False

    def _check_reaches(self, from_id: str, to_id: str, visited: set) -> bool:
        """
        Check if there's a path from from_id to to_id in the DAG.

        Args:
            from_id: Starting node
            to_id: Target node
            visited: Set of visited nodes

        Returns:
            True if to_id is reachable from from_id
        """
        if from_id == to_id:
            return True

        if from_id in visited:
            return False

        visited.add(from_id)

        task = self._get_task(from_id)
        for dep_id in task.get('depends_on', []):
            if self._check_reaches(dep_id, to_id, visited):
                return True

        return False

    def _load_manifest(self) -> Dict[str, Any]:
        """加载 manifest.json"""
        return json.loads(self.manifest_path.read_text(encoding='utf-8'))

    def _save_manifest(self) -> None:
        """保存 manifest.json"""
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def add_task(
        self,
        task_id: str,
        task_type: str,
        title: str,
        depends_on: List[str] = None,
        prd_refs: List[str] = None,
        complexity: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """Add a task node to the DAG"""
        # Validate task_id format
        if not re.match(r'^T_\d{3}$', task_id):
            raise ValueError(f"Invalid task_id format: {task_id}. Expected: T_XXX")

        # Check if task already exists
        existing_ids = [n['id'] for n in self.manifest['dag']['nodes']]
        if task_id in existing_ids:
            raise ValueError(f"Task {task_id} already exists")

        # Validate dependencies exist
        if depends_on:
            for dep in depends_on:
                if dep not in existing_ids:
                    raise ValueError(f"Dependency {dep} does not exist")

        # Check for cycles
        if depends_on and self._would_create_cycle(task_id, depends_on):
            raise ValueError(
                f"Adding task {task_id} with dependencies {depends_on} would create a cycle in the DAG"
            )

        task = {
            "id": task_id,
            "type": task_type,
            "title": title,
            "status": TaskStatus.PENDING.value,
            "depends_on": depends_on or [],
            "prd_refs": prd_refs or [],
            "artifacts": {
                "spec": None,
                "ledger": None,
                "tests": []
            },
            "estimated_complexity": complexity
        }

        self.manifest['dag']['nodes'].append(task)
        self._save_manifest()

        print(f"✓ Added task {task_id}: {title}")
        return task

    def remove_task(self, task_id: str, force: bool = False) -> bool:
        """
        Remove a task from the DAG.

        Args:
            task_id: The task ID to remove
            force: If True, remove even if other tasks depend on it

        Returns:
            True if task was removed, False otherwise

        Raises:
            ValueError: If task has dependents and force is False
        """
        task = self._get_task(task_id)

        # Check if other tasks depend on this task
        dependents = []
        for node in self.manifest['dag']['nodes']:
            if task_id in node.get('depends_on', []):
                dependents.append(node['id'])

        if dependents and not force:
            raise ValueError(
                f"Cannot remove task {task_id}: tasks {dependents} depend on it. "
                "Use --force to remove anyway."
            )

        # Remove the task
        self.manifest['dag']['nodes'] = [
            n for n in self.manifest['dag']['nodes'] if n['id'] != task_id
        ]

        # Remove task_id from all dependencies if force
        if force:
            for node in self.manifest['dag']['nodes']:
                if task_id in node.get('depends_on', []):
                    node['depends_on'].remove(task_id)

        self._save_manifest()
        print(f"✓ Removed task {task_id}")
        return True

    def update_status(
        self,
        task_id: str,
        status: str,
        error_message: str = None
    ) -> Dict[str, Any]:
        """Update task status"""
        task = self._get_task(task_id)

        old_status = task['status']
        task['status'] = status

        if error_message:
            task['error_message'] = error_message

        # Update workflow state
        if status == TaskStatus.IN_PROGRESS.value:
            self.manifest['workflow']['active_task_id'] = task_id
        elif status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
            self.manifest['workflow']['active_task_id'] = None

        # Update retry count
        if status == TaskStatus.FAILED.value:
            retry_key = task_id
            self.manifest['workflow']['retry_count'][retry_key] = \
                self.manifest['workflow']['retry_count'].get(retry_key, 0) + 1

        self._save_manifest()

        print(f"✓ Updated {task_id}: {old_status} → {status}")
        return task

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next executable task"""
        nodes = self.manifest['dag']['nodes']

        for task in nodes:
            if task['status'] != TaskStatus.PENDING.value:
                continue

            # Check if all dependencies are completed
            deps_satisfied = all(
                self._get_task(dep)['status'] == TaskStatus.COMPLETED.value
                for dep in task['depends_on']
            )

            if deps_satisfied:
                return task

        return None

    def check_dependencies(self, task_id: str) -> Dict[str, Any]:
        """Check task dependency status"""
        task = self._get_task(task_id)

        result = {
            "task_id": task_id,
            "all_satisfied": True,
            "dependencies": []
        }

        for dep_id in task['depends_on']:
            dep_task = self._get_task(dep_id)
            satisfied = dep_task['status'] == TaskStatus.COMPLETED.value
            result['dependencies'].append({
                "id": dep_id,
                "title": dep_task['title'],
                "status": dep_task['status'],
                "satisfied": satisfied
            })
            if not satisfied:
                result['all_satisfied'] = False

        return result

    def _get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task node by ID"""
        for node in self.manifest['dag']['nodes']:
            if node['id'] == task_id:
                return node
        raise ValueError(f"Task {task_id} not found")

    def list_tasks(self, status: str = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status"""
        nodes = self.manifest['dag']['nodes']

        if status:
            return [n for n in nodes if n['status'] == status]
        return nodes

    def get_dag_summary(self) -> Dict[str, Any]:
        """Get DAG summary statistics"""
        nodes = self.manifest['dag']['nodes']

        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([n for n in nodes if n['status'] == status.value])

        return {
            "total_tasks": len(nodes),
            "status_counts": status_counts,
            "active_task": self.manifest['workflow']['active_task_id'],
            "stage": self.manifest['workflow']['stage']
        }


def main():
    parser = argparse.ArgumentParser(description="Loom DAG Manager")
    parser.add_argument("--project", required=True, help="Project name")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("--id", required=True, help="Task ID (T_XXX)")
    add_parser.add_argument("--type", required=True, choices=[t.value for t in TaskType])
    add_parser.add_argument("--title", required=True, help="Task title")
    add_parser.add_argument("--depends-on", nargs="*", help="Dependency task IDs")
    add_parser.add_argument("--prd-refs", nargs="*", help="PRD references")

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("--id", required=True, help="Task ID to remove")
    remove_parser.add_argument("--force", "-f", action="store_true",
                                help="Force remove even if other tasks depend on it")

    # update command
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("--id", required=True, help="Task ID")
    update_parser.add_argument("--status", required=True, choices=[s.value for s in TaskStatus])
    update_parser.add_argument("--error", help="Error message (for FAILED status)")

    # next command
    subparsers.add_parser("next", help="Get next executable task")

    # check command
    check_parser = subparsers.add_parser("check", help="Check task dependencies")
    check_parser.add_argument("--id", required=True, help="Task ID")

    # list command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")

    # summary command
    subparsers.add_parser("summary", help="Get DAG summary")

    args = parser.parse_args()

    try:
        manager = DAGManager(args.project)

        if args.command == "add":
            manager.add_task(
                args.id, args.type, args.title,
                args.depends_on, args.prd_refs
            )
        elif args.command == "remove":
            manager.remove_task(args.id, args.force)
        elif args.command == "update":
            manager.update_status(args.id, args.status, args.error)
        elif args.command == "next":
            task = manager.get_next_task()
            if task:
                print(json.dumps(task, indent=2))
            else:
                print("No executable tasks available")
        elif args.command == "check":
            result = manager.check_dependencies(args.id)
            print(json.dumps(result, indent=2))
        elif args.command == "list":
            tasks = manager.list_tasks(args.status)
            print(json.dumps(tasks, indent=2))
        elif args.command == "summary":
            summary = manager.get_dag_summary()
            print(json.dumps(summary, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
