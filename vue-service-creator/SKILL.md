---
name: vue-service-creator
description: |
  【Vue服务脚手架】快速创建 Vue 3 / Nuxt 3 前端项目，支持 Composition API、Pinia、Vue Router。

  触发时机：
  - 用户要求"创建Vue项目"、"Nuxt项目"
  - 需要搭建 Vue 3 前端项目
category: development
---

# Vue Service Creator — Vue 3 / Nuxt 3 脚手架

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

生成标准化 Vue 3 / Nuxt 3 项目。

## Workflow

1. **选择框架** — Vue 3 + Vite / Nuxt 3
2. **配置工具链** — TypeScript, ESLint, Tailwind CSS
3. **设计结构** — 目录规范、路由、状态管理
4. **集成工具** — 测试、构建、部署
5. **生成代码** — 组件、页面、API 层

## 技术栈选择

| 场景 | 推荐 | 理由 |
|------|------|------|
| SPA 后台管理 | Vue 3 + Vite | 轻量、灵活 |
| 内容站点 / 博客 | Nuxt 3 | SSR/SSG、SEO |
| 企业官网 | Nuxt 3 | 预渲染 |

## Vue 3 + Vite 项目结构

```
my-vue-app/
├── src/
│   ├── api/                # API 请求
│   │   └── user.ts
│   ├── components/         # 通用组件
│   │   └── DataTable.vue
│   ├── composables/        # 组合式函数
│   │   └── useAuth.ts
│   ├── layouts/            # 布局
│   │   └── DefaultLayout.vue
│   ├── pages/              # 页面
│   │   ├── index.vue
│   │   └── users/
│   │       ├── index.vue
│   │       └── [id].vue
│   ├── router/             # 路由
│   │   └── index.ts
│   ├── stores/             # Pinia 状态
│   │   └── user.ts
│   ├── types/              # 类型定义
│   └── utils/              # 工具函数
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 核心代码模板

### API 请求

```typescript
// src/api/user.ts
import request from '@/utils/request'
import type { User, CreateUserInput } from '@/types/user'

export const userApi = {
  list: (params?: { page?: number; size?: number }) =>
    request.get<User[]>('/api/v1/users', { params }),
  get: (id: string) =>
    request.get<User>(`/api/v1/users/${id}`),
  create: (data: CreateUserInput) =>
    request.post<User>('/api/v1/users', data),
}
```

### Pinia Store

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '@/api/user'
import type { User } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([])
  const loading = ref(false)

  async function fetchUsers() {
    loading.value = true
    try {
      const { data } = await userApi.list()
      users.value = data
    } finally {
      loading.value = false
    }
  }

  return { users, loading, fetchUsers }
})
```

### 组合式函数

```typescript
// src/composables/useAuth.ts
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export function useAuth() {
  const router = useRouter()
  const token = ref(localStorage.getItem('token'))

  async function login(email: string, password: string) {
    const { data } = await authApi.login({ email, password })
    token.value = data.token
    localStorage.setItem('token', data.token)
    router.push('/')
  }

  function logout() {
    token.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, login, logout }
}
```

## Example

```
用户: 创建一个 Vue 3 管理后台项目

输出:
1. npm create vue@latest admin -- --typescript --router --pinia
2. 配置 Tailwind CSS
3. 创建 layouts/DefaultLayout.vue
4. 创建 pages/users/index.vue + [id].vue
5. 创建 stores/user.ts (Pinia)
6. 创建 api/user.ts (axios)
7. 配置路由守卫 (登录验证)
```

## 参考

