# GitHub API Agent 防御性工具调用方案

## 问题诊断

Agent 调用 GitHub API 出现两类核心故障：

1. **选错 endpoint** — 工具描述模糊，Agent 把 issues API 用到了 PR 上，或把 repo 级操作用到了 org 级
2. **参数错误导致 422** — owner/repo 格式不对、缺少必填字段、enum 值拼错（如 `state: "open"` 写成 `state: "opened"`）

根本原因：Schema 约束不够严格，description 没有告诉 LLM 边界条件。

---

## Step 1: 工具面审计与风险分级

先盘点 Agent 能调用的所有 GitHub API，按风险分级：

| 工具 | 风险等级 | 理由 |
|------|---------|------|
| `get_repo` | 只读 | 不修改任何状态 |
| `list_issues` | 只读 | 查询操作 |
| `search_code` | 只读 | 查询操作 |
| `create_issue` | 可逆写入 | 可以关闭/删除 |
| `create_comment` | 可逆写入 | 可以编辑/删除 |
| `merge_pr` | 不可逆写入 | 合并后无法简单回滚 |
| `delete_branch` | 不可逆写入 | 删除后需要恢复 |
| `push_code` | 危险 | 直接修改代码库 |

**处理策略：**
- 只读工具：自动执行，失败时重试
- 可逆写入：参数验证通过后执行
- 不可逆写入：参数验证 + 幂等性键
- 危险工具：默认拒绝，需显式确认

---

## Step 2: 防御性 Schema 设计

### 核心原则

1. **enum 约束所有可选值** — 不给 LLM 猜测空间
2. **pattern 约束格式** — owner/repo、issue number 等用正则
3. **description 即文档** — 写清"何时用、怎么用、什么格式"
4. **additionalProperties: false** — 防止 LLM 幻觉不存在的参数
5. **必填参数全部声明** — 不依赖 LLM 的"常识"

### GitHub 工具 Schema 定义

