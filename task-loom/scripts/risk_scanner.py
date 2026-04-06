#!/usr/bin/env python3
"""
Loom Risk Scanner

Usage:
    python risk_scanner.py --project <name>
    python risk_scanner.py --project <name> --output json
    python risk_scanner.py --project <name> --save
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional


class RiskSeverity(str, Enum):
    P0 = "P0"  # Critical - must be confirmed before proceeding
    P1 = "P1"  # High - should be reviewed
    P2 = "P2"  # Normal - automatically logged


@dataclass
class Risk:
    id: str
    severity: str
    risk_type: str
    title: str
    description: str
    location: str  # file:line format
    suggestion: str
    status: str = "PENDING"
    matched_text: str = ""  # The actual text that matched the pattern

    def to_dict(self) -> Dict:
        return asdict(self)

    def get_dedup_key(self) -> Tuple:
        """Generate a key for deduplication"""
        return (self.location, self.risk_type, self.title)


class RiskScanner:
    """PRD Risk Scanner with configurable patterns and deduplication"""

    ORCHESTRA_DIR = Path(".claude/orchestra")

    # Improved risk detection patterns with context awareness
    RISK_PATTERNS = {
        "P0": {
            "sql_injection": {
                "pattern": r"(?:SELECT|INSERT|UPDATE|DELETE)\s+[\w\*]+\s+FROM\s+[\w]+\s+WHERE\s+[\w]+\s*=\s*['\"]?\s*\{?\{?\s*\w+",
                "type": "Security Vulnerability",
                "title_template": "Potential SQL injection vulnerability",
                "suggestion": "Use parameterized queries or ORM. Never concatenate user input into SQL strings.",
                "false_positive_hints": ["example", "sample", "documentation", "comment"]
            },
            "plaintext_password_storage": {
                "pattern": r"(?:password|passwd|pwd)\s*[=:]\s*['\"][^'\"]+['\"]",
                "type": "Security Vulnerability",
                "title_template": "Password stored in plaintext",
                "suggestion": "Use bcrypt, argon2, or scrypt for password hashing. Never store passwords in plaintext.",
                "false_positive_hints": ["example", "sample", "test", "mock", "dummy"]
            },
            "missing_idempotency": {
                "pattern": r"(?:payment|callback|webhook|notification)\s+(?:handler|endpoint|api|processing)",
                "type": "Financial Security",
                "title_template": "Payment/callback handler may lack idempotency",
                "suggestion": "Implement idempotency check with unique key (e.g., order_id + callback_id). Add unique index to prevent duplicate processing.",
                "false_positive_hints": ["idempoten", "dedup", "unique"]
            },
            "missing_auth_critical": {
                "pattern": r"(?:admin|management|dashboard)\s+(?:api|endpoint|route|access)",
                "type": "Security Vulnerability",
                "title_template": "Critical endpoint may lack authentication",
                "suggestion": "Add authentication middleware for admin endpoints. Implement role-based access control (RBAC).",
                "false_positive_hints": ["auth", "login", "permission", "role", "middleware"]
            },
            "sensitive_data_exposure": {
                "pattern": r"(?:api|endpoint|response)\s+(?:return|contains?|exposes?)\s+(?:user|customer|personal)\s+(?:data|information|details)",
                "type": "Data Security",
                "title_template": "API may expose sensitive user data",
                "suggestion": "Implement data masking, field-level permissions, and audit logging for sensitive data access.",
                "false_positive_hints": ["mask", "encrypt", "permission", "authorize"]
            },
        },
        "P1": {
            "missing_input_validation": {
                "pattern": r"(?:input|param|parameter|request)\s+(?:value|data|body)(?!\s+(?:validat|check|sanitiz|escape))",
                "type": "Input Validation",
                "title_template": "Input may lack validation",
                "suggestion": "Add input validation: check type, range, format, and length. Use validation libraries.",
                "false_positive_hints": ["validat", "check", "sanitiz"]
            },
            "potential_race_condition": {
                "pattern": r"(?:increment|decrement|update|modify)\s+(?:counter|balance|stock|inventory|count)",
                "type": "Concurrency Issue",
                "title_template": "Potential race condition in update operation",
                "suggestion": "Use database transactions, optimistic locking, or atomic operations (e.g., UPDATE ... SET count = count + 1).",
                "false_positive_hints": ["transaction", "lock", "atomic", "mutex"]
            },
            "missing_error_handling": {
                "pattern": r"(?:api|function|method)\s+(?:call|request|fetch|invoke)(?!\s+(?:error|catch|try|handle|exception))",
                "type": "Error Handling",
                "title_template": "API/function call may lack error handling",
                "suggestion": "Wrap in try-catch, handle timeouts, and implement retry logic with exponential backoff.",
                "false_positive_hints": ["try", "catch", "error", "exception", "handle"]
            },
            "n_plus_one_potential": {
                "pattern": r"(?:for\s+each|loop\s+through|iterate\s+over|for\s+\w+\s+in)\s+(?:user|item|order|record)",
                "type": "Performance",
                "title_template": "Potential N+1 query pattern",
                "suggestion": "Use batch loading, eager loading, or JOIN queries to avoid N+1 queries.",
                "false_positive_hints": ["batch", "eager", "join", "preload", "include"]
            },
        },
        "P2": {
            "inconsistent_naming": {
                "pattern": r"(?:userId|user_id|uid|user-id|userIdentifier)",
                "type": "Naming Consistency",
                "title_template": "Inconsistent naming convention detected",
                "suggestion": "Standardize naming convention: use either camelCase, snake_case, or kebab-case consistently across the codebase.",
                "false_positive_hints": []
            },
            "missing_documentation": {
                "pattern": r"(?:TODO|FIXME|TBD|HACK|XXX|待定|待实现|待完善)",
                "type": "Documentation",
                "title_template": "Unfinished item detected",
                "suggestion": "Complete the implementation or document the reason for deferring.",
                "false_positive_hints": []
            },
            "vague_requirement": {
                "pattern": r"(?:should|shall|must|need)\s+(?:be\s+)?(?:fast|good|nice|better|performant|scalable|secure)",
                "type": "Requirement Quality",
                "title_template": "Vague requirement detected",
                "suggestion": "Make requirements specific and measurable: define exact metrics, thresholds, and acceptance criteria.",
                "false_positive_hints": []
            },
        }
    }

    # Window configuration
    WINDOW_SIZE = 500  # lines
    OVERLAP_RATIO = 0.1  # 10% overlap

    def __init__(self, project_name: str):
        self.project_dir = self.ORCHESTRA_DIR / project_name
        self.manifest_path = self.project_dir / "manifest.json"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        self.manifest = self._load_manifest()
        self.risks: List[Risk] = []
        self.risk_counter = 0
        self._seen_risks: Set[Tuple] = set()  # For deduplication

    def _load_manifest(self) -> Dict:
        return json.loads(self.manifest_path.read_text(encoding='utf-8'))

    def _generate_risk_id(self) -> str:
        self.risk_counter += 1
        return f"RISK-{self.risk_counter:03d}"

    def _is_false_positive(self, content: str, config: Dict, match_text: str) -> bool:
        """
        Check if a match is likely a false positive based on context.

        Args:
            content: The full content being scanned
            config: Risk pattern configuration
            match_text: The matched text

        Returns:
            True if this is likely a false positive
        """
        # Get surrounding context (100 chars before and after)
        context_lower = content.lower()

        # Check for false positive hints in the config
        for hint in config.get('false_positive_hints', []):
            if hint.lower() in context_lower:
                return True

        return False

    def scan(self) -> List[Risk]:
        """Execute risk scan with deduplication"""
        prd_files = [
            Path(f) for f in self.manifest['project_metadata']['prd_files']
        ]

        print(f"🔍 Scanning {len(prd_files)} PRD files...")

        for file_path in prd_files:
            self._scan_file(file_path)

        print(f"   Found {len(self.risks)} unique risks")
        return self.risks

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file with improved window handling"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                content = file_path.read_text(encoding='utf-8-sig')
            except:
                print(f"⚠️  Skipping {file_path}: unable to decode")
                return

        lines = content.split('\n')

        # Use sliding window with overlap for better context
        window_step = int(self.WINDOW_SIZE * (1 - self.OVERLAP_RATIO))

        for start in range(0, len(lines), window_step):
            end = min(start + self.WINDOW_SIZE, len(lines))
            window_lines = lines[start:end]
            window_content = '\n'.join(window_lines)

            self._scan_window(window_content, file_path, start + 1)

    def _scan_window(
        self,
        content: str,
        file_path: Path,
        start_line: int
    ) -> None:
        """Scan a text window for risk patterns"""
        for severity, patterns in self.RISK_PATTERNS.items():
            for risk_key, config in patterns.items():
                matches = re.finditer(
                    config['pattern'],
                    content,
                    re.IGNORECASE | re.MULTILINE
                )

                for match in matches:
                    # Calculate line number
                    line_num = content[:match.start()].count('\n') + start_line

                    # Check for false positives
                    match_text = match.group(0)
                    if self._is_false_positive(content, config, match_text):
                        continue

                    location = f"{file_path}:{line_num}"

                    risk = Risk(
                        id=self._generate_risk_id(),
                        severity=severity,
                        risk_type=config['type'],
                        title=config['title_template'],
                        description=f"Pattern matched: {risk_key}",
                        location=location,
                        suggestion=config['suggestion'],
                        matched_text=match_text[:100]  # Truncate long matches
                    )

                    # Deduplication check
                    dedup_key = risk.get_dedup_key()
                    if dedup_key not in self._seen_risks:
                        self._seen_risks.add(dedup_key)
                        self.risks.append(risk)

    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate audit report"""
        if output_format == "json":
            return self._generate_json_report()
        return self._generate_markdown_report()

    def _generate_markdown_report(self) -> str:
        """Generate Markdown format report"""
        p0_risks = [r for r in self.risks if r.severity == "P0"]
        p1_risks = [r for r in self.risks if r.severity == "P1"]
        p2_risks = [r for r in self.risks if r.severity == "P2"]

        report = f"""# Risk Audit Report

## Overview

- Scan Time: {datetime.utcnow().isoformat()}Z
- Files Scanned: {len(self.manifest['project_metadata']['prd_files'])}
- Risks Found: P0={len(p0_risks)}, P1={len(p1_risks)}, P2={len(p2_risks)}

## P0 Risks (Critical - Must Confirm)

"""

        if p0_risks:
            for risk in p0_risks:
                report += f"""### {risk.id}: {risk.title}

- **Type**: {risk.risk_type}
- **Location**: {risk.location}
- **Description**: {risk.description}
- **Suggestion**: {risk.suggestion}

"""
        else:
            report += "_No P0 risks found_\n\n"

        report += "## P1 Risks (High - Should Review)\n\n"

        if p1_risks:
            for risk in p1_risks:
                report += f"- **{risk.id}**: {risk.title} ({risk.location})\n"
        else:
            report += "_No P1 risks found_\n"

        report += "\n## P2 Risks (Normal - Auto-logged)\n\n"

        if p2_risks:
            for risk in p2_risks:
                report += f"- **{risk.id}**: {risk.title} ({risk.location})\n"
        else:
            report += "_No P2 risks found_\n"

        return report

    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        return json.dumps(
            {
                "scan_time": datetime.utcnow().isoformat() + "Z",
                "summary": {
                    "total": len(self.risks),
                    "p0": len([r for r in self.risks if r.severity == "P0"]),
                    "p1": len([r for r in self.risks if r.severity == "P1"]),
                    "p2": len([r for r in self.risks if r.severity == "P2"])
                },
                "risks": [r.to_dict() for r in self.risks]
            },
            indent=2,
            ensure_ascii=False
        )

    def save_report(self, output_format: str = "markdown") -> Path:
        """Save report to file"""
        report_content = self.generate_report(output_format)

        ext = "json" if output_format == "json" else "md"
        report_path = self.project_dir / f"vulnerability_report.{ext}"

        report_path.write_text(report_content, encoding='utf-8')
        print(f"✓ Saved report to {report_path}")

        return report_path

    def update_manifest(self) -> None:
        """Update manifest with audit results"""
        self.manifest['audit_results'] = {
            "scan_time": datetime.utcnow().isoformat() + "Z",
            "risks": [r.to_dict() for r in self.risks]
        }
        self.manifest['workflow']['stage'] = "AUDIT"

        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print("✓ Updated manifest.json")


def main():
    parser = argparse.ArgumentParser(description="Loom Risk Scanner")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    parser.add_argument("--save", action="store_true", help="Save report to file")

    args = parser.parse_args()

    try:
        scanner = RiskScanner(args.project)
        risks = scanner.scan()

        if args.save:
            scanner.save_report(args.output)
            scanner.update_manifest()
        else:
            print(scanner.generate_report(args.output))

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid manifest.json: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
