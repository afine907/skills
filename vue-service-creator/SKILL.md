---
name: vue-service-creator
description: |
  【Vue服务脚手架】快速创建 Vue 3 / Nuxt 3 前端项目，支持 Composition API、Pinia、Vue Router。
  
  触发时机：
  - 用户要求"创建Vue项目"、"Nuxt项目"
  - 需要搭建 Vue 3 前端项目
  
  生成完整项目结构、配置文件和示例代码。
category: development
---

# Vue Service Creator — Vue 3 / Nuxt 3 项目脚手架

生成标准化 Vue 3 / Nuxt 3 项目，内置 Composition API、Pinia、TypeScript 最佳实践。


## Goal

快速创建 Vue 3 / Nuxt 3 前端项目，支持 Composition API、Pinia、Vue Router

## Trigger

- 用户要求"创建Vue项目"、"Nuxt项目"
  - 需要搭建 Vue 3 前端项目

## 1. Vue 3 vs Nuxt 3 选择指南

| 场景 | 推荐框架 | 理由 |
|------|----------|------|
| SPA 后台管理系统 | Vue 3 + Vite | 轻量、灵活、构建快 |
| 内容站点 / 博客 | Nuxt 3 | SSR/SSG、SEO 友好 |
| 企业官网 | Nuxt 3 | 预渲染、路由自动生成 |
| 移动端 H5 | Vue 3 + Vite | 纯前端、打包体积小 |
| 全栈应用 | Nuxt 3 | 内置 server routes、API 层 |
| 组件库 / SDK | Vue 3 + Vite | 纯库模式、无框架依赖 |

## 2. 技术栈总览

| 层次 | Vue 3 方案 | Nuxt 3 方案 |
|------|-----------|-------------|
| 构建工具 | Vite 6 | Nuxt 内置 (Vite) |
| 状态管理 | Pinia | Pinia (内置支持) |
| 路由 | Vue Router 4 | 文件系统路由 (自动) |
| 样式 | Tailwind CSS / UnoCSS | Tailwind CSS / UnoCSS |
| 测试 | Vitest + Vue Test Utils | Vitest + Vue Test Utils |
| HTTP | ofetch / axios | useFetch / $fetch |
| 表单 | VeeValidate / FormKit | VeeValidate / FormKit |
| UI 库 | Element Plus / Naive UI | Element Plus / Naive UI |

## 3. 项目结构

### Vue 3 + Vite

```
{project-name}/
├── src/
│   ├── api/                        # API 服务层
│   │   ├── request.ts              # HTTP 客户端封装
│   │   ├── user.ts                 # 用户相关 API
│   │   └── index.ts
│   ├── assets/                     # 静态资源
│   │   ├── images/
│   │   └── styles/
│   │       └── main.css
│   ├── components/                 # 通用组件
│   │   ├── ui/                     # 基础 UI 组件
│   │   │   ├── BaseButton.vue
│   │   │   ├── BaseInput.vue
│   │   │   └── index.ts
│   │   └── layout/                 # 布局组件
│   │       ├── AppHeader.vue
│   │       ├── AppSidebar.vue
│   │       └── AppLayout.vue
│   ├── composables/                # 组合式函数
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── index.ts
│   ├── pages/                      # 页面组件
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   └── Dashboard.vue
│   ├── router/                     # 路由配置
│   │   ├── index.ts
│   │   └── guards.ts
│   ├── stores/                     # Pinia 状态
│   │   ├── modules/
│   │   │   ├── auth.ts
│   │   │   └── app.ts
│   │   └── index.ts
│   ├── types/                      # TypeScript 类型
│   │   ├── api.d.ts
│   │   ├── env.d.ts
│   │   └── index.ts
│   ├── utils/                      # 工具函数
│   │   ├── storage.ts
│   │   └── format.ts
│   ├── App.vue
│   └── main.ts
├── public/
├── tests/
│   ├── setup.ts
│   └── components/
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── components.d.ts                 # unplugin-vue-components 自动生成
├── auto-imports.d.ts               # unplugin-auto-import 自动生成
├── tailwind.config.ts
├── tsconfig.json
├── vite.config.ts
├── package.json
└── README.md
```

### Nuxt 3

