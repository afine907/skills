# Faker for Database Seeding

Using `@faker-js/faker` to generate realistic seed data for database development and testing.

## Installation

```bash
npm install @faker-js/faker --save-dev
```

## Basic Seed Script

```typescript
// scripts/seed.ts
import { faker } from '@faker-js/faker'
import { db } from '../src/db'

async function seed() {
  // Create users
  const users = Array.from({ length: 50 }, () => ({
    id: faker.string.uuid(),
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    email: faker.internet.email(),
    avatar: faker.image.avatar(),
    createdAt: faker.date.past({ years: 2 }),
  }))

  await db.user.createMany({ data: users })

  // Create posts linked to users
  const posts = users.flatMap(user =>
    Array.from({ length: faker.number.int({ min: 1, max: 10 }) }, () => ({
      id: faker.string.uuid(),
      title: faker.lorem.sentence(),
      content: faker.lorem.paragraphs(3),
      authorId: user.id,
      published: faker.datatype.boolean(0.8),
      createdAt: faker.date.between({
        from: user.createdAt,
        to: new Date(),
      }),
    }))
  )

  await db.post.createMany({ data: posts })

  console.log(`Seeded ${users.length} users and ${posts.length} posts`)
}

seed().catch(console.error)
```

## Factory Pattern with Faker

```typescript
// factories/user.factory.ts
import { faker } from '@faker-js/faker'
import { db } from '../src/db'

export class UserFactory {
  static build(overrides?: Partial<User>) {
    return {
      id: faker.string.uuid(),
      firstName: faker.person.firstName(),
      lastName: faker.person.lastName(),
      email: faker.internet.email(),
      passwordHash: '$2b$10$hashedpassword', // bcrypt hash of "password"
      role: faker.helpers.arrayElement(['user', 'admin', 'moderator']),
      isActive: true,
      createdAt: faker.date.past({ years: 1 }),
      ...overrides,
    }
  }

  static async create(overrides?: Partial<User>) {
    const data = this.build(overrides)
    return db.user.create({ data })
  }

  static async createMany(count: number, overrides?: Partial<User>) {
    const data = Array.from({ length: count }, () => this.build(overrides))
    return db.user.createMany({ data })
  }
}
```

## Generating Related Data

```typescript
// factories/order.factory.ts
import { faker } from '@faker-js/faker'

export class OrderFactory {
  static build(userIds: string[]) {
    const itemCount = faker.number.int({ min: 1, max: 5 })
    const items = Array.from({ length: itemCount }, () => ({
      productId: faker.string.uuid(),
      quantity: faker.number.int({ min: 1, max: 10 }),
      unitPrice: parseFloat(faker.commerce.price({ min: 5, max: 200 })),
    }))

    const total = items.reduce((sum, i) => sum + i.quantity * i.unitPrice, 0)

    return {
      id: faker.string.uuid(),
      userId: faker.helpers.arrayElement(userIds),
      status: faker.helpers.weightedArrayElement([
        { value: 'completed', weight: 0.5 },
        { value: 'pending', weight: 0.3 },
        { value: 'cancelled', weight: 0.1 },
        { value: 'refunded', weight: 0.1 },
      ]),
      items,
      total: Math.round(total * 100) / 100,
      shippingAddress: {
        street: faker.location.streetAddress(),
        city: faker.location.city(),
        state: faker.location.state({ abbreviated: true }),
        zip: faker.location.zipCode(),
        country: 'US',
      },
      createdAt: faker.date.past({ years: 1 }),
    }
  }
}
```

## Seeding with Deterministic Data

```typescript
// Use fixed seed for reproducible test data
faker.seed(12345)

const deterministicUsers = Array.from({ length: 10 }, () => ({
  email: faker.internet.email(),
  name: faker.person.fullName(),
}))
// Same array every time
```

## Locale-Specific Data

```typescript
import { fakerEN_US, fakerJA, fakerDE } from '@faker-js/faker'

// Generate data in specific locales
const usUser = {
  name: fakerEN_US.person.fullName(),
  address: fakerEN_US.location.streetAddress(),
}

const japaneseUser = {
  name: fakerJA.person.fullName(),
  address: fakerJA.location.streetAddress(),
}
```

## Prisma Seed Example

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client'
import { faker } from '@faker-js/faker'

const prisma = new PrismaClient()

async function main() {
  // Clean existing data
  await prisma.post.deleteMany()
  await prisma.user.deleteMany()

  // Create 20 users
  for (let i = 0; i < 20; i++) {
    await prisma.user.create({
      data: {
        email: faker.internet.email(),
        name: faker.person.fullName(),
        posts: {
          create: Array.from(
            { length: faker.number.int({ min: 0, max: 5 }) },
            () => ({
              title: faker.lorem.sentence(),
              content: faker.lorem.paragraphs(2),
              published: faker.datatype.boolean(0.7),
            })
          ),
        },
      },
    })
  }

  console.log('Database seeded successfully')
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

## Best Practices

1. Always clean/seed in a transaction for atomicity
2. Use `faker.seed()` for deterministic test environments
3. Create factory classes with `.build()` (data only) and `.create()` (persisted) methods
4. Generate realistic relationships between entities
5. Use `faker.helpers.weightedArrayElement()` for realistic status distributions
6. Keep seed scripts separate from test fixtures
