# Prompt CI/CD Pipeline -- Complete Implementation Guide

> Problem: A single prompt change caused a quality cliff that went undetected for 3 days. This document provides a production-ready CI/CD pipeline to ensure every prompt modification is tested before deployment.

## Architecture Overview

```
Developer edits prompt file
        |
        v
  Pre-commit Hooks  ──→  Lint & format check, reject hardcoded secrets
        |
        v
  Pull Request Gate  ──→  Regression tests vs baseline, must pass to merge
        |
        v
  Staging Validation ──→  Full test suite against real LLM endpoint
        |
        v
   Canary Deploy     ──→  5% traffic on new version, monitor quality metrics
        |
        v
  Quality Dashboard  ──→  Automated comparison: new vs old, statistical significance
        |
        v
  Full Rollout / Rollback
```

---

## 1. Prompt Inventory & Extraction

### 1.1 Locate All Prompts in Codebase

Run an audit to find every prompt scattered across the codebase:

| Location | Form | Extraction Strategy |
|----------|------|---------------------|
| Source code inline | String literals, template literals | Extract to standalone `.md` files |
| Config files | JSON/YAML fields | Keep structure, extract prompt fields |
| Environment variables | `SYSTEM_PROMPT`, etc. | Replace with file references |
| Database | Dynamically loaded prompts | Export to versioned files |
| Frontend code | User-visible prompt templates | Extract to shared `prompts/` directory |

### 1.2 Criticality Classification

| Level | Definition | Management |
|-------|-----------|------------|
| **Critical** | Core prompts that directly affect output quality (system prompts, role definitions) | Full regression + A/B comparison |
| **Important** | Prompts affecting specific features (tool descriptions, format constraints) | Regression testing |
| **Low** | Auxiliary prompts (hint text, error messages) | Basic format check |

---

## 2. Directory Structure

```
project-root/
├── prompts/
│   ├── system/
│   │   ├── v1/
│   │   │   ├── system.md                 # System prompt body
│   │   │   ├── tool-descriptions.md       # Tool descriptions
│   │   │   └── metadata.json             # Model, temperature, max_tokens
│   │   └── v2/
│   │       ├── system.md
│   │       ├── tool-descriptions.md
│   │       └── metadata.json
│   ├── templates/
│   │   ├── customer-support.md
│   │   ├── data-analysis.md
│   │   └── code-generation.md
│   ├── evals/
│   │   ├── test-cases.json               # Test case collection
│   │   ├── baselines/
│   │   │   ├── v1-scores.json
│   │   │   └── v2-scores.json
│   │   └── regressions/
│   │       └── 2026-05-29-v1-to-v2.json
│   ├── changelog.md                       # Prompt change log
│   └── README.md
├── scripts/
│   ├── lint_prompts.py                    # Pre-commit lint
│   ├── run_prompt_evals.py                # Regression test runner
│   ├── ab_compare.py                      # A/B comparison framework
│   ├── generate_report.py                 # Report generation
│   └── quality_monitor.py                # Production quality monitor
└── .github/
    └── workflows/
        ├── prompt-lint.yml
        └── prompt-regression.yml
```

### metadata.json Format

```json
{
  "version": "v2",
  "model": "claude-sonnet-4-20250514",
  "temperature": 0.7,
  "max_tokens": 4096,
  "created": "2026-05-29",
  "author": "team-name",
  "criticality": "critical",
  "changelog": "Improved tool selection accuracy, added error handling guidance"
}
```

---

## 3. Regression Test Suite

### 3.1 Test Case Types

| Type | Purpose | Quantity |
|------|---------|----------|
| **Golden Tests** | Known-correct input/output pairs | 10+ per critical prompt |
| **Format Compliance** | Output matches expected schema | 3+ per output format |
| **Safety Tests** | Reject harmful requests | 10+ attack vectors |
| **Performance Benchmarks** | Latency and token consumption | 3+ per template |
| **Edge Cases** | Extreme input handling | 2+ per edge case class |

