# Skill Benchmark: prompt-cicd

**Model**: claude-sonnet-4-6 | **Date**: 2026-05-29 | **Evals**: 3 (1 run each)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% (15/15) | 100% (15/15) | +0% |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill | Gap |
|------|------------|---------------|-----|
| eval-0: Prompt inventory & versioning | 5/5 (100%) | 5/5 (100%) | None |
| eval-1: A/B prompt comparison | 5/5 (100%) | 5/5 (100%) | None |
| eval-2: CI/CD pipeline setup | 5/5 (100%) | 5/5 (100%) | None |

## Analysis

All assertions are **non-discriminating**. The base model has strong CI/CD knowledge.

**Qualitative differences (with_skill is better):**
- PromptRollback class with symlink management (vs simple bash script)
- quality_monitor.py with hourly scheduled checks (vs manual monitoring)
- PromptLoader module for unified prompt loading
- Path-scoped triggers with matrix sharding by prompt type
- Pre-commit lint hook with hardcoded secret detection

**Recommendation:** Add discriminating assertions like `has_hourly_quality_monitoring`, `has_prompt_linter_with_secret_detection`, `has_matrix_sharding`.
