#!/usr/bin/env python3
"""
Loom Ledger Generator

Generates execution ledger documents for completed tasks.

Usage:
    python ledger_generator.py --project <name> --task T_001 --status COMPLETED
    python ledger_generator.py --project <name> --task T_001 --status FAILED --error "Error message"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class LedgerGenerator:
    """Generate execution ledger for tasks"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    def __init__(self, project_name: str):
        self.project_dir = self.ORCHESTRA_DIR / project_name
        self.manifest_path = self.project_dir / "manifest.json"
        self.ledgers_dir = self.project_dir / "ledgers"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        return json.loads(self.manifest_path.read_text(encoding='utf-8'))

    def _save_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        nodes = self.manifest.get('dag', {}).get('nodes', [])
        for node in nodes:
            if node['id'] == task_id:
                return node
        return None

    def generate_ledger(
        self,
        task_id: str,
        status: str,
        duration_minutes: int = 0,
        new_files: List[str] = None,
        modified_files: List[str] = None,
        decisions: List[Dict[str, str]] = None,
        exports: List[Dict[str, str]] = None,
        downstream_deps: List[Dict[str, str]] = None,
        error_message: str = None
    ) -> Path:
        """Generate a ledger file for a task"""

        self.ledgers_dir.mkdir(exist_ok=True)

        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        title = task.get('title', 'Unknown Task')
        task_type = task.get('type', 'MODULE_IMPL')

        # Build ledger content
        ledger = f"""# Ledger: {task_id} - {title}

## Execution Info

| Field | Value |
|-------|-------|
| Task ID | {task_id} |
| Task Type | {task_type} |
| Execution Time | {datetime.utcnow().isoformat()}Z |
| Status | {status} |
| Duration | ~{duration_minutes} minutes |
| Retry Count | {self.manifest.get('workflow', {}).get('retry_count', {}).get(task_id, 0)} |

## Change Summary

### New Files

"""
        if new_files:
            ledger += "| File Path | Purpose | Lines |\n"
            ledger += "|-----------|---------|-------|\n"
            for f in new_files:
                ledger += f"| {f['path']} | {f.get('purpose', '-')} | {f.get('lines', '-')} |\n"
        else:
            ledger += "*No new files created*\n"

        ledger += "\n### Modified Files\n\n"
        if modified_files:
            ledger += "| File Path | Change Description | Lines Added | Lines Deleted |\n"
            ledger += "|-----------|-------------------|-------------|---------------|\n"
            for f in modified_files:
                ledger += f"| {f['path']} | {f.get('description', '-')} | {f.get('added', '-')} | {f.get('deleted', '-')} |\n"
        else:
            ledger += "*No files modified*\n"

        ledger += "\n### Deleted Files\n\n"
        ledger += "*No files deleted*\n"

        ledger += "\n## Implicit Decisions\n\n"
        if decisions:
            for i, d in enumerate(decisions, 1):
                ledger += f"""{i}. **Decision Point**: {d.get('point', 'N/A')}
   - **Choice**: {d.get('choice', 'N/A')}
   - **Rationale**: {d.get('rationale', 'N/A')}
   - **Impact**: {d.get('impact', 'N/A')}

"""
        else:
            ledger += "*No implicit decisions recorded*\n"

        ledger += "\n## Exported Interfaces\n\n"
        if exports:
            ledger += "### Functions\n\n"
            ledger += "```typescript\n"
            for e in exports:
                if e.get('type') == 'function':
                    ledger += f"// {e.get('file', '')}\n"
                    ledger += f"export function {e.get('name', '')}({e.get('params', '')}): {e.get('return', 'void')}\n"
                    ledger += f"// {e.get('description', '')}\n\n"
            ledger += "```\n"

            ledger += "\n### Types\n\n"
            ledger += "```typescript\n"
            for e in exports:
                if e.get('type') == 'interface':
                    ledger += f"export interface {e.get('name', '')} {{\n"
                    ledger += f"  // {e.get('description', '')}\n"
                    ledger += "}\n"
            ledger += "```\n"
        else:
            ledger += "*No exported interfaces*\n"

        ledger += "\n## Downstream Dependencies\n\n"
        if downstream_deps:
            ledger += "| Dependent Task | Resource Needed | Use Case |\n"
            ledger += "|----------------|-----------------|----------|\n"
            for d in downstream_deps:
                ledger += f"| {d.get('task', '-')} | {d.get('resource', '-')} | {d.get('use_case', '-')} |\n"
        else:
            ledger += "*No downstream dependencies*\n"

        ledger += "\n## Pending Verification\n\n"
        ledger += """- [ ] Unit tests: Normal flow
- [ ] Unit tests: Error handling
- [ ] Unit tests: Edge cases
- [ ] Integration tests: End-to-end flow
"""

        ledger += "\n## Notes\n\n"
        ledger += "*Add any important notes for downstream task developers*\n"

        if error_message:
            ledger += f"\n## Error Log\n\n"
            ledger += f"| Time | Error Type | Error Message |\n"
            ledger += f"|------|------------|---------------|\n"
            ledger += f"| {datetime.utcnow().isoformat()}Z | Execution Error | {error_message} |\n"

        # Write ledger file
        ledger_path = self.ledgers_dir / f"{task_id}.md"
        ledger_path.write_text(ledger, encoding='utf-8')

        # Update task with ledger reference
        task['artifacts']['ledger'] = f"ledgers/{task_id}.md"
        task['status'] = status
        if error_message:
            task['error_message'] = error_message

        # Update workflow state
        if status == "IN_PROGRESS":
            self.manifest['workflow']['active_task_id'] = task_id
        elif status in ["COMPLETED", "FAILED"]:
            self.manifest['workflow']['active_task_id'] = None

        self._save_manifest()

        print(f"✓ Generated ledger: {ledger_path}")
        return ledger_path


def main():
    parser = argparse.ArgumentParser(description="Loom Ledger Generator")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--task", "-t", required=True, help="Task ID")
    parser.add_argument("--status", "-s", required=True,
                        choices=["IN_PROGRESS", "COMPLETED", "FAILED", "PARTIAL"],
                        help="Task status")
    parser.add_argument("--duration", "-d", type=int, default=0,
                        help="Duration in minutes")
    parser.add_argument("--error", "-e", help="Error message (for FAILED status)")

    args = parser.parse_args()

    try:
        generator = LedgerGenerator(args.project)
        generator.generate_ledger(
            task_id=args.task,
            status=args.status,
            duration_minutes=args.duration,
            error_message=args.error
        )

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
