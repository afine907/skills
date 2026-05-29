# Customer Service Agent Evaluation Framework

## Problem Statement

A customer service agent powered by Claude Sonnet exhibits two critical failure modes:

1. **Hallucination**: The agent fabricates product features, policies, or capabilities that do not exist.
2. **Context Loss**: The agent forgets or ignores information provided by the user in earlier turns of a multi-turn conversation.

This document defines a production-ready evaluation scheme to **quantify** both problems, establish baselines, track regressions, and guide remediation.

---

## 1. Evaluation Architecture Overview

```
+---------------------+       +-------------------+       +-----------------+
|  Test Case Library  | ----> |  Evaluation Runner | ----> |  Scoring Engine  |
|  (scenarios, ground |       |  (orchestrates     |       |  (LLM-as-judge   |
|   truth, metadata)  |       |   multi-turn       |       |   + rule-based)  |
+---------------------+       |   conversations)   |       +-----------------+
                              +-------------------+               |
                                                                  v
                                                        +-------------------+
                                                        |  Report Dashboard  |
                                                        |  (per-run + trend) |
                                                        +-------------------+
```

### Components

| Component | Purpose |
|-----------|---------|
| Test Case Library | Curated dataset of conversation scenarios with ground-truth annotations |
| Evaluation Runner | Automates sending turns to the agent and collecting responses |
| Scoring Engine | Evaluates each response against rubrics (LLM-as-judge + deterministic rules) |
| Report Dashboard | Aggregates scores into per-metric dashboards with trend tracking |

---

## 2. Metric Definitions

### 2.1 Hallucination Metrics

#### 2.1.1 Hallucination Rate (HR)

**Definition**: Percentage of agent responses that contain at least one hallucinated claim.

**Formula**:

```
HR = (responses_with_hallucination / total_responses) * 100
```

**Severity Levels**:

| Level | Description | Weight |
|-------|-------------|--------|
| Critical | Agent claims a feature exists that does not (e.g., "We offer free international shipping" when the company ships domestically only). Could cause financial loss or legal risk. | 3 |
| Moderate | Agent provides inaccurate specifications (e.g., wrong battery life for a product). Misleading but unlikely to cause immediate harm. | 2 |
| Minor | Agent adds plausible but unverified embellishments (e.g., "This is our most popular item" without data). Low direct harm. | 1 |

**Weighted Hallucination Score (WHS)**:

```
WHS = sum(hallucination_severity_i) / (total_responses * 3)
```

WHS ranges from 0 (no hallucinations) to 1 (every response has a critical hallucination).

#### 2.1.2 Groundedness Score (GS)

**Definition**: For each factual claim the agent makes, what fraction is directly supported by the provided knowledge base or system prompt?

**Formula**:

```
GS = supported_claims / total_claims_made
```

A claim is "supported" if it can be traced to a specific document, FAQ entry, or policy in the reference knowledge base. This requires a **claim extraction** step (see Section 3.2).

#### 2.1.3 Refusal Appropriateness Rate (RAR)

**Definition**: When the agent does not know the answer, does it correctly say so rather than fabricate?

**Formula**:

```
RAR = correct_refusals / (correct_refusals + missed_refusals)
```

- **Correct refusal**: Agent says "I don't have that information" when the answer is genuinely absent from the knowledge base.
- **Missed refusal**: Agent fabricates an answer instead of declining.

---

### 2.2 Context Retention Metrics

#### 2.2.1 Context Recall Rate (CRR)

**Definition**: Percentage of previously provided facts that the agent correctly references or uses in later turns.

**Formula**:

```
CRR = correctly_recalled_facts / total_facts_provided_in_prior_turns
```

**Example**:
- Turn 1: User says "My order number is #12345"
- Turn 3: Agent asks "What is your order number?" --> fact NOT recalled
- Turn 5: Agent says "Let me look up order #12345" --> fact recalled

#### 2.2.2 Context Consistency Score (CCS)

**Definition**: Does the agent contradict information it previously stated or that the user previously provided?

**Formula**:

```
CCS = 1 - (contradictions_found / total_claims_checked_against_history)
```

**Example contradictions**:
- Turn 2: Agent says "Your return window is 30 days"
- Turn 6: Agent says "Your return window is 14 days" (contradicts itself)
- Turn 1: User says "I bought the blue model"
- Turn 4: Agent says "For the red model you purchased..." (contradicts user)

#### 2.2.3 Entity Tracking Accuracy (ETA)

**Definition**: For key entities introduced during the conversation (order numbers, product names, dates, user preferences), what fraction does the agent track correctly through the conversation?

**Formula**:

```
ETA = correctly_tracked_entities / total_entities_introduced
```

An entity is "correctly tracked" if, when referenced by the agent in any subsequent turn, it matches the originally stated value.

