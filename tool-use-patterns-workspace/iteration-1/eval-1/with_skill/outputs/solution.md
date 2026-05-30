# Agent 安全问题修复方案

## 问题诊断

两个问题分别对应工具失败模型的不同阶段：

| 问题 | 失败阶段 | 根因 |
|------|---------|------|
| 查询时误触发 delete_record | 阶段 1：工具选择失败 + 阶段 2：参数构建失败 | delete_record 的 Schema 缺少防误触设计，description 未明确使用边界 |
| 超时重试导致重复删除 | 阶段 3：工具执行失败（重试副作用） | delete_record 缺少幂等性键，重试时无法识别重复请求 |

## 修复方案

### 修复 1：防御性 Schema 设计 -- 防止误触发删除

#### 1.1 重新设计 delete_record 的工具 Schema

**核心思路：** 通过 Schema 层面的约束，让 LLM 在"只是查询"的场景下不可能构造出合法的 delete_record 调用。

```json
{
  "name": "delete_record",
  "description": "永久删除数据库中的一条记录。此操作不可逆。仅在用户明确要求删除某条特定记录时使用。当用户只是想查看、搜索、查询数据时，绝对不要调用此工具 -- 请使用 query_records 工具。",
  "parameters": {
    "type": "object",
    "properties": {
      "table": {
        "type": "string",
        "enum": ["users", "orders", "products"],
        "description": "目标表名。必须是明确的表名，不要猜测。"
      },
      "record_id": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_-]{1,64}$",
        "description": "要删除的记录的唯一ID。格式：字母数字和下划线，长度1-64。必须是用户明确提供的ID，不要自行编造。"
      },
      "confirmation_reason": {
        "type": "string",
        "minLength": 10,
        "description": "删除原因说明。必须清晰说明为什么要删除这条记录。长度至少10个字符。"
      },
      "idempotency_key": {
        "type": "string",
        "format": "uuid",
        "description": "幂等性键（UUID格式），防止重复删除。由系统自动生成，不要自行编造。"
      }
    },
    "required": ["table", "record_id", "confirmation_reason", "idempotency_key"],
    "additionalProperties": false
  }
}
```

**设计要点：**

- `description` 明确写了"仅在用户明确要求删除时使用"和"查询时不要调用"，这是引导 LLM 工具选择的关键
- `record_id` 使用 `pattern` 约束格式，防止 LLM 幻觉出不存在的 ID
- `confirmation_reason` 强制 LLM 必须给出删除理由，增加调用的"认知成本" -- LLM 在只是查询的场景下很难编造一个合理的删除理由
- `idempotency_key` 防止重试导致的重复删除（修复问题 2）
- `additionalProperties: false` 阻止 LLM 添加幻觉参数

#### 1.2 为其他 7 个工具的 description 添加互斥声明

确保查询类工具的 description 中明确说明"用于查询，不用于删除"：

```json
{
  "name": "query_records",
  "description": "查询数据库中的记录并返回结果列表。仅用于读取数据。当用户想查看、搜索、筛选数据时使用此工具。如果用户要求删除记录，请使用 delete_record 工具。",
  "parameters": {
    "type": "object",
    "properties": {
      "table": {
        "type": "string",
        "enum": ["users", "orders", "products"],
        "description": "目标表名"
      },
      "filters": {
        "type": "object",
        "description": "过滤条件。字段名:字段值 的键值对。"
      },
      "limit": {
        "type": "integer",
        "default": 20,
        "minimum": 1,
        "maximum": 100,
        "description": "返回结果数量上限。默认20。"
      }
    },
    "required": ["table"],
    "additionalProperties": false
  }
}
```

### 修复 2：代码层防御 -- 双重确认机制

仅靠 Schema 和 description 不够可靠（LLM 仍可能忽略 description 中的提示）。必须在代码层面添加防护。

```python
import uuid
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ToolRisk(Enum):
    READ_ONLY = "read_only"
    REVERSIBLE_WRITE = "reversible_write"
    IRREVERSIBLE_WRITE = "irreversible_write"
    DANGEROUS = "dangerous"


@dataclass
class ToolMeta:
    """工具元数据，记录风险等级和调用约束。"""
    name: str
    risk: ToolRisk
    requires_confirmation: bool = False
    max_calls_per_session: int = 0  # 0 表示无限制


# 工具注册表 -- 8 个工具的元数据
TOOL_REGISTRY: dict[str, ToolMeta] = {
    "query_records":     ToolMeta("query_records",     ToolRisk.READ_ONLY),
    "search_documents":  ToolMeta("search_documents",  ToolRisk.READ_ONLY),
    "get_user_profile":  ToolMeta("get_user_profile",  ToolRisk.READ_ONLY),
    "list_orders":       ToolMeta("list_orders",       ToolRisk.READ_ONLY),
    "create_record":     ToolMeta("create_record",     ToolRisk.REVERSIBLE_WRITE),
    "update_record":     ToolMeta("update_record",     ToolMeta.REVERSIBLE_WRITE),
    "export_report":     ToolMeta("export_report",     ToolRisk.READ_ONLY),
    "delete_record":     ToolMeta("delete_record",     ToolRisk.IRREVERSIBLE_WRITE,
                                   requires_confirmation=True,
                                   max_calls_per_session=10),
}
```