```python
# tools/github_tools.py

GITHUB_TOOL_SCHEMAS = [
    # ============================================================
    # 只读工具
    # ============================================================
    {
        "name": "get_repo",
        "description": (
            "获取 GitHub 仓库的基本信息（名称、描述、默认分支、语言等）。"
            "仅用于查询仓库元数据，不要用于获取文件内容或代码搜索。"
            "返回仓库的 JSON 信息。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "description": (
                        "仓库所有者的用户名或组织名。"
                        "格式：只允许字母、数字、连字符，不能以连字符开头或结尾。"
                        "示例：'anthropics'、'facebook'"
                    ),
                },
                "repo": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "description": (
                        "仓库名称。"
                        "格式：只允许字母、数字、点、下划线、连字符。"
                        "示例：'claude-code'、'react-native'"
                    ),
                },
            },
            "required": ["owner", "repo"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_issues",
        "description": (
            "列出 GitHub 仓库的 Issues。仅用于查询 issues，不要用于查询 Pull Requests。"
            "Pull Requests 请使用 list_pull_requests 工具。"
            "返回 issue 列表，每条包含编号、标题、状态、标签。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "description": "仓库所有者。示例：'anthropics'",
                },
                "repo": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "description": "仓库名称。示例：'claude-code'",
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "default": "open",
                    "description": "Issue 状态过滤。默认 'open'。注意：GitHub API 使用 'open'/'closed'，不是 'opened'/'closed'。",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 10,
                    "description": "按标签过滤。示例：['bug', 'priority:high']",
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "comments"],
                    "default": "created",
                    "description": "排序字段。默认 'created'。",
                },
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "排序方向。默认 'desc'（最新在前）。",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 30,
                    "description": "每页结果数。默认 30，最大 100。",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "页码。默认 1。",
                },
            },
            "required": ["owner", "repo"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_pull_requests",
        "description": (
            "列出 GitHub 仓库的 Pull Requests。仅用于查询 PR，不要用于查询 Issues。"
            "Issues 请使用 list_issues 工具。"
            "返回 PR 列表，每条包含编号、标题、状态、分支信息。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "description": "仓库所有者。示例：'anthropics'",
                },
                "repo": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "description": "仓库名称。示例：'claude-code'",
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "default": "open",
                    "description": "PR 状态过滤。默认 'open'。",
                },
                "sort": {
                    "type": "string",
                    "enum": ["created", "updated", "popularity", "long-running"],
                    "default": "created",
                    "description": "排序字段。默认 'created'。",
                },
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "排序方向。默认 'desc'。",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 30,
                    "description": "每页结果数。默认 30。",
                },
            },
            "required": ["owner", "repo"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_file_content",
        "description": (
            "获取仓库中单个文件的内容。仅用于获取单个文件，不要用于列出目录或搜索代码。"
            "列目录用 list_directory，搜索代码用 search_code。"
            "返回文件的文本内容和元数据。大文件（>1MB）会被截断。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "description": "仓库所有者。",
                },
                "repo": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "description": "仓库名称。",
                },
                "path": {
                    "type": "string",
                    "minLength": 1,
                    "description": (
                        "文件路径，相对于仓库根目录。不能以 / 开头。"
                        "示例：'src/main.py'、'README.md'"
                    ),
                },
                "ref": {
                    "type": "string",
                    "default": None,
                    "description": (
                        "Git 引用（分支名、tag 或 commit SHA）。"
                        "默认使用仓库的默认分支。示例：'main'、'v1.0.0'、'abc123'"
                    ),
                },
            },
            "required": ["owner", "repo", "path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search_code",
        "description": (
            "在 GitHub 仓库中搜索代码。使用 GitHub Search API。"
            "返回匹配的文件和代码片段。注意：搜索结果可能有延迟（非实时索引）。"
            "不要用于获取完整文件内容，获取完整文件请用 get_file_content。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "description": (
                        "搜索查询字符串。支持 GitHub 搜索语法。"
                        "示例：'repo:anthropics/claude-code filename:*.py import anthropic'"
                    ),
                },
                "sort": {
                    "type": "string",
                    "enum": ["indexed"],
                    "description": "排序方式。目前仅支持 'indexed'（按索引时间）。",
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 30,
                    "description": "每页结果数。默认 30。",
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "页码。默认 1。",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },

    # ============================================================
    # 可逆写入工具
    # ============================================================
    {
        "name": "create_issue",
        "description": (
            "在 GitHub 仓库中创建新 Issue。返回创建的 issue 编号和 URL。"
            "注意：此操作会修改仓库状态，但可以后续关闭 issue。"
            "创建前请确认 owner/repo 正确，且你有写入权限。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "description": "仓库所有者。",
                },
                "repo": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "description": "仓库名称。",
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 256,
                    "description": "Issue 标题。必填，不能为空。",
                },
                "body": {
                    "type": "string",
                    "maxLength": 65536,
                    "default": "",
                    "description": "Issue 正文。支持 Markdown。默认为空。",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 20,
                    "default": [],
                    "description": "标签列表。标签必须已存在于仓库中，否则会被忽略。",
                },
                "assignees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 10,
                    "default": [],
                    "description": "指派的用户名列表。用户必须有仓库访问权限。",
                },
                "idempotency_key": {
                    "type": "string",
                    "description": (
                        "幂等性键，防止重复创建。格式：UUID v4。"
                        "相同 key 的重复调用返回原 issue 而非创建新 issue。"
                        "示例：'550e8400-e29b-41d4-a716-446655440000'"
                    ),
                },
            },
            "required": ["owner", "repo", "title", "idempotency_key"],
            "additionalProperties": False,
        },
    },
    {
        "name": "create_comment",
        "description": (
            "在 GitHub Issue 或 Pull Request 上添加评论。返回评论 ID。"
            "注意：issue_number 同时适用于 Issue 和 PR（GitHub 的 PR 也有编号）。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "description": "仓库所有者。",
                },
                "repo": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "description": "仓库名称。",
                },
                "issue_number": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Issue 或 PR 的编号。注意：是数字编号，不是 URL。",
                },
                "body": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 65536,
                    "description": "评论内容。支持 Markdown。不能为空。",
                },
                "idempotency_key": {
                    "type": "string",
                    "description": "幂等性键。格式：UUID v4。",
                },
            },
            "required": ["owner", "repo", "issue_number", "body", "idempotency_key"],
            "additionalProperties": False,
        },
    },
]


# ============================================================
# Schema 版本管理 — 检测 API 漂移
# ============================================================
SCHEMA_VERSION = "2024-01-15"  # 对应 GitHub API 版本

def get_tools_for_agent() -> list[dict]:
    """返回给 Anthropic Agent 的工具列表，附带版本元数据。"""
    return [
        {**tool, "_schema_version": SCHEMA_VERSION}
        for tool in GITHUB_TOOL_SCHEMAS
    ]
```

**Schema 设计要点（对应 Step 2 原则）：**

- `state` 参数用 `enum: ["open", "closed", "all"]` 而非自由文本 — 防止 LLM 写成 `"opened"`
- `owner` 和 `repo` 用 `pattern` 正则约束 — 防止传入 URL 或 `owner/repo` 组合格式
- `per_page` 用 `minimum`/`maximum` 约束范围 — 防止传入 0 或 10000
- `additionalProperties: false` — 防止 LLM 幻觉不存在的参数（如给 `list_issues` 传 `branch`）
- 写入工具都有 `idempotency_key` — 防止重试导致重复创建
- description 中明确写出"不要用于 X" — 减少工具选错的概率

---

## Step 3: 防御性工具执行层

这一层在 Agent 和 GitHub API 之间，负责参数验证、重试、断路器、错误结构化。

