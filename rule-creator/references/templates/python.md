---
paths: ["**/*.py"]
---

# Python Conventions

## Code Style

- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Line length: 88 characters (Black default)

## Naming Conventions

```python
# ✅ Good
def calculate_total(items: list[Item]) -> float:
    """Calculate total price of all items."""
    total = sum(item.price for item in items)
    return total

class UserService:
    """Handle user operations."""
    
    MAX_RETRIES = 3
    
    def get_user(self, user_id: str) -> User:
        """Fetch user by ID."""
        pass

# ❌ Avoid
def CalculateTotal(items):
    total = sum(item.price for item in items)
    return total

class user_service:
    max_retries = 3
    
    def GetUser(self, user_id):
        pass
```

### Names
- `snake_case` for functions, variables, methods
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- `_leading_underscore` for private attributes
- `trailing_underscore` to avoid keyword conflicts

## Type Hints

Always use type hints:

```python
from typing import Optional

# ✅ Good
def process_data(
    items: list[dict],
    timeout: float = 30.0,
    retry: bool = False
) -> Optional[Result]:
    """Process data with optional retry."""
    pass

# ❌ Avoid
def process_data(items, timeout=30.0, retry=False):
    pass
```

## Docstrings

Use Google-style docstrings:

```python
def fetch_user(user_id: str, include_posts: bool = False) -> User:
    """Fetch a user by ID.
    
    Args:
        user_id: The unique user identifier
        include_posts: Whether to include user's posts
        
    Returns:
        User object with requested data
        
    Raises:
        UserNotFoundError: If user doesn't exist
        APIError: If external API fails
    """
    pass
```

## Error Handling

```python
# ✅ Good
try:
    result = await api.fetch_user(user_id)
except ValidationError as e:
    logger.warning(f"Invalid user ID: {user_id}", extra={"error": e})
    raise
except APIError as e:
    logger.error(f"API failed for user {user_id}", extra={"error": e})
    raise ServiceUnavailableError("User service unavailable") from e

# ❌ Avoid
try:
    result = await api.fetch_user(user_id)
except:
    pass
```

## Async/Await

- Use `async/await` for I/O operations
- Don't mix sync and async code
- Use `asyncio.gather()` for parallel operations

```python
# ✅ Good
async def get_multiple_users(user_ids: list[str]) -> list[User]:
    """Fetch multiple users in parallel."""
    tasks = [fetch_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)

# ❌ Avoid
def get_multiple_users(user_ids):
    return [fetch_user(uid) for uid in user_ids]  # Sequential!
```

## Testing

- Use pytest
- Name test files `test_*.py`
- Use fixtures for setup
- Use `@pytest.mark.parametrize` for multiple inputs

```python
import pytest

@pytest.fixture
def sample_user():
    return User(id="1", name="Test User")

def test_calculate_total(sample_user):
    items = [Item(price=10), Item(price=20)]
    assert calculate_total(items) == 30

@pytest.mark.parametrize("items,expected", [
    ([], 0),
    ([Item(price=10)], 10),
    ([Item(price=10), Item(price=20)], 30),
])
def test_calculate_total_parametrized(items, expected):
    assert calculate_total(items) == expected
```

## Imports

```python
# ✅ Good — Grouped and sorted
import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import UserCreate, UserResponse

# ❌ Avoid
from .schemas import UserResponse
from fastapi import APIRouter
import logging
from .database import get_db
from typing import Optional
```
