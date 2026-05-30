# Agent Tool Safety: Fixing Accidental Deletes and Duplicate Deletions

## Problem Summary

Two safety bugs exist in the agent's tool usage:

1. **False-positive delete triggering** — The agent calls `delete_record` when the user only intends to query/read data.
2. **Duplicate deletions on timeout retry** — When a tool call times out, the retry logic re-executes `delete_record`, causing double deletes.

## Root Cause Analysis

### Issue 1: Accidental Delete on Query Intent

The agent's tool selection logic does not distinguish between read-only intent and destructive intent. Common causes:

- The system prompt does not explicitly instruct the agent to prefer read-only tools for queries.
- `delete_record` is not gated behind a confirmation step.
- Tool descriptions are ambiguous — "remove from results" could be misinterpreted as delete.

### Issue 2: Duplicate Delete on Retry

Standard retry logic treats all tool calls the same: on timeout, re-execute. But `delete_record` is **not idempotent** — calling it twice deletes two things (or errors). The retry mechanism has no concept of idempotency or deduplication.

---

## Solution

### Fix 1: Guard Destructive Tools with Confirmation and Intent Classification

#### 1a. Add explicit system prompt instructions

Add the following to the agent's system prompt:

```
## Tool Usage Rules

- For ANY query, search, lookup, or read operation, you MUST use read-only tools only.
- NEVER call delete_record unless the user's message explicitly contains words like
  "delete", "remove", "drop", "destroy", or "eliminate" AND refers to a specific record.
- When in doubt about user intent, ASK the user to confirm before calling delete_record.
- Prefer the most conservative tool that satisfies the user's request.
```

#### 1b. Implement a confirmation gate in the tool wrapper

```python
import re

# Patterns that indicate destructive intent
DESTRUCTIVE_PATTERNS = [
    r"\bdelete\b",
    r"\bremove\b",
    r"\bdrop\b",
    r"\bdestroy\b",
    r"\beliminate\b",
    r"\bget rid of\b",
    r"\bpermanently\b",
]

# Patterns that indicate read-only intent (should NEVER trigger delete)
READ_ONLY_PATTERNS = [
    r"\b(show|list|find|search|query|get|fetch|view|display|read|check|look\s*up)\b",
    r"\bhow many\b",
    r"\bwhat are\b",
    r"\btell me\b",
]


def classify_user_intent(user_message: str) -> str:
    """Classify user message as 'read', 'write', or 'ambiguous'."""
    msg_lower = user_message.lower()

    has_destructive = any(re.search(p, msg_lower) for p in DESTRUCTIVE_PATTERNS)
    has_read_only = any(re.search(p, msg_lower) for p in READ_ONLY_PATTERNS)

    if has_destructive and not has_read_only:
        return "destructive"
    elif has_read_only and not has_destructive:
        return "read_only"
    elif has_destructive and has_read_only:
        # e.g., "delete the record that shows X" — still destructive, but confirm
        return "ambiguous"
    else:
        return "read_only"  # default to safe


def should_allow_delete(user_message: str) -> tuple[bool, str]:
    """Determine if delete_record should be allowed. Returns (allowed, reason)."""
    intent = classify_user_intent(user_message)

    if intent == "read_only":
        return False, "User intent appears to be read-only. Delete is not appropriate."
    elif intent == "ambiguous":
        return False, "User intent is ambiguous. Please ask the user to confirm deletion."
    else:
        return True, "Destructive intent confirmed."
```

#### 1c. Wrap the tool call with the guard

```python
async def safe_tool_call(tool_name: str, tool_args: dict, user_message: str):
    """Wrapper that enforces safety checks before tool execution."""

    if tool_name == "delete_record":
        allowed, reason = should_allow_delete(user_message)
        if not allowed:
            return {
                "error": "BLOCKED",
                "reason": reason,
                "suggestion": "Ask the user: 'Did you want to delete this record, or just view it?'"
            }

    # Proceed with actual tool execution
    return await execute_tool(tool_name, tool_args)
```