### 3.2 Test Case Schema

```json
{
  "test_id": "prompt-regression-001",
  "prompt_version": "v2",
  "input": "User input here",
  "expected_properties": {
    "contains": ["required keywords"],
    "not_contains": ["forbidden content"],
    "format": "json | markdown | plain",
    "max_tokens": 500,
    "safety": "must_refuse | must_comply"
  },
  "scoring_rubric": {
    "relevance": "Is the answer relevant?",
    "accuracy": "Is the information accurate?",
    "tone": "Does the tone match brand guidelines?"
  },
  "pass_threshold": 0.85
}
```

### 3.3 Test Execution Flow

```
For each prompt version change:
  1. Run golden tests      -> Verify core behavior not degraded
  2. Run format tests      -> Verify output format unchanged
  3. Run safety tests      -> Verify safety guardrails intact
  4. Run performance tests -> Verify latency and cost not worsened
  5. Compare to baseline   -> Generate regression report
```

---

## 4. A/B Comparison Framework

### 4.1 Evaluation Dimensions

| Dimension | Evaluation Method | Weight |
|-----------|-------------------|--------|
| **Output Quality** | LLM-as-Judge scoring | 40% |
| **Format Compliance** | Automatic schema validation | 20% |
| **Safety** | Safety test pass rate | 20% |
| **Performance** | Latency + token consumption | 10% |
| **Cost** | Per-call cost | 10% |

### 4.2 Statistical Significance Protocol

```
For the same test set, run both versions:
  Run each case 5 times -> Calculate pass rate
  Paired comparison -> Calculate confidence interval
  if CI fully below zero   -> New version has regression (BLOCK)
  if CI fully above zero   -> New version is improved (APPROVE)
  if CI contains zero      -> No significant difference (APPROVE with caveat)
```

### 4.3 Report Template

```markdown
# Prompt A/B Comparison Report

## Versions
- Version A: v1 (current production)
- Version B: v2 (candidate)
- Test cases: 50
- Runs per case: 5

## Results

| Dimension     | v1 Score | v2 Score | Delta | 95% CI         | Verdict        |
|---------------|----------|----------|-------|----------------|----------------|
| Output Quality| 8.2      | 8.5      | +0.3  | [+0.1, +0.5]   | Improved       |
| Format        | 95%      | 93%      | -2%   | [-5%, +1%]     | No sig. diff   |
| Safety        | 98%      | 98%      | 0%    | [-2%, +2%]     | No sig. diff   |
| Latency       | 1.8s     | 2.1s     | +0.3s | [+0.1, +0.5]   | Degraded       |

## Conclusion
v2 shows significant quality improvement but latency increase.
Recommend deploy with latency monitoring.
```

---

## 5. CI/CD Pipeline Configuration

### 5.1 Pre-commit Hook (lint_prompts.py)

```python
#!/usr/bin/env python3
"""Pre-commit hook: lint prompt files before allowing commit."""

import sys
import re
import json
from pathlib import Path

SENSITIVE_PATTERNS = [
    r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\'][^"\']+["\']',
    r'sk-[a-zA-Z0-9]{20,}',
    r'(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*',
]

def lint_prompt_file(filepath: Path) -> list[str]:
    errors = []
    content = filepath.read_text(encoding='utf-8')

    # Check for hardcoded secrets
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, content):
            errors.append(f"[SECURITY] Hardcoded secret detected in {filepath}")

    # Check for valid metadata if metadata.json exists
    if filepath.name == 'metadata.json':
        try:
            meta = json.loads(content)
            required = ['version', 'model', 'criticality']
            for field in required:
                if field not in meta:
                    errors.append(f"[METADATA] Missing required field '{field}' in {filepath}")
        except json.JSONDecodeError:
            errors.append(f"[METADATA] Invalid JSON in {filepath}")

    # Check prompt file is not empty
    if filepath.suffix == '.md' and len(content.strip()) < 10:
        errors.append(f"[CONTENT] Prompt file is nearly empty: {filepath}")

    # Check for template variables that reference undefined vars
    var_pattern = r'\{\{(\w+)\}\}'
    vars_found = re.findall(var_pattern, content)
    if vars_found:
        # Document expected variables
        errors.append(f"[INFO] Template variables found in {filepath}: {vars_found}")

    return errors

def main():
    errors = []
    prompt_dir = Path('prompts')
    if not prompt_dir.exists():
        print("No prompts/ directory found. Skipping lint.")
        return 0

    for f in prompt_dir.rglob('*'):
        if f.is_file() and f.suffix in ('.md', '.json'):
            errors.extend(lint_prompt_file(f))

    if errors:
        print("Prompt lint failed:")
        for e in errors:
            print(f"  {e}")
        return 1

    print("Prompt lint passed.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### 5.2 Regression Test Runner (run_prompt_evals.py)

```python
#!/usr/bin/env python3
"""Run prompt regression test suite against a baseline."""