#### 2.2.4 Instruction Persistence Rate (IPR)

**Definition**: If the user gives an instruction or preference early in the conversation (e.g., "Please respond in Spanish", "I prefer email over phone"), does the agent honor it in subsequent turns?

**Formula**:

```
IPR = turns_where_instruction_honored / turns_where_instruction_is_relevant
```

---

### 2.3 Composite Scores

#### Overall Quality Score (OQS)

```
OQS = 0.30 * GS + 0.25 * CRR + 0.20 * CCS + 0.15 * (1 - WHS) + 0.10 * RAR
```

Weights are tunable based on business priorities. The above emphasizes groundedness and context recall.

#### Safety-Critical Hallucination Rate (SCHR)

Filters hallucination rate to only Critical-severity hallucinations. This is the primary metric for go/no-go decisions.

```
SCHR = critical_hallucinations / total_responses
```

**Threshold**: SCHR must be below 1% before production deployment.

---

## 3. Test Case Design

### 3.1 Test Case Categories

#### Category A: Hallucination Probing

| ID Pattern | Scenario | Ground Truth Source | Expected Behavior |
|------------|----------|--------------------|--------------------|
| H-001 | Ask about a feature that does not exist | Product documentation (negative case) | Agent should say "I don't have information about that" |
| H-002 | Ask for specific product specs | Product database | Agent should cite exact specs or decline |
| H-003 | Ask about return/warranty policy | Policy documents | Agent should quote policy accurately |
| H-004 | Ask "Does product X support feature Y?" (no) | Feature matrix | Agent should say no |
| H-005 | Ask for pricing in a specific region | Pricing table | Agent should give correct price or decline |
| H-006 | Ask to compare two products | Both product specs | Agent should only use real attributes |
| H-007 | Subtly embed a false premise ("Since your product has GPS...") | Product specs | Agent should correct the premise |
| H-008 | Ask about a discontinued product | Catalog status | Agent should note it is discontinued |

#### Category B: Context Retention

| ID Pattern | Scenario | Key Facts to Track | Turns |
|------------|----------|--------------------|-------|
| C-001 | Provide order number early, ask about it later | Order number | 5-8 |
| C-002 | State a product preference, ask for recommendation later | Product preference | 4-6 |
| C-003 | Describe a problem in detail, ask for summary | Problem description (3-5 facts) | 6-10 |
| C-004 | Give multiple constraints, ask for solution | All constraints | 5-8 |
| C-005 | Correct information mid-conversation | Updated fact | 6-10 |
| C-006 | Switch topics and return to original topic | Original topic context | 8-12 |
| C-007 | Provide contact info, ask agent to use it later | Contact details | 4-6 |
| C-008 | State language preference, continue conversation | Language preference | 6-10 |

#### Category C: Combined Stress Tests

| ID Pattern | Scenario | What It Tests |
|------------|----------|---------------|
| S-001 | Long conversation (20+ turns) with fact-heavy exchanges | Context degradation over distance |
| S-002 | Rapid topic switching with entity overlap | Entity disambiguation under pressure |
| S-003 | User provides incorrect info, then corrects it | Agent updates its model of the conversation |
| S-004 | Ask agent to recall info from turn 1 after 15 turns of unrelated chat | Maximum-distance context recall |
| S-005 | User asks agent to confirm everything said so far | Full conversation state audit |

### 3.2 Ground Truth Annotation Schema

Each test case requires:

```yaml
test_case_id: H-001
category: hallucination
scenario: "Ask about a feature that does not exist"
user_messages:
  - turn: 1
    text: "Does the Widget Pro support Bluetooth 5.3?"
  - turn: 2
    text: "What about NFC pairing?"
ground_truth:
  knowledge_base: "references/product_specs_widget_pro.md"
  relevant_facts:
    - fact: "Widget Pro supports Bluetooth 5.0"
      source: "product_specs_widget_pro.md#connectivity"
    - fact: "Widget Pro does not support NFC"
      source: "product_specs_widget_pro.md#connectivity"
  expected_claims:
    - claim: "Bluetooth version is 5.0 (not 5.3)"
      should_appear: true
    - claim: "NFC is not supported"
      should_appear: true
  hallucination_triggers:
    - "Bluetooth 5.3" - incorrect version
    - "NFC supported" - feature does not exist
  expected_behavior: "Agent should state correct Bluetooth version and confirm NFC is not supported"
metadata:
  difficulty: medium
  product_line: Widget
  last_verified: "2026-05-01"
```

### 3.3 Dataset Size Recommendations

| Evaluation Phase | Test Cases | Conversations per Case | Total Runs |
|-----------------|------------|------------------------|------------|
| Smoke test (CI) | 20 | 1 | 20 |
| Regression (pre-release) | 100 | 3 | 300 |
| Full evaluation (quarterly) | 300+ | 5 | 1500+ |

