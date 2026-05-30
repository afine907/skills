# 工具 Schema 模板

## 通用模板

```json
{
  "name": "tool_name",
  "description": "明确描述：做什么 + 返回什么 + 什么时候该用 + 什么时候不该用",
  "parameters": {
    "type": "object",
    "properties": {
      "required_param": {
        "type": "string",
        "description": "参数含义。格式约束：XXX。示例：'example_value'"
      },
      "optional_param": {
        "type": "integer",
        "default": 10,
        "description": "参数含义。默认值：10。范围：1-100"
      }
    },
    "required": ["required_param"],
    "additionalProperties": false
  }
}
```

## 常见工具类型模板

### 查询类工具（只读）

```json
{
  "name": "search_documents",
  "description": "在知识库中搜索与查询相关的文档。返回匹配文档列表，每条包含标题、摘要、相关度分数。当用户需要查找信息时使用，不要用于修改或删除操作。",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "搜索查询文本。自然语言或关键词均可。示例：'2024年Q3销售报告'"
      },
      "limit": {
        "type": "integer",
        "default": 10,
        "minimum": 1,
        "maximum": 100,
        "description": "返回结果数量。默认10。"
      },
      "filter": {
        "type": "object",
        "properties": {
          "date_from": { "type": "string", "format": "date" },
          "date_to": { "type": "string", "format": "date" },
          "category": { "type": "string", "enum": ["report", "memo", "contract"] }
        },
        "description": "可选过滤条件"
      }
    },
    "required": ["query"],
    "additionalProperties": false
  }
}
```

### 写入类工具（有副作用）

```json
{
  "name": "create_record",
  "description": "在数据库中创建一条新记录。返回创建的记录ID。注意：此操作不可逆，请确认数据正确后再调用。",
  "parameters": {
    "type": "object",
    "properties": {
      "table": {
        "type": "string",
        "enum": ["users", "orders", "products"],
        "description": "目标表名"
      },
      "data": {
        "type": "object",
        "description": "要创建的记录数据，字段取决于table选择"
      },
      "idempotency_key": {
        "type": "string",
        "description": "幂等性键，防止重复创建。格式：UUID。相同key的重复调用返回原记录而非创建新记录。"
      }
    },
    "required": ["table", "data", "idempotency_key"],
    "additionalProperties": false
  }
}
```

### 执行类工具（外部命令）

```json
{
  "name": "run_query",
  "description": "执行只读SQL查询并返回结果。仅支持SELECT语句。不支持INSERT/UPDATE/DELETE等写操作。",
  "parameters": {
    "type": "object",
    "properties": {
      "sql": {
        "type": "string",
        "pattern": "^\\s*SELECT\\s",
        "description": "SQL查询语句。必须以SELECT开头。示例：'SELECT * FROM users LIMIT 10'"
      },
      "database": {
        "type": "string",
        "enum": ["main", "analytics", "readonly_replica"],
        "default": "readonly_replica",
        "description": "目标数据库。默认使用只读副本。"
      },
      "timeout_ms": {
        "type": "integer",
        "default": 5000,
        "maximum": 30000,
        "description": "查询超时（毫秒）。默认5000。最大30000。"
      }
    },
    "required": ["sql"],
    "additionalProperties": false
  }
}
```

### 复合工具（多步操作）

```json
{
  "name": "process_order",
  "description": "处理订单：验证库存 → 计算价格 → 创建订单。任一步骤失败则整体回滚。返回订单确认信息。",
  "parameters": {
    "type": "object",
    "properties": {
      "items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "product_id": { "type": "string" },
            "quantity": { "type": "integer", "minimum": 1 }
          },
          "required": ["product_id", "quantity"]
        },
        "minItems": 1,
        "description": "订单商品列表"
      },
      "customer_id": {
        "type": "string",
        "description": "客户ID"
      },
      "idempotency_key": {
        "type": "string",
        "description": "幂等性键"
      }
    },
    "required": ["items", "customer_id", "idempotency_key"],
    "additionalProperties": false
  }
}
```

## Schema 设计检查清单

- [ ] description 明确说明"做什么"和"返回什么"
- [ ] description 包含使用场景和不适用场景
- [ ] 所有必填参数在 `required` 数组中
- [ ] 有 enum 可选值的参数使用了 enum 约束
- [ ] 有格式要求的参数使用了 format/pattern 约束
- [ ] 有范围要求的参数使用了 minimum/maximum 约束
- [ ] 可选参数有 default 值
- [ ] 设置了 `additionalProperties: false`
- [ ] 有副作用的工具有幂等性键参数
- [ ] description 中有示例值
