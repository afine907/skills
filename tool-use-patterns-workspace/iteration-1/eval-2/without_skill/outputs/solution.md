# Multi-Tool Orchestration with Rollback

## Problem

An Agent must execute three sequential steps -- query user info, create a payment order, send an email -- and roll back all completed steps if any step fails.

## Design Principles

1. **Explicit rollback handlers** -- every step declares its inverse operation up front.
2. **Saga pattern** -- each step is a local transaction; failure triggers compensating transactions in reverse order.
3. **Idempotency** -- rollback handlers must be safe to call even if the step was only partially executed.
4. **Observability** -- log every step start, success, failure, and rollback attempt.

## Architecture

```
Step 1: Query User DB  ──success──>  Step 2: Create Payment Order  ──success──>  Step 3: Send Email
       │                                      │                                        │
     fail                                   fail                                     fail
       │                                      │                                        │
       ▼                                      ▼                                        ▼
   (nothing to                           Rollback Step 2                          Rollback Step 3
    roll back)                           Rollback Step 1                          Rollback Step 2
                                                                                   Rollback Step 1
```

## Python Implementation

### Core Saga Runner

```python
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class Step:
    """One step in the saga: an action and its compensating (rollback) action."""

    name: str
    action: Callable[..., Any]
    rollback: Callable[..., None]
    result: Any = field(default=None, init=False)
    executed: bool = field(default=False, init=False)


class SagaRunner:
    """Execute a list of Steps sequentially; roll back completed steps on failure."""

    def __init__(self, steps: list[Step]):
        self.steps = steps

    def run(self) -> list[Any]:
        completed: list[Step] = []

        for step in self.steps:
            try:
                logger.info("Executing step: %s", step.name)
                step.result = step.action()
                step.executed = True
                completed.append(step)
                logger.info("Step %s succeeded", step.name)
            except Exception as exc:
                logger.error("Step %s failed: %s", step.name, exc)
                self._rollback(completed)
                raise RuntimeError(
                    f"Saga aborted at step '{step.name}': {exc}"
                ) from exc

        return [s.result for s in self.steps]

    def _rollback(self, completed: list[Step]) -> None:
        for step in reversed(completed):
            try:
                logger.info("Rolling back step: %s", step.name)
                step.rollback()
                logger.info("Rollback of %s succeeded", step.name)
            except Exception as exc:
                # Log but do not swallow -- we still want to attempt
                # remaining rollbacks.
                logger.critical(
                    "Rollback of %s failed: %s. Manual intervention required.",
                    step.name,
                    exc,
                )
```

### Concrete Usage: DB + Payment + Email

```python
import smtplib
from email.mime.text import MIMEText

import requests
import sqlite3


# ---------- Tool implementations ----------

def query_user_db(user_id: int) -> dict:
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"User {user_id} not found")
        return dict(row)
    finally:
        conn.close()


def create_payment_order(user: dict, amount: float) -> dict:
    """Call the payment API. Returns the order object (must include order_id)."""
    resp = requests.post(
        "https://api.payment.example.com/orders",
        json={"user_id": user["id"], "amount": amount},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()  # expects {"order_id": "ord_xxx", ...}


def cancel_payment_order(order_id: str) -> None:
    resp = requests.delete(
        f"https://api.payment.example.com/orders/{order_id}",
        timeout=10,
    )
    resp.raise_for_status()


def send_email(to: str, subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@example.com"
    msg["To"] = to
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("user", "password")
        server.send_message(msg)


# Email is fire-and-forget in most systems; "rollback" means sending
# a cancellation notice. If the original email was never delivered
# (e.g. SMTP timeout), the cancellation is harmless.
def send_cancellation_email(to: str, order_id: str) -> None:
    send_email(
        to=to,
        subject="Order Cancelled",
        body=f"Order {order_id} has been cancelled.",
    )


# ---------- Orchestrator ----------

def place_order(user_id: int, amount: float) -> dict:
    """
    End-to-end flow:
      1. Look up the user in the database.
      2. Create a payment order via the payment API.
      3. Send a confirmation email.

    On failure at any step, all prior steps are rolled back.
    """
    user: dict = {}
    order: dict = {}

    def step1_action():
        nonlocal user
        user = query_user_db(user_id)
        return user

    def step2_action():
        nonlocal order
        order = create_payment_order(user, amount)
        return order

    def step3_action():
        send_email(
            to=user["email"],
            subject="Order Confirmed",
            body=f"Your order {order['order_id']} for {amount} has been created.",
        )

    # Rollback handlers are closures that capture the state from earlier steps.
    saga = SagaRunner(
        steps=[
            Step(
                name="query_user",
                action=step1_action,
                rollback=lambda: None,  # read-only, nothing to undo
            ),
            Step(
                name="create_payment_order",
                action=step2_action,
                rollback=lambda: cancel_payment_order(order["order_id"]),
            ),
            Step(
                name="send_email",
                action=step3_action,
                rollback=lambda: send_cancellation_email(
                    user["email"], order["order_id"]
                ),
            ),
        ]
    )

    results = saga.run()
    logger.info("Order placed successfully: %s", results)
    return order


# ---------- Entry point ----------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        result = place_order(user_id=42, amount=99.99)
        print(f"Success: {result}")
    except RuntimeError as e:
        print(f"Failed and rolled back: {e}")
```

