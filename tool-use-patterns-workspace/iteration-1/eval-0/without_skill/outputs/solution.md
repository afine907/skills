# Defensive GitHub API Tool Calling for Anthropic SDK Agents

## Problem Analysis

Common failure modes when an LLM agent calls GitHub API:

1. **Wrong endpoint** -- e.g. `PATCH /repos/{owner}/{repo}/issues/{issue_number}` vs `PATCH /repos/{owner}/{repo}/pulls/{pull_number}`
2. **Missing required parameters** -- e.g. `POST /repos/{owner}/{repo}/issues` without `title`
3. **Wrong HTTP method** -- e.g. `GET` instead of `POST`
4. **Malformed parameter values** -- e.g. passing a string where an integer is expected, or omitting `{owner}` placeholder substitution
5. **Endpoint / parameter confusion** -- e.g. mixing up `pull_number` and `issue_number`

The root cause: the LLM is generating free-form tool calls from a flat list of tools with JSON Schema descriptions, without structural guidance.

## Solution: Three Layers of Defense

```
Layer 1: Tool Schema Design       -- make wrong calls hard to construct
Layer 2: Pre-call Validation       -- reject bad calls before they hit the network
Layer 3: Post-call Error Recovery  -- handle 4xx/5xx with targeted retry logic
```

---

## Layer 1: Tool Schema Design

### Principle: One tool per *intent*, not per endpoint

Instead of exposing raw GitHub endpoints as tools, expose **intent-based tools** that encapsulate the correct endpoint, method, and parameter mapping internally.

```python
# --- tools.py ---

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolParam:
    """A single parameter definition."""
    name: str
    type: str  # "string", "integer", "boolean", "array", "object"
    description: str
    required: bool = False
    enum: list[str] | None = None
    pattern: str | None = None  # regex for validation
    default: Any = None


@dataclass
class ToolSpec:
    """
    A self-contained tool definition that knows exactly how to map
    LLM-generated arguments to a real API call.
    """
    name: str
    description: str
    method: str                          # GET, POST, PATCH, DELETE, PUT
    endpoint_template: str               # e.g. "/repos/{owner}/{repo}/issues"
    params: list[ToolParam] = field(default_factory=list)
    path_params: list[str] = field(default_factory=list)   # params that go into the URL path
    query_params: list[str] = field(default_factory=list)  # params that go into the query string
    body_params: list[str] = field(default_factory=list)   # params that go into the JSON body

    def to_anthropic_tool(self) -> dict:
        """Convert to Anthropic tool_use format."""
        properties = {}
        required = []
        for p in self.params:
            prop: dict[str, Any] = {"type": p.type, "description": p.description}
            if p.enum:
                prop["enum"] = p.enum
            properties[p.name] = prop
            if p.required:
                required.append(p.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
```

### Define tools with explicit intent boundaries

