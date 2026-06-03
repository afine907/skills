---
paths: ["**/*.test.ts", "**/*.spec.ts", "**/__tests__/**", "**/*.test.js", "**/*.spec.js"]
---

# Testing Conventions

## Framework

- Use Jest as the test runner
- Use React Testing Library for component tests
- Use Supertest for API endpoint tests

## File Naming

- Test files: `*.test.ts` or `*.spec.ts`
- Test directories: `__tests__/`
- Co-locate tests with source files when possible

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx    ← Co-located
├── utils/
│   └── helpers.ts
└── __tests__/
    └── integration/
        └── api.test.ts    ← Separate directory
```

## Test Structure

Use the AAA pattern (Arrange, Act, Assert):

```typescript
describe('calculateTotal', () => {
  it('should sum all item prices', () => {
    // Arrange
    const items = [{ price: 10 }, { price: 20 }, { price: 30 }];
    
    // Act
    const total = calculateTotal(items);
    
    // Assert
    expect(total).toBe(60);
  });
});
```

## Naming Conventions

- `describe` block: The function or component name
- `it` block: What the test verifies, starting with "should"
- Use `it` not `test` for consistency

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user with valid data', () => {});
    it('should throw an error for duplicate email', () => {});
  });
});
```

## Assertions

- Use `expect()` with matchers
- Prefer `toBeInTheDocument()` for DOM elements
- Use `toHaveBeenCalledWith()` for spy verification

```typescript
// ✅ Good
expect(screen.getByText('Submit')).toBeInTheDocument();
expect(mockFn).toHaveBeenCalledWith(expectedArgs);

// ❌ Avoid
expect(screen.getByText('Submit')).toBeTruthy();
expect(mockFn).toBeCalledTimes(1);
```

## Coverage

- New functions must have unit tests
- Complex logic requires integration tests
- Aim for 80%+ coverage on business logic
- Skip coverage for simple wrappers and types

## Mocking

- Mock external dependencies, not internal modules
- Use `jest.mock()` at the top of the file
- Clear mocks in `beforeEach`

```typescript
beforeEach(() => {
  jest.clearAllMocks();
});
```