```
{project-name}/
├── app.vue                         # 根组件
├── error.vue                       # 错误页面
├── assets/
│   └── css/
│       └── main.css
├── components/                     # 自动导入组件
│   ├── ui/
│   │   ├── BaseButton.vue
│   │   └── BaseInput.vue
│   └── layout/
│       ├── AppHeader.vue
│       └── AppSidebar.vue
├── composables/                    # 自动导入组合式函数
│   ├── useAuth.ts
│   └── useApi.ts
├── layouts/                        # 布局模板
│   ├── default.vue
│   └── auth.vue
├── middleware/                     # 路由中间件
│   ├── auth.ts
│   └── guest.ts
├── pages/                          # 文件系统路由
│   ├── index.vue
│   ├── login.vue
│   ├── dashboard/
│   │   ├── index.vue
│   │   └── settings.vue
│   └── users/
│       ├── index.vue
│       └── [id].vue
├── plugins/                        # 插件
│   └── api.ts
├── public/                         # 静态资源
├── server/                         # 服务端
│   ├── api/                        # API 路由
│   │   ├── auth/
│   │   │   ├── login.post.ts
│   │   │   └── me.get.ts
│   │   └── users/
│   │       ├── index.get.ts
│   │       └── [id].get.ts
│   ├── middleware/                  # 服务端中间件
│   │   └── auth.ts
│   ├── plugins/
│   └── utils/
│       └── db.ts
├── stores/                         # Pinia stores
│   ├── auth.ts
│   └── app.ts
├── types/
│   └── index.d.ts
├── tests/
├── nuxt.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

## 4. 配置文件

### vite.config.ts (Vue 3)

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
      dts: 'auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
        },
      },
    },
  },
});
```

### nuxt.config.ts (Nuxt 3)

```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@vueuse/nuxt',
  ],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    // 服务端私有变量
    jwtSecret: process.env.JWT_SECRET || '',
    // 客户端公开变量（以 public 开头）
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
    },
  },

  routeRules: {
    '/dashboard/**': { ssr: false },         // SPA 模式
    '/': { prerender: true },                 // 预渲染
    '/api/**': { cors: true },                // CORS
  },

  nitro: {
    compressPublicAssets: true,
  },

  app: {
    head: {
      title: 'My Nuxt App',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
    pageTransition: { name: 'page', mode: 'out-in' },
  },

  typescript: {
    strict: true,
  },
});
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM"],
    "skipLibCheck": true,
    "noEmit": true,
    "paths": {
      "@/*": ["./src/*"]           // Vue 3: ./src/*，Nuxt 3: ./*
    },
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue"],
  "exclude": ["node_modules", "dist"]
}
```

## 5. Composition API 核心模式

### ref 与 reactive

```typescript
import { ref, reactive, toRefs } from 'vue';

// ref — 适用于基本类型或单个对象
const count = ref(0);
const user = ref<User | null>(null);

// reactive — 适用于对象/数组（注意不能解构，需 toRefs）
const form = reactive({
  username: '',
  password: '',
  remember: false,
});

// toRefs 保持响应性
const { username, password } = toRefs(form);
```

### computed

```typescript
import { computed } from 'vue';

const fullName = computed(() => `${firstName.value} ${lastName.value}`);

// 可写 computed
const fullNameRW = computed({
  get: () => `${firstName.value} ${lastName.value}`,
  set: (val: string) => {
    const [first, last] = val.split(' ');
    firstName.value = first;
    lastName.value = last;
  },
});
```

### watch 与 watchEffect

```typescript
import { watch, watchEffect } from 'vue';

// watch — 精确追踪
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) await fetchUser(Number(newId));
  },
  { immediate: true }
);

// watchEffect — 自动追踪依赖
watchEffect(async () => {
  const data = await fetchUser(userId.value);
  user.value = data;
});
```

### 生命周期钩子

```typescript
import { onMounted, onUnmounted, onUpdated } from 'vue';

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
```

## 6. Pinia 状态管理

```typescript
// stores/modules/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/api/request';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string>(localStorage.getItem('token') || '');

  // Getters
  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');

  // Actions
  async function login(username: string, password: string) {
    const { data } = await apiClient.post('/auth/login', {
      username,
      password,
    });
    token.value = data.access_token;
    user.value = data.user;
    localStorage.setItem('token', data.access_token);
  }

  async function fetchCurrentUser() {
    if (!token.value) return;
    try {
      const { data } = await apiClient.get('/auth/me');
      user.value = data;
    } catch {
      logout();
    }
  }

  function logout() {
    user.value = null;
    token.value = '';
    localStorage.removeItem('token');
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    login,
    fetchCurrentUser,
    logout,
  };
});
```

## 7. 路由配置

### Vue Router (Vue 3)

```typescript
// router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/pages/Home.vue') },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'users',
        children: [
          { path: '', name: 'user-list', component: () => import('@/pages/users/UserList.vue') },
          { path: ':id', name: 'user-detail', component: () => import('@/pages/users/UserDetail.vue') },
        ],
      },
    ],
  },
  { path: '/login', name: 'login', component: () => import('@/pages/Login.vue') },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/pages/NotFound.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
```

### 路由守卫

