---
name: typescript-service-creator
description: |
  【TypeScript服务脚手架】快速创建 TypeScript 后端服务项目，支持 Express/Hono/Fastify 框架。

  触发时机：
  - 用户要求"创建TypeScript服务"、"TS后端项目"
  - 需要搭建 Express/Hono/Fastify 项目

  生成完整项目结构、配置文件和示例代码。
category: development
---

# TypeScript Service Creator — TypeScript 后端服务脚手架

快速创建生产级 TypeScript 后端服务，支持 Express、Hono、Fastify 三大框架。


## Goal

快速创建 TypeScript 后端服务项目，支持 Express/Hono/Fastify 框架

## Trigger

- 用户要求"创建TypeScript服务"、"TS后端项目"
  - 需要搭建 Express/Hono/Fastify 项目

## 工作流程

```
框架选择 → 项目生成 → 核心代码 → 验证构建
```

### Step 1: 框架选择
- 根据需求选择 Express / Hono / Fastify
- 确定技术栈（ORM、验证库、日志库）

### Step 2: 项目生成
- 创建项目目录结构
- 生成配置文件（tsconfig.json, .eslintrc 等）
- 生成 package.json（依赖版本锁定）

### Step 3: 核心代码
- 生成路由定义和中间件
- 生成错误处理中间件
- 生成数据模型和验证 schema
- 生成数据库连接配置

### Step 4: 验证构建
- 安装依赖（npm install）
- 运行构建（npx tsc --noEmit）
- 运行测试（npm test）

## 框架选择决策流程

```
用户需求分析
  │
  ├─ 部署到边缘 / Cloudflare Workers？──是──→ Hono
  │
  ├─ 需要最大中间件生态 / 兼容性？──是──→ Express
  │
  ├─ 需要高性能 / 微服务架构？──是──→ Fastify
  │
  ├─ 团队无特殊偏好？→ Fastify（类型安全 + 性能）
  │
  └─ 快速原型 / 简单 API？→ Express（学习曲线最低）
```

## 框架选择

| 框架 | 适用场景 | 性能 | 学习曲线 | 生态 |
|------|----------|------|----------|------|
| **Express** | 传统 Web API、中间件丰富 | 中 | 低 | 最成熟 |
| **Hono** | 边缘计算、Cloudflare Workers、轻量 API | 高 | 低 | 快速增长 |
| **Fastify** | 高性能 API、微服务 | 高 | 中 | 成熟 |

**选择建议**：
- 需要最大兼容性和中间件 → Express
- 需要边缘部署或极致轻量 → Hono
- 需要高性能和类型安全 → Fastify

## 项目结构

### Express 项目

```
my-express-app/
├── src/
│   ├── app.ts              # Express 应用配置
│   ├── server.ts           # 服务器启动
│   ├── routes/             # 路由定义
│   │   ├── index.ts
│   │   └── users.ts
│   ├── middleware/          # 中间件
│   │   ├── errorHandler.ts
│   │   ├── validate.ts
│   │   └── auth.ts
│   ├── services/           # 业务逻辑
│   │   └── userService.ts
│   ├── models/             # 数据模型
│   │   └── user.ts
│   ├── utils/              # 工具函数
│   │   └── logger.ts
│   └── types/              # 类型定义
│       └── index.ts
├── tests/
│   └── users.test.ts
├── package.json
├── tsconfig.json
├── .eslintrc.json
└── vitest.config.ts
```

### Hono 项目

```
my-hono-app/
├── src/
│   ├── index.ts            # 入口文件
│   ├── app.ts              # Hono 应用配置
│   ├── routes/             # 路由
│   │   ├── users.ts
│   │   └── health.ts
│   ├── middleware/          # 中间件
│   │   ├── auth.ts
│   │   └── cors.ts
│   └── services/           # 业务逻辑
│       └── userService.ts
├── package.json
├── tsconfig.json
└── wrangler.toml           # Cloudflare Workers 配置（可选）
```

### Fastify 项目