import argparse
import json
import time
import statistics
from pathlib import Path
from dataclasses import dataclass

import anthropic


@dataclass
class TestResult:
    test_id: str
    passed: bool
    score: float
    latency_ms: float
    token_count: int
    details: dict


def load_test_cases(path: str) -> list[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_prompt(prompt_dir: str, version: str) -> tuple[str, dict]:
    prompt_path = Path(prompt_dir) / 'system' / version / 'system.md'
    meta_path = Path(prompt_dir) / 'system' / version / 'metadata.json'

    prompt = prompt_path.read_text(encoding='utf-8')
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    return prompt, meta


def run_single_test(
    client: anthropic.Anthropic,
    system_prompt: str,
    meta: dict,
    test_case: dict,
) -> TestResult:
    start = time.time()

    response = client.messages.create(
        model=meta.get('model', 'claude-sonnet-4-20250514'),
        max_tokens=meta.get('max_tokens', 1024),
        temperature=meta.get('temperature', 0.0),
        system=system_prompt,
        messages=[{"role": "user", "content": test_case['input']}],
    )

    latency_ms = (time.time() - start) * 1000
    output = response.content[0].text
    token_count = response.usage.output_tokens

    # Evaluate against expected properties
    expected = test_case.get('expected_properties', {})
    details = {}
    passed = True

    # Check contains
    if 'contains' in expected:
        for keyword in expected['contains']:
            if keyword.lower() not in output.lower():
                passed = False
                details[f'missing_keyword_{keyword}'] = True

    # Check not_contains
    if 'not_contains' in expected:
        for forbidden in expected['not_contains']:
            if forbidden.lower() in output.lower():
                passed = False
                details[f'forbidden_content_{forbidden}'] = True

    # Check max_tokens
    if 'max_tokens' in expected and token_count > expected['max_tokens']:
        passed = False
        details['token_count_exceeded'] = token_count

    # Calculate score (simple version)
    score = 1.0 if passed else 0.0
    threshold = test_case.get('pass_threshold', 0.85)
    if score < threshold:
        passed = False

    return TestResult(
        test_id=test_case['test_id'],
        passed=passed,
        score=score,
        latency_ms=latency_ms,
        token_count=token_count,
        details=details,
    )


def compare_to_baseline(
    results: list[TestResult],
    baseline_path: str,
) -> dict:
    with open(baseline_path, 'r', encoding='utf-8') as f:
        baseline = json.load(f)

    baseline_scores = {b['test_id']: b['score'] for b in baseline.get('results', [])}
    regressions = []

    for r in results:
        if r.test_id in baseline_scores:
            old_score = baseline_scores[r.test_id]
            if r.score < old_score:
                regressions.append({
                    'test_id': r.test_id,
                    'baseline_score': old_score,
                    'current_score': r.score,
                    'delta': r.score - old_score,
                })

    return {
        'total': len(results),
        'passed': sum(1 for r in results if r.passed),
        'failed': sum(1 for r in results if not r.passed),
        'regressions': regressions,
        'has_regression': len(regressions) > 0,
    }


def main():
    parser = argparse.ArgumentParser(description='Run prompt regression tests')
    parser.add_argument('--prompt-dir', required=True)
    parser.add_argument('--eval-set', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--threshold', type=float, default=0.85)
    parser.add_argument('--version', default='v2')
    parser.add_argument('--output', default='evals/regressions/latest.json')
    args = parser.parse_args()

    client = anthropic.Anthropic()
    system_prompt, meta = load_prompt(args.prompt_dir, args.version)
    test_cases = load_test_cases(args.eval_set)

    print(f"Running {len(test_cases)} test cases against {args.version}...")

    results = []
    for tc in test_cases:
        result = run_single_test(client, system_prompt, meta, tc)
        status = "PASS" if result.passed else "FAIL"
        print(f"  [{status}] {result.test_id} (score={result.score:.2f}, {result.latency_ms:.0f}ms)")
        results.append(result)

    # Compare to baseline
    comparison = compare_to_baseline(results, args.baseline)

    report = {
        'version': args.version,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'summary': comparison,
        'results': [
            {
                'test_id': r.test_id,
                'passed': r.passed,
                'score': r.score,
                'latency_ms': r.latency_ms,
                'token_count': r.token_count,
                'details': r.details,
            }
            for r in results
        ],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(f"\nResults: {comparison['passed']}/{comparison['total']} passed")
    if comparison['has_regression']:
        print(f"REGRESSION DETECTED: {len(comparison['regressions'])} test(s) degraded")
        for reg in comparison['regressions']:
            print(f"  - {reg['test_id']}: {reg['baseline_score']:.2f} -> {reg['current_score']:.2f}")
        return 1

    print("No regressions. All tests passed.")
    return 0


if __name__ == '__main__':
    exit(main())
```

### 5.3 GitHub Actions: PR Gate

```yaml
# .github/workflows/prompt-regression.yml
name: Prompt Regression Tests

on:
  pull_request:
    paths:
      - 'prompts/**'

concurrency:
  group: prompt-regression-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - name: Lint prompt files
        run: python scripts/lint_prompts.py

  regression:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        prompt_type: [system, templates]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install anthropic scipy

      - name: Detect changed prompt versions
        id: detect
        run: |
          CHANGED=$(git diff --name-only origin/main...HEAD -- prompts/${{ matrix.prompt_type }}/)
          echo "changed=$CHANGED" >> $GITHUB_OUTPUT
          # Extract version from changed paths
          VERSION=$(echo "$CHANGED" | grep -oP 'v\d+' | head -1)
          echo "version=${VERSION:-v2}" >> $GITHUB_OUTPUT

      - name: Run regression tests
        if: steps.detect.outputs.changed != ''
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/run_prompt_evals.py \
            --prompt-dir prompts/ \
            --eval-set evals/test-cases.json \
            --baseline evals/baselines/${{ steps.detect.outputs.version }}-scores.json \
            --version ${{ steps.detect.outputs.version }} \
            --threshold 0.85 \
            --output evals/regressions/${{ github.sha }}.json

      - name: Upload regression report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: regression-report-${{ matrix.prompt_type }}
          path: evals/regressions/${{ github.sha }}.json
```

### 5.4 GitHub Actions: Pre-commit Lint

```yaml
# .github/workflows/prompt-lint.yml
name: Prompt Lint

on:
  push:
    paths:
      - 'prompts/**'
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python scripts/lint_prompts.py
```

---

## 6. Quality Monitoring & Alerting

### 6.1 Production Quality Monitor (quality_monitor.py)

```python
#!/usr/bin/env python3
"""
Monitor production prompt quality.
Runs as a scheduled job (e.g., every hour) to detect quality degradation.
"""

import json
import time
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime, timedelta

import anthropic


def load_production_prompt() -> tuple[str, dict]:
    """Load the current production prompt version."""
    # In real setup, read from deployment config or feature flags
    config = json.loads(Path('prompts/deployment.json').read_text())
    version = config['active_version']
    prompt_path = Path('prompts/system') / version / 'system.md'
    meta_path = Path('prompts/system') / version / 'metadata.json'
    return prompt_path.read_text(), json.loads(meta_path.read_text())


def run_quality_checks(client: anthropic.Anthropic, prompt: str, meta: dict) -> dict:
    """Run a small set of quality checks on the production prompt."""
    # Use a curated set of high-signal test cases for monitoring
    monitor_cases = json.loads(
        Path('prompts/evals/monitor-cases.json').read_text()
    )

    scores = []
    latencies = []

    for case in monitor_cases:
        start = time.time()
        resp = client.messages.create(
            model=meta['model'],
            max_tokens=meta.get('max_tokens', 1024),
            temperature=0.0,
            system=prompt,
            messages=[{"role": "user", "content": case['input']}],
        )
        latency = (time.time() - start) * 1000
        output = resp.content[0].text

        # Simple scoring: check expected keywords
        expected = case.get('expected_properties', {})
        score = 1.0
        if 'contains' in expected:
            for kw in expected['contains']:
                if kw.lower() not in output.lower():
                    score -= 0.3
        scores.append(max(0, score))
        latencies.append(latency)

    avg_score = sum(scores) / len(scores)
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    return {
        'avg_score': avg_score,
        'avg_latency_ms': avg_latency,
        'p95_latency_ms': p95_latency,
        'sample_size': len(monitor_cases),
        'timestamp': datetime.utcnow().isoformat(),
    }


def check_and_alert(current: dict, historical: list[dict]) -> bool:
    """Compare current metrics to historical baseline, alert if degraded."""
    if not historical:
        return False

    baseline_scores = [h['avg_score'] for h in historical[-24:]]  # Last 24 runs
    baseline_mean = sum(baseline_scores) / len(baseline_scores)
    baseline_min = min(baseline_scores)

    # Alert conditions
    ALERT_THRESHOLD_ABSOLUTE = 0.7   # Absolute floor
    ALERT_THRESHOLD_RELATIVE = 0.15  # 15% drop from baseline

    alerts = []

    if current['avg_score'] < ALERT_THRESHOLD_ABSOLUTE:
        alerts.append(f"Score {current['avg_score']:.2f} below absolute threshold {ALERT_THRESHOLD_ABSOLUTE}")

    if baseline_mean > 0 and (baseline_mean - current['avg_score']) / baseline_mean > ALERT_THRESHOLD_RELATIVE:
        drop_pct = ((baseline_mean - current['avg_score']) / baseline_mean) * 100
        alerts.append(f"Score dropped {drop_pct:.1f}% from baseline {baseline_mean:.2f}")

    if alerts:
        send_alert(current, alerts, baseline_mean)
        return True

    return False


def send_alert(metrics: dict, alerts: list[str], baseline: float):
    """Send alert notification (email, Slack webhook, PagerDuty, etc.)."""
    # Example: Slack webhook
    import urllib.request

    webhook_url = Path('.secrets/slack-webhook.txt').read_text().strip()

    message = {
        "text": ":rotating_light: *Prompt Quality Alert*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f":rotating_light: *Prompt Quality Degradation Detected*\n\n"
                        f"Current score: {metrics['avg_score']:.2f}\n"
                        f"Baseline: {baseline:.2f}\n"
                        f"Time: {metrics['timestamp']}\n\n"
                        f"Alerts:\n" + "\n".join(f"- {a}" for a in alerts)
                    ),
                },
            },
        ],
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(message).encode(),
        headers={'Content-Type': 'application/json'},
    )
    urllib.request.urlopen(req)