```python
# --- github_tools.py ---

from tools import ToolSpec, ToolParam

# Instead of one generic "call_github_api" tool, create intent-specific tools:

ISSUE_TOOLS = [
    ToolSpec(
        name="list_issues",
        description="List issues for a repository. Use state='open' or state='closed' to filter.",
        method="GET",
        endpoint_template="/repos/{owner}/{repo}/issues",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
            ToolParam("state", "string", "Issue state filter", enum=["open", "closed", "all"], default="open"),
            ToolParam("labels", "string", "Comma-separated label names", required=False),
            ToolParam("per_page", "integer", "Results per page (max 100)", default=30),
        ],
        path_params=["owner", "repo"],
        query_params=["state", "labels", "per_page"],
    ),

    ToolSpec(
        name="get_issue",
        description="Get a single issue by number.",
        method="GET",
        endpoint_template="/repos/{owner}/{repo}/issues/{issue_number}",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
            ToolParam("issue_number", "integer", "Issue number", required=True),
        ],
        path_params=["owner", "repo", "issue_number"],
    ),

    ToolSpec(
        name="create_issue",
        description="Create a new issue in a repository.",
        method="POST",
        endpoint_template="/repos/{owner}/{repo}/issues",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
            ToolParam("title", "string", "Issue title (required by GitHub)", required=True),
            ToolParam("body", "string", "Issue body in markdown", required=False),
            ToolParam("labels", "array", "Label names to apply", required=False),
            ToolParam("assignees", "array", "Usernames to assign", required=False),
        ],
        path_params=["owner", "repo"],
        body_params=["title", "body", "labels", "assignees"],
    ),

    ToolSpec(
        name="update_issue",
        description="Update an existing issue. Only include fields you want to change.",
        method="PATCH",
        endpoint_template="/repos/{owner}/{repo}/issues/{issue_number}",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
            ToolParam("issue_number", "integer", "Issue number", required=True),
            ToolParam("title", "string", "New title", required=False),
            ToolParam("body", "string", "New body", required=False),
            ToolParam("state", "string", "New state", enum=["open", "closed"], required=False),
            ToolParam("labels", "array", "New label list (replaces existing)", required=False),
        ],
        path_params=["owner", "repo", "issue_number"],
        body_params=["title", "body", "state", "labels"],
    ),
]

PULL_REQUEST_TOOLS = [
    ToolSpec(
        name="list_pull_requests",
        description="List pull requests for a repository.",
        method="GET",
        endpoint_template="/repos/{owner}/{repo}/pulls",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
            ToolParam("state", "string", "PR state filter", enum=["open", "closed", "all"], default="open"),
            ToolParam("per_page", "integer", "Results per page (max 100)", default=30),
        ],
        path_params=["owner", "repo"],
        query_params=["state", "per_page"],
    ),

    ToolSpec(
        name="get_pull_request",
        description="Get a single pull request by number.",
        method="GET",
        endpoint_template="/repos/{owner}/{repo}/pulls/{pull_number}",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
            ToolParam("pull_number", "integer", "Pull request number", required=True),
        ],
        path_params=["owner", "repo", "pull_number"],
    ),
]

ALL_TOOLS = ISSUE_TOOLS + PULL_REQUEST_TOOLS
```

**Why this helps:** The LLM sees `create_issue` with a `title` field marked `required`, not a generic `call_api` with 47 optional params. The schema itself constrains the output.

---

## Layer 2: Pre-call Validation

Before sending any request to GitHub, validate the tool call against the spec.

```python
# --- validator.py ---

import re
from dataclasses import dataclass
from typing import Any

from tools import ToolSpec, ToolParam


@dataclass
class ValidationError:
    field: str
    message: str
    severity: str  # "error" blocks execution, "warn" logs but proceeds


class ToolCallValidator:
    """Validates LLM-generated tool calls against their ToolSpec before execution."""

    def validate(self, tool_spec: ToolSpec, arguments: dict[str, Any]) -> list[ValidationError]:
        errors: list[ValidationError] = []

        # 1. Check all required params are present
        for param in tool_spec.params:
            if param.required and param.name not in arguments:
                errors.append(ValidationError(
                    field=param.name,
                    message=f"Missing required parameter '{param.name}'. "
                            f"Description: {param.description}",
                    severity="error",
                ))

        # 2. Check for unknown parameters (likely hallucinated by LLM)
        known_names = {p.name for p in tool_spec.params}
        for key in arguments:
            if key not in known_names:
                errors.append(ValidationError(
                    field=key,
                    message=f"Unknown parameter '{key}' is not accepted by '{tool_spec.name}'. "
                            f"Valid parameters: {sorted(known_names)}",
                    severity="error",
                ))

        # 3. Type coercion and validation per parameter
        for param in tool_spec.params:
            if param.name not in arguments:
                continue
            value = arguments[param.name]
            param_errors = self._validate_param(param, value)
            errors.extend(param_errors)

        # 4. Validate that path parameters can be interpolated
        for path_param in tool_spec.path_params:
            if path_param in arguments:
                val = str(arguments[path_param])
                if not val or val.strip() == "":
                    errors.append(ValidationError(
                        field=path_param,
                        message=f"Path parameter '{path_param}' cannot be empty.",
                        severity="error",
                    ))

        return errors

    def _validate_param(self, param: ToolParam, value: Any) -> list[ValidationError]:
        errors = []

        # Enum check
        if param.enum and value not in param.enum:
            errors.append(ValidationError(
                field=param.name,
                message=f"'{param.name}' must be one of {param.enum}, got '{value}'.",
                severity="error",
            ))

        # Type coercion for integers (LLMs often return "42" instead of 42)
        if param.type == "integer":
            try:
                int(value)
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    field=param.name,
                    message=f"'{param.name}' must be an integer, got '{value}' ({type(value).__name__}).",
                    severity="error",
                ))

        # Pattern validation (e.g., GitHub username format)
        if param.pattern and isinstance(value, str):
            if not re.match(param.pattern, value):
                errors.append(ValidationError(
                    field=param.name,
                    message=f"'{param.name}' does not match expected pattern {param.pattern}.",
                    severity="warn",
                ))

        return errors
```