```python
# executor/github_executor.py

import time
import uuid
import logging
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass, field

import httpx
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# ============================================================
# 结构化错误返回（永远不要返回 None 或抛异常给 LLM）
# ============================================================

class ErrorType(str, Enum):
    TRANSIENT = "transient"        # 可重试：超时、5xx、限流
    PARAMETER = "parameter"        # 参数错误：4xx、验证失败
    UNAVAILABLE = "unavailable"    # 工具不可用：连接拒绝、服务下线
    OUTPUT = "output"              # 输出异常：格式不符


@dataclass
class ToolResult:
    """工具执行结果的统一包装。"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    retryable: bool = False
    tool_name: str = ""
    execution_time_ms: float = 0
    attempt: int = 1

    def to_llm_message(self) -> dict:
        """转换为可以返回给 LLM 的格式。"""
        if self.success:
            return {
                "type": "tool_result",
                "content": str(self.data),
            }
        else:
            return {
                "type": "tool_result",
                "content": (
                    f"[工具调用失败] {self.tool_name}\n"
                    f"错误类型: {self.error_type.value}\n"
                    f"错误信息: {self.error}\n"
                    f"可重试: {self.retryable}\n"
                    f"建议: {self._get_suggestion()}"
                ),
                "is_error": True,
            }

    def _get_suggestion(self) -> str:
        suggestions = {
            ErrorType.TRANSIENT: "服务暂时不可用，请稍后重试。",
            ErrorType.PARAMETER: "请检查参数格式后重试。常见问题：owner/repo 格式、state 值拼写、缺少必填字段。",
            ErrorType.UNAVAILABLE: "GitHub API 当前不可用，请稍后重试或使用替代方案。",
            ErrorType.OUTPUT: "返回数据格式异常，请尝试其他查询方式。",
        }
        return suggestions.get(self.error_type, "请检查输入后重试。")


# ============================================================
# 参数预验证（在发请求之前拦截错误）
# ============================================================

class GitHubOwnerRepo(BaseModel):
    """owner/repo 参数的 Pydantic 验证模型。"""
    owner: str = Field(pattern=r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$")
    repo: str = Field(pattern=r"^[a-zA-Z0-9._-]+$")

    @field_validator("owner")
    @classmethod
    def owner_not_url(cls, v: str) -> str:
        if "/" in v or "://" in v:
            raise ValueError(
                f"owner 参数不应包含 '/' 或 URL。"
                f"你传入的 '{v}' 看起来像 URL 或 owner/repo 组合。"
                f"请只传 owner 部分，repo 单独传。"
            )
        return v

    @field_validator("repo")
    @classmethod
    def repo_not_full_path(cls, v: str) -> str:
        if "/" in v:
            raise ValueError(
                f"repo 参数不应包含 '/'。"
                f"你传入的 '{v}' 看起来像完整路径。"
                f"请只传仓库名，owner 单独传。"
            )
        return v


class IssueState(BaseModel):
    """Issue/PR 状态参数验证。"""
    state: str = Field(pattern=r"^(open|closed|all)$")

    @field_validator("state")
    @classmethod
    def state_value_check(cls, v: str) -> str:
        # 常见拼写错误映射
        corrections = {
            "opened": "open",
            "closed": "closed",
            "all": "all",
            "merged": "closed",  # PR 的 merged 状态在 GitHub API 中是 closed
        }
        if v not in ("open", "closed", "all"):
            corrected = corrections.get(v)
            if corrected:
                raise ValueError(
                    f"state 值 '{v}' 不正确。GitHub API 使用 '{corrected}'。"
                    f"有效值：'open'、'closed'、'all'"
                )
            raise ValueError(f"state 值 '{v}' 无效。有效值：'open'、'closed'、'all'")
        return v


def validate_params(tool_name: str, params: dict) -> Optional[ToolResult]:
    """
    在发送请求前验证参数。返回 None 表示验证通过，返回 ToolResult 表示验证失败。

    这是防止 422 错误的第一道防线。
    """
    try:
        # 所有 GitHub 工具都需要 owner + repo
        if "owner" in params or "repo" in params:
            GitHubOwnerRepo(
                owner=params.get("owner", ""),
                repo=params.get("repo", ""),
            )

        # 状态参数验证
        if "state" in params:
            IssueState(state=params["state"])

        # issue_number 验证
        if "issue_number" in params:
            num = params["issue_number"]
            if not isinstance(num, int) or num < 1:
                return ToolResult(
                    success=False,
                    error=f"issue_number 必须是正整数，收到：{num}",
                    error_type=ErrorType.PARAMETER,
                    retryable=False,
                    tool_name=tool_name,
                )

        # path 验证（防止路径穿越）
        if "path" in params:
            path = params["path"]
            if ".." in path or path.startswith("/"):
                return ToolResult(
                    success=False,
                    error=f"path 参数不能包含 '..' 或以 '/' 开头。收到：'{path}'",
                    error_type=ErrorType.PARAMETER,
                    retryable=False,
                    tool_name=tool_name,
                )

        return None  # 验证通过

    except Exception as e:
        return ToolResult(
            success=False,
            error=f"参数验证失败: {str(e)}",
            error_type=ErrorType.PARAMETER,
            retryable=False,
            tool_name=tool_name,
        )


# ============================================================
# 断路器（代码级，不依赖提示）
# ============================================================

class CircuitBreaker:
    """
    断路器模式：连续失败 N 次后暂停调用。

    三种状态：
    - CLOSED（正常）：请求正常通过
    - OPEN（熔断）：请求被拒绝，直接返回错误
    - HALF_OPEN（试探）：允许一个请求通过，成功则关闭断路器
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        # HALF_OPEN: 允许一次试探
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"断路器打开：连续 {self.failure_count} 次失败，"
                f"暂停 {self.recovery_timeout} 秒"
            )


# 每个工具独立的断路器
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(tool_name: str) -> CircuitBreaker:
    if tool_name not in _circuit_breakers:
        _circuit_breakers[tool_name] = CircuitBreaker()
    return _circuit_breakers[tool_name]


# ============================================================
# 幂等性键管理
# ============================================================

_idempotency_cache: dict[str, ToolResult] = {}


def check_idempotency(key: Optional[str]) -> Optional[ToolResult]:
    """检查幂等性缓存，如果存在则返回缓存结果。"""
    if key and key in _idempotency_cache:
        logger.info(f"幂等性命中：key={key}")
        return _idempotency_cache[key]
    return None


def store_idempotency(key: Optional[str], result: ToolResult):
    """存储幂等性结果。"""
    if key:
        _idempotency_cache[key] = result


# ============================================================
# 错误分类
# ============================================================

def classify_error(status_code: int, error_body: str) -> tuple[ErrorType, bool, str]:
    """
    将 HTTP 错误分类为结构化信息。

    返回：(error_type, retryable, message)
    """
    if status_code == 422:
        # GitHub 422 通常是参数错误 — 最常见的问题
        return (
            ErrorType.PARAMETER,
            False,
            f"参数验证失败 (HTTP 422)。GitHub 返回：{error_body}。"
            f"常见原因：owner/repo 拼写错误、缺少必填字段、enum 值不对（如 state 应为 'open' 而非 'opened'）。",
        )
    elif status_code == 404:
        return (
            ErrorType.PARAMETER,
            False,
            f"资源不存在 (HTTP 404)。请检查 owner/repo 是否正确，issue/PR 编号是否存在。",
        )
    elif status_code == 403:
        return (
            ErrorType.UNAVAILABLE,
            False,
            f"权限不足 (HTTP 403)。可能原因：Token 过期、超出速率限制、仓库为私有且无访问权限。",
        )
    elif status_code == 401:
        return (
            ErrorType.UNAVAILABLE,
            False,
            f"认证失败 (HTTP 401)。请检查 GitHub Token 是否有效。",
        )
    elif status_code == 429:
        retry_after = 60  # 默认等待时间
        return (
            ErrorType.TRANSIENT,
            True,
            f"速率限制 (HTTP 429)。请等待 {retry_after} 秒后重试。",
        )
    elif status_code >= 500:
        return (
            ErrorType.TRANSIENT,
            True,
            f"GitHub 服务端错误 (HTTP {status_code})。请稍后重试。",
        )
    else:
        return (
            ErrorType.OUTPUT,
            False,
            f"未知错误 (HTTP {status_code})：{error_body}",
        )


# ============================================================
# 主执行函数
# ============================================================

async def execute_github_tool(
    tool_name: str,
    params: dict,
    github_client: httpx.AsyncClient,
    max_retries: int = 3,
) -> ToolResult:
    """
    防御性工具执行入口。

    流程：参数验证 → 断路器检查 → 幂等性检查 → 执行 → 错误分类 → 重试
    """
    start_time = time.monotonic()

    # 1. 参数预验证（防止 422 的第一道防线）
    validation_error = validate_params(tool_name, params)
    if validation_error:
        return validation_error

    # 2. 断路器检查
    breaker = get_circuit_breaker(tool_name)
    if not breaker.can_execute():
        return ToolResult(
            success=False,
            error=f"工具 {tool_name} 的断路器已打开，暂停调用。请稍后重试。",
            error_type=ErrorType.UNAVAILABLE,
            retryable=True,
            tool_name=tool_name,
        )

    # 3. 幂等性检查
    idempotency_key = params.get("idempotency_key")
    cached = check_idempotency(idempotency_key)
    if cached:
        return cached

    # 4. 执行（带重试）
    last_result = None
    for attempt in range(1, max_retries + 1):
        try:
            result = await _dispatch_to_github(tool_name, params, github_client)
            result.attempt = attempt
            result.tool_name = tool_name

            if result.success:
                breaker.record_success()
                store_idempotency(idempotency_key, result)
                result.execution_time_ms = (time.monotonic() - start_time) * 1000
                return result

            # 失败：判断是否可重试
            if not result.retryable or attempt == max_retries:
                breaker.record_failure()
                result.execution_time_ms = (time.monotonic() - start_time) * 1000
                return result

            # 指数退避
            wait_time = min(2 ** attempt, 30)
            logger.info(f"重试 {tool_name} 第 {attempt} 次，等待 {wait_time} 秒")
            await _async_sleep(wait_time)

        except httpx.TimeoutException:
            last_result = ToolResult(
                success=False,
                error=f"请求超时（第 {attempt} 次尝试）",
                error_type=ErrorType.TRANSIENT,
                retryable=True,
                tool_name=tool_name,
                attempt=attempt,
            )
            if attempt < max_retries:
                wait_time = min(2 ** attempt, 30)
                await _async_sleep(wait_time)
                continue

        except httpx.ConnectError:
            last_result = ToolResult(
                success=False,
                error="无法连接到 GitHub API，请检查网络。",
                error_type=ErrorType.UNAVAILABLE,
                retryable=True,
                tool_name=tool_name,
                attempt=attempt,
            )
            breaker.record_failure()
            break  # 连接错误不重试

    # 所有重试都失败
    if last_result:
        last_result.execution_time_ms = (time.monotonic() - start_time) * 1000
        return last_result

    return ToolResult(
        success=False,
        error="未知错误：所有重试都失败",
        error_type=ErrorType.OUTPUT,
        retryable=False,
        tool_name=tool_name,
        execution_time_ms=(time.monotonic() - start_time) * 1000,
    )


# ============================================================
# GitHub API 调度器（映射工具名到实际 API 调用）
# ============================================================

# 工具名 → GitHub API endpoint 的精确映射
# 这是防止选错 endpoint 的核心：Agent 只需传工具名，路由逻辑在这里
TOOL_ENDPOINT_MAP = {
    "get_repo":          "GET /repos/{owner}/{repo}",
    "list_issues":       "GET /repos/{owner}/{repo}/issues",
    "list_pull_requests": "GET /repos/{owner}/{repo}/pulls",
    "get_file_content":  "GET /repos/{owner}/{repo}/contents/{path}",
    "search_code":       "GET /search/code",
    "create_issue":      "POST /repos/{owner}/{repo}/issues",
    "create_comment":    "POST /repos/{owner}/{repo}/issues/{issue_number}/comments",
}


async def _dispatch_to_github(
    tool_name: str,
    params: dict,
    client: httpx.AsyncClient,
) -> ToolResult:
    """
    将工具调用映射到具体的 GitHub API 请求。

    Agent 永远不直接构造 URL — 这一层负责路由。
    """
    if tool_name not in TOOL_ENDPOINT_MAP:
        return ToolResult(
            success=False,
            error=f"未知工具：{tool_name}。可用工具：{list(TOOL_ENDPOINT_MAP.keys())}",
            error_type=ErrorType.PARAMETER,
            retryable=False,
        )

    method, path_template = TOOL_ENDPOINT_MAP[tool_name].split(" ", 1)

    # 构造路径参数
    try:
        path = path_template.format(**params)
    except KeyError as e:
        return ToolResult(
            success=False,
            error=f"缺少路径参数：{e}",
            error_type=ErrorType.PARAMETER,
            retryable=False,
        )

    url = f"https://api.github.com{path}"

    # 构造查询参数（GET 请求）或请求体（POST 请求）
    query_params = {}
    json_body = {}

    if method == "GET":
        # 过滤掉路径参数，剩余的作为查询参数
        path_params = _extract_path_params(path_template)
        query_params = {
            k: v for k, v in params.items()
            if k not in path_params and v is not None
        }
    elif method == "POST":
        # POST 请求的 body
        body_fields = _get_body_fields(tool_name)
        json_body = {
            k: v for k, v in params.items()
            if k in body_fields and v is not None
        }

    # 发送请求
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    # Token 从环境变量或客户端配置中获取
    if "authorization" not in client.headers:
        pass  # 客户端已配置 Token

    response = await client.request(
        method=method,
        url=url,
        params=query_params,
        json=json_body if method == "POST" else None,
        headers=headers,
        timeout=30.0,
    )

    if response.status_code < 400:
        return ToolResult(
            success=True,
            data=_format_response(tool_name, response.json()),
        )
    else:
        error_type, retryable, message = classify_error(
            response.status_code,
            response.text[:500],  # 截断避免过长
        )
        return ToolResult(
            success=False,
            error=message,
            error_type=error_type,
            retryable=retryable,
        )


def _extract_path_params(template: str) -> set[str]:
    """从路径模板中提取参数名，如 /repos/{owner}/{repo} → {'owner', 'repo'}"""
    import re
    return set(re.findall(r"\{(\w+)\}", template))


def _get_body_fields(tool_name: str) -> set[str]:
    """返回每个工具的请求体字段。"""
    body_fields_map = {
        "create_issue": {"title", "body", "labels", "assignees"},
        "create_comment": {"body"},
    }
    return body_fields_map.get(tool_name, set())


def _format_response(tool_name: str, data: Any) -> Any:
    """
    格式化 GitHub API 响应，截断过大数据，提取关键字段。

    防止超大响应撑爆 LLM 上下文窗口。
    """
    import json

    # 对列表响应，只保留关键字段
    if isinstance(data, list):
        formatted = []
        for item in data[:30]:  # 最多 30 条
            if isinstance(item, dict):
                formatted.append(_extract_key_fields(tool_name, item))
            else:
                formatted.append(item)
        return formatted

    # 对对象响应，提取关键字段
    if isinstance(data, dict):
        return _extract_key_fields(tool_name, data)

    return data


def _extract_key_fields(tool_name: str, item: dict) -> dict:
    """根据工具类型提取关键字段，避免返回过大的原始 JSON。"""
    key_fields = {
        "get_repo": ["id", "name", "full_name", "description", "default_branch", "language", "stargazers_count"],
        "list_issues": ["number", "title", "state", "labels", "user.login", "created_at", "html_url"],
        "list_pull_requests": ["number", "title", "state", "user.login", "head.ref", "base.ref", "html_url"],
        "get_file_content": ["name", "path", "size", "content", "encoding"],
        "search_code": ["name", "path", "repository.full_name", "html_url"],
        "create_issue": ["number", "title", "state", "html_url"],
        "create_comment": ["id", "body", "created_at", "html_url"],
    }

    fields = key_fields.get(tool_name, list(item.keys())[:10])
    result = {}
    for field_path in fields:
        parts = field_path.split(".")
        value = item
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        if value is not None:
            # 用点号路径作为 key
            result[field_path] = value

    return result


async def _async_sleep(seconds: float):
    """异步等待。"""
    import asyncio
    await asyncio.sleep(seconds)
```

