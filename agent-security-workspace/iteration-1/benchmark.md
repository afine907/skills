# Skill Benchmark: agent-security

**Model**: claude-sonnet-4-6 | **Date**: 2026-05-29 | **Evals**: 3 (1 run each)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% (15/15) | 100% (15/15) | +0% |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill | Gap |
|------|------------|---------------|-----|
| eval-0: Threat model & permissions | 5/5 (100%) | 5/5 (100%) | None |
| eval-1: Injection defense layers | 5/5 (100%) | 5/5 (100%) | None |
| eval-2: Security audit checklist | 5/5 (100%) | 5/5 (100%) | None |

## Analysis

All assertions are **non-discriminating**. The base model has strong security knowledge.

**Qualitative differences (with_skill is better):**
- Uses Agent-specific threat taxonomy (6 categories) vs generic STRIDE
- 4-tier permission model from skill's references (Autonomous/Confirm/Approve/Deny)
- HITL gate patterns with concrete Python implementation code
- 4-layer injection defense with code examples from skill's references
- 20+ red team test cases organized by attack category

**Recommendation:** Add discriminating assertions like `has_agent_specific_threat_categories` (not STRIDE), `has_hitl_code_implementation`, `has_injection_defense_code_example`.
