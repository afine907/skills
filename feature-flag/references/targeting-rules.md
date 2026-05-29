# Feature Flag Targeting Rules

## Rule Structure

A targeting rule defines who sees a feature variation based on user attributes.

```json
{
  "flag": "new-checkout",
  "rules": [
    {
      "conditions": [
        { "attribute": "country", "operator": "in", "values": ["US", "CA"] },
        { "attribute": "plan", "operator": "eq", "values": ["premium"] }
      ],
      "variation": "enabled",
      "percentage": 100
    }
  ],
  "defaultVariation": "disabled"
}
```

## Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `country eq "US"` |
| `neq` | Not equals | `plan neq "free"` |
| `in` | In list | `country in ["US", "CA", "UK"]` |
| `not_in` | Not in list | `role not_in ["admin", "tester"]` |
| `gt` / `gte` | Greater than (or equal) | `age gte 18` |
| `lt` / `lte` | Less than (or equal) | `account_age lte 30` |
| `contains` | String contains | `email contains "@company.com"` |
| `starts_with` | String prefix | `user_id starts_with "test_"` |
| `regex` | Regular expression | `email regex ".*@example\.com"` |
| `exists` | Attribute is present | `beta_key exists` |
| `semver_gte` | Semantic version >= | `app_version semver_gte "2.1.0"` |

## Percentage Rollouts

### Consistent Hashing

Use a deterministic hash to ensure the same user always gets the same variation.

```python
import hashlib

def get_variation(user_id: str, flag_key: str, percentage: int) -> str:
    """Deterministically assign a user to a variation."""
    hash_input = f"{flag_key}:{user_id}"
    hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
    bucket = hash_value % 10000  # 0.01% precision

    if bucket < percentage * 100:
        return "enabled"
    return "disabled"
```

### Gradual Rollout Strategy

```
Day 1:  1%   (canary - catch critical bugs)
Day 3:  5%   (early adopters)
Day 7:  25%  (broader validation)
Day 14: 50%  (half traffic)
Day 21: 100% (full rollout)
```

## Multi-Variate Flags

```json
{
  "flag": "pricing-display",
  "variations": [
    { "key": "control", "value": "original" },
    { "key": "variant-a", "value": "with-savings" },
    { "key": "variant-b", "value": "comparison-table" }
  ],
  "rules": [
    {
      "conditions": [{ "attribute": "country", "operator": "eq", "values": ["US"] }],
      "distribution": [
        { "variation": "control", "percentage": 34 },
        { "variation": "variant-a", "percentage": 33 },
        { "variation": "variant-b", "percentage": 33 }
      ]
    }
  ],
  "defaultVariation": "control"
}
```

## Segments

Reusable groups of users for targeting.

```json
{
  "segments": {
    "internal-testers": {
      "description": "Company employees for dogfooding",
      "rules": [
        {
          "conditions": [
            { "attribute": "email", "operator": "ends_with", "values": ["@company.com"] }
          ]
        }
      ]
    },
    "beta-users": {
      "description": "Opted-in beta program participants",
      "rules": [
        {
          "conditions": [
            { "attribute": "beta_opt_in", "operator": "eq", "values": ["true"] },
            { "attribute": "account_age_days", "operator": "gte", "values": [7] }
          ]
        }
      ]
    }
  }
}
```

### Using Segments in Rules

```json
{
  "flag": "new-dashboard",
  "rules": [
    {
      "conditions": [
        { "attribute": "segment", "operator": "in", "values": ["internal-testers"] }
      ],
      "variation": "enabled"
    },
    {
      "conditions": [
        { "attribute": "segment", "operator": "in", "values": ["beta-users"] },
        { "attribute": "country", "operator": "in", "values": ["US", "UK"] }
      ],
      "variation": "enabled",
      "percentage": 50
    }
  ],
  "defaultVariation": "disabled"
}
```

## Flag Prerequisites

A flag can depend on another flag being enabled first.

```json
{
  "flag": "new-checkout-flow",
  "prerequisites": [
    { "flag": "new-cart", "variation": "enabled" }
  ],
  "rules": [...]
}
```

## Evaluation Order

1. Check prerequisites - if any fail, return default
2. Evaluate rules top-to-bottom - first match wins
3. If no rules match, return default variation
4. User-level overrides take highest priority

## Best Practices

### Naming Attributes

```
Good:               Bad:
user.plan           plan
device.os           os
account.created_at  created_at
```

### Rule Complexity

- Keep rules simple (2-3 conditions max per rule)
- Use segments for complex groups
- Document the purpose of each rule
- Test rules with sample user payloads before deploying

### Common Attributes

| Attribute | Type | Source |
|-----------|------|--------|
| `user_id` | string | Authentication |
| `email` | string | Authentication |
| `country` | string | GeoIP / profile |
| `plan` | string | Subscription system |
| `account_age_days` | number | Registration date |
| `device.platform` | string | User agent |
| `app_version` | string | Client metadata |
| `custom_prop_*` | varies | Application-specific |
