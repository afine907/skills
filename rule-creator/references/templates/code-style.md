---
paths: ["src/**/*", "lib/**/*"]
---

# Code Style Guidelines

## Formatting

- Use Prettier for formatting
- Run `npm run format` before committing
- No manual formatting changes

## Indentation

- 2 spaces for TypeScript/JavaScript
- 4 spaces for Python
- Tabs for Makefiles

## Naming Conventions

### Variables and Functions
- Use `camelCase` for variables and functions
- Use `PascalCase` for classes, interfaces, and components
- Use `UPPER_SNAKE_CASE` for constants

```typescript
// ✅ Good
const userName = 'John';
function calculateTotal() {}
const MAX_RETRIES = 3;
class UserService {}

// ❌ Avoid
const user_name = 'John';
function CalculateTotal() {}
const maxRetries = 3;
class user_service {}
```

### Files
- Use `kebab-case` for file names: `user-service.ts`
- Use `PascalCase` for React components: `UserProfile.tsx`
- Test files: `*.test.ts` or `*.spec.ts`

## Imports

- Group imports: external → internal → relative
- Use absolute imports for `src/`
- Remove unused imports

```typescript
// ✅ Good
import React from 'react';
import { useRouter } from 'next/router';

import { UserService } from '@/services/user';
import { Button } from '@/components/Button';

import { formatDate } from './utils';

// ❌ Avoid
import { formatDate } from './utils';
import { Button } from '@/components/Button';
import React from 'react';
```

## Comments

- Use `//` for single-line comments
- Use `/** */` for JSDoc on public APIs
- Explain *why*, not *what*

```typescript
// ✅ Good
// Cache to avoid repeated API calls during render
const cache = new Map();

/**
 * Calculates total price with tax
 * @param subtotal - Price before tax
 * @param taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 */
function calculateTotal(subtotal: number, taxRate: number): number {}

// ❌ Avoid
// This is a cache
const cache = new Map();

// Calculate total
function calculateTotal(subtotal: number, taxRate: number): number {}
```

## Error Handling

- Use specific error types
- Always handle promise rejections
- Log errors with context

```typescript
// ✅ Good
try {
  await saveUser(data);
} catch (error) {
  if (error instanceof ValidationError) {
    logger.warn('Invalid user data', { fields: error.fields });
  } else {
    logger.error('Failed to save user', { error, userId: data.id });
    throw new SaveError('User save failed', { cause: error });
  }
}

// ❌ Avoid
try {
  await saveUser(data);
} catch (e) {
  console.log(e);
}
```