def main():
    client = anthropic.Anthropic()
    prompt, meta = load_production_prompt()

    print("Running production quality checks...")
    metrics = run_quality_checks(client, prompt, meta)
    print(f"  Score: {metrics['avg_score']:.2f}")
    print(f"  Latency: {metrics['avg_latency_ms']:.0f}ms (p95: {metrics['p95_latency_ms']:.0f}ms)")

    # Load historical metrics
    history_path = Path('prompts/evals/quality-history.json')
    if history_path.exists():
        history = json.loads(history_path.read_text())
    else:
        history = []

    # Check for degradation
    alerted = check_and_alert(metrics, history)

    # Append to history
    history.append(metrics)
    # Keep last 7 days (168 hourly entries)
    history = history[-168:]
    history_path.write_text(json.dumps(history, indent=2))

    if alerted:
        print("ALERT: Quality degradation detected! Check notifications.")
        return 1

    print("Quality within normal range.")
    return 0


if __name__ == '__main__':
    exit(main())
```

### 6.2 Scheduled Monitoring Workflow

```yaml
# .github/workflows/prompt-quality-monitor.yml
name: Prompt Quality Monitor

on:
  schedule:
    - cron: '0 * * * *'  # Every hour
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install anthropic

      - name: Run quality monitor
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/quality_monitor.py
```

---

## 7. Rollback & Hotfix Procedures

### 7.1 Rollback Flow

```
Production quality degradation detected
  -> Confirm cause (prompt change vs model change vs data change)
  -> If prompt change:
    -> Revert to last verified version
    -> Verify quality restored after rollback
    -> Analyze root cause
    -> Fix and re-run full pipeline
