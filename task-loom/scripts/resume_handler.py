#!/usr/bin/env python3
"""
Task-Loom Resume Handler

Usage:
    python resume_handler.py --project <name>
    python resume_handler.py --project <name> --reset
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class ResumeHandler:
    """Task-Loom Resume Handler for checkpoint recovery"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    # Stage flow order
    STAGE_ORDER = ["INIT", "AUDIT", "PLAN", "EXECUTE", "VERIFY", "COMPLETED"]

    def __init__(self, project_name: str):
        self.project_dir = self.ORCHESTRA_DIR / project_name
        self.manifest_path = self.project_dir / "manifest.json"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest.json"""
        return json.loads(self.manifest_path.read_text(encoding='utf-8'))

    def _save_manifest(self) -> None:
        """Save manifest.json"""
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def get_resume_point(self) -> Dict[str, Any]:
        """Get the resume point information"""
        workflow = self.manifest.get('workflow', {})
        stage = workflow.get('stage', 'INIT')
        active_task_id = workflow.get('active_task_id')

        result = {
            "stage": stage,
            "active_task_id": active_task_id,
            "can_resume": True,
            "resume_action": None,
            "resume_target": None,
            "message": ""
        }

        # Check for HALTED state
        if stage == "HALTED":
            halt_reason = workflow.get('halt_reason', 'Unknown reason')
            result["can_resume"] = False
            result["message"] = f"Project is HALTED: {halt_reason}"
            return result

        # Check for active task
        if active_task_id:
            task = self._get_task(active_task_id)
            if task:
                result["resume_action"] = "CONTINUE_TASK"
                result["resume_target"] = active_task_id
                result["message"] = f"Resume task {active_task_id}: {task.get('title', 'N/A')}"
                return result

        # Determine next action based on stage
        if stage == "INIT":
            result["resume_action"] = "NEXT_STAGE"
            result["resume_target"] = "AUDIT"
            result["message"] = "Ready to start AUDIT phase. Run `/task-loom audit`"

        elif stage == "AUDIT":
            # Check if audit is complete
            audit_results = self.manifest.get('audit_results')
            if audit_results:
                # Check for P0 risks that need confirmation
                p0_pending = any(
                    r.get('status') == 'PENDING' and r.get('severity') == 'P0'
                    for r in audit_results.get('risks', [])
                )
                if p0_pending:
                    result["resume_action"] = "CONFIRM_RISKS"
                    result["message"] = "P0 risks pending confirmation"
                else:
                    result["resume_action"] = "NEXT_STAGE"
                    result["resume_target"] = "PLAN"
                    result["message"] = "AUDIT complete. Run `/task-loom plan`"
            else:
                result["resume_action"] = "RUN_AUDIT"
                result["message"] = "AUDIT not run yet. Run `/task-loom audit`"

        elif stage == "PLAN":
            # Check if DAG has tasks
            nodes = self.manifest.get('dag', {}).get('nodes', [])
            if nodes:
                result["resume_action"] = "NEXT_STAGE"
                result["resume_target"] = "EXECUTE"
                result["message"] = f"PLAN complete with {len(nodes)} tasks. Run `/task-loom execute`"
            else:
                result["resume_action"] = "RUN_PLAN"
                result["message"] = "DAG is empty. Run `/task-loom plan`"

        elif stage == "EXECUTE":
            # Find next executable task
            next_task = self._get_next_task()
            if next_task:
                result["resume_action"] = "EXECUTE_TASK"
                result["resume_target"] = next_task['id']
                result["message"] = f"Execute task {next_task['id']}: {next_task.get('title', 'N/A')}"
            else:
                # Check if all tasks are completed
                nodes = self.manifest.get('dag', {}).get('nodes', [])
                all_done = all(n.get('status') == 'COMPLETED' for n in nodes)
                if all_done:
                    result["resume_action"] = "NEXT_STAGE"
                    result["resume_target"] = "VERIFY"
                    result["message"] = "All tasks completed. Run `/task-loom verify`"
                else:
                    result["can_resume"] = False
                    result["message"] = "No executable tasks available. Check for blocked tasks."

        elif stage == "VERIFY":
            result["resume_action"] = "RUN_VERIFY"
            result["message"] = "Run `/task-loom verify` to validate completion"

        else:
            result["can_resume"] = False
            result["message"] = f"Unknown stage: {stage}"

        return result

    def _get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        nodes = self.manifest.get('dag', {}).get('nodes', [])
        for node in nodes:
            if node['id'] == task_id:
                return node
        return None

    def _get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next executable task (PENDING with satisfied dependencies)"""
        nodes = self.manifest.get('dag', {}).get('nodes', [])

        for task in nodes:
            if task.get('status') != 'PENDING':
                continue

            # Check dependencies
            deps = task.get('depends_on', [])
            all_deps_done = all(
                self._get_task(dep).get('status') == 'COMPLETED'
                for dep in deps
                if self._get_task(dep)
            )

            if all_deps_done:
                return task

        return None

    def reset_task(self, task_id: str) -> bool:
        """Reset a task to PENDING status"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task['status'] = 'PENDING'
        task.pop('error_message', None)

        # Clear from retry count
        retry_count = self.manifest.get('workflow', {}).get('retry_count', {})
        retry_count.pop(task_id, None)

        self._save_manifest()
        return True

    def clear_halt(self) -> bool:
        """Clear HALTED state and reset failed task"""
        workflow = self.manifest.get('workflow', {})

        if workflow.get('stage') != 'HALTED':
            return False

        # Find failed task
        active_task_id = workflow.get('active_task_id')
        if active_task_id:
            task = self._get_task(active_task_id)
            if task and task.get('status') == 'FAILED':
                task['status'] = 'PENDING'
                task.pop('error_message', None)

        # Reset workflow state
        workflow['stage'] = 'EXECUTE'
        workflow['active_task_id'] = None
        workflow['halt_reason'] = None

        self._save_manifest()
        return True

    def format_resume_info(self) -> str:
        """Format resume information for display"""
        resume_point = self.get_resume_point()
        project_name = self.manifest.get('project_metadata', {}).get('name', 'Unknown')

        output = f"""
{'='*60}
  TASK-LOOM RESUME POINT
{'='*60}

