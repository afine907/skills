# Factory Pattern for Database Seeding

The factory pattern creates reusable, composable data generators for test and seed data.

## Core Concepts

- **Factory**: A class/function that produces test data instances
- **build()**: Creates data object without persisting to database
- **create()**: Creates and persists to database
- **traits**: Named variations of a factory (e.g., "admin", "inactive")
- **sequences**: Auto-incrementing unique values

## Basic Factory (TypeScript)

```typescript
// factories/user.factory.ts
import { faker } from '@faker-js/faker'

let sequence = 0

export const UserFactory = {
  build(overrides?: Partial<User>): User {
    sequence++
    return {
      id: faker.string.uuid(),
      email: `user${sequence}@example.com`,
      firstName: faker.person.firstName(),
      lastName: faker.person.lastName(),
      role: 'user',
      isActive: true,
      createdAt: new Date(),
      ...overrides,
    }
  },

  async create(overrides?: Partial<User>): Promise<User> {
    const data = this.build(overrides)
    return prisma.user.create({ data })
  },

  async createMany(count: number, overrides?: Partial<User>): Promise<User[]> {
    return Promise.all(
      Array.from({ length: count }, () => this.create(overrides))
    )
  },
}
```

## Traits (Named Variations)

```typescript
export const UserFactory = {
  build(overrides?: Partial<User>): User {
    return { /* base defaults */ ...overrides }
  },

  // Trait methods return factory with preset overrides
  admin(overrides?: Partial<User>) {
    return this.build({ role: 'admin', ...overrides })
  },

  inactive(overrides?: Partial<User>) {
    return this.build({ isActive: false, deactivatedAt: new Date(), ...overrides })
  },

  withAvatar(overrides?: Partial<User>) {
    return this.build({ avatar: faker.image.avatar(), ...overrides })
  },

  async createAdmin(overrides?: Partial<User>) {
    const data = this.admin(overrides)
    return prisma.user.create({ data })
  },
}
```

## Associations (Related Models)

```typescript
export const PostFactory = {
  build(authorId: string, overrides?: Partial<Post>): Post {
    return {
      id: faker.string.uuid(),
      title: faker.lorem.sentence(),
      content: faker.lorem.paragraphs(3),
      authorId,
      published: true,
      createdAt: faker.date.recent(),
      ...overrides,
    }
  },

  async create(authorId: string, overrides?: Partial<Post>): Promise<Post> {
    return prisma.post.create({ data: this.build(authorId, overrides) })
  },
}

// Usage: create user with posts
async function createUserWithPosts(postCount = 3) {
  const user = await UserFactory.create()
  const posts = await Promise.all(
    Array.from({ length: postCount }, () => PostFactory.create(user.id))
  )
  return { user, posts }
}
```

## Sequence Counter

```typescript
class SequenceFactory {
  private counter = 0

  next(): number {
    return ++this.counter
  }

  reset(): void {
    this.counter = 0
  }
}

const seq = new SequenceFactory()

export const EmailFactory = {
  build(): string {
    return `test-user-${seq.next()}@example.com`
  },
}

// Always unique emails even in parallel
const emails = Array.from({ length: 100 }, () => EmailFactory.build())
```

## Python Factory (factory_boy)

```python
# factories/user_factory.py
import factory
from factory import fuzzy
from app.models import User, Post, db

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    id = factory.LazyFunction(uuid4)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: f'{o.first_name.lower()}@example.com')
    role = 'user'
    is_active = True

    class Params:
        admin = factory.Trait(
            role='admin',
            email=factory.LazyAttribute(lambda o: f'admin-{o.first_name.lower()}@example.com')
        )
        inactive = factory.Trait(
            is_active=False,
            deactivated_at=factory.LazyFunction(datetime.utcnow)
        )


class PostFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session = db.session

    id = factory.LazyFunction(uuid4)
    title = factory.Faker('sentence')
    content = factory.Faker('paragraphs', nb=3)
    author = factory.SubFactory(UserFactory)
    published = True
```

```python
# Usage
user = UserFactory()
admin = UserFactory(admin=True)
posts = PostFactory.create_batch(5, author=user)
```

## Nesting Factories

```typescript
// Create a complete scenario in one call
export async function createFullScenario() {
  // Users
  const admin = await UserFactory.createAdmin()
  const users = await UserFactory.createMany(10)

  // Posts for each user
  const posts = await Promise.all(
    users.flatMap(user =>
      Array.from({ length: 3 }, () => PostFactory.create(user.id))
    )
  )

  // Comments on posts
  const comments = await Promise.all(
    posts.flatMap(post =>
      Array.from({ length: 5 }, () =>
        CommentFactory.create(post.id, faker.helpers.arrayElement(users).id)
      )
    )
  )

  return { admin, users, posts, comments }
}
```

## Cleanup Utilities

```typescript
// Track created records for cleanup
class FactoryTracker {
  private created: { model: string; id: string }[] = []

  track(model: string, id: string) {
    this.created.push({ model, id })
  }

  async cleanup() {
    // Delete in reverse order (respect foreign keys)
    for (const record of this.created.reverse()) {
      await prisma[record.model].delete({ where: { id: record.id } })
    }
    this.created = []
  }
}

export const tracker = new FactoryTracker()
```

## Best Practices

1. Keep factories simple -- one factory per model
2. Use `build()` for unit tests (no DB), `create()` for integration tests
3. Implement traits for common variations (admin, inactive, etc.)
4. Use sequences for unique fields (emails, usernames)
5. Clean up created data in `afterEach` hooks
6. Co-locate factories with their models
7. Use `SubFactory` for related model creation
