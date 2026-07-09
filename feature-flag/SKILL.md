---
name: feature-flag
description: |
  【功能开关】设计和实现功能开关系统，支持灰度发布、A/B测试、动态配置、紧急降级。

  触发时机：
  - 用户要求"功能开关"、"灰度发布"、"Feature Flag"
  - 需要控制功能的上线节奏
  - 需要做 A/B 测试
category: development
---

# Feature Flag — 功能开关

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

设计和实现功能开关系统，支持灰度发布和 A/B 测试。

## Workflow

1. **创建开关** — 定义 key、类型、默认值
2. **配置规则** — 灰度百分比、定向规则、用户白名单
3. **集成代码** — 业务逻辑中读取开关状态
4. **灰度发布** — 10% → 50% → 100%，逐步放量
5. **清理** — 稳定后删除开关，硬编码为 true

## 开关类型

| 类型 | 用途 | 生命周期 |
|------|------|----------|
| 发布开关 | 控制功能发布节奏 | 短期 |
| 实验开关 | A/B 测试 | 中期 |
| 运维开关 | 紧急降级 | 长期 |
| 权限开关 | 按用户/租户控制 | 长期 |

## 核心实现

### 评估逻辑

```python
class FeatureFlagService:
    def evaluate(self, flag_key: str, user_id: str, context: dict = None) -> bool:
        flag = self.get_flag(flag_key)
        if not flag or not flag.enabled:
            return flag.default_value if flag else False

        # 用户级覆盖
        override = self.get_override(flag_key, user_id)
        if override is not None:
            return override.value

        # 定向规则
        if flag.targeting_rules and self._match_targeting(flag.targeting_rules, user_id, context):
            return True

        # 灰度百分比（一致性哈希）
        if flag.rollout_percentage < 100:
            hash_val = int(hashlib.md5(f"{flag_key}:{user_id}".encode()).hexdigest()[:8], 16) % 100
            return hash_val < flag.rollout_percentage

        return True
```

### 数据模型

```sql
CREATE TABLE feature_flags (
    id                BIGINT PRIMARY KEY AUTO_INCREMENT,
    key               VARCHAR(100) NOT NULL UNIQUE,
    name              VARCHAR(200) NOT NULL,
    type              VARCHAR(20) NOT NULL,  -- release/experiment/ops/permission
    enabled           BOOLEAN DEFAULT FALSE,
    rollout_percentage INT DEFAULT 100,
    targeting_rules   JSON,
    default_value     BOOLEAN DEFAULT FALSE
);
```

### 前端集成

```typescript
function useFeatureFlag(flagKey: string): boolean {
  const [enabled, setEnabled] = useState(false);
  useEffect(() => {
    fetch(`/api/v1/flags/${flagKey}/evaluate`, {
      method: 'POST',
      body: JSON.stringify({ user_id: getCurrentUserId() })
    }).then(res => res.json()).then(data => setEnabled(data.value));
  }, [flagKey]);
  return enabled;
}
```

## 定向规则

```json
{
  "user_ids": ["user-1", "user-2"],
  "attributes": {
    "plan": { "operator": "in", "values": ["premium", "enterprise"] },
    "country": { "operator": "eq", "value": "CN" }
  }
}
```

## Example

```
用户: 为新支付流程创建功能开关，先灰度 10% 用户

输出:
1. INSERT INTO feature_flags (key, name, type, enabled, rollout_percentage)
   VALUES ('new_payment_flow', '新支付流程', 'release', true, 10);
2. 业务代码: if flags.evaluate('new_payment_flow', user_id): use_new_flow()
3. 监控错误率，逐步扩大到 50% → 100%
```

## 参考

- 定向规则: [references/targeting-rules.md](references/targeting-rules.md)
- A/B 测试: [references/ab-testing.md](references/ab-testing.md)
