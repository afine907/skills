# System Prompt A/B Testing Framework

## 1. Overview

This document provides a production-ready framework for scientifically comparing two system prompt versions:

- **v1 (Control)**: Simple role definition
- **v2 (Treatment)**: Role definition + chain-of-thought (CoT) + few-shot examples

The framework uses controlled experimentation with statistical hypothesis testing to determine whether v2 produces measurably better outputs than v1.

---

## 2. Experiment Design

### 2.1 Hypothesis

- **H0 (Null)**: There is no significant difference in output quality between v1 and v2.
- **H1 (Alternative)**: v2 produces significantly higher quality outputs than v1 (one-tailed test).

### 2.2 Evaluation Dimensions

Each model response is scored on multiple dimensions using a 1-5 Likert scale:

| Dimension | Description | Weight |
|-----------|-------------|--------|
| **Correctness** | Factual accuracy and logical validity | 0.30 |
| **Completeness** | Coverage of all required aspects | 0.25 |
| **Instruction Following** | Adherence to format/constraint requirements | 0.20 |
| **Coherence** | Clarity, structure, and readability | 0.15 |
| **Efficiency** | Conciseness without sacrificing quality | 0.10 |

The **composite score** is the weighted sum: `S = 0.30*C + 0.25*Co + 0.20*IF + 0.15*Ch + 0.10*E`

### 2.3 Sample Size Calculation