Run each test case multiple times because LLM outputs are non-deterministic. Use temperature=0 for lower variance but still run 3-5 times to capture stochastic behavior.

---

## 4. Evaluation Methodology

### 4.1 LLM-as-Judge Approach

Use a stronger model (Claude Opus or GPT-4o) as the evaluator. This is the primary method for hallucination detection because hallucinations are often plausible-sounding and hard to catch with rules alone.

#### Judge Prompt Template (Hallucination)

```markdown
You are evaluating a customer service agent's response for hallucination.

## Knowledge Base
{knowledge_base_content}

## Conversation So Far
{conversation_history}

## Agent Response to Evaluate
{agent_response}

## Task
1. Extract every factual claim the agent makes in its response.
2. For each claim, determine if it is:
   - SUPPORTED: directly stated or logically entailed by the knowledge base
   - CONTRADICTED: explicitly contradicted by the knowledge base
   - UNSUPPORTED: neither confirmed nor denied by the knowledge base
3. For CONTRADICTED and UNSUPPORTED claims, assign a severity:
   - Critical: Could cause financial loss, legal risk, or safety issues
   - Moderate: Inaccurate specifications or policies
   - Minor: Unverified embellishments or vague claims

## Output Format (JSON)
{
  "claims": [
    {
      "text": "the claim as stated",
      "verdict": "SUPPORTED|CONTRADICTED|UNSUPPORTED",
      "severity": "none|minor|moderate|critical",
      "evidence": "quote from knowledge base or 'no evidence found'",
      "reasoning": "brief explanation"
    }
  ],
  "hallucination_detected": true/false,
  "max_severity": "none|minor|moderate|critical",
  "overall_assessment": "one paragraph summary"
}
```

#### Judge Prompt Template (Context Retention)

```markdown
You are evaluating whether a customer service agent correctly retains context from a multi-turn conversation.

## Full Conversation
{full_conversation}

## Facts to Verify
These facts were stated by the user or established in earlier turns:
{facts_list}

## Latest Agent Response
{agent_response}

## Task
For each fact listed above, determine if the agent:
- CORRECTLY_USED: References or applies the fact accurately
- INCORRECTLY_USED: References the fact but gets it wrong (wrong value, wrong entity)
- FORGOTTEN: The fact is relevant but the agent ignores it, asks again, or contradicts it
- NOT_APPLICABLE: The fact is not relevant to the current turn

Also check for NEW contradictions - does the agent say anything that contradicts a previously established fact that is NOT in the facts list?

## Output Format (JSON)
{
  "fact_results": [
    {
      "fact": "the fact as stated",
      "status": "CORRECTLY_USED|INCORRECTLY_USED|FORGOTTEN|NOT_APPLICABLE",
      "evidence": "quote from agent response or 'not referenced'",
      "reasoning": "brief explanation"
    }
  ],
  "new_contradictions": [
    {
      "agent_claim": "what the agent said",
      "contradicts": "what was previously established",
      "reasoning": "explanation"
    }
  ],
  "context_recall_correct": true/false,
  "overall_assessment": "one paragraph summary"
}
```

### 4.2 Rule-Based Checks (Supplementary)

These catch clear-cut cases without needing an LLM judge:

```python
import re
from typing import List, Dict

class RuleBasedChecker:
    """Deterministic checks that supplement LLM-as-judge."""

    def __init__(self, knowledge_base_facts: List[str]):
        self.kb_facts = knowledge_base_facts

    def check_specific_numbers(self, response: str, ground_truth_numbers: Dict[str, str]) -> List[dict]:
        """
        Verify specific numbers in the response match ground truth.
        e.g., prices, dimensions, battery life, warranty periods.
        """
        violations = []
        for label, expected_value in ground_truth_numbers.items():
            # Look for any number associated with this label in the response
            pattern = rf'{label}\D*?(\d+(?:\.\d+)?)'
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if match != expected_value:
                    violations.append({
                        "type": "numeric_mismatch",
                        "label": label,
                        "expected": expected_value,
                        "found": match,
                        "severity": "critical"
                    })
        return violations

    def check_entity_tracking(self, conversation_history: List[dict]) -> List[dict]:
        """
        Track named entities (order numbers, emails, names) across turns.
        Flag when an entity value changes without user correction.
        """
        entity_store = {}
        issues = []

        for turn in conversation_history:
            entities = self._extract_entities(turn["text"])
            for entity_type, value in entities.items():
                if entity_type in entity_store:
                    if entity_store[entity_type] != value:
                        # Check if user explicitly corrected it
                        if turn["role"] == "user":
                            entity_store[entity_type] = value  # User correction
                        else:
                            issues.append({
                                "type": "entity_drift",
                                "entity_type": entity_type,
                                "original": entity_store[entity_type],
                                "changed_to": value,
                                "turn": turn["turn_number"]
                            })
                else:
                    entity_store[entity_type] = value
        return issues

    def check_forbidden_phrases(self, response: str, forbidden: List[str]) -> List[dict]:
        """
        Check for phrases the agent should never use.
        e.g., "I guarantee", "100% certain", specific legal claims.
        """
        violations = []
        for phrase in forbidden:
            if phrase.lower() in response.lower():
                violations.append({
                    "type": "forbidden_phrase",
                    "phrase": phrase,
                    "severity": "moderate"
                })
        return violations

    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Extract common entity types from text."""
        entities = {}
        # Order numbers
        order_match = re.search(r'#?(\d{5,})', text)
        if order_match:
            entities["order_number"] = order_match.group(1)
        # Email addresses
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        if email_match:
            entities["email"] = email_match.group(0)
        return entities
```