#### 2.1 工具调度层 -- 意图校验中间件

在工具执行之前，检查调用上下文是否合理：

```python
class ToolDispatcher:
    """工具调度器，在执行前进行安全校验。"""

    def __init__(self, tool_registry: dict[str, ToolMeta]):
        self.registry = tool_registry
        self.idempotency_store: dict[str, dict] = {}  # 幂等性键 -> 执行结果
        self.call_counts: dict[str, int] = {}  # 工具名 -> 本次会话调用次数

    async def dispatch(
        self,
        tool_name: str,
        params: dict[str, Any],
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        调度工具调用，执行以下安全检查：
        1. 工具是否存在
        2. 参数 Schema 验证
        3. 危险工具的意图校验
        4. 幂等性检查
        5. 频率限制
        """

        # --- 检查 1: 工具存在性 ---
        meta = self.registry.get(tool_name)
        if meta is None:
            return {"success": False, "error": f"未知工具: {tool_name}", "retryable": False}

        # --- 检查 2: 参数 Schema 验证 ---
        validation_error = self._validate_params(tool_name, params)
        if validation_error:
            return {"success": False, "error": validation_error, "retryable": False}

        # --- 检查 3: 不可逆写入工具的意图校验 ---
        if meta.risk in (ToolRisk.IRREVERSIBLE_WRITE, ToolRisk.DANGEROUS):
            intent_check = self._check_delete_intent(user_message, conversation_history)
            if not intent_check["passed"]:
                logger.warning(
                    f"Blocked {tool_name}: intent check failed. "
                    f"User message: {user_message[:100]}"
                )
                return {
                    "success": False,
                    "error": intent_check["reason"],
                    "retryable": False,
                    "suggested_tool": intent_check.get("suggested_tool"),
                }

        # --- 检查 4: 幂等性 ---
        idempotency_key = params.get("idempotency_key")
        if idempotency_key:
            if idempotency_key in self.idempotency_store:
                cached = self.idempotency_store[idempotency_key]
                logger.info(f"Idempotent hit for key={idempotency_key}, returning cached result")
                return cached

        # --- 检查 5: 频率限制 ---
        if meta.max_calls_per_session > 0:
            current_count = self.call_counts.get(tool_name, 0)
            if current_count >= meta.max_calls_per_session:
                return {
                    "success": False,
                    "error": f"工具 {tool_name} 已达到本次会话最大调用次数 ({meta.max_calls_per_session})",
                    "retryable": False,
                }
            self.call_counts[tool_name] = current_count + 1

        # --- 执行工具 ---
        result = await self._execute_tool(tool_name, params)

        # --- 缓存结果（用于幂等性） ---
        if idempotency_key:
            self.idempotency_store[idempotency_key] = result

        return result
```

#### 2.2 意图校验逻辑 -- 防止查询场景误触删除

```python
    def _check_delete_intent(
        self,
        user_message: str,
        conversation_history: list[dict] | None,
    ) -> dict[str, Any]:
        """
        校验用户意图是否真的要执行删除。
        
        规则：
        1. 用户消息中必须包含明确的删除意图词
        2. 用户消息中不能同时包含查询意图词（歧义场景拒绝执行）
        3. 如果有对话历史，检查用户是否在之前的轮次中确认了删除
        """

        # 删除意图关键词
        delete_keywords = ["删除", "删掉", "remove", "delete", "移除", "清除", "destroy"]
        # 查询意图关键词（与删除互斥）
        query_keywords = ["查询", "查看", "搜索", "找", "search", "query", "find", "list", "show", "get", "看看", "了解"]

        user_msg_lower = user_message.lower()

        has_delete_intent = any(kw in user_msg_lower for kw in delete_keywords)
        has_query_intent = any(kw in user_msg_lower for kw in query_keywords)

        # 情况 1: 明确的查询意图 -- 拒绝删除，建议使用查询工具
        if has_query_intent and not has_delete_intent:
            return {
                "passed": False,
                "reason": "用户意图是查询数据，不是删除。请使用 query_records 工具。",
                "suggested_tool": "query_records",
            }

        # 情况 2: 没有明确的删除意图 -- 拒绝执行
        if not has_delete_intent:
            return {
                "passed": False,
                "reason": "未检测到明确的删除意图。删除操作需要用户明确要求。如果用户确实想删除，请让用户确认。",
            }

        # 情况 3: 有删除意图但同时有查询意图（如"帮我查一下然后删除"）-- 需要对话历史中的确认
        if has_delete_intent and has_query_intent and conversation_history:
            # 检查最近的对话中是否有用户确认
            recent_user_messages = [
                msg for msg in conversation_history[-5:]
                if msg.get("role") == "user"
            ]
            confirmed = any(
                any(kw in msg.get("content", "").lower() for kw in ["确认", "确定", "confirm", "yes", "是的", "好的"])
                for msg in recent_user_messages
            )
            if not confirmed:
                return {
                    "passed": False,
                    "reason": "用户请求中同时包含查询和删除意图，需要用户明确确认删除。请先展示查询结果，然后询问用户是否确认删除。",
                    "suggested_tool": "query_records",
                }

        return {"passed": True}
```

