---
paths: ["src/**/*.ts", "src/**/*.tsx"]
---

# TypeScript Conventions

## Type Safety

- Use `strict: true` in tsconfig
- Avoid `any` type — use `unknown` if type is truly unknown
- Use interfaces for object shapes, types for unions/intersections

```typescript
// ✅ Good
interface User {
  id: string;
  name: string;
  email: string;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

// ❌ Avoid
const user: any = { id: '1', name: 'John' };
```

## Function Types

- Always specify return types for exported functions
- Use `void` for functions with no return value
- Use `Promise<T>` for async functions

```typescript
// ✅ Good
export function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

export async function fetchUser(id: string): Promise<User> {
  const response = await api.get(`/users/${id}`);
  return response.data;
}

// ❌ Avoid
export function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

## Enums vs Unions

- Prefer union types over enums for simple cases
- Use enums when you need reverse mapping

```typescript
// ✅ Good — Union type
type Direction = 'up' | 'down' | 'left' | 'right';

// ✅ Good — Enum when needed
enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
}
```

## Utility Types

Use built-in utility types:

```typescript
// Partial — All properties optional
type UpdateUser = Partial<User>;

// Pick — Only specific properties
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit — Exclude properties
type CreateUser = Omit<User, 'id'>;

// Record — Object with specific keys
type UserRoles = Record<string, 'admin' | 'user' | 'guest'>;
```

## Type Guards

Use type guards for runtime type checking:

```typescript
// ✅ Good
function isError(value: unknown): value is Error {
  return value instanceof Error;
}

if (isError(error)) {
  console.error(error.message);
}

// ✅ Good — Discriminated unions
type Result<T> = 
  | { success: true; data: T }
  | { success: false; error: string };

function handleResult(result: Result<User>) {
  if (result.success) {
    console.log(result.data.name);
  } else {
    console.error(result.error);
  }
}
```

## Generics

Use generics for reusable components:

```typescript
// ✅ Good
function first<T>(array: T[]): T | undefined {
  return array[0];
}

const num = first([1, 2, 3]);      // number
const str = first(['a', 'b']);     // string

// ✅ Good — Constrained generics
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

## Avoid

- `any` type — Use `unknown` and narrow
- `@ts-ignore` — Fix the type error instead
- Type assertions (`as`) — Use type guards
- `!` non-null assertion — Handle null explicitly