```typescript
// router/guards.ts
import type { Router } from 'vue-router';
import { useAuthStore } from '@/stores/modules/auth';

export function setupRouteGuards(router: Router) {
  router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } });
    } else if (to.meta.guestOnly && authStore.isAuthenticated) {
      next({ name: 'home' });
    } else {
      next();
    }
  });
}
```

### Nuxt 文件路由

```
pages/
├── index.vue               → /
├── about.vue               → /about
├── login.vue               → /login
├── users/
│   ├── index.vue           → /users
│   ├── [id].vue            → /users/:id
│   └── [id]/
│       └── edit.vue        → /users/:id/edit
└── [...slug].vue           → /*  (catch-all)
```

Nuxt 中间件：

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore();
  if (!authStore.isAuthenticated) {
    return navigateTo('/login', { redirectCode: 302 });
  }
});
```

## 8. 组件模式

### Slots 插槽

```vue
<!-- BaseCard.vue -->
<template>
  <div class="rounded-lg border bg-white p-4 shadow-sm">
    <header v-if="$slots.header" class="mb-3 border-b pb-2">
      <slot name="header" />
    </header>
    <main>
      <slot /> <!-- 默认插槽 -->
    </main>
    <footer v-if="$slots.footer" class="mt-3 border-t pt-2">
      <slot name="footer" />
    </footer>
  </div>
</template>
```

```vue
<!-- 使用 -->
<BaseCard>
  <template #header>
    <h2>用户信息</h2>
  </template>
  <p>姓名：{{ user.name }}</p>
  <template #footer>
    <BaseButton @click="edit">编辑</BaseButton>
  </template>
</BaseCard>
```

### provide / inject

```typescript
// 父组件 provide
import { provide, ref } from 'vue';

const theme = ref<'light' | 'dark'>('light');
provide('theme', theme);
provide('toggleTheme', () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light';
});

// 子/孙组件 inject
import { inject } from 'vue';

const theme = inject<Ref<'light' | 'dark'>>('theme');
const toggleTheme = inject<() => void>('toggleTheme');
```

### Composables 组合式函数

```typescript
// composables/useApi.ts
import { ref } from 'vue';
import type { Ref } from 'vue';

export function useApi<T>(apiFn: (...args: any[]) => Promise<T>) {
  const data: Ref<T | null> = ref(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  async function execute(...args: any[]) {
    loading.value = true;
    error.value = null;
    try {
      data.value = await apiFn(...args);
      return data.value;
    } catch (err) {
      error.value = err as Error;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return { data, loading, error, execute };
}
```

## 9. 测试配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.ts', 'src/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
```

```typescript
// tests/setup.ts
import { config } from '@vue/test-utils';

config.global.mocks = {
  $t: (key: string) => key,        // i18n mock
  $route: { path: '/' },
};
```

```typescript
// tests/components/BaseButton.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseButton from '@/components/ui/BaseButton.vue';

describe('BaseButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click me' },
    });
    expect(wrapper.text()).toBe('Click me');
  });

  it('emits click event', async () => {
    const wrapper = mount(BaseButton);
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toHaveLength(1);
  });

  it('is disabled when loading', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
    });
    expect(wrapper.attributes('disabled')).toBeDefined();
  });
});
```

## 10. 样式方案

### Tailwind CSS 配置

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

export default {
  content: [
    './index.html',
    './src/**/*.{vue,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: { 50: '#eff6ff', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8' },
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
} satisfies Config;
```

### UnoCSS 配置（替代方案）

```typescript
// uno.config.ts
import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss';

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({ scale: 1.2 }),
  ],
  shortcuts: {
    'btn': 'px-4 py-2 rounded-md font-medium transition-colors',
    'btn-primary': 'btn bg-blue-600 text-white hover:bg-blue-700',
    'btn-secondary': 'btn bg-gray-200 text-gray-900 hover:bg-gray-300',
  },
});
```

## 11. 快速使用示例

```
# 创建 Vue 3 项目
创建一个 Vue 3 + Vite 项目，用于企业后台管理系统，使用 Element Plus + Pinia

# 创建 Nuxt 3 项目
创建一个 Nuxt 3 项目，用于技术博客，支持 SSR 和暗黑模式

# 添加功能模块
为项目添加用户管理模块，包含列表、详情、编辑页面

# 生成组件
生成一个 DataTable 组件，支持排序、分页、筛选，基于 Composition API

# 生成 composable
写一个 usePagination composable，支持分页逻辑复用

# 生成 store
写一个 useProductStore，包含商品的 CRUD 操作
```

## 参考资料

- Composition API 模式与最佳实践: [references/composition-api.md](references/composition-api.md)
- Nuxt 3 特有模式: [references/nuxt-patterns.md](references/nuxt-patterns.md)
