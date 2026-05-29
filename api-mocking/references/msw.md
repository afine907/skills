# Mock Service Worker (MSW) Guide

MSW intercepts requests at the network level using Service Worker API, providing seamless API mocking for browser and Node.js.

## Installation

```bash
npm install msw --save-dev
npx msw init public/ --save   # Creates service worker file in public/
```

## Basic Setup

### Define Handlers

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

const users = [
  { id: 1, name: 'Alice', email: 'alice@example.com' },
  { id: 2, name: 'Bob', email: 'bob@example.com' },
]

export const handlers = [
  // GET request
  http.get('/api/users', () => {
    return HttpResponse.json(users)
  }),

  // GET with path parameter
  http.get('/api/users/:id', ({ params }) => {
    const user = users.find(u => u.id === Number(params.id))
    if (!user) {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json(user)
  }),

  // POST request
  http.post('/api/users', async ({ request }) => {
    const body = await request.json()
    const newUser = { id: users.length + 1, ...body }
    users.push(newUser)
    return HttpResponse.json(newUser, { status: 201 })
  }),

  // Error response
  http.get('/api/error', () => {
    return HttpResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }),
]
```

### Browser Setup

```typescript
// src/mocks/browser.ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)
```

```typescript
// src/main.tsx (conditional start)
async function enableMocking() {
  if (process.env.NODE_ENV !== 'development') return
  const { worker } = await import('./mocks/browser')
  return worker.start({ onUnhandledRequest: 'bypass' })
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(<App />)
})
```

### Node.js Setup (for testing)

```typescript
// src/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

```typescript
// jest.setup.ts or vitest.setup.ts
import { server } from './src/mocks/server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## Advanced Patterns

### Response Delay (simulate latency)

```typescript
http.get('/api/slow', async () => {
  await delay(2000) // 2 second delay
  return HttpResponse.json({ data: 'loaded' })
})
```

### Conditional Responses

```typescript
http.get('/api/users', ({ request }) => {
  const url = new URL(request.url)
  const role = url.searchParams.get('role')

  if (role === 'admin') {
    return HttpResponse.json([{ id: 1, name: 'Admin', role: 'admin' }])
  }
  return HttpResponse.json(users)
})
```

### Network Error Simulation

```typescript
http.get('/api/unstable', () => {
  return HttpResponse.error()
})
```

### Request Assertion in Tests

```typescript
import { http, HttpResponse } from 'msw'
import { server } from './mocks/server'

it('sends correct request body', async () => {
  let capturedBody: any

  server.use(
    http.post('/api/users', async ({ request }) => {
      capturedBody = await request.json()
      return HttpResponse.json({ id: 3, ...capturedBody })
    })
  )

  await createUser({ name: 'Charlie' })
  expect(capturedBody).toEqual({ name: 'Charlie' })
})
```

### Override Handlers per Test

```typescript
it('handles 404', async () => {
  server.use(
    http.get('/api/users/:id', () => {
      return new HttpResponse(null, { status: 404 })
    })
  )

  const result = await fetchUser(999)
  expect(result).toBeNull()
})
```

## TypeScript Types

```typescript
import { http, HttpResponse, delay } from 'msw'

interface User {
  id: number
  name: string
  email: string
}

// Typed handler
http.get<never, never, User[]>('/api/users', () => {
  return HttpResponse.json([
    { id: 1, name: 'Alice', email: 'alice@example.com' }
  ])
})
```

## Best Practices

1. Keep handlers in a central `handlers.ts` file
2. Use `server.resetHandlers()` in `afterEach` to isolate tests
3. Use `onUnhandledRequest: 'error'` in tests to catch unmocked requests
4. Use `onUnhandledRequest: 'bypass'` in development to allow real API calls
5. Mock only what you need; let non-API requests pass through
