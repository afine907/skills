# Faker Data Generation Guide

Faker generates realistic mock data for testing and development. This guide covers `@faker-js/faker`, the community-maintained fork.

## Installation

```bash
npm install @faker-js/faker --save-dev
```

## Basic Usage

```typescript
import { faker } from '@faker-js/faker'

// Set locale (optional)
faker.locale = 'en'

// Seed for reproducible data
faker.seed(123)
```

## Common Data Types

### Personal Information

```typescript
faker.person.fullName()       // "John Smith"
faker.person.firstName()      // "Alice"
faker.person.lastName()       // "Johnson"
faker.person.jobTitle()       // "Regional Accounts Director"
faker.internet.email()        // "bob59@example.com"
faker.phone.number()          // "(555) 123-4567"
faker.date.birthdate()        // Date object
```

### Addresses

```typescript
faker.location.streetAddress() // "786 Kihn Throughway"
faker.location.city()          // "Lake Raoul"
faker.location.state()         // "California"
faker.location.zipCode()       // "90210"
faker.location.country()       // "United States"
faker.location.latitude()      // 34.0522
```

### Internet & Tech

```typescript
faker.internet.url()           // "https://example.com"
faker.internet.domainName()    // "example.com"
faker.internet.ip()            // "192.168.1.1"
faker.internet.mac()           // "00:1a:2b:3c:4d:5e"
faker.system.fileName()        // "report.pdf"
faker.git.commitMessage()      // "fix: resolve login issue"
```

### Commerce & Finance

```typescript
faker.commerce.productName()   // "Ergonomic Steel Chair"
faker.commerce.price()         // "49.99"
faker.commerce.department()    // "Electronics"
faker.finance.amount()         // "382.52"
faker.finance.iban()           // "DE89370400440532013000"
faker.finance.creditCardNumber() // "4485-1234-5678-9012"
```

### Text & Content

```typescript
faker.lorem.sentence()         // "Voluptas qui qui et."
faker.lorem.paragraph()        // Multi-sentence paragraph
faker.lorem.paragraphs(3)      // Three paragraphs
faker.hacker.phrase()          // "If we bypass the firewall, we can get to the TCP port"
faker.company.catchPhrase()    // "Grass-roots 24/7 hub"
```

## Creating Test Fixtures

### Generate a User Object

```typescript
function createFakeUser(overrides?: Partial<User>): User {
  return {
    id: faker.string.uuid(),
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    email: faker.internet.email(),
    avatar: faker.image.avatar(),
    createdAt: faker.date.past(),
    ...overrides,
  }
}

// Generate multiple
const users = faker.helpers.multiple(createFakeUser, { count: 10 })
```

### Generate API Response

```typescript
function createFakeApiResponse<T>(data: T) {
  return {
    data,
    meta: {
      total: faker.number.int({ min: 50, max: 500 }),
      page: 1,
      perPage: 20,
    },
    requestId: faker.string.uuid(),
  }
}
```

### Generate with Weighted Distribution

```typescript
function createFakeOrder() {
  return {
    id: faker.string.uuid(),
    status: faker.helpers.weightedArrayElement([
      { value: 'completed', weight: 0.6 },
      { value: 'pending', weight: 0.25 },
      { value: 'cancelled', weight: 0.15 },
    ]),
    total: faker.commerce.price({ min: 10, max: 500 }),
    items: faker.number.int({ min: 1, max: 10 }),
  }
}
```

## Reproducible Data with Seeds

```typescript
// Same seed produces same data every time
faker.seed(42)
const user1 = faker.person.fullName() // Always the same name

// Reset seed in tests for consistency
beforeEach(() => {
  faker.seed(Date.now()) // Fresh random per test
})

// Or use fixed seed for snapshot tests
beforeEach(() => {
  faker.seed(12345) // Deterministic for snapshots
})
```

## Combining with MSW

```typescript
import { http, HttpResponse } from 'msw'
import { faker } from '@faker-js/faker'

const users = faker.helpers.multiple(
  () => ({
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
  }),
  { count: 50 }
)

export const handlers = [
  http.get('/api/users', ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page') ?? 1)
    const perPage = 20
    const start = (page - 1) * perPage

    return HttpResponse.json({
      data: users.slice(start, start + perPage),
      total: users.length,
      page,
    })
  }),
]
```

## Best Practices

1. Use `faker.seed()` in tests for deterministic results
2. Create factory functions with override support for flexibility
3. Use `faker.helpers.multiple()` for generating arrays
4. Set locale with `faker.locale = 'xx'` for region-specific data
5. Keep factory functions co-located with test files or in a shared `factories/` directory