To detect a medium effect size (Cohen's d = 0.5) with:
- Significance level (alpha) = 0.05
- Statistical power (1 - beta) = 0.80

Required sample size per group:

```
n = 2 * ((Z_alpha + Z_beta) / d)^2
n = 2 * ((1.645 + 0.842) / 0.5)^2
n = 2 * (4.974)^2
n ≈ 50 samples per group
```

**Recommendation**: Use 60 samples per group (120 total) to account for potential data loss.

### 2.4 Randomization and Assignment

```python
import random
import hashlib

def assign_variant(sample_id: str, salt: str = "prompt_ab_test_2026") -> str:
    """Deterministic assignment using hash to ensure reproducibility."""
    hash_input = f"{salt}:{sample_id}"
    hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
    return "v1" if hash_value % 2 == 0 else "v2"
```

Each test case (prompt + input pair) is assigned to exactly one variant. The assignment is deterministic based on the sample ID, ensuring reproducibility.

---

## 3. Test Dataset Construction

### 3.1 Test Case Categories

Create a balanced test set across these categories:

| Category | Count | Examples |
|----------|-------|---------|
| Simple factual questions | 15 | "What is the capital of France?" |
| Multi-step reasoning | 15 | "A store has 3 items with different discounts..." |
| Instruction-following tasks | 15 | "List 5 points in markdown, each under 20 words" |
| Creative generation | 15 | "Write a product description for X" |
| Edge cases / adversarial | 10 | Ambiguous prompts, contradictory instructions |
| **Total** | **70** | |

### 3.2 Test Case Format

```json
{
  "test_id": "TC-001",
  "category": "multi_step_reasoning",
  "user_prompt": "A train travels at 60 km/h for 2 hours, then at 80 km/h for 1.5 hours. What is the average speed for the entire journey?",
  "expected_output_format": "number with units",
  "reference_answer": "68 km/h",
  "difficulty": "medium",
  "evaluation_criteria": {
    "correctness": "Must show correct calculation: (120+120)/3.5 = 68.57 km/h",
    "completeness": "Should show intermediate steps",
    "instruction_following": "N/A"
  }
}
```

---

## 4. Prompt Definitions

### 4.1 v1 — Simple Role Definition

```
You are a helpful assistant. Answer the user's question clearly and accurately.
```

### 4.2 v2 — CoT + Few-Shot

```
You are a helpful assistant. Answer the user's question clearly and accurately.

## Reasoning Approach
Before answering, think step-by-step:
1. Identify what the question is asking
2. List the relevant facts and constraints
3. Work through the logic systematically
4. Verify your answer makes sense

## Examples

**User**: If I buy 3 apples at $2 each and get a 10% discount, how much do I pay?
**Assistant**:
Let me work through this step-by-step:
1. Cost before discount: 3 apples x $2 = $6
2. Discount amount: $6 x 10% = $0.60
3. Final cost: $6 - $0.60 = $5.40

Answer: $5.40

**User**: List the pros and cons of remote work. Keep it to 3 points each.
**Assistant**:
**Pros:**
- No commute saves time and money
- Flexible schedule improves work-life balance
- Access to a wider talent pool for employers

**Cons:**
- Reduced face-to-face collaboration
- Potential for isolation and disconnection
- Blurred boundaries between work and personal life

**User**: {user_question}
**Assistant**:
```

---

## 5. Evaluation Pipeline

### 5.1 Architecture

```
┌─────────────────────────────────────────────────┐
│                  Test Runner                      │
│                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐ │
│  │ Test Case │──>│ Variant  │──>│ LLM API Call │ │
│  │  Loader   │   │ Router   │   │  (per prompt)│ │
│  └──────────┘   └──────────┘   └──────┬───────┘ │
│                                        │         │
│                                        v         │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐ │
│  │ Results  │<──│ Stat     │<──│  LLM Judge   │ │
│  │ Database │   │ Analyzer │   │  (Scoring)   │ │
│  └──────────┘   └──────────┘   └──────────────┘ │
└─────────────────────────────────────────────────┘
```

### 5.2 Implementation

```python
import json
import time
import statistics
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


class Dimension(str, Enum):
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    INSTRUCTION_FOLLOWING = "instruction_following"
    COHERENCE = "coherence"
    EFFICIENCY = "efficiency"


@dataclass
class TestCase:
    test_id: str
    category: str
    user_prompt: str
    reference_answer: Optional[str] = None
    difficulty: str = "medium"
    evaluation_criteria: dict = field(default_factory=dict)


@dataclass
class ScoredResult:
    test_id: str
    variant: str
    model_response: str
    scores: dict  # dimension -> 1-5 score
    composite_score: float
    latency_ms: float
    token_count: int
    judge_model: str
    timestamp: str


# Weight configuration
DIMENSION_WEIGHTS = {
    Dimension.CORRECTNESS: 0.30,
    Dimension.COMPLETENESS: 0.25,
    Dimension.INSTRUCTION_FOLLOWING: 0.20,
    Dimension.COHERENCE: 0.15,
    Dimension.EFFICIENCY: 0.10,
}


JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator. Score the following AI response on a scale of 1-5 for each dimension.

## User Prompt
{user_prompt}

## Reference Answer (if available)
{reference_answer}

## AI Response to Evaluate
{model_response}

## Evaluation Criteria
{evaluation_criteria}

## Scoring Rubric
- 1: Very poor - fails to address the question or is fundamentally wrong
- 2: Poor - partially addresses the question but has major errors
- 3: Adequate - addresses the question with minor issues
- 4: Good - fully addresses the question with clear reasoning
- 5: Excellent - comprehensive, accurate, well-structured response

## Output Format
Return ONLY a JSON object with scores for each dimension:
{{
  "correctness": <1-5>,
  "completeness": <1-5>,
  "instruction_following": <1-5>,
  "coherence": <1-5>,
  "efficiency": <1-5>,
  "reasoning": "<brief justification>"
}}"""


def compute_composite_score(scores: dict) -> float:
    """Compute weighted composite score from dimension scores."""
    total = 0.0
    for dim, weight in DIMENSION_WEIGHTS.items():
        total += scores.get(dim.value, 0) * weight
    return round(total, 3)


def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4") -> tuple[str, float, int]:
    """
    Call the LLM API. Returns (response_text, latency_ms, token_count).

    Replace this with your actual API client (OpenAI, Anthropic, etc.).
    """
    import openai  # or your preferred client

    start = time.perf_counter()
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,  # Deterministic for fair comparison
        max_tokens=1024,
    )
    latency_ms = (time.perf_counter() - start) * 1000

    text = response.choices[0].message.content
    tokens = response.usage.total_tokens
    return text, latency_ms, tokens


def judge_response(
    test_case: TestCase,
    model_response: str,
    judge_model: str = "gpt-4o",
) -> dict:
    """Use an LLM judge to score a response across all dimensions."""
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        user_prompt=test_case.user_prompt,
        reference_answer=test_case.reference_answer or "N/A",
        model_response=model_response,
        evaluation_criteria=json.dumps(test_case.evaluation_criteria, indent=2),
    )

    raw, _, _ = call_llm(
        system_prompt="You are a strict, impartial evaluator. Output only valid JSON.",
        user_prompt=judge_prompt,
        model=judge_model,
    )

    # Parse JSON from response, handling potential markdown wrapping
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]

    return json.loads(cleaned)


def run_single_test(
    test_case: TestCase,
    variant: str,
    system_prompts: dict,
    target_model: str = "gpt-4",
    judge_model: str = "gpt-4o",
) -> ScoredResult:
    """Run a single test case against one prompt variant."""
    system_prompt = system_prompts[variant]

    response, latency_ms, token_count = call_llm(
        system_prompt=system_prompt,
        user_prompt=test_case.user_prompt,
        model=target_model,
    )

    scores = judge_response(test_case, response, judge_model)

    return ScoredResult(
        test_id=test_case.test_id,
        variant=variant,
        model_response=response,
        scores=scores,
        composite_score=compute_composite_score(scores),
        latency_ms=latency_ms,
        token_count=token_count,
        judge_model=judge_model,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
```

---

## 6. Statistical Analysis

### 6.1 Analysis Methods

```python
import numpy as np
from scipy import stats
from dataclasses import dataclass


@dataclass
class ABTestResult:
    metric: str
    v1_mean: float
    v2_mean: float
    v1_std: float
    v2_std: float
    v1_n: int
    v2_n: int
    mean_difference: float
    effect_size_cohens_d: float
    t_statistic: float
    p_value: float
    confidence_interval: tuple  # 95% CI for the difference
    is_significant: bool
    interpretation: str


def welch_t_test(v1_scores: list[float], v2_scores: list[float], alpha: float = 0.05) -> ABTestResult:
    """
    Perform Welch's t-test (does not assume equal variances).
    This is preferred over Student's t-test for prompt comparison
    because variance between prompt versions may differ substantially.
    """
    v1 = np.array(v1_scores)
    v2 = np.array(v2_scores)

    n1, n2 = len(v1), len(v2)
    m1, m2 = v1.mean(), v2.mean()
    s1, s2 = v1.std(ddof=1), v2.std(ddof=1)

    # Welch's t-test
    t_stat, p_value = stats.ttest_ind(v1, v2, equal_var=False)

    # Cohen's d (pooled standard deviation)
    pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    cohens_d = (m2 - m1) / pooled_std if pooled_std > 0 else 0.0

    # 95% Confidence interval for difference in means
    se = np.sqrt(s1**2 / n1 + s2**2 / n2)
    df = (s1**2 / n1 + s2**2 / n2)**2 / (
        (s1**2 / n1)**2 / (n1 - 1) + (s2**2 / n2)**2 / (n2 - 1)
    )
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    diff = m2 - m1
    ci_lower = diff - t_crit * se
    ci_upper = diff + t_crit * se

    # Interpret effect size
    if abs(cohens_d) < 0.2:
        effect_desc = "negligible"
    elif abs(cohens_d) < 0.5:
        effect_desc = "small"
    elif abs(cohens_d) < 0.8:
        effect_desc = "medium"
    else:
        effect_desc = "large"

    is_sig = p_value < alpha
    if is_sig:
        direction = "higher" if diff > 0 else "lower"
        interpretation = (
            f"v2 scores are significantly {direction} than v1 "
            f"(p={p_value:.4f}, d={cohens_d:.3f}, {effect_desc} effect). "
            f"The 95% CI for the difference is [{ci_lower:.3f}, {ci_upper:.3f}]."
        )
    else:
        interpretation = (
            f"No statistically significant difference (p={p_value:.4f}). "
            f"Effect size: {effect_desc} (d={cohens_d:.3f}). "
            f"Consider increasing sample size if the effect is practically meaningful."
        )

    return ABTestResult(
        metric="composite_score",
        v1_mean=round(m1, 4),
        v2_mean=round(m2, 4),
        v1_std=round(s1, 4),
        v2_std=round(s2, 4),
        v1_n=n1,
        v2_n=n2,
        mean_difference=round(diff, 4),
        effect_size_cohens_d=round(cohens_d, 4),
        t_statistic=round(t_stat, 4),
        p_value=round(p_value, 6),
        confidence_interval=(round(ci_lower, 4), round(ci_upper, 4)),
        is_significant=is_sig,
        interpretation=interpretation,
    )


def mann_whitney_test(v1_scores: list[float], v2_scores: list[float], alpha: float = 0.05) -> dict:
    """
    Non-parametric alternative. Use when scores are ordinal (Likert scale)
    or when the normality assumption is violated.
    """
    stat, p_value = stats.mannwhitneyu(v1_scores, v2_scores, alternative='two-sided')

    # Effect size (rank-biserial correlation)
    n1, n2 = len(v1_scores), len(v2_scores)
    effect_size = 1 - (2 * stat) / (n1 * n2)

    return {
        "test": "Mann-Whitney U",
        "U_statistic": round(stat, 4),
        "p_value": round(p_value, 6),
        "effect_size_rank_biserial": round(effect_size, 4),
        "is_significant": p_value < alpha,
    }


def bootstrap_confidence_interval(
    v1_scores: list[float],
    v2_scores: list[float],
    n_bootstrap: int = 10000,
    ci_level: float = 0.95,
) -> dict:
    """
    Bootstrap resampling for confidence interval of the mean difference.
    More robust than parametric methods for small samples or non-normal data.
    """
    rng = np.random.default_rng(seed=42)
    v1 = np.array(v1_scores)
    v2 = np.array(v2_scores)

    diffs = []
    for _ in range(n_bootstrap):
        boot_v1 = rng.choice(v1, size=len(v1), replace=True)
        boot_v2 = rng.choice(v2, size=len(v2), replace=True)
        diffs.append(boot_v2.mean() - boot_v1.mean())

    alpha = 1 - ci_level
    ci_lower = np.percentile(diffs, 100 * alpha / 2)
    ci_upper = np.percentile(diffs, 100 * (1 - alpha / 2))

    return {
        "method": "Bootstrap (percentile)",
        "n_bootstrap": n_bootstrap,
        "mean_difference": round(np.mean(diffs), 4),
        "ci_level": ci_level,
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "contains_zero": ci_lower <= 0 <= ci_upper,
    }


def per_dimension_analysis(results: list[ScoredResult]) -> dict:
    """Run statistical tests on each evaluation dimension separately."""
    v1_by_dim = {}
    v2_by_dim = {}

    for r in results:
        target = v1_by_dim if r.variant == "v1" else v2_by_dim
        for dim, score in r.scores.items():
            if dim == "reasoning":
                continue
            target.setdefault(dim, []).append(score)

    dimensions = set(v1_by_dim.keys()) & set(v2_by_dim.keys())
    analysis = {}

    for dim in dimensions:
        result = welch_t_test(v1_by_dim[dim], v2_by_dim[dim])
        analysis[dim] = {
            "v1_mean": result.v1_mean,
            "v2_mean": result.v2_mean,
            "mean_difference": result.mean_difference,
            "p_value": result.p_value,
            "effect_size": result.effect_size_cohens_d,
            "significant": result.is_significant,
        }

    return analysis


def category_analysis(results: list[ScoredResult], test_cases: dict[str, TestCase]) -> dict:
    """Analyze performance by test category."""
    v1_by_cat = {}
    v2_by_cat = {}

    for r in results:
        cat = test_cases[r.test_id].category
        target = v1_by_cat if r.variant == "v1" else v2_by_cat
        target.setdefault(cat, []).append(r.composite_score)

    categories = set(v1_by_cat.keys()) & set(v2_by_cat.keys())
    analysis = {}

    for cat in categories:
        if len(v1_by_cat[cat]) >= 5 and len(v2_by_cat[cat]) >= 5:
            result = welch_t_test(v1_by_cat[cat], v2_by_cat[cat])
            analysis[cat] = {
                "v1_mean": result.v1_mean,
                "v2_mean": result.v2_mean,
                "p_value": result.p_value,
                "effect_size": result.effect_size_cohens_d,
                "significant": result.is_significant,
                "winner": "v2" if result.mean_difference > 0 and result.is_significant else
                          "v1" if result.mean_difference < 0 and result.is_significant else "tie",
            }

    return analysis
```

### 6.2 Multiple Comparison Correction

When testing across multiple dimensions or categories, apply Bonferroni or Benjamini-Hochberg correction:

```python
def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    """
    Benjamini-Hochberg procedure for controlling False Discovery Rate (FDR).
    Less conservative than Bonferroni when many tests are performed.
    """
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    thresholds = [(i + 1) / n * alpha for i in range(n)]

    # Find the largest k where p(k) <= threshold(k)
    significant = [False] * n
    max_k = -1
    for k in range(n):
        if sorted_p[k] <= thresholds[k]:
            max_k = k

    if max_k >= 0:
        for k in range(max_k + 1):
            significant[sorted_indices[k]] = True

    return significant
```

---

## 7. Reporting

### 7.1 Report Generation

```python
def generate_report(
    results: list[ScoredResult],
    test_cases: dict[str, TestCase],
    alpha: float = 0.05,
) -> str:
    """Generate a comprehensive A/B test report."""

    v1_scores = [r.composite_score for r in results if r.variant == "v1"]
    v2_scores = [r.composite_score for r in results if r.variant == "v2"]

    overall = welch_t_test(v1_scores, v2_scores, alpha)
    bootstrap = bootstrap_confidence_interval(v1_scores, v2_scores)
    mw_test = mann_whitney_test(v1_scores, v2_scores, alpha)
    dim_analysis = per_dimension_analysis(results)
    cat_analysis = category_analysis(results, test_cases)

    v1_latency = [r.latency_ms for r in results if r.variant == "v1"]
    v2_latency = [r.latency_ms for r in results if r.variant == "v2"]
    v1_tokens = [r.token_count for r in results if r.variant == "v1"]
    v2_tokens = [r.token_count for r in results if r.variant == "v2"]

    report = f"""# System Prompt A/B Test Report

## Summary

| Metric | v1 (Control) | v2 (Treatment) | Difference |
|--------|-------------|----------------|------------|
| N | {overall.v1_n} | {overall.v2_n} | - |
| Mean Composite Score | {overall.v1_mean:.3f} | {overall.v2_mean:.3f} | {overall.mean_difference:+.3f} |
| Std Dev | {overall.v1_std:.3f} | {overall.v2_std:.3f} | - |
| Mean Latency (ms) | {statistics.mean(v1_latency):.0f} | {statistics.mean(v2_latency):.0f} | {statistics.mean(v2_latency) - statistics.mean(v1_latency):+.0f} |
| Mean Tokens | {statistics.mean(v1_tokens):.0f} | {statistics.mean(v2_tokens):.0f} | {statistics.mean(v2_tokens) - statistics.mean(v1_tokens):+.0f} |

## Statistical Tests

### Welch's t-test (Primary)
- t-statistic: {overall.t_statistic}
- p-value: {overall.p_value}
- 95% CI for difference: [{overall.confidence_interval[0]}, {overall.confidence_interval[1]}]
- Cohen's d: {overall.effect_size_cohens_d}
- **Significant at alpha={alpha}: {overall.is_significant}**

### Mann-Whitney U (Non-parametric confirmation)
- U-statistic: {mw_test['U_statistic']}
- p-value: {mw_test['p_value']}
- Rank-biserial effect size: {mw_test['effect_size_rank_biserial']}

### Bootstrap 95% CI
- Mean difference: {bootstrap['mean_difference']}
- CI: [{bootstrap['ci_lower']}, {bootstrap['ci_upper']}]
- Contains zero: {bootstrap['contains_zero']}

## Per-Dimension Breakdown

| Dimension | v1 Mean | v2 Mean | Diff | p-value | Effect Size | Significant |
|-----------|---------|---------|------|---------|-------------|-------------|
"""

    for dim, data in sorted(dim_analysis.items()):
        sig_marker = "**Yes**" if data["significant"] else "No"
        report += f"| {dim} | {data['v1_mean']:.2f} | {data['v2_mean']:.2f} | {data['mean_difference']:+.2f} | {data['p_value']:.4f} | {data['effect_size']:.3f} | {sig_marker} |\n"

    report += f"""
## Per-Category Analysis

| Category | v1 Mean | v2 Mean | p-value | Effect Size | Winner |
|----------|---------|---------|---------|-------------|--------|
"""

    for cat, data in sorted(cat_analysis.items()):
        report += f"| {cat} | {data['v1_mean']:.2f} | {data['v2_mean']:.2f} | {data['p_value']:.4f} | {data['effect_size']:.3f} | {data['winner']} |\n"

    report += f"""
## Interpretation

{overall.interpretation}

## Recommendation

"""

    if overall.is_significant and overall.mean_difference > 0:
        report += (
            "**Deploy v2.** The chain-of-thought and few-shot additions produce "
            "statistically significant improvements in output quality. "
            f"The effect size ({overall.effect_size_cohens_d:.3f}) indicates "
            "a practically meaningful improvement."
        )
    elif overall.is_significant and overall.mean_difference < 0:
        report += (
            "**Keep v1.** v2 performs significantly worse. "
            "The added complexity may be introducing noise or confusion."
        )
    else:
        report += (
            "**No clear winner.** Consider: (1) increasing sample size, "
            "(2) examining category-specific results for targeted improvements, "
            "(3) evaluating whether the cost of longer prompts in v2 is justified "
            "by any observed trends."
        )

    return report
```

### 7.2 Sample Report Output

```
# System Prompt A/B Test Report

## Summary

| Metric | v1 (Control) | v2 (Treatment) | Difference |
|--------|-------------|----------------|------------|
| N | 60 | 60 | - |
| Mean Composite Score | 3.245 | 3.712 | +0.467 |
| Std Dev | 0.834 | 0.691 | - |
| Mean Latency (ms) | 1247 | 2134 | +887 |
| Mean Tokens | 187 | 412 | +225 |

## Statistical Tests

### Welch's t-test (Primary)
- t-statistic: -3.287
- p-value: 0.0013
- 95% CI for difference: [-0.753, -0.181]
- Cohen's d: 0.608
- Significant at alpha=0.05: True

## Interpretation

v2 scores are significantly higher than v1 (p=0.0013, d=0.608, medium effect).
The 95% CI for the difference is [-0.753, -0.181].

## Recommendation

Deploy v2. The chain-of-thought and few-shot additions produce statistically
significant improvements in output quality. The effect size (0.608) indicates
a practically meaningful improvement.
```

---

## 8. Cost and Latency Analysis

Prompt v2 is longer (CoT + examples), which increases token usage and latency. Factor this into the decision:

```python
def cost_benefit_analysis(results: list[ScoredResult], cost_per_1k_tokens: float = 0.03) -> dict:
    """Quantify the cost trade-off of the quality improvement."""
    v1_tokens = [r.token_count for r in results if r.variant == "v1"]
    v2_tokens = [r.token_count for r in results if r.variant == "v2"]
    v1_scores = [r.composite_score for r in results if r.variant == "v1"]
    v2_scores = [r.composite_score for r in results if r.variant == "v2"]

    v1_cost = statistics.mean(v1_tokens) / 1000 * cost_per_1k_tokens
    v2_cost = statistics.mean(v2_tokens) / 1000 * cost_per_1k_tokens
    cost_increase = (v2_cost - v1_cost) / v1_cost * 100

    score_improvement = (statistics.mean(v2_scores) - statistics.mean(v1_scores)) / statistics.mean(v1_scores) * 100

    return {
        "v1_avg_cost_per_call": round(v1_cost, 4),
        "v2_avg_cost_per_call": round(v2_cost, 4),
        "cost_increase_pct": round(cost_increase, 1),
        "quality_improvement_pct": round(score_improvement, 1),
        "quality_per_dollar_v1": round(statistics.mean(v1_scores) / v1_cost, 2),
        "quality_per_dollar_v2": round(statistics.mean(v2_scores) / v2_cost, 2),
        "verdict": "v2 is cost-effective" if score_improvement > cost_increase else "v2 quality gain does not justify cost increase",
    }
```

---

## 9. Judge Reliability

To ensure the LLM judge itself is reliable:

### 9.1 Inter-Rater Agreement

```python
def compute_inter_rater_agreement(
    scores_judge_a: list[dict],
    scores_judge_b: list[dict],
) -> dict:
    """
    Run the same 20% of samples through two different judge models
    (e.g., GPT-4o and Claude) to check agreement.
    """
    from sklearn.metrics import cohen_kappa_score

    a_scores = [s["correctness"] for s in scores_judge_a]
    b_scores = [s["correctness"] for s in scores_judge_b]

    kappa = cohen_kappa_score(a_scores, b_scores, weights="quadratic")

    return {
        "quadratic_weighted_kappa": round(kappa, 4),
        "interpretation": (
            "Almost perfect" if kappa > 0.81 else
            "Substantial" if kappa > 0.61 else
            "Moderate" if kappa > 0.41 else
            "Fair" if kappa > 0.21 else
            "Slight" if kappa > 0 else
            "Poor"
        ),
        "recommendation": (
            "Judge agreement is acceptable." if kappa > 0.6 else
            "Judge agreement is low. Consider refining the rubric or using a different judge model."
        ),
    }
```

### 9.2 Positional Bias Check

Swap the order of v1/v2 outputs presented to the judge and check for bias:

```python
def check_positional_bias(results_forward: list, results_reversed: list) -> dict:
    """
    Run 20% of evaluations twice: once with v2 listed first, once with v1 first.
    Compare results to detect order bias in the judge.
    """
    fwd_v2_win_rate = sum(1 for r in results_forward if r.variant == "v2" and r.composite_score > 3.5) / len(results_forward)
    rev_v2_win_rate = sum(1 for r in results_reversed if r.variant == "v2" and r.composite_score > 3.5) / len(results_reversed)

    bias = abs(fwd_v2_win_rate - rev_v2_win_rate)

    return {
        "forward_v2_win_rate": round(fwd_v2_win_rate, 3),
        "reversed_v2_win_rate": round(rev_v2_win_rate, 3),
        "positional_bias": round(bias, 3),
        "bias_detected": bias > 0.05,
        "recommendation": "Use randomized presentation order." if bias > 0.05 else "No significant positional bias detected.",
    }
```

---

## 10. Full Orchestration Script

```python
import json
import os
from datetime import datetime


def run_ab_test(
    test_cases_path: str,
    output_dir: str,
    target_model: str = "gpt-4",
    judge_model: str = "gpt-4o",
    alpha: float = 0.05,
    cost_per_1k_tokens: float = 0.03,
):
    """End-to-end A/B test execution."""

    os.makedirs(output_dir, exist_ok=True)

    # Load test cases
    with open(test_cases_path) as f:
        raw_cases = json.load(f)
    test_cases = {tc["test_id"]: TestCase(**tc) for tc in raw_cases}

    # Define prompt variants
    system_prompts = {
        "v1": "You are a helpful assistant. Answer the user's question clearly and accurately.",
        "v2": """You are a helpful assistant. Answer the user's question clearly and accurately.

## Reasoning Approach
Before answering, think step-by-step:
1. Identify what the question is asking
2. List the relevant facts and constraints
3. Work through the logic systematically
4. Verify your answer makes sense

## Examples

**User**: If I buy 3 apples at $2 each and get a 10% discount, how much do I pay?
**Assistant**:
Let me work through this step-by-step:
1. Cost before discount: 3 apples x $2 = $6
2. Discount amount: $6 x 10% = $0.60
3. Final cost: $6 - $0.60 = $5.40

Answer: $5.40

**User**: {user_question}
**Assistant**:""",
    }

    # Run tests
    results = []
    for tc_id, tc in test_cases.items():
        variant = assign_variant(tc_id)
        print(f"Running {tc_id} with {variant}...")
        result = run_single_test(tc, variant, system_prompts, target_model, judge_model)
        results.append(result)

    # Save raw results
    results_path = os.path.join(output_dir, "results.jsonl")
    with open(results_path, "w") as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + "\n")

    # Generate report
    report = generate_report(results, test_cases, alpha)
    report_path = os.path.join(output_dir, "report.md")
    with open(report_path, "w") as f:
        f.write(report)

    # Cost analysis
    cost_analysis = cost_benefit_analysis(results, cost_per_1k_tokens)
    cost_path = os.path.join(output_dir, "cost_analysis.json")
    with open(cost_path, "w") as f:
        json.dump(cost_analysis, f, indent=2)

    print(f"\nResults saved to {output_dir}")
    print(f"Report: {report_path}")

    return results, report


if __name__ == "__main__":
    run_ab_test(
        test_cases_path="test_cases.json",
        output_dir=f"ab_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        target_model="gpt-4",
        judge_model="gpt-4o",
    )
```

---

## 11. Checklist Before Running

- [ ] Test cases cover all target categories with adequate sample size (50+ per group)
- [ ] Temperature is set to 0.0 for deterministic comparison
- [ ] Same model and parameters used for both variants (only system prompt differs)
- [ ] Judge model is different from the target model to avoid self-preference bias
- [ ] 20% of samples are evaluated by a second judge for inter-rater reliability
- [ ] Positional bias has been checked with order-swapped evaluations
- [ ] Multiple comparison correction applied when testing across dimensions/categories
- [ ] Both parametric (Welch's t) and non-parametric (Mann-Whitney) tests are run
- [ ] Bootstrap confidence intervals computed as a robustness check
- [ ] Cost and latency differences are documented alongside quality metrics
- [ ] Results are saved as structured data (JSONL) for reproducibility
- [ ] Random seed is fixed for reproducibility

---

## 12. Interpreting Results Decision Matrix

| Statistical Significance | Practical Significance (Effect Size) | Cost Impact | Decision |
|--------------------------|--------------------------------------|-------------|----------|
| Yes | Medium/Large (d >= 0.5) | Acceptable | **Deploy v2** |
| Yes | Medium/Large (d >= 0.5) | High | Deploy v2 if quality is critical; optimize prompt length |
| Yes | Small (d < 0.5) | Acceptable | Deploy v2 if cost is negligible |
| Yes | Small (d < 0.5) | High | Keep v1; improvement does not justify cost |
| No | Any | Any | Keep v1; insufficient evidence of improvement |
| No | Trend toward improvement | Low | Consider increasing sample size |

---

## 13. Limitations and Mitigations

| Limitation | Mitigation |
|-----------|------------|
| LLM judge may have biases | Use multiple judges, check inter-rater agreement, randomize presentation order |
| Temperature=0 may not reflect real usage | Run a separate test with temperature=0.7 to check if findings hold |
| Test set may not represent production traffic | Weight categories by actual usage distribution; periodically refresh test cases |
| Single evaluation per sample may be noisy | Each sample is evaluated once by the judge; for borderline results (p < 0.10), re-run with more samples |
| v2 uses more tokens, increasing cost | Factor cost-per-quality-point into the final decision (Section 8) |
| Prompt effects may vary by model | Re-run the test if the target model changes (e.g., GPT-4 -> GPT-5) |
