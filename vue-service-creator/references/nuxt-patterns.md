# Nuxt 3 特有模式

Nuxt 3 框架专属的开发模式、约定和最佳实践参考。

## 服务端 API 路由

### 基础路由

```typescript
// server/api/users/index.get.ts — GET /api/users
export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const page = Number(query.page) || 1;
  const pageSize = Number(query.pageSize) || 10;

  const users = await db.user.findMany({
    skip: (page - 1) * pageSize,
    take: pageSize,
  });

  return { data: users, total: await db.user.count() };
});
```

```typescript
// server/api/users/index.post.ts — POST /api/users
export default defineEventHandler(async (event) => {
  const body = await readBody(event);

  // 参数校验
  const result = await zodValidate(body, userCreateSchema);
  if (!result.success) {
    throw createError({ statusCode: 400, message: result.error.message });
  }

  const user = await db.user.create({ data: result.data });
  return { data: user };
});
```

```typescript
// server/api/users/[id].get.ts — GET /api/users/:id
export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'));
  if (isNaN(id)) {
    throw createError({ statusCode: 400, message: 'Invalid user ID' });
  }

  const user = await db.user.findUnique({ where: { id } });
  if (!user) {
    throw createError({ statusCode: 404, message: 'User not found' });
  }

  return { data: user };
});
```

### 路由文件命名约定

```
server/api/
├── auth/
│   ├── login.post.ts         → POST /api/auth/login
│   ├── logout.post.ts        → POST /api/auth/logout
│   └── me.get.ts             → GET  /api/auth/me
├── users/
│   ├── index.get.ts          → GET  /api/users
│   ├── index.post.ts         → POST /api/users
│   ├── [id].get.ts           → GET  /api/users/:id
│   ├── [id].put.ts           → PUT  /api/users/:id
│   ├── [id].delete.ts        → DELETE /api/users/:id
│   └── [id]/
│       └── posts.get.ts      → GET  /api/users/:id/posts
└── [...].ts                  → 兜底路由
```

### 服务端工具函数

```typescript
// server/utils/db.ts — 自动导入
export function useDb() {
  // 返回 Prisma / Drizzle 等数据库实例
  return prisma;
}

// server/utils/auth.ts
export function requireAuth(event: H3Event) {
  const session = event.context.session;
  if (!session) {
    throw createError({ statusCode: 401, message: 'Unauthorized' });
  }
  return session;
}

export function requireAdmin(event: H3Event) {
  const session = requireAuth(event);
  if (session.user.role !== 'admin') {
    throw createError({ statusCode: 403, message: 'Forbidden' });
  }
  return session;
}
```

## 中间件

### 路由中间件（客户端）

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) {
    return navigateTo('/login', {
      redirectCode: 302,
      replace: true,
    });
  }
});

// middleware/guest.ts — 仅限未登录用户访问
export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore();
  if (authStore.isAuthenticated) {
    return navigateTo('/dashboard');
  }
});

// middleware/admin.ts — 管理员权限
export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore();
  if (!authStore.isAdmin) {
    throw createError({ statusCode: 403, message: 'Access denied' });
  }
});
```

```vue
<!-- pages/admin.vue — 使用中间件 -->
<script setup lang="ts">
definePageMeta({
  middleware: ['auth', 'admin'],
  layout: 'admin',
});
</script>
```

### 服务端中间件

```typescript
// server/middleware/auth.ts
export default defineEventHandler(async (event) => {
  // 每个请求都会执行
  const token = getCookie(event, 'auth_token') ||
                getHeader(event, 'authorization')?.replace('Bearer ', '');

  if (token) {
    try {
      const session = await verifyToken(token);
      event.context.session = session;
    } catch {
      // token 无效，不设置 session
    }
  }
});
```

## 布局系统

### 默认布局

```vue
<!-- layouts/default.vue -->
<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1 container mx-auto px-4 py-8">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>
```

### 管理后台布局

```vue
<!-- layouts/admin.vue -->
<template>
  <div class="flex h-screen">
    <AppSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppHeader />
      <main class="flex-1 overflow-y-auto bg-gray-50 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
```

```vue
<!-- pages/dashboard.vue — 指定布局 -->
<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
});
</script>
```

## 数据获取

### useFetch — 推荐方式

```vue
<script setup lang="ts">
// 自动处理 SSR、缓存、错误
const { data: users, pending, error, refresh } = await useFetch('/api/users', {
  query: { page: 1, pageSize: 10 },
  // 可选：转换响应数据
  transform: (response) => response.data,
  // 可选：缓存 key
  key: 'users-list',
});
</script>
```

### useAsyncData — 灵活方式

```vue
<script setup lang="ts">
// 自定义获取函数
const { data: user } = await useAsyncData(
  `user-${route.params.id}`,
  () => $fetch(`/api/users/${route.params.id}`),
  {
    watch: [() => route.params.id],  // 依赖变化时重新获取
  }
);
</script>
```

### $fetch — 直接调用

```vue
<script setup lang="ts">
// 在事件处理中使用
async function deleteUser(id: number) {
  await $fetch(`/api/users/${id}`, { method: 'DELETE' });
  await refreshNuxtData(); // 刷新所有 useFetch/useAsyncData 缓存
}

