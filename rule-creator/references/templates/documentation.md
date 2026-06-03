---
paths: ["**/*.md", "docs/**/*"]
---

# Documentation Conventions

## README Structure

Every project should have a README with:

```markdown
# Project Name

Brief description of what this project does.

## Features

- Feature 1
- Feature 2

## Installation

```bash
npm install project-name
```

## Usage

```typescript
import { something } from 'project-name';

// Example usage
```

## API Reference

### `functionName(param: Type): ReturnType`

Description of what it does.

**Parameters:**
- `param` — Description

**Returns:**
- Description of return value

**Example:**
```typescript
const result = functionName('value');
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT
```

## Code Comments

### When to Comment

✅ **Good reasons to comment:**
- Explaining *why* something is done a certain way
- Documenting non-obvious behavior
- Marking TODOs with context
- Clarifying business logic

❌ **Bad reasons to comment:**
- Explaining *what* the code does (code should be self-documenting)
- Restating the code in English
- Commenting out code (use git history instead)

### Comment Style

```typescript
// ✅ Good — Explains why
// Cache results to avoid hitting rate limit during peak hours
const cache = new TTLCache({ ttl: 60_000 });

// ✅ Good — Documents non-obvious behavior
// Uses bitwise AND to check if user has all required permissions
// See: https://example.com/permissions-explained
function hasPermission(user: User, required: Permission[]): boolean {
  return (user.permissions & required) === required;
}

// ❌ Bad — Explains what (code is clear)
// Increment counter by 1
counter++;

// ❌ Bad — Restates code
// Check if x is greater than 0
if (x > 0) {}
```

## TODO Format

Use consistent TODO format:

```typescript
// TODO(username): Description of what needs to be done
// FIXME(username): Description of what's broken
// HACK(username): Description of why this is a workaround
// NOTE: Additional context

// Examples
// TODO(john): Add caching for this API call
// FIXME(jane): Race condition when multiple saves happen
// HACK(mike): Temporary workaround until upstream fixes #123
```

## Type Documentation

Document complex types:

```typescript
/**
 * Configuration for the API client
 * @property baseUrl - Base URL for all requests
 * @property timeout - Request timeout in milliseconds
 * @property retries - Number of retry attempts
 * @property headers - Default headers for all requests
 */
interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  headers?: Record<string, string>;
}
```

## Changelog Format

Follow Keep a Changelog:

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- OAuth2 authentication
- Rate limiting

### Changed
- Updated API to v2

### Fixed
- Null pointer exception in user service

### Removed
- Deprecated legacy endpoints

## [1.1.0] - 2024-01-01
...
```

## Markdown Style

- Use ATX-style headers (`#`, not underline)
- Use fenced code blocks with language
- Use `**bold**` for emphasis, *italics* for minor emphasis
- Use lists for multiple items
- Keep lines under 80 characters when possible
