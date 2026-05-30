# Express 模式参考

## 中间件模式

### 自定义中间件

```typescript
import { Request, Response, NextFunction } from 'express'

// 异步中间件包装器
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => (req: Request, res: Response, next: NextFunction) => {
  Promise.resolve(fn(req, res, next)).catch(next)
}

// 请求计时中间件
export function requestTimer(req: Request, res: Response, next: NextFunction) {
  const start = Date.now()
  res.on('finish', () => {
    const duration = Date.now() - start
    console.log(`${req.method} ${req.url} ${res.statusCode} ${duration}ms`)
  })
  next()
}
```

### CORS 配置

```typescript
import cors from 'cors'

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400,
}))
```

### 速率限制

```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests',
  standardHeaders: true,
  legacyHeaders: false,
})

app.use('/api/', limiter)
```

## 路由模式

### 模块化路由

```typescript
// routes/users.ts
import { Router } from 'express'
import { asyncHandler } from '../middleware/asyncHandler.js'

const router = Router()

router.get('/', asyncHandler(async (req, res) => {
  const users = await userService.findAll()
  res.json(users)
}))

router.get('/:id', asyncHandler(async (req, res) => {
  const user = await userService.findById(req.params.id)
  res.json(user)
}))

export { router as userRoutes }

// app.ts
import { userRoutes } from './routes/users.js'
app.use('/api/users', userRoutes)
```

### 嵌套路由

```typescript
// routes/users/posts.ts
import { Router } from 'express'

const router = Router({ mergeParams: true })

router.get('/', async (req, res) => {
  const { userId } = req.params
  const posts = await postService.findByUser(userId)
  res.json(posts)
})

export { router as userPostRoutes }

// routes/users.ts
import { userPostRoutes } from './posts.js'
router.use('/:userId/posts', userPostRoutes)
```

## 文件上传

```typescript
import multer from 'multer'

const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => {
    const uniqueSuffix = `${Date.now()}-${Math.round(Math.random() * 1E9)}`
    cb(null, `${uniqueSuffix}-${file.originalname}`)
  },
})

const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true)
    } else {
      cb(new Error('Only images allowed'))
    }
  },
})

router.post('/avatar', upload.single('avatar'), async (req, res) => {
  res.json({ url: `/uploads/${req.file?.filename}` })
})
```

## Session 和 Cookie

```typescript
import session from 'express-session'

app.use(session({
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  },
}))
```

## 模板引擎

```typescript
import { engine } from 'express-handlebars'

app.engine('hbs', engine({
  extname: '.hbs',
  defaultLayout: 'main',
}))
app.set('view engine', 'hbs')
app.set('views', './views')

app.get('/dashboard', (req, res) => {
  res.render('dashboard', { user: req.user })
})
```

## 静态文件

```typescript
app.use(express.static('public', {
  maxAge: '1d',
  etag: true,
  lastModified: true,
}))

app.use('/uploads', express.static('uploads', {
  immutable: true,
  maxAge: '365d',
}))
```

## 健康检查

```typescript
app.get('/health', async (req, res) => {
  const checks = {
    uptime: process.uptime(),
    timestamp: Date.now(),
    database: await checkDatabase(),
    redis: await checkRedis(),
  }

  const isHealthy = Object.values(checks).every(v => v !== false)
  res.status(isHealthy ? 200 : 503).json(checks)
})
```
