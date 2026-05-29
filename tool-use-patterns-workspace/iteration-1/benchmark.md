# Skill Benchmark: tool-use-patterns

**Model**: claude-sonnet-4-6
**Date**: 2026-05-29
**Evals**: 0, 1, 2 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 74% ± 12% | +0.26 |
| Time | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Tokens | 0 ± 0 | 0 ± 0 | +0 |

## Per-Eval Breakdown

| Eval | With Skill | Without Skill | Gap |
|------|------------|---------------|-----|
| eval-0: GitHub API defensive tooling | 6/6 (100%) | 5/6 (83%) | Missing circuit breaker |
| eval-1: Destructive tool safety | 5/5 (100%) | 4/5 (80%) | Missing risk classification |
| eval-2: Saga rollback pattern | 5/5 (100%) | 3/5 (60%) | Missing step logging + idempotency |

## Notes

- with_skill consistently achieves 100% pass rate across all 3 evals
- without_skill misses critical patterns: circuit breaker (eval-0), risk classification (eval-1), step logging + idempotency (eval-2)
- Biggest gap in eval-2 (saga rollback): with_skill 100% vs without_skill 60% — the skill's composition patterns and idempotency guidance are the key differentiators

## Key Differentiators

The skill adds the most value in these areas:
1. **Circuit breaker pattern** — without_skill never implements this; the skill provides a code-level (not prompt-level) template
2. **Risk classification** — without_skill relies on regex intent matching; the skill's 4-tier classification (read-only/reversible-write/irreversible-write/dangerous) is more systematic
3. **Structured step logging** — without_skill has no execution ledger; the skill's composition patterns include saga with full state tracking
4. **Idempotency keys** — without_skill mentions but doesn't implement; the skill includes concrete key generation and caching patterns