### Integrate validation into the execution loop

```python
# --- agent.py ---

import json
from typing import Any

import anthropic

from github_tools import ALL_TOOLS
from tools import ToolSpec
from validator import ToolCallValidator, ValidationError


class GitHubAgent:
    """
    Defensive GitHub API agent with three layers of protection:
    1. Intent-based tool schemas (prevention)
    2. Pre-call validation (detection)
    3. Error recovery with retry (correction)
    """

    MAX_TOOL_RETRIES = 2
    VALIDATION_FEEDBACK_PREFIX = "[Tool call rejected] "

    def __init__(self, github_token: str, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.github_token = github_token
        self.validator = ToolCallValidator()
        self.tool_specs: dict[str, ToolSpec] = {t.name: t for t in ALL_TOOLS}
        self.anthropic_tools = [t.to_anthropic_tool() for t in ALL_TOOLS]

    def run(self, user_message: str, max_turns: int = 10) -> str:
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

        for turn in range(max_turns):
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=self.anthropic_tools,
                messages=messages,
            )

            # If the model is done thinking, return
            if response.stop_reason == "end_turn":
                return self._extract_text(response)

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = self._process_tool_calls(response)
                # Feed results (including validation errors) back to the model
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

        return "Agent reached maximum turns without completing."

    def _process_tool_calls(self, response) -> list[dict]:
        """Process each tool call with validation and error recovery."""
        results = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            arguments = block.input
            tool_use_id = block.id

            # --- Layer 2: Pre-call validation ---
            tool_spec = self.tool_specs.get(tool_name)
            if not tool_spec:
                results.append(self._make_tool_result(
                    tool_use_id,
                    f"Unknown tool '{tool_name}'. Available tools: {list(self.tool_specs.keys())}",
                    is_error=True,
                ))
                continue

            validation_errors = self.validator.validate(tool_spec, arguments)

            # Separate hard errors from warnings
            hard_errors = [e for e in validation_errors if e.severity == "error"]
            warnings = [e for e in validation_errors if e.severity == "warn"]

            if hard_errors:
                # DO NOT call the API. Return structured error feedback to the LLM.
                error_summary = self._format_validation_errors(tool_name, arguments, hard_errors, tool_spec)
                results.append(self._make_tool_result(tool_use_id, error_summary, is_error=True))
                continue

            if warnings:
                # Log warnings but proceed
                for w in warnings:
                    print(f"[WARN] {w.field}: {w.message}")

            # --- Layer 3: Execute with error recovery ---
            result = self._execute_with_retry(tool_spec, arguments, tool_use_id)
            results.append(result)

        return results

    def _execute_with_retry(self, tool_spec: ToolSpec, arguments: dict, tool_use_id: str) -> dict:
        """Execute the API call, and on 4xx errors, return structured feedback for retry."""
        last_error = None

        for attempt in range(self.MAX_TOOL_RETRIES + 1):
            try:
                response_data = self._call_github_api(tool_spec, arguments)

                # Success (2xx)
                return self._make_tool_result(
                    tool_use_id,
                    json.dumps(response_data, indent=2),
                )
            except GitHubAPIError as e:
                last_error = e

                # Only retry on 422 (validation failed) -- these are often fixable
                if e.status_code == 422 and attempt < self.MAX_TOOL_RETRIES:
                    error_feedback = self._format_api_error(
                        tool_spec, arguments, e, attempt + 1
                    )
                    # Return error to LLM so it can self-correct
                    return self._make_tool_result(tool_use_id, error_feedback, is_error=True)

                # For other errors (404, 403, 500), don't retry -- just report
                error_feedback = self._format_api_error(tool_spec, arguments, e, attempt)
                return self._make_tool_result(tool_use_id, error_feedback, is_error=True)

        # Should not reach here, but just in case
        return self._make_tool_result(
            tool_use_id,
            f"Failed after {self.MAX_TOOL_RETRIES} retries: {last_error}",
            is_error=True,
        )

    def _call_github_api(self, tool_spec: ToolSpec, arguments: dict) -> dict:
        """Build and execute the actual GitHub API call."""
        import requests

        # Build the URL
        url = "https://api.github.com" + tool_spec.endpoint_template
        for param_name in tool_spec.path_params:
            url = url.replace(f"{{{param_name}}}", str(arguments[param_name]))

        # Build query params
        params = {}
        for param_name in tool_spec.query_params:
            if param_name in arguments:
                params[param_name] = arguments[param_name]

        # Build request body
        body = {}
        for param_name in tool_spec.body_params:
            if param_name in arguments:
                body[param_name] = arguments[param_name]

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.request(
            method=tool_spec.method,
            url=url,
            params=params if params else None,
            json=body if body else None,
            headers=headers,
        )

        if response.status_code >= 400:
            raise GitHubAPIError(
                status_code=response.status_code,
                response_body=response.text,
                url=url,
                method=tool_spec.method,
            )

        return response.json()

    def _format_validation_errors(
        self, tool_name: str, arguments: dict,
        errors: list[ValidationError], tool_spec: ToolSpec
    ) -> str:
        """Format validation errors into actionable feedback for the LLM."""
        lines = [
            f"Your tool call to '{tool_name}' was rejected before execution.",
            "",
            "Errors found:",
        ]
        for e in errors:
            lines.append(f"  - {e.message}")

        lines.append("")
        lines.append(f"Your arguments were: {json.dumps(arguments, indent=2)}")
        lines.append("")
        lines.append("Correct usage:")
        lines.append(f"  Tool: {tool_spec.name}")
        lines.append(f"  Description: {tool_spec.description}")
        lines.append(f"  Required params: {[p.name for p in tool_spec.params if p.required]}")
        lines.append(f"  Optional params: {[p.name for p in tool_spec.params if not p.required]}")

        return "\n".join(lines)

    def _format_api_error(
        self, tool_spec: ToolSpec, arguments: dict,
        error: "GitHubAPIError", attempt: int
    ) -> str:
        """Format an API error into actionable feedback for the LLM."""
        lines = [
            f"GitHub API returned {error.status_code} for {error.method} {error.url}",
            f"Attempt: {attempt + 1}/{self.MAX_TOOL_RETRIES + 1}",
            "",
            "Response body:",
            error.response_body[:1000],
            "",
            "Your arguments:",
            json.dumps(arguments, indent=2),
        ]

        # Add specific guidance for common 422 causes
        if error.status_code == 422:
            lines.append("")
            lines.append("Common causes of 422 errors:")
            lines.append("  - Required field is missing or empty string")
            lines.append("  - Invalid characters in owner/repo name")
            lines.append("  - Issue/PR number does not exist in this repo")
            lines.append("  - Label name does not exist in this repo")
            lines.append("")
            lines.append("Please check your arguments and try again with corrected values.")

        return "\n".join(lines)

    def _extract_text(self, response) -> str:
        """Extract text content from the response."""
        texts = [block.text for block in response.content if block.type == "text"]
        return "\n".join(texts) if texts else ""

    def _make_tool_result(self, tool_use_id: str, content: str, is_error: bool = False) -> dict:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content,
            "is_error": is_error,
        }


class GitHubAPIError(Exception):
    def __init__(self, status_code: int, response_body: str, url: str, method: str):
        self.status_code = status_code
        self.response_body = response_body
        self.url = url
        self.method = method
        super().__init__(f"{method} {url} -> {status_code}")
```

