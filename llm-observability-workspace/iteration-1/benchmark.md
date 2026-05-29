# Skill Benchmark: llm-observability

**Model**: claude-sonnet-4-6 | **Date**: 2026-05-29 | **Evals**: 3 (1 run each)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% (15/15) | 93.3% (14/15) | **+6.7%** |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill | Gap |
|------|------------|---------------|-----|
| eval-0: Context degradation monitoring | 5/5 (100%) | 4/5 (80%) | **Missing MTTD target** |
| eval-1: Cost/loop detection | 5/5 (100%) | 5/5 (100%) | None |
| eval-2: Unified dashboard design | 5/5 (100%) | 5/5 (100%) | None |

## Analysis

**The only discriminating eval across all 5 skills.** The skill's explicit MTTD target guidance ensures this critical operational metric is always addressed.

**Key differentiation in eval-0:**
- with_skill: Sets explicit MTTD targets (loops 1min, context overflow 5min, hallucination 1hr)
- without_skill: Defines processing latency per layer but no explicit Mean Time to Detect target

**Qualitative advantages:**
- OpenTelemetry integration from skill's references
- Context-lens patterns (beginning-anchored, tool burial, instruction drift)
- Structured trace schemas with JSON Schema
- 28 metrics across 6 categories vs ad-hoc metric lists
