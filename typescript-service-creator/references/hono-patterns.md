# Hono 模式参考

## 基础路由

```typescript
import { Hono } from 'hono'

const app = new Hono()

// 路由分组
const userRoutes = new Hono()
userRoutes.get('/', async (c) => {
  const users = await userService.findAll()
  return c.json(users)
})
userRoutes.get('/:id', async (c) => {
  const user = await userService.findById(c.req.param('id'))
  return c.json(user)
})

app.route('/api/users', userRoutes)
```

## 中间件

```typescript
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { prettyJSON } from 'hono/pretty-json'
import { jwt } from 'hono/jwt'

// 全局中间件
app.use('*', logger())
app.use('*', cors())

// 路由级中间件
app.use('/api/*', jwt({ secret: process.env.JWT_SECRET! }))

// 自定义中间件
const timing = async (c, next) => {
  const start = Date.now()
  await next()
  const duration = Date.now() - start
  c.header('X-Response-Time', `${duration}ms`)
}

app.use('*', timing)
```

## 类型安全的路由

```typescript
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
})

const app = new Hono()

app.post('/users', zValidator('json', UserSchema), async (c) => {
  const data = c.req.valid('json') // 类型安全
  const user = await userService.create(data)
  return c.json(user, 201)
})
```

## 错误处理

```typescript
import { HTTPException } from 'hono/http-exception'

// 全局错误处理
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return c.json({ error: err.message }, err.status)
  }
  console.error(err)
  return c.json({ error: 'Internal server error' }, 500)
})

// 404 处理
app.notFound((c) => {
  return c.json({ error: 'Not found' }, 404)
})

// 抛出错误
app.get('/users/:id', async (c) => {
  const user = await userService.findById(c.req.param('id'))
  if (!user) {
    throw new HTTPException(404, { message: 'User not found' })
  }
  return c.json(user)
})
```

## Cloudflare Workers 部署

```typescript
// src/index.ts
import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
  DB: D1Database
  KV: KVNamespace
  R2: R2Bucket
}

const app = new Hono<{ Bindings: Bindings }>()

app.use('*', cors())

app.get('/users', async (c) => {
  const { results } = await c.env.DB.prepare(
    'SELECT * FROM users'
  ).all()
  return c.json(results)
})

app.get('/cache/:key', async (c) => {
  const key = c.req.param('key')
  const value = await c.env.KV.get(key)
  return c.json({ key, value })
})

export default app
```

```toml
# wrangler.toml
name = "my-api"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxx"

[[kv_namespaces]]
binding = "KV"
id = "xxx"

[[r2_buckets]]
binding = "R2"
bucket_name = "my-bucket"
```

## RPC 模式

```typescript
// 服务端
const routes = app.get('/users', async (c) => {
  const users = await userService.findAll()
  return c.json(users)
})

export type AppType = typeof routes

// 客户端
import { hc } from 'hono/client'
import type { AppType } from './server'

const client = hc<AppType>('http://localhost:3000')
const res = await client.users.$get()
const users = await res.json()
```

## WebSocket

```typescript
import { Hono } from 'hono'
import { upgradeWebSocket } from 'hono/cloudflare-workers'

const app = new Hono()

app.get('/ws', upgradeWebSocket((c) => {
  return {
    onMessage(event, ws) {
      console.log(`Message: ${event.data}`)
      ws.send(`Echo: ${event.data}`)
    },
    onClose() {
      console.log('Connection closed')
    },
  }
}))
```

## 环境变量

```typescript
type Env = {
  DATABASE_URL: string
  JWT_SECRET: string
  NODE_ENV: 'development' | 'production'
}

const app = new Hono<{ Bindings: Env }>()

app.get('/config', (c) => {
  return c.json({
    env: c.env.NODE_ENV,
    // 不要暴露敏感信息
  })
})
```