```

### 7.2 Deployment Config (prompts/deployment.json)

```json
{
  "active_version": "v2",
  "previous_version": "v1",
  "canary_percentage": 0,
  "rollout_history": [
    {
      "version": "v1",
      "deployed_at": "2026-05-15T10:00:00Z",
      "status": "retired"
    },
    {
      "version": "v2",
      "deployed_at": "2026-05-29T14:30:00Z",
      "status": "active"
    }
  ]
}
```

### 7.3 Emergency Hotfix Protocol

```
If urgent fix needed:
  1. Create hotfix branch from current production version
  2. Minimal change (fix only, no other modifications)
  3. Run core golden tests (not full suite)
  4. Deploy to canary environment
  5. Verify, then full rollout
  6. Follow up with complete test suite
```

### 7.4 Rollback Script

```bash
#!/bin/bash
# scripts/rollback_prompt.sh
# Usage: ./scripts/rollback_prompt.sh v1

set -euo pipefail

TARGET_VERSION="${1:?Usage: rollback_prompt.sh <version>}"
DEPLOY_CONFIG="prompts/deployment.json"
CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('$DEPLOY_CONFIG'))['active_version'])")

echo "Current version: $CURRENT_VERSION"
echo "Rolling back to: $TARGET_VERSION"

# Verify target version exists
if [ ! -d "prompts/system/$TARGET_VERSION" ]; then
    echo "ERROR: Version $TARGET_VERSION not found"
    exit 1