---

## Layer 3 (Bonus): System Prompt Guardrails

In addition to the code-level defenses, craft the system prompt to guide the LLM toward correct tool use:

```python
SYSTEM_PROMPT = """You are a GitHub operations assistant. You have access to tools
that interact with the GitHub API. Follow these rules strictly:

1. ALWAYS provide all required parameters. Never pass empty strings for required fields.
2. Use the EXACT parameter names defined in the tool schema. Do not invent parameters.
3. For issue_number and pull_number, always pass an integer (e.g. 42), not a string ("42").
4. owner = the GitHub username or org name. repo = the repository name (without .git).
5. If you are unsure about a value, ask the user before making a tool call.
6. When a tool call returns an error, READ the error message carefully and fix exactly
   what it says before retrying. Do not retry with the same arguments.
"""
```

---

## Complete Working Example

```python
# --- main.py ---

from agent import GitHubAgent


def main():
    agent = GitHubAgent(
        github_token="ghp_...",
        anthropic_api_key="sk-ant-...",
    )

    # Example: the LLM will call list_issues with proper params
    result = agent.run(
        "Show me the open issues on the anthropics/anthropic-sdk-python repo"
    )
    print(result)

    # Example: creating an issue -- the validator catches missing 'title'
    # If the LLM tries: create_issue(owner="foo", repo="bar")  -> rejected before API call
    result = agent.run(
        "Create an issue in myorg/myrepo titled 'Fix login bug' "
        "with body 'The login page returns 500 on Safari'"
    )
    print(result)


if __name__ == "__main__":
    main()
```