### 修复 3：幂等性执行层 -- 防止重复删除

这是解决"超时重试导致重复删除"的核心机制。

```python
    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        执行工具调用，带指数退避重试。
        
        关键规则：
        - 有副作用的工具必须携带 idempotency_key
        - 重试前检查幂等性缓存，避免重复执行
        - 最多重试 3 次
        """

        meta = self.registry[tool_name]
        idempotency_key = params.get("idempotency_key")

        # 有副作用的工具必须有幂等性键
        if meta.risk in (ToolRisk.IRREVERSIBLE_WRITE, ToolRisk.REVERSIBLE_WRITE):
            if not idempotency_key:
                return {
                    "success": False,
                    "error": f"工具 {tool_name} 是有副作用的操作，必须提供 idempotency_key 参数",
                    "retryable": False,
                }

        max_retries = 3
        base_delay = 1.0  # 秒

        for attempt in range(max_retries):
            try:
                # 重试前再次检查幂等性缓存（防止网络超时后重试时重复执行）
                if attempt > 0 and idempotency_key:
                    if idempotency_key in self.idempotency_store:
                        logger.info(
                            f"Retry {attempt}: idempotent key {idempotency_key} already executed, "
                            f"returning cached result"
                        )
                        return self.idempotency_store[idempotency_key]

                result = await self._call_actual_tool(tool_name, params)

                # 执行成功 -- 缓存结果
                if idempotency_key and result.get("success"):
                    self.idempotency_store[idempotency_key] = result

                return result

            except TimeoutError:
                logger.warning(f"Tool {tool_name} timed out (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # 指数退避: 1s, 2s, 4s
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    return {
                        "success": False,
                        "error": f"工具 {tool_name} 超时，已重试 {max_retries} 次",
                        "retryable": True,
                    }

            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                return {
                    "success": False,
                    "error": f"工具执行异常: {str(e)}",
                    "retryable": False,
                }

    async def _call_actual_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """调用实际的工具实现（需根据项目替换）。"""
        # 这里是实际调用数据库/API 的地方
        # 示例实现：
        raise NotImplementedError("请替换为实际的工具调用逻辑")
```

### 修复 4：断路器 -- 防止持续失败时的级联问题

```python
@dataclass
class CircuitBreaker:
    """断路器：连续失败达到阈值后暂停调用。"""
    failure_threshold: int = 3
    recovery_timeout: float = 30.0  # 秒

    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _state: str = field(default="closed", init=False)  # closed / open / half_open

    @property
    def is_open(self) -> bool:
        if self._state == "open":
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._state = "half_open"
                return False
            return True
        return False

    def record_success(self):
        self._failure_count = 0
        self._state = "closed"

    def record_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning(f"Circuit breaker OPEN after {self._failure_count} consecutive failures")


# 在 ToolDispatcher 中集成断路器
class SafeToolDispatcher(ToolDispatcher):
    """集成断路器的安全工具调度器。"""

    def __init__(self, tool_registry: dict[str, ToolMeta]):
        super().__init__(tool_registry)
        self.breakers: dict[str, CircuitBreaker] = {}

    async def dispatch(self, tool_name: str, params: dict, user_message: str,
                       conversation_history: list[dict] | None = None) -> dict:
        # 获取或创建断路器
        if tool_name not in self.breakers:
            self.breakers[tool_name] = CircuitBreaker()

        breaker = self.breakers[tool_name]

        # 断路器打开时拒绝调用
        if breaker.is_open:
            return {
                "success": False,
                "error": f"工具 {tool_name} 暂时不可用（断路器已打开），请稍后重试",
                "retryable": True,
                "retry_after_seconds": int(breaker.recovery_timeout),
            }

        # 执行工具调用
        result = await super().dispatch(tool_name, params, user_message, conversation_history)

        # 更新断路器状态
        if result.get("success"):
            breaker.record_success()
        elif result.get("retryable"):
            breaker.record_failure()

        return result
```