```
my-fastify-app/
├── src/
│   ├── app.ts              # Fastify 应用配置
│   ├── server.ts           # 服务器启动
│   ├── routes/             # 路由（支持 Schema 验证）
│   │   └── users.ts
│   ├── plugins/            # Fastify 插件
│   │   ├── auth.ts
│   │   └── swagger.ts
│   └── services/           # 业务逻辑
│       └── userService.ts
├── package.json
└── tsconfig.json
```

## 配置文件

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### package.json

```json
{
  "name": "my-service",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "test": "vitest",
    "test:run": "vitest run",
    "lint": "eslint src/",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "express": "^4.18.0",
    "zod": "^3.22.0",
    "pino": "^8.16.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0",
    "tsx": "^4.6.0",
    "vitest": "^1.0.0",
    "eslint": "^8.50.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0"
  }
}
```

## 核心模式

### Express 应用配置

```typescript
// src/app.ts
import express from 'express'
import { errorHandler } from './middleware/errorHandler.js'
import { requestLogger } from './middleware/logger.js'
import { userRoutes } from './routes/users.js'

export function createApp() {
  const app = express()

  app.use(express.json())
  app.use(requestLogger)

  app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() })
  })

  app.use('/api/users', userRoutes)

  app.use(errorHandler)

  return app
}

// src/server.ts
import { createApp } from './app.js'

const app = createApp()
const port = process.env.PORT || 3000

app.listen(port, () => {
  console.log(`Server running on port ${port}`)
})
```

### Hono 应用配置

```typescript
// src/app.ts
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { userRoutes } from './routes/users.js'

const app = new Hono()

app.use('*', logger())
app.use('*', cors())

app.get('/health', (c) => c.json({ status: 'ok' }))
app.route('/api/users', userRoutes)

export default app

// src/index.ts（Cloudflare Workers）
import app from './app.js'
export default app

// src/server.ts（Node.js）
import { serve } from '@hono/node-server'
import app from './app.js'
serve({ fetch: app.fetch, port: 3000 })
```

### Fastify 应用配置

```typescript
// src/app.ts
import Fastify from 'fastify'
import { userRoutes } from './routes/users.js'

export async function createApp() {
  const app = Fastify({ logger: true })

  app.get('/health', async () => ({ status: 'ok' }))

  await app.register(userRoutes, { prefix: '/api/users' })

  return app
}

// src/server.ts
import { createApp } from './app.js'

const app = await createApp()
await app.listen({ port: 3000 })
```

### Zod 请求验证

```typescript
// src/middleware/validate.ts
import { z } from 'zod'
import { Request, Response, NextFunction } from 'express'

export function validate<T extends z.ZodType>(schema: T) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body)
    if (!result.success) {
      return res.status(400).json({
        error: 'Validation failed',
        details: result.error.flatten(),
      })
    }
    req.body = result.data
    next()
  }
}

// src/routes/users.ts
import { z } from 'zod'
import { Router } from 'express'
import { validate } from '../middleware/validate.js'

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(50),
  role: z.enum(['user', 'admin']).default('user'),
})

const router = Router()

router.post('/', validate(CreateUserSchema), async (req, res) => {
  const user = await userService.create(req.body)
  res.status(201).json(user)
})

export { router as userRoutes }
```

### 错误处理

```typescript
// src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express'

export class AppError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public code?: string
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction
) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.message,
      code: err.code,
    })
  }

  console.error('Unhandled error:', err)
  res.status(500).json({ error: 'Internal server error' })
}
```

### 数据库集成 (Prisma)

```typescript
// src/services/userService.ts
import { prisma } from '../lib/prisma.js'
import { AppError } from '../middleware/errorHandler.js'

export const userService = {
  async findAll(page = 1, pageSize = 20) {
    const skip = (page - 1) * pageSize
    const [users, total] = await Promise.all([
      prisma.user.findMany({ skip, take: pageSize }),
      prisma.user.count(),
    ])
    return { users, total, page, pageSize }
  },

  async findById(id: string) {
    const user = await prisma.user.findUnique({ where: { id } })
    if (!user) throw new AppError(404, 'User not found', 'USER_NOT_FOUND')
    return user
  },

  async create(data: CreateUserInput) {
    return prisma.user.create({ data })
  },

  async update(id: string, data: UpdateUserInput) {
    await this.findById(id)
    return prisma.user.update({ where: { id }, data })
  },

  async delete(id: string) {
    await this.findById(id)
    return prisma.user.delete({ where: { id } })
  },
}
```