---

### Fix 2: Make Delete Idempotent with Deduplication

#### 2a. Add an idempotency key to every delete call

Every `delete_record` invocation must carry a unique, deterministic idempotency key. On retry, the same key is reused so the backend can detect and reject duplicates.

```python
import hashlib
import time
import uuid


class IdempotencyManager:
    """Ensures no destructive tool is executed more than once for the same logical operation."""

    def __init__(self):
        # Maps idempotency_key -> result (cached for dedup window)
        self._executed: dict[str, dict] = {}
        # Default dedup window: 10 minutes
        self._dedup_window_seconds = 600

    def generate_key(self, tool_name: str, tool_args: dict, conversation_id: str) -> str:
        """
        Generate a deterministic idempotency key from the tool call parameters.
        Same inputs always produce the same key, so retries reuse it.
        """
        # Sort args for deterministic hashing
        canonical = f"{tool_name}:{conversation_id}:{sorted(tool_args.items())}"
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def is_duplicate(self, key: str) -> tuple[bool, dict | None]:
        """Check if this operation was already executed successfully."""
        if key in self._executed:
            entry = self._executed[key]
            elapsed = time.time() - entry["timestamp"]
            if elapsed < self._dedup_window_seconds:
                return True, entry["result"]
            else:
                # Expired, allow re-execution
                del self._executed[key]
        return False, None

    def record_execution(self, key: str, result: dict):
        """Record that this operation was executed, along with its result."""
        self._executed[key] = {
            "result": result,
            "timestamp": time.time(),
        }

    def cleanup_expired(self):
        """Remove expired entries (call periodically)."""
        now = time.time()
        expired = [
            k for k, v in self._executed.items()
            if now - v["timestamp"] >= self._dedup_window_seconds
        ]
        for k in expired:
            del self._executed[k]


# Global instance (or inject via dependency)
idempotency_mgr = IdempotencyManager()
```

#### 2b. Integrate deduplication into the retry-aware tool executor

```python
import asyncio
from typing import Any


# List of tools that are NOT idempotent and require dedup protection
DESTRUCTIVE_TOOLS = {"delete_record", "update_record", "transfer_funds", "send_email"}


class ToolExecutionError(Exception):
    """Raised when a tool call fails."""
    def __init__(self, message: str, is_timeout: bool = False):
        super().__init__(message)
        self.is_timeout = is_timeout


async def execute_tool_with_retry(
    tool_name: str,
    tool_args: dict,
    user_message: str,
    conversation_id: str,
    max_retries: int = 3,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """
    Execute a tool with retry logic and destructive-tool safety guards.

    Safety features:
    1. Intent guard — blocks delete on read-only intent
    2. Idempotency — prevents duplicate execution on retry
    3. Timeout-aware retries — only retries timeout errors, not business errors
    """

    # --- Step 1: Intent guard for destructive tools ---
    if tool_name in DESTRUCTIVE_TOOLS:
        allowed, reason = should_allow_delete(user_message)
        if not allowed:
            return {
                "status": "blocked",
                "tool": tool_name,
                "reason": reason,
            }

    # --- Step 2: Generate idempotency key for destructive tools ---
    idempotency_key = None
    if tool_name in DESTRUCTIVE_TOOLS:
        idempotency_key = idempotency_mgr.generate_key(
            tool_name, tool_args, conversation_id
        )
        is_dup, cached_result = idempotency_mgr.is_duplicate(idempotency_key)
        if is_dup:
            return {
                "status": "deduplicated",
                "tool": tool_name,
                "cached_result": cached_result,
                "message": "This operation was already executed. Returning cached result.",
            }

    # --- Step 3: Execute with timeout and retry ---
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = await asyncio.wait_for(
                call_tool_backend(tool_name, tool_args),
                timeout=timeout_seconds,
            )

            # --- Step 4: Record successful execution for dedup ---
            if idempotency_key:
                idempotency_mgr.record_execution(idempotency_key, result)

            return {
                "status": "success",
                "tool": tool_name,
                "result": result,
                "attempt": attempt,
            }

        except asyncio.TimeoutError:
            last_error = ToolExecutionError(
                f"Tool '{tool_name}' timed out on attempt {attempt}",
                is_timeout=True,
            )
            # For destructive tools, check dedup before retrying
            # (the call might have succeeded on the server side despite the timeout)
            if idempotency_key:
                # Wait briefly, then check if the operation actually went through
                await asyncio.sleep(1)
                is_dup, cached_result = idempotency_mgr.is_duplicate(idempotency_key)
                if is_dup:
                    return {
                        "status": "recovered_after_timeout",
                        "tool": tool_name,
                        "cached_result": cached_result,
                        "message": "Operation may have succeeded. Returning cached result.",
                    }

            # Only retry on timeout, not on business logic errors
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s...
                backoff = 2 ** (attempt - 1)
                await asyncio.sleep(backoff)
                continue

        except Exception as e:
            # Business logic error — do NOT retry
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e),
                "attempt": attempt,
            }

    # All retries exhausted
    return {
        "status": "failed",
        "tool": tool_name,
        "error": str(last_error),
        "attempts": max_retries,
        "recommendation": "Check server logs. The operation may or may not have completed.",
    }


async def call_tool_backend(tool_name: str, tool_args: dict) -> dict:
    """Placeholder for actual tool execution (API call, DB operation, etc.)."""
    raise NotImplementedError("Implement this to call your actual tool backend.")
```

