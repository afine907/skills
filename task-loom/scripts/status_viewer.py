#!/usr/bin/env python3
"""
Task-Loom Status Viewer

Usage:
    python status_viewer.py --project <name>
    python status_viewer.py --project <name> --verbose
    python status_viewer.py --list-projects
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class StatusViewer:
    """Task-Loom Project Status Viewer"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    def __init__(self, project_name: str = None):
        self.project_name = project_name
        self.manifest = None

        if project_name:
            self.project_dir = self.ORCHESTRA_DIR / project_name
            self.manifest_path = self.project_dir / "manifest.json"

            if not self.manifest_path.exists():
                raise FileNotFoundError(f"Project '{project_name}' not found")

            self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest.json"""
        return json.loads(self.manifest_path.read_text(encoding='utf-8'))

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all Task-Loom projects"""
        projects = []

        if not self.ORCHESTRA_DIR.exists():
            return projects

        for project_dir in self.ORCHESTRA_DIR.iterdir():
            if project_dir.is_dir():
                manifest_path = project_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                        projects.append({
                            "name": project_dir.name,
                            "stage": manifest.get('workflow', {}).get('stage', 'UNKNOWN'),
                            "created_at": manifest.get('project_metadata', {}).get('created_at', 'N/A'),
                            "prd_count": len(manifest.get('project_metadata', {}).get('prd_files', []))
                        })
                    except:
                        projects.append({
                            "name": project_dir.name,
                            "stage": "ERROR",
                            "created_at": "N/A",
                            "prd_count": 0
                        })

        return projects

    def get_status_summary(self) -> Dict[str, Any]:
        """Get project status summary"""
        if not self.manifest:
            raise ValueError("No project loaded")

        nodes = self.manifest.get('dag', {}).get('nodes', [])
        workflow = self.manifest.get('workflow', {})

        # Count tasks by status
        status_counts = {
            "PENDING": 0,
            "IN_PROGRESS": 0,
            "COMPLETED": 0,
            "FAILED": 0,
            "BLOCKED": 0
        }

        for node in nodes:
            status = node.get('status', 'PENDING')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Get active task info
        active_task = None
        active_task_id = workflow.get('active_task_id')
        if active_task_id:
            for node in nodes:
                if node['id'] == active_task_id:
                    active_task = node
                    break

        # Get audit summary
        audit_results = self.manifest.get('audit_results', {})
        risk_counts = {"P0": 0, "P1": 0, "P2": 0}
        if audit_results and 'risks' in audit_results:
            for risk in audit_results['risks']:
                severity = risk.get('severity', 'P2')
                risk_counts[severity] = risk_counts.get(severity, 0) + 1

        return {
            "project_name": self.project_name,
            "stage": workflow.get('stage', 'INIT'),
            "schema_version": self.manifest.get('schema_version', '0.0.0'),
            "created_at": self.manifest.get('project_metadata', {}).get('created_at', 'N/A'),
            "total_tasks": len(nodes),
            "status_counts": status_counts,
            "active_task": active_task,
            "risk_counts": risk_counts,
            "retry_count": workflow.get('retry_count', {})
        }

    def format_status(self, verbose: bool = False) -> str:
        """Format status for display"""
        summary = self.get_status_summary()

        output = f"""
{'='*60}
  TASK-LOOM PROJECT STATUS
{'='*60}

Project: {summary['project_name']}
Stage: {summary['stage']}
Schema Version: {summary['schema_version']}
Created: {summary['created_at']}

{'─'*60}
  TASK SUMMARY
{'─'*60}

Total Tasks: {summary['total_tasks']}

Status Breakdown:
  ● Completed:  {summary['status_counts']['COMPLETED']:3d}
  ● In Progress: {summary['status_counts']['IN_PROGRESS']:3d}
  ● Pending:    {summary['status_counts']['PENDING']:3d}
  ● Failed:     {summary['status_counts']['FAILED']:3d}
  ● Blocked:    {summary['status_counts']['BLOCKED']:3d}

Progress: {self._calculate_progress(summary['status_counts']):.1f}%
"""

        if summary['active_task']:
            task = summary['active_task']
            output += f"""
{'─'*60}
  ACTIVE TASK
{'─'*60}

ID: {task['id']}
Title: {task.get('title', 'N/A')}
Type: {task.get('type', 'N/A')}
Status: {task.get('status', 'N/A')}
"""

        if any(summary['risk_counts'].values()):
            output += f"""
{'─'*60}
  RISK SUMMARY
{'─'*60}

P0 (Critical): {summary['risk_counts']['P0']}
P1 (High):     {summary['risk_counts']['P1']}
P2 (Normal):   {summary['risk_counts']['P2']}
"""

        if summary['retry_count'] and verbose:
            output += f"""
{'─'*60}
  RETRY COUNT
{'─'*60}

{json.dumps(summary['retry_count'], indent=2)}
"""

        if verbose and self.manifest:
            nodes = self.manifest.get('dag', {}).get('nodes', [])
            if nodes:
                output += f"""
{'─'*60}
  TASK LIST
{'─'*60}

"""
                for node in nodes:
                    status_icon = {
                        'PENDING': '○',
                        'IN_PROGRESS': '◐',
                        'COMPLETED': '●',
                        'FAILED': '✗',
                        'BLOCKED': '⊡'
                    }.get(node.get('status', 'PENDING'), '?')

                    deps = ', '.join(node.get('depends_on', [])) or '-'
                    output += f"  {status_icon} {node['id']}: {node.get('title', 'N/A')}\n"
                    output += f"    Type: {node.get('type', 'N/A')} | Status: {node.get('status', 'N/A')}\n"
                    if verbose:
                        output += f"    Dependencies: {deps}\n"
                    output += "\n"

        output += f"{'='*60}\n"
        return output

    def _calculate_progress(self, status_counts: Dict[str, int]) -> float:
        """Calculate completion progress percentage"""
        total = sum(status_counts.values())
        if total == 0:
            return 0.0
        completed = status_counts.get('COMPLETED', 0)
        return (completed / total) * 100

    def format_projects_list(self) -> str:
        """Format projects list for display"""
        projects = self.list_projects()

        if not projects:
            return "No Task-Loom projects found.\n\nRun `/task-loom init <project_name> <prd_paths>` to create one."

        output = f"""
{'='*60}
  TASK-LOOM PROJECTS
{'='*60}

"""
        for p in projects:
            stage_icon = {
                'INIT': '🔵',
                'AUDIT': '🟡',
                'PLAN': '🟠',
                'EXECUTE': '🟢',
                'VERIFY': '🟣',
                'HALTED': '🔴'
            }.get(p['stage'], '⚪')

            output += f"  {stage_icon} {p['name']}\n"
            output += f"      Stage: {p['stage']} | PRD Files: {p['prd_count']}\n"
            output += f"      Created: {p['created_at']}\n\n"

        output += f"{'='*60}\n"
        return output


def main():
    parser = argparse.ArgumentParser(description="Loom Status Viewer")
    parser.add_argument("--project", "-p", help="Project name to view status")
    parser.add_argument("--list-projects", "-l", action="store_true",
                        help="List all Loom projects")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed information")

    args = parser.parse_args()

    try:
        if args.list_projects:
            viewer = StatusViewer()
            print(viewer.format_projects_list())
        elif args.project:
            viewer = StatusViewer(args.project)
            print(viewer.format_status(verbose=args.verbose))
        else:
            # Default: list projects
            viewer = StatusViewer()
            print(viewer.format_projects_list())

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
