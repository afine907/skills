#!/usr/bin/env python3
"""
Loom Spec Generator

Generates technical specification documents for each task based on PRD content.

Usage:
    python spec_generator.py --project <name>
    python spec_generator.py --project <name> --task T_001
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class SpecGenerator:
    """Generate technical specifications for tasks"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    def __init__(self, project_name: str):
        self.project_dir = self.ORCHESTRA_DIR / project_name
        self.manifest_path = self.project_dir / "manifest.json"
        self.constitution_path = self.project_dir / "constitution.md"
        self.specs_dir = self.project_dir / "specs"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        self.manifest = self._load_manifest()
        self.constitution = self._load_constitution()

    def _load_manifest(self) -> Dict[str, Any]:
        return json.loads(self.manifest_path.read_text(encoding='utf-8'))

    def _save_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _load_constitution(self) -> str:
        if self.constitution_path.exists():
            return self.constitution_path.read_text(encoding='utf-8')
        return ""

    def _read_prd_section(self, prd_ref: str) -> str:
        """Read a specific section from PRD file"""
        # Parse prd_ref format: "docs/prd.md L15-55"
        match = re.match(r'(.+)\s+L(\d+)-L?(\d+)', prd_ref)
        if not match:
            return ""

        prd_path = Path(match.group(1))
        start_line = int(match.group(2))
        end_line = int(match.group(3))

        # Find the actual file
        prd_files = self.manifest.get('project_metadata', {}).get('prd_files', [])
        actual_path = None
        for pf in prd_files:
            if pf.endswith(match.group(1)) or match.group(1) in pf:
                actual_path = Path(pf)
                break

        if not actual_path or not actual_path.exists():
            return ""

        lines = actual_path.read_text(encoding='utf-8').split('\n')
        return '\n'.join(lines[start_line-1:end_line])

    def _extract_invariants_for_task(self, task: Dict[str, Any]) -> List[str]:
        """Extract relevant invariants for a task"""
        invariants = []
        constitution = self.constitution

        # Extract rules from constitution
        rule_pattern = r'\d+\.\s+(.+)'
        matches = re.findall(rule_pattern, constitution)
        return matches

    def generate_spec(self, task: Dict[str, Any]) -> str:
        """Generate specification document for a task"""
        task_id = task['id']
        task_type = task.get('type', 'MODULE_IMPL')
        title = task.get('title', 'Unknown Task')
        prd_refs = task.get('prd_refs', [])
        depends_on = task.get('depends_on', [])

        # Read PRD sections
        prd_content = ""
        for ref in prd_refs:
            prd_content += self._read_prd_section(ref) + "\n\n"

        # Get relevant invariants
        invariants = self._extract_invariants_for_task(task)

        # Generate spec content
        spec = f"""# Technical Specification: {task_id} - {title}

## Document Info

| Field | Value |
|-------|-------|
| Task ID | {task_id} |
| Task Type | {task_type} |
| Generated At | {datetime.utcnow().isoformat()}Z |
| Status | {task.get('status', 'PENDING')} |

## Overview

**Title**: {title}

**Description**: Implementation of {title.lower()} as defined in the PRD.

## Dependencies

"""
        if depends_on:
            spec += "This task depends on:\n"
            for dep in depends_on:
                spec += f"- {dep}\n"
        else:
            spec += "No dependencies.\n"

        spec += f"""
## PRD References

"""
        for ref in prd_refs:
            spec += f"- {ref}\n"

        if prd_content:
            spec += f"""
## PRD Content

```
{prd_content.strip()}
```

"""

        if invariants:
            spec += """## Global Invariants (Must Adhere)

The following rules from constitution.md are immutable constraints for this task:

"""
            for i, inv in enumerate(invariants, 1):
                spec += f"{i}. {inv}\n"

        spec += f"""
## Functional Requirements

### Core Features

*Extract from PRD content above*

### API Endpoints

*To be defined based on PRD content*

### Data Models

*To be defined based on PRD content*

## Technical Design

### Implementation Approach

*To be determined during implementation*

### File Structure

```
src/
├── {task_id.lower().replace('_', '/')}/
│   ├── index.ts
│   ├── handler.ts
│   ├── service.ts
│   └── types.ts
└── tests/
    └── {task_id.lower()}.test.ts
```

### Interfaces

```typescript
// To be defined
interface {task_id.replace('T_', 'I')} {{
  // ...
}}
```

## Acceptance Criteria

- [ ] All functional requirements implemented
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Code review approved
- [ ] Documentation updated

## Test Cases

### Unit Tests

- [ ] Test case 1: Normal flow
- [ ] Test case 2: Error handling
- [ ] Test case 3: Edge cases

### Integration Tests

- [ ] End-to-end flow
- [ ] API contract validation

## Risks and Mitigations

*Refer to vulnerability_report.md for identified risks*

## Notes

- This spec is auto-generated from PRD content
- Update this spec as implementation progresses
- Link to ledger after execution: `ledgers/{task_id}.md`
"""

        return spec

    def generate_all_specs(self) -> List[Path]:
        """Generate specs for all tasks"""
        self.specs_dir.mkdir(exist_ok=True)

        generated = []
        nodes = self.manifest.get('dag', {}).get('nodes', [])

        for task in nodes:
            spec_content = self.generate_spec(task)
            spec_path = self.specs_dir / f"{task['id']}.md"
            spec_path.write_text(spec_content, encoding='utf-8')

            # Update task with spec reference
            task['artifacts']['spec'] = f"specs/{task['id']}.md"

            print(f"✓ Generated spec: {spec_path}")
            generated.append(spec_path)

        self._save_manifest()
        return generated

    def generate_spec_for_task(self, task_id: str) -> Optional[Path]:
        """Generate spec for a specific task"""
        self.specs_dir.mkdir(exist_ok=True)

        nodes = self.manifest.get('dag', {}).get('nodes', [])
        task = None
        for node in nodes:
            if node['id'] == task_id:
                task = node
                break

        if not task:
            raise ValueError(f"Task {task_id} not found")

        spec_content = self.generate_spec(task)
        spec_path = self.specs_dir / f"{task_id}.md"
        spec_path.write_text(spec_content, encoding='utf-8')

        # Update task with spec reference
        task['artifacts']['spec'] = f"specs/{task_id}.md"
        self._save_manifest()

        print(f"✓ Generated spec: {spec_path}")
        return spec_path


def main():
    parser = argparse.ArgumentParser(description="Loom Spec Generator")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--task", "-t", help="Generate spec for specific task only")

    args = parser.parse_args()

    try:
        generator = SpecGenerator(args.project)

        if args.task:
            generator.generate_spec_for_task(args.task)
        else:
            generator.generate_all_specs()

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