---

### Fix 3 (Bonus): Add a Dry-Run Mode for Destructive Tools

For extra safety, implement a dry-run preview that the agent can show to the user before executing:

```python
async def preview_delete(record_id: str) -> dict:
    """
    Fetch the record that would be deleted, without deleting it.
    The agent should show this preview to the user for confirmation.
    """
    record = await call_tool_backend("get_record", {"id": record_id})
    return {
        "action": "delete",
        "record_id": record_id,
        "record_data": record,
        "warning": "This record will be permanently deleted. Confirm?",
    }
```

Agent prompt instruction for using dry-run:

```
## Before Calling delete_record

1. Call preview_delete(record_id) to fetch the record.
2. Show the user: "I found this record: [data]. Do you want me to delete it?"
3. Only proceed with delete_record after the user explicitly says "yes" or "confirm".
```

---

## Summary of Changes

| Problem | Fix | Mechanism |
|---------|-----|-----------|
| Accidental delete on query | Intent classification + system prompt rules | `classify_user_intent()` blocks delete when user only wants to read |
| No confirmation before delete | Dry-run preview + prompt instructions | `preview_delete()` shows data, agent asks user to confirm |
| Duplicate delete on timeout retry | Idempotency keys + dedup manager | `IdempotencyManager` tracks executed ops, returns cached result on retry |
| Retrying non-idempotent operations | Timeout-only retry with backoff | Only `asyncio.TimeoutError` triggers retry; business errors fail immediately |

## How to Apply These Fixes

1. **System prompt**: Add the "Tool Usage Rules" section from Fix 1a to your agent's system prompt.
2. **Tool wrapper**: Install `safe_tool_call` or `execute_tool_with_retry` as the entry point for all tool invocations.
3. **Idempotency store**: For production, back `IdempotencyManager` with Redis or a database table instead of an in-memory dict, so dedup survives restarts and works across multiple agent instances.
4. **Testing**: Write unit tests that verify:
   - `classify_user_intent("show me all users")` returns `"read_only"`
   - `classify_user_intent("delete user 123")` returns `"destructive"`
   - Calling `execute_tool_with_retry` twice with the same args returns deduplicated result on second call
   - A timeout on the first call followed by a successful retry records the result correctly