---

## Step 4: Agent 主循环集成

把上述组件集成到 Anthropic SDK 的 tool use 循环中：

```python
# agent/github_agent.py

import os
import json
import asyncio
from anthropic import Anthropic

from tools.github_tools import GITHUB_TOOL_SCHEMAS
from executor.github_executor import execute_github_tool, ToolResult

import httpx


async def run_github_agent(user_message: str):
    """
    GitHub Agent 主循环。

    关键设计：
    1. 工具 Schema 严格约束参数（防止 422）
    2. 执行层做参数预验证 + 重试 + 断路器（防止级联失败）
    3. 错误结构化返回给 LLM（让 LLM 能自我修正）
    4. 总步骤硬上限（防止无限循环）
    """
    client = Anthropic()
    github_token = os.environ.get("GITHUB_TOKEN")

    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {github_token}"},
        timeout=30.0,
    ) as http_client:

        messages = [{"role": "user", "content": user_message}]
        max_turns = 15  # 硬上限：最多 15 轮工具调用
        turn = 0

        while turn < max_turns:
            turn += 1

            # 调用 Claude
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=GITHUB_TOOL_SCHEMAS,
                messages=messages,
            )

            # 如果没有工具调用，Agent 完成了
            if response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                return final_text

            # 处理工具调用
            if response.stop_reason == "tool_use":
                # 把 Assistant 的响应加入消息历史
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_use_id = block.id

                        print(f"[Turn {turn}] 调用工具: {tool_name}")
                        print(f"  参数: {json.dumps(tool_input, ensure_ascii=False)[:200]}")

                        # 执行工具（带全部防御措施）
                        result: ToolResult = await execute_github_tool(
                            tool_name=tool_name,
                            params=tool_input,
                            github_client=http_client,
                        )

                        status = "成功" if result.success else "失败"
                        print(f"  结果: {status} (尝试 {result.attempt}, "
                              f"{result.execution_time_ms:.0f}ms)")

                        # 将结构化结果返回给 LLM
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result.to_llm_message()["content"],
                            **({"is_error": True} if not result.success else {}),
                        })

                # 把工具结果加入消息历史
                messages.append({"role": "user", "content": tool_results})

            else:
                # 非预期的 stop_reason
                return f"Agent 意外停止: {response.stop_reason}"

        return "Agent 达到最大轮次限制（15 轮），请简化任务后重试。"


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    result = asyncio.run(
        run_github_agent(
            "查看 anthropics/claude-code 仓库最近的 5 个 open issues，"
            "然后在第一个 issue 下面发一条评论说 '正在跟进此问题'"
        )
    )
    print(result)
```