Project: {project_name}
Current Stage: {resume_point['stage']}

Status: {'✅ Can Resume' if resume_point['can_resume'] else '⛔ Blocked'}

Message: {resume_point['message']}

"""

        if resume_point['can_resume'] and resume_point['resume_action']:
            output += f"""Action Required: {resume_point['resume_action']}
Target: {resume_point.get('resume_target', 'N/A')}

"""

            # Provide specific command suggestions
            action = resume_point['resume_action']
            if action == "NEXT_STAGE":
                output += f"Suggested Command: /task-loom {resume_point['resume_target'].lower()}\n"
            elif action == "CONTINUE_TASK":
                output += f"Suggested Command: /task-loom execute --task {resume_point['resume_target']}\n"
            elif action == "EXECUTE_TASK":
                output += f"Suggested Command: /task-loom execute --task {resume_point['resume_target']}\n"
            elif action == "CONFIRM_RISKS":
                output += "Action: Review and confirm P0 risks in vulnerability_report.md\n"
            elif action in ["RUN_AUDIT", "RUN_PLAN", "RUN_VERIFY"]:
                output += f"Suggested Command: /task-loom {action.split('_')[1].lower()}\n"

        if not resume_point['can_resume']:
            output += """
To clear HALTED state and retry:
  python resume_handler.py --project <name> --clear-halt

To reset a specific task:
  python resume_handler.py --project <name> --reset-task T_XXX
"""

        output += f"\n{'='*60}\n"
        return output


def main():
    parser = argparse.ArgumentParser(description="Task-Loom Resume Handler")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--reset-task", help="Reset a specific task to PENDING")
    parser.add_argument("--clear-halt", action="store_true",
                        help="Clear HALTED state")

    args = parser.parse_args()

    try:
        handler = ResumeHandler(args.project)

        if args.reset_task:
            success = handler.reset_task(args.reset_task)
            if success:
                print(f"✓ Task {args.reset_task} reset to PENDING")
        elif args.clear_halt:
            success = handler.clear_halt()
            if success:
                print(f"✓ HALTED state cleared, project ready to resume")
            else:
                print(f"⚠️  Project is not in HALTED state")
        else:
            print(handler.format_resume_info())

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