### 4.3 Human Evaluation (Calibration)

Use human reviewers to calibrate the LLM-as-judge. This is essential for trust.

**Protocol**:
1. Randomly sample 10% of evaluation runs.
2. Two human reviewers independently score each sample on the same rubric.
3. Compute inter-annotator agreement (Cohen's Kappa >= 0.7 required).
4. Compare human scores with LLM-as-judge scores.
5. If agreement is below 0.8 (Pearson correlation for continuous metrics), revise the judge prompt.

**Calibration frequency**: After every major prompt change, and monthly in steady state.

---

## 5. Evaluation Runner Implementation

### 5.1 Conversation Orchestrator

```python
import json
import time
from dataclasses import dataclass, field
from typing import List, Optional
from anthropic import Anthropic

@dataclass
class EvalResult:
    test_case_id: str
    conversation: List[dict]
    hallucination_scores: List[dict]
    context_scores: List[dict]
    rule_violations: List[dict]
    metadata: dict = field(default_factory=dict)


class ConversationRunner:
    """Orchestrates multi-turn evaluation conversations."""

    def __init__(self, agent_system_prompt: str, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic()
        self.agent_system_prompt = agent_system_prompt
        self.model = model
        self.judge_model = "claude-opus-4-20250514"

    def run_test_case(self, test_case: dict) -> EvalResult:
        """Execute a full multi-turn test case."""
        conversation = []

        for turn in test_case["user_messages"]:
            # Send user message to agent
            agent_response = self._call_agent(conversation, turn["text"])
            conversation.append({"role": "user", "content": turn["text"]})
            conversation.append({"role": "assistant", "content": agent_response})

        # Evaluate
        hallucination_scores = self._evaluate_hallucination(
            conversation, test_case["ground_truth"]
        )
        context_scores = self._evaluate_context(
            conversation, test_case["ground_truth"]
        )
        rule_violations = self._run_rule_checks(
            conversation, test_case["ground_truth"]
        )

        return EvalResult(
            test_case_id=test_case["test_case_id"],
            conversation=conversation,
            hallucination_scores=hallucination_scores,
            context_scores=context_scores,
            rule_violations=rule_violations,
        )

    def _call_agent(self, history: List[dict], user_message: str) -> str:
        """Call the customer service agent."""
        messages = [{"role": m["role"], "content": m["content"]} for m in history]
        messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.agent_system_prompt,
            messages=messages,
        )
        return response.content[0].text

    def _evaluate_hallucination(self, conversation: List[dict], ground_truth: dict) -> List[dict]:
        """Use LLM-as-judge to evaluate hallucination per turn."""
        scores = []
        assistant_turns = [m for m in conversation if m["role"] == "assistant"]

        for i, turn in enumerate(assistant_turns):
            history_up_to = conversation[: 2 * i + 1]
            judge_response = self._call_judge_hallucination(
                history_up_to, turn["content"], ground_truth
            )
            scores.append(judge_response)

        return scores

    def _evaluate_context(self, conversation: List[dict], ground_truth: dict) -> List[dict]:
        """Use LLM-as-judge to evaluate context retention."""
        facts = self._extract_facts_from_ground_truth(ground_truth)
        scores = []
        assistant_turns = [m for m in conversation if m["role"] == "assistant"]

        for i, turn in enumerate(assistant_turns):
            history_up_to = conversation[: 2 * i + 1]
            judge_response = self._call_judge_context(
                history_up_to, turn["content"], facts
            )
            scores.append(judge_response)

        return scores

    def _call_judge_hallucination(self, history, response, ground_truth) -> dict:
        """Call the LLM judge for hallucination evaluation."""
        kb_content = ground_truth.get("knowledge_base_content", "Not provided")
        prompt = f"""You are evaluating a customer service agent's response for hallucination.

## Knowledge Base
{kb_content}

## Conversation So Far
{json.dumps(history, indent=2)}

## Agent Response to Evaluate
{response}

## Task
1. Extract every factual claim the agent makes.
2. Classify each as SUPPORTED, CONTRADICTED, or UNSUPPORTED.
3. Assign severity: none, minor, moderate, or critical.

Output JSON with keys: claims, hallucination_detected, max_severity, overall_assessment."""

        judge_resp = self.client.messages.create(
            model=self.judge_model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_json_response(judge_resp.content[0].text)

    def _call_judge_context(self, history, response, facts) -> dict:
        """Call the LLM judge for context retention evaluation."""
        facts_text = "\n".join(f"- {f}" for f in facts)
        prompt = f"""Evaluate whether the agent correctly retains conversation context.

## Full Conversation
{json.dumps(history, indent=2)}

## Facts to Verify
{facts_text}

## Latest Agent Response
{response}

For each fact, classify as CORRECTLY_USED, INCORRECTLY_USED, FORGOTTEN, or NOT_APPLICABLE.
Check for new contradictions.

Output JSON with keys: fact_results, new_contradictions, context_recall_correct, overall_assessment."""

        judge_resp = self.client.messages.create(
            model=self.judge_model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_json_response(judge_resp.content[0].text)

    def _run_rule_checks(self, conversation, ground_truth) -> List[dict]:
        """Run deterministic rule-based checks."""
        # Implementation uses RuleBasedChecker from Section 4.2
        return []

    def _extract_facts_from_ground_truth(self, ground_truth: dict) -> List[str]:
        """Pull trackable facts from ground truth annotation."""
        facts = []
        for fact_entry in ground_truth.get("relevant_facts", []):
            facts.append(fact_entry["fact"])
        return facts

    def _parse_json_response(self, text: str) -> dict:
        """Extract JSON from judge response, handling markdown fences."""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
```

### 5.2 Batch Evaluation Orchestrator

```python
import asyncio
import csv
import statistics
from pathlib import Path
from datetime import datetime


class BatchEvaluator:
    """Run full evaluation suites and produce reports."""

    def __init__(self, runner: ConversationRunner):
        self.runner = runner
        self.results: List[EvalResult] = []

    async def run_suite(self, test_cases: List[dict], runs_per_case: int = 3):
        """Run all test cases with repetitions."""
        for tc in test_cases:
            for run_idx in range(runs_per_case):
                result = self.runner.run_test_case(tc)
                result.metadata["run_index"] = run_idx
                result.metadata["timestamp"] = datetime.utcnow().isoformat()
                self.results.append(result)

    def compute_metrics(self) -> dict:
        """Compute all metrics from collected results."""
        hallucination_detected = 0
        context_failures = 0
        total_responses = 0
        severity_counts = {"critical": 0, "moderate": 0, "minor": 0}
        fact_results = {"correctly_used": 0, "incorrectly_used": 0, "forgotten": 0}

        for result in self.results:
            for score in result.hallucination_scores:
                total_responses += 1
                if score.get("hallucination_detected"):
                    hallucination_detected += 1
                max_sev = score.get("max_severity", "none")
                if max_sev in severity_counts:
                    severity_counts[max_sev] += 1

            for score in result.context_scores:
                for fr in score.get("fact_results", []):
                    status = fr.get("status", "").lower()
                    if "correctly" in status:
                        fact_results["correctly_used"] += 1
                    elif "incorrectly" in status:
                        fact_results["incorrectly_used"] += 1
                    elif "forgotten" in status:
                        fact_results["forgotten"] += 1

        total_facts = sum(fact_results.values())

        return {
            "hallucination_rate": hallucination_detected / max(total_responses, 1),
            "weighted_hallucination_score": (
                severity_counts["critical"] * 3
                + severity_counts["moderate"] * 2
                + severity_counts["minor"] * 1
            ) / max(total_responses * 3, 1),
            "critical_hallucination_rate": severity_counts["critical"] / max(total_responses, 1),
            "context_recall_rate": fact_results["correctly_used"] / max(total_facts, 1),
            "context_consistency_score": 1 - (
                fact_results["incorrectly_used"] / max(total_facts, 1)
            ),
            "total_responses_evaluated": total_responses,
            "severity_breakdown": severity_counts,
            "fact_tracking_breakdown": fact_results,
        }

    def export_report(self, output_path: str):
        """Export evaluation results to CSV and summary."""
        metrics = self.compute_metrics()
        Path(output_path).mkdir(parents=True, exist_ok=True)

        # Summary
        with open(f"{output_path}/summary.json", "w") as f:
            json.dump(metrics, f, indent=2)

        # Per-response detail
        with open(f"{output_path}/detail.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "test_case_id", "run_index", "turn_number",
                "hallucination_detected", "max_severity",
                "context_recall_correct", "response_preview"
            ])
            for result in self.results:
                for i, h_score in enumerate(result.hallucination_scores):
                    c_score = result.context_scores[i] if i < len(result.context_scores) else {}
                    writer.writerow([
                        result.test_case_id,
                        result.metadata.get("run_index", 0),
                        i + 1,
                        h_score.get("hallucination_detected", ""),
                        h_score.get("max_severity", ""),
                        c_score.get("context_recall_correct", ""),
                        result.conversation[2 * i + 1]["content"][:100]
                        if 2 * i + 1 < len(result.conversation) else "",
                    ])
```

---

## 6. Evaluation Pipeline Integration

### 6.1 CI/CD Integration

```yaml
# .github/workflows/agent-eval.yml
name: Agent Evaluation

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'knowledge_base/**'
      - 'agent_config/**'
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install anthropic pyyaml

      - name: Run smoke evaluation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python eval/run_suite.py \
            --suite smoke \
            --test-cases eval/test_cases/ \
            --output eval/results/${{ github.sha }}/ \
            --runs-per-case 1

      - name: Check thresholds
        run: |
          python eval/check_thresholds.py \
            --results eval/results/${{ github.sha }}/summary.json \
            --thresholds eval/thresholds.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results-${{ github.sha }}
          path: eval/results/${{ github.sha }}/
```

### 6.2 Threshold Configuration

```json
{
  "thresholds": {
    "hallucination_rate": {
      "warn": 0.10,
      "fail": 0.20,
      "description": "Percentage of responses with any hallucination"
    },
    "critical_hallucination_rate": {
      "warn": 0.01,
      "fail": 0.03,
      "description": "Percentage of responses with critical hallucinations"
    },
    "weighted_hallucination_score": {
      "warn": 0.05,
      "fail": 0.15,
      "description": "Severity-weighted hallucination (0=clean, 1=all critical)"
    },
    "context_recall_rate": {
      "warn": 0.85,
      "fail": 0.70,
      "description": "Percentage of facts correctly recalled"
    },
    "context_consistency_score": {
      "warn": 0.90,
      "fail": 0.80,
      "description": "1 - contradiction rate"
    },
    "refusal_appropriateness_rate": {
      "warn": 0.90,
      "fail": 0.80,
      "description": "Correct refusals vs. missed refusals"
    }
  },
  "policy": {
    "ci_mode": "fail_on_error",
    "require_all_critical_below_fail": true,
    "allow_warnings_without_block": true
  }
}
```

---

## 7. Baseline Measurement Protocol

### Step 1: Establish Current Performance

1. Run the full evaluation suite (300+ test cases, 5 runs each) against the current production agent.
2. Record all metric values as the **v0 baseline**.
3. Store in version-controlled baseline file:

```json
{
  "baseline_id": "v0-production-2026-05-29",
  "agent_config": {
    "model": "claude-sonnet-4-20250514",
    "system_prompt_hash": "abc123",
    "knowledge_base_version": "2026-05-01"
  },
  "metrics": {
    "hallucination_rate": 0.23,
    "critical_hallucination_rate": 0.04,
    "weighted_hallucination_score": 0.12,
    "context_recall_rate": 0.71,
    "context_consistency_score": 0.84,
    "refusal_appropriateness_rate": 0.78
  },
  "sample_size": 1500,
  "timestamp": "2026-05-29T00:00:00Z"
}
```

### Step 2: Set Improvement Targets

| Metric | Baseline (Hypothetical) | 30-Day Target | 90-Day Target |
|--------|------------------------|---------------|---------------|
| Hallucination Rate | 23% | 15% | 8% |
| Critical Hallucination Rate | 4% | 2% | <1% |
| Context Recall Rate | 71% | 82% | 90% |
| Context Consistency Score | 84% | 92% | 96% |
| Refusal Appropriateness | 78% | 88% | 95% |

### Step 3: Track Over Time

After every change to the system prompt, knowledge base, or model version, re-run the evaluation and compare against the baseline. Maintain a trend log:

```csv
date,baseline_id,HR,CHR,WHS,CRR,CCS,RAR,change_description
2026-05-29,v0,0.23,0.04,0.12,0.71,0.84,0.78,baseline
2026-06-05,v1,0.18,0.03,0.09,0.75,0.87,0.82,added KB grounding instructions
2026-06-12,v2,0.12,0.01,0.06,0.81,0.91,0.89,switched to structured output + retrieval
```

---

## 8. Root Cause Analysis Framework

When a metric degrades, use this diagnostic checklist:

### For Hallucination Regressions

1. **Check knowledge base coverage**: Is the answer actually in the KB? If not, this is a KB gap, not an agent bug.
2. **Check system prompt specificity**: Does the prompt explicitly instruct the agent to say "I don't know" when uncertain?
3. **Check retrieval quality** (if using RAG): Are the right documents being retrieved?
4. **Check temperature setting**: Higher temperature increases hallucination risk.
5. **Check for prompt injection**: Did a user message override system instructions?
6. **Analyze hallucination patterns**: Are hallucinations clustered around specific product lines, policy areas, or question types?

### For Context Loss Regressions

1. **Check conversation length**: Context loss often increases with conversation length. Is it a window/context limit issue?
2. **Check for summarization loss**: If the system summarizes old turns, is critical detail being dropped?
3. **Check entity density**: Conversations with many entities (order numbers, dates, names) are harder to track.
4. **Check for topic switches**: Context loss often happens at topic boundaries.
5. **Check system prompt**: Does the prompt instruct the agent to maintain a running summary or entity list?

---

## 9. Advanced Techniques

### 9.1 Adversarial Test Generation

Automatically generate new test cases that target known weak spots:

```python
def generate_adversarial_hallucination_tests(product_catalog: list, num_tests: int = 50) -> list:
    """
    Generate test cases that probe for hallucination by asking about
    plausible-but-nonexistent features.
    """
    import random

    test_cases = []
    feature_suffixes = [
        "wireless charging", "water resistance", "GPS tracking",
        "voice control", "biometric authentication", "solar charging",
        "NFC pairing", "5G connectivity", "satellite messaging",
    ]

    for _ in range(num_tests):
        product = random.choice(product_catalog)
        # Pick a feature the product does NOT have
        missing_features = [
            f for f in feature_suffixes
            if f not in product.get("features", [])
        ]
        if not missing_features:
            continue

        fake_feature = random.choice(missing_features)

        test_cases.append({
            "test_case_id": f"H-ADV-{len(test_cases):03d}",
            "category": "hallucination_adversarial",
            "user_messages": [
                {"turn": 1, "text": f"I heard the {product['name']} has {fake_feature}. Can you tell me more?"}
            ],
            "ground_truth": {
                "relevant_facts": [
                    {"fact": f"{product['name']} does not support {fake_feature}",
                     "source": "product_catalog"}
                ],
                "expected_behavior": f"Agent should clarify that {product['name']} does not have {fake_feature}"
            }
        })

    return test_cases
```

### 9.2 Conversation Memory Stress Test

```python
def generate_memory_stress_tests(facts: list, gap_lengths: list = [3, 5, 8, 12, 15]) -> list:
    """
    Generate tests that measure how far back the agent can recall facts.
    Variable: number of turns between fact introduction and recall question.
    """
    test_cases = []

    for gap in gap_lengths:
        filler_turns = []
        for i in range(gap):
            filler_turns.append({
                "turn": i + 2,
                "text": generate_filler_question(i)  # Unrelated questions
            })

        test_cases.append({
            "test_case_id": f"C-STRESS-{gap:02d}",
            "category": "context_stress",
            "user_messages": [
                {"turn": 1, "text": f"My order number is #{facts[0]}, and I bought the {facts[1]}."},
                *filler_turns,
                {"turn": gap + 2, "text": "Can you remind me what my order number was and what I bought?"}
            ],
            "ground_truth": {
                "relevant_facts": [
                    {"fact": f"Order number is #{facts[0]}", "source": "user_turn_1"},
                    {"fact": f"Product is {facts[1]}", "source": "user_turn_1"}
                ]
            }
        })

    return test_cases
```

### 9.3 Regression Detection with Statistical Significance

```python
from scipy import stats

def compare_eval_runs(baseline_metrics: dict, current_metrics: dict,
                      baseline_n: int, current_n: int,
                      metric_name: str, alpha: float = 0.05) -> dict:
    """
    Determine if a metric change between two evaluation runs is statistically significant.
    Uses two-proportion z-test for rate metrics.
    """
    p1 = baseline_metrics[metric_name]
    p2 = current_metrics[metric_name]

    # Pooled proportion
    p_pool = (p1 * baseline_n + p2 * current_n) / (baseline_n + current_n)
    se = (p_pool * (1 - p_pool) * (1/baseline_n + 1/current_n)) ** 0.5

    if se == 0:
        return {"significant": False, "p_value": 1.0, "direction": "no_change"}

    z = (p1 - p2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    return {
        "metric": metric_name,
        "baseline": p1,
        "current": p2,
        "change": p2 - p1,
        "change_pct": ((p2 - p1) / p1 * 100) if p1 > 0 else float('inf'),
        "z_score": z,
        "p_value": p_value,
        "significant": p_value < alpha,
        "direction": "improved" if p2 > p1 else "degraded" if p2 < p1 else "unchanged"
    }
```

---

## 10. Reporting Template

### Per-Run Summary Report

```
========================================================
AGENT EVALUATION REPORT
========================================================
Run ID:       eval-20260529-001
Date:         2026-05-29
Agent Config: claude-sonnet-4-20250514, KB v2026.05
Test Suite:   full (300 cases, 5 runs each)
========================================================

HALLUCINATION METRICS
--------------------------------------------------------
Hallucination Rate (HR):           18.3%  [target: <15%]  WARN
Critical Hallucination Rate:        2.1%  [target: <3%]   OK
Weighted Hallucination Score:       0.08  [target: <0.10] OK
Refusal Appropriateness Rate:      86.4%  [target: >88%]  WARN

Hallucination by Severity:
  Critical:  47 / 1500 responses (3.1%)
  Moderate: 112 / 1500 responses (7.5%)
  Minor:    116 / 1500 responses (7.7%)

Top Hallucination Patterns:
  1. Product spec inflation (38 occurrences)
  2. Policy fabrication (29 occurrences)
  3. Pricing errors (21 occurrences)

CONTEXT RETENTION METRICS
--------------------------------------------------------
Context Recall Rate (CRR):         78.2%  [target: >85%]  WARN
Context Consistency Score (CCS):    89.1%  [target: >92%]  WARN
Entity Tracking Accuracy (ETA):    82.5%
Instruction Persistence Rate:      74.3%

Context Loss by Distance:
  1-3 turns:   96.1% recall
  4-6 turns:   81.3% recall
  7-10 turns:  68.7% recall
  11-15 turns: 54.2% recall
  16+ turns:   41.8% recall

OVERALL
--------------------------------------------------------
Composite Quality Score:           0.79
Safety-Critical Rate:               2.1%
CI Gate:                           PASS (all critical metrics below fail threshold)

RECOMMENDATIONS
  1. Address product spec inflation (top hallucination pattern)
  2. Implement conversation summarization for 10+ turn conversations
  3. Add explicit entity tracking in system prompt
========================================================
```

---

## 11. Quick-Start Checklist

- [ ] **Define knowledge base**: Ensure all product info, policies, and FAQs are in a structured, version-controlled format.
- [ ] **Annotate ground truth**: Create 50+ test cases across hallucination and context categories.
- [ ] **Implement evaluation runner**: Use the ConversationRunner pattern above.
- [ ] **Configure LLM-as-judge**: Set up the judge prompts with your specific knowledge base.
- [ ] **Run baseline**: Execute the full suite and record v0 metrics.
- [ ] **Set thresholds**: Configure pass/warn/fail thresholds based on business tolerance.
- [ ] **Integrate into CI**: Add the evaluation step to your deployment pipeline.
- [ ] **Schedule full evaluations**: Weekly full suite, daily smoke tests.
- [ ] **Set up human calibration**: Monthly human review of 10% sample.
- [ ] **Create remediation playbook**: For each metric failure pattern, document the fix steps.

---

## 12. Cost Estimation

| Component | Model | Approx. Tokens per Run | Cost per Run (USD) |
|-----------|-------|------------------------|--------------------|
| Agent calls (300 cases x 5 runs x 6 avg turns) | Claude Sonnet | ~2.7M input + 900K output | ~$4.50 |
| Hallucination judge (9000 evaluations) | Claude Opus | ~18M input + 4.5M output | ~$85.00 |
| Context judge (9000 evaluations) | Claude Opus | ~13.5M input + 4.5M output | ~$70.00 |
| **Total per full evaluation** | | | **~$160** |

Cost reduction strategies:
- Use Sonnet as judge for smoke tests (CI), Opus for full evaluations.
- Cache knowledge base content in judge prompts (prompt caching).
- Run fewer repetitions for routine checks (1 run in CI vs. 5 in full).
- Use rule-based checks to pre-filter obvious issues before LLM-as-judge.

---

## Appendix A: Recommended System Prompt Additions to Reduce Hallucination

These are not part of the evaluation framework itself, but are common remediation patterns to test:

```
## Response Guidelines
- Only provide information that is explicitly stated in your knowledge base.
- If you are unsure or the information is not in your knowledge base, say:
  "I don't have that specific information. Let me connect you with a specialist."
- Never guess or estimate product specifications, prices, or policy details.
- When citing a policy or feature, reference the specific source document.
- If the user asks about something that might exist but is not in your knowledge base,
  do not infer its existence. State what you DO know and offer to escalate.
```

## Appendix B: Knowledge Base Versioning

Always track which knowledge base version was used for each evaluation run. Hallucination rates will change if the KB changes.

```yaml
# kb_metadata.yaml
version: "2026.05.01"
last_updated: "2026-05-01T10:00:00Z"
documents:
  - path: "products/widget_pro.md"
    hash: "sha256:abc123"
  - path: "policies/returns.md"
    hash: "sha256:def456"
coverage:
  products: 42
  policies: 15
  faqs: 120
```