### 修复 5：完整调用示例

将以上所有组件组合起来，展示完整的安全调用流程：

```python
import asyncio
import uuid


async def main():
    """演示修复后的安全工具调用流程。"""

    dispatcher = SafeToolDispatcher(TOOL_REGISTRY)

    # --- 场景 1: 用户只是查询，不应触发删除 ---
    print("=== 场景 1: 查询意图 ===")
    result = await dispatcher.dispatch(
        tool_name="delete_record",
        params={
            "table": "users",
            "record_id": "user_123",
            "confirmation_reason": "用户想查看记录",
            "idempotency_key": str(uuid.uuid4()),
        },
        user_message="帮我查一下用户 user_123 的信息",
    )
    print(f"结果: {result}")
    # 预期输出:
    # {
    #   "success": False,
    #   "error": "用户意图是查询数据，不是删除。请使用 query_records 工具。",
    #   "retryable": False,
    #   "suggested_tool": "query_records"
    # }

    # --- 场景 2: 用户明确要求删除 ---
    print("\n=== 场景 2: 明确删除意图 ===")
    delete_key = str(uuid.uuid4())
    result = await dispatcher.dispatch(
        tool_name="delete_record",
        params={
            "table": "users",
            "record_id": "user_123",
            "confirmation_reason": "用户明确要求删除此用户账户",
            "idempotency_key": delete_key,
        },
        user_message="请删除用户 user_123 的记录",
    )
    print(f"结果: {result}")

    # --- 场景 3: 超时重试时，幂等性键阻止重复删除 ---
    print("\n=== 场景 3: 重试幂等性 ===")
    result_retry = await dispatcher.dispatch(
        tool_name="delete_record",
        params={
            "table": "users",
            "record_id": "user_123",
            "confirmation_reason": "用户明确要求删除此用户账户",
            "idempotency_key": delete_key,  # 相同的幂等性键
        },
        user_message="请删除用户 user_123 的记录",
    )
    print(f"重试结果: {result_retry}")
    # 预期: 返回缓存的结果，不重复执行删除

    # --- 场景 4: 查询操作正常执行 ---
    print("\n=== 场景 4: 正常查询 ===")
    result = await dispatcher.dispatch(
        tool_name="query_records",
        params={
            "table": "users",
            "filters": {"status": "active"},
            "limit": 10,
        },
        user_message="帮我查一下所有活跃用户",
    )
    print(f"结果: {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

## 修复总结

| 问题 | 修复层 | 具体措施 |
|------|--------|---------|
| 查询时误触发删除 | Schema 层 | delete_record 的 description 明确写"仅在用户明确要求删除时使用"；增加 `confirmation_reason` 强制 LLM 给出删除理由 |
| 查询时误触发删除 | Schema 层 | 查询类工具的 description 中声明"用于查询，不用于删除"，与 delete_record 形成互斥 |
| 查询时误触发删除 | Schema 层 | `additionalProperties: false` 阻止 LLM 幻觉参数 |
| 查询时误触发删除 | 代码层 | `_check_delete_intent()` 意图校验中间件，检查用户消息中的关键词，查询意图时直接拦截 |
| 查询时误触发删除 | 代码层 | `ToolRisk.IRREVERSIBLE_WRITE` 风险分级，不可逆操作自动触发意图校验 |
| 超时重试重复删除 | Schema 层 | `idempotency_key` 作为 required 参数，强制每次调用携带唯一标识 |
| 超时重试重复删除 | 代码层 | `idempotency_store` 缓存已执行的结果，重试时直接返回缓存 |
| 超时重试重复删除 | 代码层 | 重试循环中每次检查幂等性缓存，防止网络超时后的"幽灵重试" |
| 超时重试重复删除 | 代码层 | 断路器模式，连续 3 次失败后暂停调用 30 秒，防止级联失败 |

## 关键设计原则

1. **不信任 LLM 输出** -- Schema 和 description 是第一道防线，但代码层的意图校验和幂等性检查才是真正的安全保障
2. **有副作用的工具必须有幂等性键** -- 这是防止重试导致重复执行的唯一可靠方法
3. **防御纵深** -- Schema 约束 + 意图校验 + 幂等性 + 断路器，每一层都能独立阻止问题
4. **结构化错误返回** -- 工具失败时返回 `{ success, error, retryable }` 而非抛异常，让 LLM 能据此决策