---

## Step 5: 输出验证层

对工具返回的数据做二次验证，防止畸形数据级联腐化：

```python
# validation/output_validator.py

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class IssueOutput(BaseModel):
    """Issue 输出验证模型。"""
    number: int = Field(gt=0)
    title: str = Field(min_length=1)
    state: str = Field(pattern=r"^(open|closed)$")
    html_url: str = Field(pattern=r"^https://github\.com/")

    class Config:
        extra = "allow"  # 允许额外字段，但核心字段必须存在


class RepoOutput(BaseModel):
    """仓库输出验证模型。"""
    name: str
    full_name: str = Field(pattern=r"^[^/]+/[^/]+$")
    default_branch: str


class FileContentOutput(BaseModel):
    """文件内容输出验证模型。"""
    name: str
    path: str
    content: Optional[str] = None
    encoding: Optional[str] = None
    size: int = Field(ge=0)

    @field_validator("content")
    @classmethod
    def check_content_not_corrupted(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) == 0:
            # 空字符串可能意味着编码问题
            return None  # 标记为缺失，而非空
        return v


# 验证器注册表
OUTPUT_VALIDATORS = {
    "get_repo": RepoOutput,
    "list_issues": list,  # 列表类型用特殊处理
    "list_pull_requests": list,
    "get_file_content": FileContentOutput,
    "create_issue": IssueOutput,
    "create_comment": dict,
}


def validate_output(tool_name: str, data: Any) -> tuple[bool, Any, list[str]]:
    """
    验证工具输出。返回：(is_valid, validated_data, warnings)

    - is_valid: 数据是否可用
    - validated_data: 验证后的数据
    - warnings: 非致命问题列表
    """
    warnings = []

    # 空响应检测
    if data is None:
        return False, None, ["工具返回 null，可能是查询无结果或执行失败"]

    if isinstance(data, list) and len(data) == 0:
        return True, [], ["返回空列表，可能无匹配结果"]

    validator = OUTPUT_VALIDATORS.get(tool_name)
    if validator is None:
        return True, data, []  # 无验证器，直接返回

    # 列表类型：逐项验证
    if validator is list:
        if not isinstance(data, list):
            return False, data, [f"期望列表但收到 {type(data).__name__}"]
        validated_items = []
        item_validator = _get_list_item_validator(tool_name)
        for i, item in enumerate(data):
            if item_validator:
                try:
                    validated = item_validator.model_validate(item)
                    validated_items.append(validated.model_dump())
                except Exception as e:
                    warnings.append(f"第 {i} 项验证失败: {e}")
                    validated_items.append(item)  # 保留原始数据
            else:
                validated_items.append(item)
        return True, validated_items, warnings

    # 单对象类型
    try:
        validated = validator.model_validate(data)
        return True, validated.model_dump(), warnings
    except Exception as e:
        warnings.append(f"输出验证失败: {e}")
        return True, data, warnings  # 返回原始数据，但附带警告


def _get_list_item_validator(tool_name: str) -> Optional[type]:
    """获取列表项的验证模型。"""
    validators = {
        "list_issues": IssueOutput,
        "list_pull_requests": IssueOutput,  # PR 和 Issue 结构类似
    }
    return validators.get(tool_name)
```