// 也可以在 composables 中使用
async function createUser(data: CreateUserInput) {
  return await $fetch('/api/users', {
    method: 'POST',
    body: data,
  });
}
</script>
```

## 插件系统

### 客户端插件

```typescript
// plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();

  const api = $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ options }) {
      const token = useCookie('auth_token');
      if (token.value) {
        options.headers.set('Authorization', `Bearer ${token.value}`);
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        navigateTo('/login');
      }
    },
  });

  return {
    provide: { api },
  };
});
```

```vue
<!-- 使用注入的 api -->
<script setup lang="ts">
const { $api } = useNuxtApp();
const users = await $api('/api/users');
</script>
```

### 仅客户端插件

```typescript
// plugins/analytics.client.ts — .client 后缀表示仅客户端
export default defineNuxtPlugin(() => {
  const router = useRouter();

  router.afterEach((to) => {
    trackPageView(to.fullPath);
  });
});
```

### 仅服务端插件

```typescript
// plugins/db.server.ts — .server 后缀表示仅服务端
export default defineNuxtPlugin(() => {
  const db = createDatabaseConnection();
  return {
    provide: { db },
  };
});
```

## 组合式函数（自动导入）

Nuxt 3 自动导入 `composables/` 目录下的函数：

```typescript
// composables/useAuth.ts — 全局可用，无需 import
export function useAuth() {
  const user = useState<User | null>('auth-user', () => null);
  const token = useCookie('auth_token');

  async function login(email: string, password: string) {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    });
    token.value = response.access_token;
    user.value = response.user;
  }

  async function fetchUser() {
    if (!token.value) return;
    try {
      user.value = await $fetch('/api/auth/me');
    } catch {
      logout();
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    navigateTo('/login');
  }

  return { user, login, fetchUser, logout };
}
```

## SEO 与 Head 管理

```vue
<script setup lang="ts">
// 页面级别 SEO
useHead({
  title: '用户管理',
  meta: [
    { name: 'description', content: '管理系统用户列表' },
  ],
});

// 动态 SEO
useSeoMeta({
  title: () => `${user.value?.name} - 个人主页`,
  ogTitle: '用户主页',
  description: '查看用户详细信息',
  ogImage: '/og-default.png',
});
</script>
```

## 路由规则与预渲染

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    // 静态预渲染
    '/': { prerender: true },
    '/about': { prerender: true },
    // SPA 模式（无 SSR）
    '/dashboard/**': { ssr: false },
    '/settings/**': { ssr: false },
    // 服务端缓存
    '/api/products/**': { swr: 3600 },       // 缓存 1 小时
    '/api/categories': { isr: 86400 },       // ISR 每天刷新
    // 重定向
    '/old-page': { redirect: '/new-page' },
    // CORS
    '/api/**': { cors: true },
  },
});
```

## Nitro 服务端功能

### 定时任务

```typescript
// server/tasks/cleanup.ts
export default defineTask({
  meta: {
    name: 'cleanup',
    description: '清理过期数据',
  },
  async run() {
    await db.session.deleteMany({
      where: { expiresAt: { lt: new Date() } },
    });
    return { result: 'ok' };
  },
});
```

### 服务端存储

```typescript
// 使用 Nitro 内置存储
export default defineEventHandler(async () => {
  // 使用 useStorage 访问多种存储后端
  const storage = useStorage('redis');

  await storage.setItem('cache:key', { data: 'value' });
  const cached = await storage.getItem('cache:key');

  return cached;
});
```

## 错误处理

```vue
<!-- error.vue — 全局错误页面 -->
<script setup lang="ts">
import type { NuxtError } from '#app';

const props = defineProps<{
  error: NuxtError;
}>();

function handleError() {
  clearError({ redirect: '/' });
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-300">{{ error.statusCode }}</h1>
      <p class="mt-4 text-xl text-gray-600">
        {{ error.statusCode === 404 ? '页面不存在' : '服务器错误' }}
      </p>
      <button
        class="mt-6 rounded-md bg-blue-600 px-6 py-2 text-white"
        @click="handleError"
      >
        返回首页
      </button>
    </div>
  </div>
</template>
```

```typescript
// 服务端抛出错误
throw createError({
  statusCode: 404,
  statusMessage: 'User not found',
  message: '未找到该用户',
  fatal: true,  // 触发 error.vue
});
```

## 环境变量

```bash
# .env
NUXT_PUBLIC_API_BASE=https://api.example.com
NUXT_JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://...
```

```typescript
// 使用
const config = useRuntimeConfig();
console.log(config.public.apiBase);  // 客户端可访问
console.log(config.jwtSecret);       // 仅服务端可访问
```