---

## Key Design Decisions Summary

| Decision | Why |
|---|---|
| One tool per intent, not per endpoint | Reduces LLM confusion between similar endpoints |
| `required: true` on schema fields | Anthropic SDK enforces this at the prompt level |
| Pre-call validation before HTTP | Catches errors without wasting API rate limit |
| Structured error feedback to LLM | Lets the model self-correct on the next turn |
| Type coercion warnings | LLMs often return `"42"` instead of `42` -- fix silently |
| Unknown parameter rejection | Catches LLM hallucinated params like `issueId` instead of `issue_number` |
| Max 2 retries on 422 only | 422 is often fixable; 404/403/500 are not worth retrying |
| System prompt guardrails | First line of defense, costs nothing |

## Adding New GitHub Endpoints

When you need to support a new endpoint, create a new `ToolSpec`:

```python
REPO_TOOLS = [
    ToolSpec(
        name="get_repo",
        description="Get repository metadata including description, stars, and default branch.",
        method="GET",
        endpoint_template="/repos/{owner}/{repo}",
        params=[
            ToolParam("owner", "string", "Repository owner", required=True),
            ToolParam("repo", "string", "Repository name", required=True),
        ],
        path_params=["owner", "repo"],
    ),
]
```

Then add `REPO_TOOLS` to `ALL_TOOLS` in `github_tools.py`. The validator and executor automatically pick up the new tool -- no other code changes needed.