---

## Step 6: 完整的测试方案

```python
# tests/test_github_tools.py

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from executor.github_executor import (
    execute_github_tool,
    validate_params,
    classify_error,
    CircuitBreaker,
    ErrorType,
    ToolResult,
    check_idempotency,
    store_idempotency,
)
from validation.output_validator import validate_output


# ============================================================
# 参数验证测试（防止 422 的核心）
# ============================================================

class TestParameterValidation:
    """测试参数预验证是否能拦截常见错误。"""

    def test_valid_params_pass(self):
        """正常参数通过验证。"""
        result = validate_params("get_repo", {"owner": "anthropics", "repo": "claude-code"})
        assert result is None  # None = 验证通过

    def test_owner_with_slash_rejected(self):
        """owner 包含 '/' 被拦截（用户传了 owner/repo 组合）。"""
        result = validate_params("get_repo", {"owner": "anthropics/claude-code", "repo": "claude-code"})
        assert result is not None
        assert result.success is False
        assert "owner" in result.error.lower() or "/" in result.error

    def test_owner_as_url_rejected(self):
        """owner 传了完整 URL 被拦截。"""
        result = validate_params("get_repo", {"owner": "https://github.com/anthropics", "repo": "claude-code"})
        assert result is not None
        assert result.success is False

    def test_state_opened_corrected(self):
        """state='opened' 被纠正为 'open'。"""
        result = validate_params("list_issues", {"owner": "a", "repo": "b", "state": "opened"})
        assert result is not None
        assert "open" in result.error  # 错误信息中应提示正确值

    def test_invalid_state_rejected(self):
        """无效的 state 值被拦截。"""
        result = validate_params("list_issues", {"owner": "a", "repo": "b", "state": "pending"})
        assert result is not None
        assert result.success is False

    def test_negative_issue_number_rejected(self):
        """负数 issue 编号被拦截。"""
        result = validate_params("create_comment", {
            "owner": "a", "repo": "b", "issue_number": -1, "body": "test",
        })
        assert result is not None
        assert result.success is False

    def test_path_traversal_rejected(self):
        """路径穿越被拦截。"""
        result = validate_params("get_file_content", {
            "owner": "a", "repo": "b", "path": "../../../etc/passwd",
        })
        assert result is not None
        assert result.success is False

    def test_path_absolute_rejected(self):
        """绝对路径被拦截。"""
        result = validate_params("get_file_content", {
            "owner": "a", "repo": "b", "path": "/etc/passwd",
        })
        assert result is not None
        assert result.success is False


# ============================================================
# 错误分类测试
# ============================================================

class TestErrorClassification:
    """测试 HTTP 错误是否被正确分类。"""

    def test_422_is_parameter_error(self):
        """422 错误归类为参数错误，不可重试。"""
        error_type, retryable, msg = classify_error(422, '{"message":"Validation Failed"}')
        assert error_type == ErrorType.PARAMETER
        assert retryable is False
        assert "422" in msg

    def test_404_is_parameter_error(self):
        """404 归类为参数错误（资源不存在）。"""
        error_type, retryable, _ = classify_error(404, "Not Found")
        assert error_type == ErrorType.PARAMETER
        assert retryable is False

    def test_429_is_transient(self):
        """429 归类为瞬时故障，可重试。"""
        error_type, retryable, _ = classify_error(429, "Rate limited")
        assert error_type == ErrorType.TRANSIENT
        assert retryable is True

    def test_500_is_transient(self):
        """5xx 归类为瞬时故障，可重试。"""
        error_type, retryable, _ = classify_error(503, "Service Unavailable")
        assert error_type == ErrorType.TRANSIENT
        assert retryable is True

    def test_403_is_unavailable(self):
        """403 归类为不可用（权限问题）。"""
        error_type, retryable, _ = classify_error(403, "Forbidden")
        assert error_type == ErrorType.UNAVAILABLE
        assert retryable is False


# ============================================================
# 断路器测试
# ============================================================

class TestCircuitBreaker:
    """测试断路器行为。"""

    def test_starts_closed(self):
        """断路器初始状态为 CLOSED。"""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == "CLOSED"
        assert cb.can_execute() is True

    def test_opens_after_threshold(self):
        """连续失败达到阈值后打开。"""
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == "OPEN"
        assert cb.can_execute() is False

    def test_half_open_after_timeout(self):
        """超时后进入半开状态。"""
        import time
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "OPEN"
        time.sleep(0.15)
        assert cb.can_execute() is True
        assert cb.state == "HALF_OPEN"

    def test_success_resets(self):
        """成功调用重置断路器。"""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0


# ============================================================
# 幂等性测试
# ============================================================

class TestIdempotency:
    """测试幂等性缓存。"""

    def test_same_key_returns_cached(self):
        """相同幂等键返回缓存结果。"""
        _idempotency_cache.clear()
        key = "test-key-123"
        result = ToolResult(success=True, data={"id": 1})
        store_idempotency(key, result)
        cached = check_idempotency(key)
        assert cached is not None
        assert cached.data == {"id": 1}

    def test_different_key_returns_none(self):
        """不同幂等键返回 None。"""
        _idempotency_cache.clear()
        store_idempotency("key-a", ToolResult(success=True, data="a"))
        assert check_idempotency("key-b") is None


# ============================================================
# 输出验证测试
# ============================================================

class TestOutputValidation:
    """测试输出验证。"""

    def test_valid_issue_output(self):
        """有效的 Issue 输出通过验证。"""
        data = {"number": 42, "title": "Bug report", "state": "open", "html_url": "https://github.com/a/b/issues/42"}
        is_valid, validated, warnings = validate_output("create_issue", data)
        assert is_valid is True
        assert len(warnings) == 0

    def test_empty_list_returns_warning(self):
        """空列表返回警告但标记为有效。"""
        is_valid, data, warnings = validate_output("list_issues", [])
        assert is_valid is True
        assert len(warnings) > 0

    def test_null_returns_invalid(self):
        """null 返回无效。"""
        is_valid, _, warnings = validate_output("get_repo", None)
        assert is_valid is False

    def test_missing_required_field_returns_warning(self):
        """缺少必需字段返回警告。"""
        data = {"number": 42}  # 缺少 title, state, html_url
        is_valid, _, warnings = validate_output("create_issue", data)
        assert len(warnings) > 0


# ============================================================
# 端到端集成测试（Mock GitHub API）
# ============================================================

class TestEndToEnd:
    """端到端测试，Mock GitHub API 响应。"""

    @pytest.mark.asyncio
    async def test_successful_get_repo(self):
        """正常获取仓库信息。"""
        mock_response = httpx.Response(
            200,
            json={"name": "claude-code", "full_name": "anthropics/claude-code", "default_branch": "main", "language": "Python"},
        )
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response

        result = await execute_github_tool(
            "get_repo",
            {"owner": "anthropics", "repo": "claude-code"},
            mock_client,
        )
        assert result.success is True
        assert result.data["name"] == "claude-code"

    @pytest.mark.asyncio
    async def test_422_returns_structured_error(self):
        """422 错误返回结构化信息，不崩溃。"""
        mock_response = httpx.Response(
            422,
            json={"message": "Validation Failed", "errors": [{"field": "state", "code": "invalid"}]},
        )
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response

        result = await execute_github_tool(
            "list_issues",
            {"owner": "anthropics", "repo": "claude-code", "state": "open"},
            mock_client,
        )
        assert result.success is False
        assert result.error_type == ErrorType.PARAMETER
        assert result.retryable is False
        assert "422" in result.error

    @pytest.mark.asyncio
    async def test_429_triggers_retry(self):
        """429 触发重试，第二次成功。"""
        rate_limit_response = httpx.Response(429, json={"message": "rate limited"})
        success_response = httpx.Response(200, json=[{"number": 1, "title": "Test", "state": "open", "html_url": "https://github.com/a/b/issues/1"}])

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.side_effect = [rate_limit_response, success_response]

        result = await execute_github_tool(
            "list_issues",
            {"owner": "anthropics", "repo": "claude-code"},
            mock_client,
            max_retries=3,
        )
        assert result.success is True
        assert result.attempt == 2
        assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_owner_slash_repo_rejected_before_api_call(self):
        """owner/repo 组合格式在发请求前就被拦截。"""
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        result = await execute_github_tool(
            "get_repo",
            {"owner": "anthropics/claude-code", "repo": "claude-code"},
            mock_client,
        )
        assert result.success is False
        assert result.error_type == ErrorType.PARAMETER
        # API 请求不应该被发出
        mock_client.request.assert_not_called()
```

