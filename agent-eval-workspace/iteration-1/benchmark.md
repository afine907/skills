# Skill Benchmark: agent-eval

**Model**: claude-sonnet-4-6 | **Date**: 2026-05-29 | **Evals**: 3 (1 run each)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% (16/16) | 100% (16/16) | +0% |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill | Gap |
|------|------------|---------------|-----|
| eval-0: Hallucination eval design | 6/6 (100%) | 6/6 (100%) | None |
| eval-1: A/B comparison framework | 5/5 (100%) | 5/5 (100%) | None |
| eval-2: Tool accuracy eval | 5/5 (100%) | 5/5 (100%) | None |

## Analysis

All assertions are **non-discriminating** — both configurations pass 100%. The base model already has strong knowledge of evaluation methodology.

**Qualitative differences (with_skill is better):**
- 35 structured test cases vs 80+ templates (more actionable)
- Explicit LLM-as-Judge prompt templates with calibration protocol
- Domain-specific scoring rubrics (hallucination types, coherence metrics)
- Continuous monitoring plan with online metrics

**Recommendation:** Add discriminating assertions like `has_llm_as_judge_prompt_template`, `has_calibration_protocol`, `has_adversarial_test_generation` to better measure skill impact.
