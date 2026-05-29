# A/B Testing Reference

## Experiment Lifecycle

```
Hypothesis → Design → Implement → Run → Analyze → Decide → Ship/Rollback
```

## Hypothesis Format

```
If we [change], then [metric] will [improve/decrease] by [amount],
because [reasoning].
```

**Example**: "If we move the CTA button above the fold, then click-through rate will increase by 15%, because users will see it without scrolling."

## Experiment Design

### Sample Size Calculation

```python
from scipy import stats
import numpy as np

def required_sample_size(
    baseline_rate: float,       # e.g., 0.10 (10% conversion)
    minimum_detectable_effect: float,  # e.g., 0.02 (2% absolute lift)
    alpha: float = 0.05,        # significance level
    power: float = 0.80,        # 1 - beta
) -> int:
    """Calculate required sample size per variant."""
    p1 = baseline_rate
    p2 = baseline_rate + minimum_detectable_effect

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    n = ((z_alpha * np.sqrt(2 * p1 * (1 - p1)) +
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) **
         2 / (p2 - p1) ** 2)

    return int(np.ceil(n))

# Example: 10% baseline, want to detect 2% lift
n = required_sample_size(0.10, 0.02)
print(f"Need {n} users per variant")
```

### Duration Estimation

```
Duration (days) = Sample Size / Daily Traffic

Example:
  Sample size needed: 3,800 per variant
  Daily traffic: 1,000
  Variants: 2 (control + treatment)
  Duration = 3,800 / 1,000 = ~4 days (run at least 7 for weekly cycles)
```

## Implementation with Feature Flags

```typescript
interface Experiment {
  id: string;
  flag: string;
  variants: Variant[];
  metrics: Metric[];
  startDate: Date;
  endDate: Date;
}

interface Variant {
  key: string;
  weight: number;  // percentage of traffic
  payload?: any;
}

interface Metric {
  name: string;
  type: 'conversion' | 'revenue' | 'duration' | 'count';
  isPrimary: boolean;
}

// Track exposure
function trackExposure(userId: string, experiment: Experiment, variant: string) {
  analytics.track('experiment_exposed', {
    experiment_id: experiment.id,
    variant,
    user_id: userId,
    timestamp: new Date().toISOString(),
  });
}

// Track conversion
function trackConversion(userId: string, experiment: Experiment, metric: string, value?: number) {
  analytics.track('experiment_conversion', {
    experiment_id: experiment.id,
    metric,
    value,
    user_id: userId,
    timestamp: new Date().toISOString(),
  });
}
```

## Statistical Analysis

### Frequentist Approach (Chi-Square Test)

```python
from scipy.stats import chi2_contingency

def analyze_ab_test(control_conversions, control_visitors,
                    treatment_conversions, treatment_visitors):
    """Analyze A/B test results using chi-square test."""
    table = [
        [control_conversions, control_visitors - control_conversions],
        [treatment_conversions, treatment_visitors - treatment_conversions],
    ]

    chi2, p_value, dof, expected = chi2_contingency(table)

    control_rate = control_conversions / control_visitors
    treatment_rate = treatment_conversions / treatment_visitors
    lift = (treatment_rate - control_rate) / control_rate * 100

    return {
        "control_rate": f"{control_rate:.2%}",
        "treatment_rate": f"{treatment_rate:.2%}",
        "lift": f"{lift:+.1f}%",
        "p_value": p_value,
        "significant": p_value < 0.05,
    }
```

### Bayesian Approach

```python
import numpy as np

def bayesian_ab_test(control_success, control_total,
                     treatment_success, treatment_total,
                     simulations=100000):
    """Estimate probability that treatment beats control."""
    # Beta posterior for each variant
    control_samples = np.random.beta(
        control_success + 1,
        control_total - control_success + 1,
        simulations,
    )
    treatment_samples = np.random.beta(
        treatment_success + 1,
        treatment_total - treatment_success + 1,
        simulations,
    )

    prob_treatment_better = np.mean(treatment_samples > control_samples)
    expected_lift = np.mean((treatment_samples - control_samples) / control_samples)

    return {
        "prob_treatment_better": f"{prob_treatment_better:.1%}",
        "expected_lift": f"{expected_lift:+.1%}",
    }
```

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Peeking | Checking results before reaching sample size | Pre-commit to duration, use sequential testing |
| Novelty effect | Users try new feature just because it's new | Run longer, analyze trend over time |
| Sample ratio mismatch | Unequal traffic split | Monitor split ratio daily |
| Multiple testing | Testing many metrics inflates false positives | Use Bonferroni correction, pre-register metrics |
| Survivorship bias | Only measuring users who completed flow | Track all exposed users |
| Interaction effects | Two experiments affect each other | Use mutually exclusive layers |

## Decision Framework

```
If p-value < 0.05 AND lift > MDE:
  → Ship the treatment

If p-value < 0.05 AND lift < 0:
  → Keep control, investigate why treatment hurt

If p-value >= 0.05:
  → Inconclusive. Options:
     - Run longer if close to significance
     - Accept that effect is smaller than MDE
     - Try a bolder change
```

## Reporting Template

```markdown
## Experiment: [Name]

**Hypothesis**: [Statement]
**Duration**: [Start] to [End] ([N] days)
**Sample**: [N] users per variant

### Results

| Metric | Control | Treatment | Lift | p-value | Significant |
|--------|---------|-----------|------|---------|-------------|
| Primary: conversion | 10.2% | 12.1% | +18.6% | 0.003 | Yes |
| Secondary: revenue | $45.20 | $47.80 | +5.8% | 0.12 | No |

### Decision
Ship treatment. Primary metric shows statistically significant improvement.

### Follow-up
- Investigate revenue lift (not significant yet)
- Monitor for novelty effect over next 2 weeks
```