---

## 设计总结

整个方案的防御层次：

```
用户请求
    ↓
[第 1 层] Schema 约束 — enum、pattern、additionalProperties:false
    ↓         防止 LLM 生成无效参数
[第 2 层] 参数预验证 — Pydantic 模型校验
    ↓         在发请求前拦截格式错误（如 owner 含 /、state 拼错）
[第 3 层] 路由映射 — TOOL_ENDPOINT_MAP
    ↓         Agent 不直接构造 URL，由代码映射工具名到 endpoint
[第 4 层] 断路器 — 连续失败后暂停
    ↓         防止持续调用一个已经出问题的 API
[第 5 层] 重试 + 指数退避 — 瞬时故障自动恢复
    ↓         429/5xx/超时自动重试，422 不重试
[第 6 层] 结构化错误返回 — 错误信息 + 建议
    ↓         LLM 收到错误后能自我修正参数
[第 7 层] 输出验证 — Pydantic 模型校验返回数据
    ↓         防止畸形数据级联腐化后续步骤
[第 8 层] 响应截断 — 提取关键字段，控制上下文大小
              防止超大响应撑爆 LLM 上下文
```

**关键设计决策：**

1. **Agent 不直接构造 GitHub API URL** — 所有路由在 `TOOL_ENDPOINT_MAP` 中静态定义，Agent 只需传工具名和参数。这从根本上防止了选错 endpoint。

2. **enum 覆盖所有可选值** — `state` 用 `enum: ["open", "closed", "all"]` 而非自由文本，`sort` 用 `enum` 约束。LLM 没有猜测空间。

3. **422 不重试，直接返回给 LLM** — 422 是参数错误，重试同样的参数没有意义。把错误信息返回给 LLM，让它修正参数后重试，这是最高效的恢复路径。

4. **幂等性键防重复** — 写入操作必须携带 `idempotency_key`，重试不会产生重复副作用。

5. **断路器在代码层实现** — 不依赖提示中的"不要循环超过 N 次"，而是在执行层硬编码 3 次失败后暂停 30 秒。