### 认证中间件 (JWT)

```typescript
// src/middleware/auth.ts
import jwt from 'jsonwebtoken'
import { Request, Response, NextFunction } from 'express'
import { AppError } from './errorHandler.js'

interface JwtPayload {
  userId: string
  role: string
}

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload
    }
  }
}

export function authenticate(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '')
  if (!token) throw new AppError(401, 'No token provided')

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload
    req.user = payload
    next()
  } catch {
    throw new AppError(401, 'Invalid token')
  }
}

export function authorize(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      throw new AppError(403, 'Insufficient permissions')
    }
    next()
  }
}
```

## 测试

```typescript
// tests/users.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import request from 'supertest'
import { createApp } from '../src/app.js'

describe('Users API', () => {
  const app = createApp()

  it('should create a user', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test User' })

    expect(res.status).toBe(201)
    expect(res.body).toMatchObject({
      email: 'test@example.com',
      name: 'Test User',
    })
  })

  it('should return 400 for invalid input', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'invalid' })

    expect(res.status).toBe(400)
  })
})
```

## Docker

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## 输出模板

Claude 创建 TypeScript 服务时，按以下格式输出：

```
## 服务脚手架报告

### 框架选择
- 框架：{Express / Hono / Fastify}
- 理由：{选择原因}

### 生成文件清单
| 文件路径 | 说明 | 状态 |
|---------|------|------|
| src/app.ts | 应用配置 | 新建 |
| src/server.ts | 服务器启动 | 新建 |
| src/routes/users.ts | 用户路由 | 新建 |
| src/middleware/errorHandler.ts | 错误处理 | 新建 |
| src/middleware/validate.ts | Zod 验证中间件 | 新建 |
| tsconfig.json | TypeScript 配置 | 新建 |
| package.json | 依赖配置 | 新建 |
| ... | ... | ... |

### 关键代码
（展示应用配置、路由、验证、错误处理的完整代码）

### 后续步骤
1. cd {project-name} && npm install
2. npm run dev 启动开发服务器
3. 配置数据库连接（如已选 ORM）
```

**端到端示例：**

用户输入：`创建一个 Hono 服务，部署到 Cloudflare Workers`

Claude 输出以上模板，文件清单中包含 Hono 应用结构、wrangler.toml、路由定义、中间件配置等，并附上 app.ts 和 index.ts 的完整代码。

## 快速使用

```
# 创建 Express 服务
帮我创建一个 TypeScript Express 用户管理 API，使用 Prisma 和 PostgreSQL

# 创建 Hono 服务
创建一个 Hono 服务，部署到 Cloudflare Workers

# 创建 Fastify 服务
用 Fastify 创建一个高性能的订单处理 API

# 添加认证
给现有 Express 服务添加 JWT 认证

# 添加测试
为用户 API 编写 Vitest 测试
```

## Edge Cases

- 已有 JS 项目迁移到 TS：不使用脚手架，手动添加 tsconfig.json 并渐进式迁移
- 需要 ORM：推荐 Drizzle ORM（类型安全）或 Prisma（功能丰富）
- 需要 GraphQL：推荐 Apollo Server 或 Mercurius
- 微服务架构：每个服务独立脚手架，使用 shared 包共享类型
- 旧版 Node.js（<18）：部分框架不支持，需检查兼容性

## 不适用

- Python 后端 → 使用 [python-service-creator](../python-service-creator/SKILL.md)
- Go 微服务 → 使用 [go-service-creator](../go-service-creator/SKILL.md)
- React 前端 → 使用 [react-service-creator](../react-service-creator/SKILL.md)

## 参考资料

- Express 模式: [references/express-patterns.md](references/express-patterns.md)
- Hono 模式: [references/hono-patterns.md](references/hono-patterns.md)
