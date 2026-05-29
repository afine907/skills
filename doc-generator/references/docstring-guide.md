# Docstring Guide

## Python (Google Style)

### Function

```python
def fetch_user(
    user_id: int,
    include_posts: bool = False,
    timeout: float = 30.0,
) -> User:
    """Fetch a user by their ID.

    Retrieves user information from the database and optionally
    includes their recent posts.

    Args:
        user_id: The unique identifier of the user.
        include_posts: If True, also fetch the user's recent posts.
            Defaults to False.
        timeout: Maximum time in seconds to wait for the query.
            Defaults to 30.0.

    Returns:
        A User object containing the user's profile data. If
        include_posts is True, the posts field will be populated.

    Raises:
        UserNotFoundError: If no user exists with the given ID.
        TimeoutError: If the database query exceeds the timeout.

    Example:
        >>> user = fetch_user(123, include_posts=True)
        >>> print(user.name)
        'Alice'
    """
```

### Class

```python
class UserRepository:
    """Repository for user data access.

    Provides methods to query and mutate user records in the
    database. All methods are async and return domain objects.

    Attributes:
        db: The database connection pool.
        cache: Redis client for caching.

    Example:
        >>> repo = UserRepository(db_pool, redis_client)
        >>> user = await repo.get_by_id(123)
    """

    def __init__(self, db: AsyncPool, cache: Redis):
        """Initialize the repository.

        Args:
            db: Async database connection pool.
            cache: Redis client for read-through caching.
        """
```

### Module

```python
"""User management module.

This module provides the core user management functionality,
including user creation, authentication, and profile management.

Typical usage example:

    from app.users import UserService

    service = UserService()
    user = await service.create_user(email='alice@example.com')
"""
```

## TypeScript (TSDoc)

### Function

```typescript
/**
 * Fetches a user by their unique identifier.
 *
 * @param userId - The unique identifier of the user to fetch.
 * @param options - Optional configuration for the request.
 * @param options.includePosts - Whether to include user's posts.
 * @param options.timeout - Request timeout in milliseconds.
 * @returns A promise that resolves to the User object.
 * @throws {UserNotFoundError} When no user exists with the given ID.
 * @throws {TimeoutError} When the request exceeds the timeout.
 *
 * @example
 * ```typescript
 * const user = await fetchUser(123, { includePosts: true });
 * console.log(user.name); // 'Alice'
 * ```
 */
async function fetchUser(
  userId: number,
  options?: { includePosts?: boolean; timeout?: number }
): Promise<User> {
```

### Interface

```typescript
/**
 * Configuration options for the API client.
 *
 * @remarks
 * All options have sensible defaults. Only `apiKey` is required
 * for basic usage.
 */
interface ApiClientOptions {
  /** The API key for authentication. */
  apiKey: string;

  /** Base URL for API requests. @defaultValue "https://api.example.com" */
  baseUrl?: string;

  /** Request timeout in milliseconds. @defaultValue 30000 */
  timeout?: number;

  /** Number of retry attempts for failed requests. @defaultValue 3 */
  retries?: number;
}
```

### React Component

```tsx
/**
 * A button component that handles loading states and confirmation.
 *
 * @example
 * ```tsx
 * <SubmitButton
 *   onClick={handleSubmit}
 *   loading={isSubmitting}
 *   confirm="Are you sure?"
 * >
 *   Submit Form
 * </SubmitButton>
 * ```
 */
interface SubmitButtonProps {
  /** Click handler. Receives the click event. */
  onClick: (e: React.MouseEvent) => void;

  /** Whether to show a loading spinner. @defaultValue false */
  loading?: boolean;

  /** Confirmation message shown before executing onClick. */
  confirm?: string;

  /** Button content. */
  children: React.ReactNode;
}
```

## Java (Javadoc)

```java
/**
 * Fetches a user by their unique identifier.
 *
 * <p>This method retrieves user information from the database
 * and optionally includes their recent posts in the response.</p>
 *
 * @param userId       the unique identifier of the user
 * @param includePosts whether to include the user's recent posts
 * @param timeout      maximum time to wait, in milliseconds
 * @return the User object, or empty if not found
 * @throws UserNotFoundException if no user exists with the given ID
 * @throws TimeoutException      if the query exceeds the timeout
 *
 * @see UserRepository#findById(long)
 * @since 2.0.0
 */
public Optional<User> fetchUser(
    long userId,
    boolean includePosts,
    Duration timeout
) throws UserNotFoundException, TimeoutException {
```

## Writing Guidelines

### What to Document

| Item | Document? | Priority |
|------|-----------|----------|
| Public API functions/methods | Always | High |
| Classes and interfaces | Always | High |
| Module/package level | Yes | Medium |
| Complex algorithms | Yes | High |
| Private helper functions | If complex | Low |
| Simple getters/setters | No | - |
| Self-evident code | No | - |

### Description Best Practices

1. **First line**: One-sentence summary ending with a period
2. **Blank line**: Separates summary from details
3. **Details**: Additional context, usage notes, caveats
4. **Parameters**: Describe constraints, valid ranges, defaults
5. **Returns**: Describe the type and what it represents
6. **Exceptions**: When and why they are thrown

### Anti-Patterns

```python
# BAD: Restating the signature
def get_user(user_id: int) -> User:
    """Gets a user by user_id."""
    ...

# GOOD: Explains behavior and constraints
def get_user(user_id: int) -> User:
    """Fetch a user from the primary database.

    Returns cached data if available and fresh. Raises
    UserNotFoundError if the user does not exist.
    """
```
