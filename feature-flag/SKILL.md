---
name: feature-flag
description: |
  【功能开关】设计和实现功能开关（Feature Flag）系统，支持灰度发布、A/B测试、动态配置、紧急降级。

  触发时机：
  - 用户要求"功能开关"、"灰度发布"、"Feature Flag"
  - 需要控制功能的上线节奏
  - 需要做 A/B 测试

  提供设计方案和代码实现。
category: development
---

# Feature Flag — 功能开关技能

设计和实现功能开关系统，支持精细化的功能发布控制。


## Goal

设计和实现功能开关（Feature Flag）系统，支持灰度发布、A/B测试、动态配置、紧急降级

## Trigger

- 用户要求"功能开关"、"灰度发布"、"Feature Flag"
  - 需要控制功能的上线节奏
  - 需要做 A/B 测试

## 功能开关类型

| 类型 | 用途 | 生命周期 |
|------|------|----------|
| 发布开关 | 控制功能发布节奏 | 短期（发布后删除） |
| 实验开关 | A/B 测试 | 中期（实验结束删除） |
| 运维开关 | 紧急降级 | 长期 |
| 权限开关 | 按用户/租户控制 | 长期 |

## 设计方案

### 数据模型

```sql
CREATE TABLE feature_flags (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    key             VARCHAR(100) NOT NULL UNIQUE COMMENT '开关标识',
    name            VARCHAR(200) NOT NULL COMMENT '开关名称',
    description     TEXT COMMENT '开关说明',
    type            VARCHAR(20) NOT NULL COMMENT '类型: release/experiment/ops/permission',
    enabled         BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用',
    rollout_percentage INT DEFAULT 100 COMMENT '灰度比例(0-100)',
    targeting_rules JSON COMMENT '定向规则',
    default_value   BOOLEAN DEFAULT FALSE COMMENT '默认值',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (key),
    INDEX idx_type (type)
);

CREATE TABLE feature_flag_evaluations (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    flag_key        VARCHAR(100) NOT NULL,
    user_id         VARCHAR(100),
    value           BOOLEAN NOT NULL,
    reason          VARCHAR(50) COMMENT '评估原因: default/percentage/targeting/override',
    evaluated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_flag_user (flag_key, user_id)
);
```

### API 设计

```
GET    /api/v1/flags                    # 列表
GET    /api/v1/flags/{key}              # 详情
POST   /api/v1/flags                    # 创建
PUT    /api/v1/flags/{key}              # 更新
DELETE /api/v1/flags/{key}              # 删除
POST   /api/v1/flags/{key}/evaluate     # 评估开关状态
POST   /api/v1/flags/{key}/override     # 用户级覆盖
```

### 评估逻辑

```python
class FeatureFlagService:
    def evaluate(self, flag_key: str, user_id: str, context: dict = None) -> bool:
        """评估功能开关状态"""
        flag = self.get_flag(flag_key)
        
        if not flag:
            return False  # 开关不存在，默认关闭
        
        if not flag.enabled:
            return flag.default_value  # 开关未启用
        
        # 检查用户级覆盖
        override = self.get_override(flag_key, user_id)
        if override is not None:
            return override.value
        
        # 检查定向规则
        if flag.targeting_rules:
            if self._match_targeting(flag.targeting_rules, user_id, context):
                return True
        
        # 灰度百分比
        if flag.rollout_percentage < 100:
            hash_value = self._hash(flag_key, user_id)
            return hash_value < flag.rollout_percentage
        
        return True
    
    def _hash(self, flag_key: str, user_id: str) -> int:
        """一致性哈希，确保同一用户总是得到相同结果"""
        import hashlib
        hash_input = f"{flag_key}:{user_id}"
        hash_hex = hashlib.md5(hash_input.encode()).hexdigest()
        return int(hash_hex[:8], 16) % 100
    
    def _match_targeting(self, rules: dict, user_id: str, context: dict) -> bool:
        """匹配定向规则"""
        # 用户ID白名单
        if "user_ids" in rules and user_id in rules["user_ids"]:
            return True
        
        # 用户属性匹配
        if "attributes" in rules and context:
            for attr, condition in rules["attributes"].items():
                value = context.get(attr)
                if not self._match_condition(value, condition):
                    return False
            return True
        
        return False
```

### 使用示例

```python
# 在业务代码中使用
class OrderService:
    def __init__(self, flag_service: FeatureFlagService):
        self.flags = flag_service
    
    async def create_order(self, user_id: str, order_data: dict):
        # 检查是否启用新下单流程
        if self.flags.evaluate("new_order_flow", user_id):
            return await self._create_order_v2(user_id, order_data)
        else:
            return await self._create_order_v1(user_id, order_data)
    
    async def _create_order_v1(self, user_id, order_data):
        """旧版下单流程"""
        # ...
    
    async def _create_order_v2(self, user_id, order_data):
        """新版下单流程"""
        # ...
```

### 前端集成

```typescript
// React Hook
function useFeatureFlag(flagKey: string): boolean {
  const [enabled, setEnabled] = useState(false);
  
  useEffect(() => {
    fetch(`/api/v1/flags/${flagKey}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: getCurrentUserId() })
    })
      .then(res => res.json())
      .then(data => setEnabled(data.value));
  }, [flagKey]);
  
  return enabled;
}

// 使用
function App() {
  const showNewUI = useFeatureFlag('new_ui_design');
  
  return showNewUI ? <NewDashboard /> : <OldDashboard />;
}
```

## 定向规则格式

```json
{
  "user_ids": ["user-1", "user-2"],
  "user_attributes": {
    "plan": {
      "operator": "in",
      "values": ["premium", "enterprise"]
    },
    "country": {
      "operator": "eq",
      "value": "CN"
    },
    "created_at": {
      "operator": "gt",
      "value": "2026-01-01"
    }
  },
  "environments": ["production", "staging"]
}
```

## 灰度发布流程

```
1. 创建功能开关，默认关闭
2. 开发完成，开启内部测试（10%）
3. 测试通过，扩大到 50%
4. 无问题，全量 100%
5. 稳定后，删除开关，硬编码为 true
```

## 快速使用

```
# 设计功能开关系统
设计一个功能开关系统，支持灰度发布和A/B测试

# 创建功能开关
为新支付流程创建功能开关，先灰度 10% 用户

# 实现评估逻辑
实现功能开关的评估逻辑，支持百分比和定向规则

# 紧急降用
使用功能开关紧急关闭某个出问题的功能
```

## 参考资料

- 定向规则设计: [references/targeting-rules.md](references/targeting-rules.md)
- A/B 测试方案: [references/ab-testing.md](references/ab-testing.md)