## Async Variant (for I/O-bound tools)

If the tools are async (e.g. `aiohttp`, async DB drivers), replace `Callable` with coroutines:

```python
import asyncio

class AsyncSagaRunner:
    def __init__(self, steps: list["AsyncStep"]):
        self.steps = steps

    async def run(self) -> list[Any]:
        completed: list[AsyncStep] = []
        for step in self.steps:
            try:
                logger.info("Executing step: %s", step.name)
                step.result = await step.action()
                step.executed = True
                completed.append(step)
            except Exception as exc:
                logger.error("Step %s failed: %s", step.name, exc)
                await self._rollback(completed)
                raise RuntimeError(
                    f"Saga aborted at step '{step.name}': {exc}"
                ) from exc
        return [s.result for s in self.steps]

    async def _rollback(self, completed):
        for step in reversed(completed):
            try:
                logger.info("Rolling back step: %s", step.name)
                await step.rollback()
            except Exception as exc:
                logger.critical(
                    "Rollback of %s failed: %s", step.name, exc
                )
```

## When This Pattern Applies to an LLM Agent

When the Agent uses tool-calling (function calling) rather than writing code directly, the same logic maps to a **structured tool-use loop**:

```
Agent prompt (system message excerpt):

You have three tools available:
  - lookup_user(user_id) -> user_info
  - create_order(user_id, amount) -> {order_id}
  - send_confirmation_email(email, order_id) -> success

RULES:
  1. Call tools in order: lookup_user -> create_order -> send_confirmation_email.
  2. If any tool call fails, IMMEDIATELY call rollback tools for all
     previously completed steps in reverse order:
       - cancel_order(order_id)   (if create_order succeeded)
  3. After rolling back, report the failure to the user.
  4. Do NOT skip rollback even if the error looks transient.
```

A simplified prompt-based implementation:

```python
import json

TOOLS = [
    {
        "name": "lookup_user",
        "description": "Get user info by ID",
        "parameters": {"user_id": "int"},
    },
    {
        "name": "create_order",
        "description": "Create a payment order",
        "parameters": {"user_id": "int", "amount": "float"},
    },
    {
        "name": "send_confirmation_email",
        "description": "Send order confirmation email",
        "parameters": {"email": "str", "order_id": "str"},
    },
    {
        "name": "cancel_order",
        "description": "Cancel an existing order (rollback only)",
        "parameters": {"order_id": "str"},
    },
]

SYSTEM_PROMPT = """\
You are an order-processing agent. Follow this exact sequence:

Step 1: Call lookup_user(user_id).
Step 2: Call create_order(user_id, amount).
Step 3: Call send_confirmation_email(email, order_id).

ROLLBACK RULES:
- If Step 2 fails: call nothing (Step 1 is read-only).
- If Step 3 fails: call cancel_order(order_id) to undo Step 2.

Always report the final status (success or failure + what was rolled back).
"""
```

## Key Takeaways

| Concern | Solution |
|---------|----------|
| Step ordering | Sequential execution with explicit dependency on prior results |
| Rollback on failure | Reverse-order compensating transactions (Saga pattern) |
| Partial rollback failure | Log critically, continue rolling back remaining steps |
| Read-only steps | No-op rollback (e.g. DB SELECT) |
| Idempotency | Rollback handlers should be safe to call multiple times |
| Async tools | Swap to `async/await` variant; same structure |
| LLM Agent context | Encode rollback rules in the system prompt; use tool descriptions that include rollback tools |