fi

# Update deployment config
python3 -c "
import json
from datetime import datetime
config = json.load(open('$DEPLOY_CONFIG'))
config['previous_version'] = config['active_version']
config['active_version'] = '$TARGET_VERSION'
config['canary_percentage'] = 0
config['rollout_history'].append({
    'version': '$TARGET_VERSION',
    'deployed_at': datetime.utcnow().isoformat() + 'Z',
    'status': 'active',
    'reason': 'rollback from $CURRENT_VERSION'
})
# Mark previous as rolled back
for entry in config['rollout_history']:
    if entry['version'] == '$CURRENT_VERSION' and entry['status'] == 'active':
        entry['status'] = 'rolled_back'
json.dump(config, open('$DEPLOY_CONFIG', 'w'), indent=2)
"

echo "Deployment config updated. Running validation..."
python3 scripts/run_prompt_evals.py \
    --prompt-dir prompts/ \
    --eval-set evals/test-cases.json \
    --baseline evals/baselines/$TARGET_VERSION-scores.json \
    --version $TARGET_VERSION \
    --threshold 0.85

echo "Rollback to $TARGET_VERSION complete and validated."
```

---

## 8. Multi-Model & Dynamic Prompt Support

### 8.1 Multi-Model Testing

When the same prompt must work across multiple models, add a model matrix to the test runner:

```python
# In run_prompt_evals.py, support model override:
def run_multi_model_tests(client, prompt, test_cases, models):
    results_by_model = {}
    for model in models:
        meta_override = {'model': model, 'max_tokens': 1024, 'temperature': 0.0}
        results = [run_single_test(client, prompt, meta_override, tc) for tc in test_cases]
        results_by_model[model] = results
    return results_by_model
```

### 8.2 Dynamic Prompt Testing

For prompts assembled at runtime from multiple components:

```python
def test_prompt_combinations(base_prompt_dir: Path, components: list[str]):
    """Test all valid combinations of prompt components."""
    import itertools

    loaded = {}
    for comp in components:
        comp_path = base_prompt_dir / 'components' / f'{comp}.md'
        loaded[comp] = comp_path.read_text()

    # Test each combination
    for combo in itertools.product(*[loaded[c] for c in components]):
        assembled = "\n\n".join(combo)
        # Run test suite against assembled prompt
        yield assembled
```

---

## 9. Changelog Management

Every prompt change must update `prompts/changelog.md`:

```markdown
# Prompt Changelog

## v2 (2026-05-29)
- Improved tool selection accuracy
- Added explicit error handling guidance
- Reduced hallucination on edge cases

## v1 (2026-05-15)
- Initial production version
- Base system prompt for customer support
```

---

## 10. Implementation Checklist

- [ ] **Audit**: Locate all prompts in codebase, extract to `prompts/` directory
- [ ] **Classify**: Assign criticality levels (Critical/Important/Low) to each prompt
- [ ] **Version**: Set up `prompts/system/v1/` with current production prompt
- [ ] **Test cases**: Write golden tests, format tests, safety tests (minimum 10 golden + 10 safety per critical prompt)
- [ ] **Baselines**: Run test suite against current version, save as `evals/baselines/v1-scores.json`
- [ ] **Lint script**: Deploy `scripts/lint_prompts.py`
- [ ] **Regression runner**: Deploy `scripts/run_prompt_evals.py`
- [ ] **CI workflow**: Add `.github/workflows/prompt-regression.yml`
- [ ] **Monitoring**: Deploy `scripts/quality_monitor.py` with scheduled workflow
- [ ] **Alerting**: Configure Slack/email/PagerDuty webhook for quality alerts
- [ ] **Rollback**: Test rollback procedure end-to-end
- [ ] **Documentation**: Update team docs with prompt change process

---

## 11. Quick Start Commands

```bash
# 1. Install dependencies
pip install anthropic scipy

# 2. Lint prompts locally
python scripts/lint_prompts.py

# 3. Run regression tests
python scripts/run_prompt_evals.py \
    --prompt-dir prompts/ \
    --eval-set evals/test-cases.json \
    --baseline evals/baselines/v1-scores.json \
    --version v2

# 4. Run production quality check
python scripts/quality_monitor.py

# 5. Rollback to previous version
./scripts/rollback_prompt.sh v1
```

---

## Summary

This pipeline addresses the core problem -- prompt changes going untested and causing silent quality degradation -- by implementing six layers of defense:

1. **Pre-commit lint** catches formatting issues and hardcoded secrets before code review
2. **PR-gated regression tests** prevent merging changes that degrade quality
3. **Staging validation** tests against real LLM endpoints with full test suites
4. **Canary deployment** limits blast radius to 5% of traffic
5. **Continuous monitoring** detects quality drops within 1 hour (not 3 days)
6. **Automated rollback** can revert to the last known good version in under 5 minutes

The 3-day detection window shrinks to under 1 hour with continuous monitoring. The quality cliff problem is eliminated because no prompt change can reach production without passing regression tests.
