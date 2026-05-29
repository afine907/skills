---
name: react-service-creator
description: |
  【React脚手架】生成 React 项目脚手架，支持 Next.js/Vite/CRA，包含路由、状态管理、API层、组件规范、测试配置。

  触发时机：
  - 用户要求"创建React项目"、"React脚手架"
  - 新建前端项目需要标准化模板
  - 需要统一团队 React 项目结构

  生成完整可运行的项目骨架。
category: development
---

# React Service Creator — React 项目脚手架

生成标准化 React 项目，内置最佳实践和统一规范。


## Goal

生成 React 项目脚手架，支持 Next.js/Vite/CRA，包含路由、状态管理、API层、组件规范、测试配置

## Trigger

- 用户要求"创建React项目"、"React脚手架"
  - 新建前端项目需要标准化模板
  - 需要统一团队 React 项目结构

## Workflow

```
输入 → 处理 → 输出
```
## 技术栈选择

| 框架 | 构建工具 | 状态管理 | 样式方案 | 测试 |
|------|----------|----------|----------|------|
| Next.js 14 | Turbopack | Zustand | Tailwind CSS | Jest + RTL |
| Vite + React | Vite | Zustand | Tailwind CSS | Vitest + RTL |
| CRA (legacy) | Webpack | Redux Toolkit | CSS Modules | Jest + RTL |

## 项目结构

```
{project-name}/
├── src/
│   ├── app/                    # Next.js App Router / 入口
│   │   ├── layout.tsx          # 根布局
│   │   ├── page.tsx            # 首页
│   │   └── globals.css         # 全局样式
│   ├── components/             # 通用组件
│   │   ├── ui/                 # 基础 UI 组件
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   └── layout/             # 布局组件
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Sidebar.tsx
│   ├── features/               # 功能模块
│   │   └── auth/
│   │       ├── components/     # 模块组件
│   │       ├── hooks/          # 模块 hooks
│   │       ├── services/       # API 调用
│   │       ├── stores/         # 状态管理
│   │       ├── types/          # 类型定义
│   │       └── index.ts        # 模块导出
│   ├── hooks/                  # 公共 hooks
│   ├── lib/                    # 工具库
│   │   ├── api.ts              # API 客户端
│   │   ├── auth.ts             # 认证工具
│   │   └── utils.ts            # 通用工具
│   ├── services/               # API 服务层
│   │   ├── api.ts              # Axios/fetch 配置
│   │   └── index.ts
│   ├── stores/                 # 全局状态
│   │   ├── useAuthStore.ts
│   │   └── index.ts
│   ├── types/                  # 全局类型
│   │   ├── api.ts              # API 响应类型
│   │   └── index.ts
│   └── styles/                 # 样式
│       └── theme.ts
├── public/                     # 静态资源
├── tests/                      # 测试配置
│   ├── setup.ts
│   └── mocks/
├── .env.example                # 环境变量模板
├── .eslintrc.json              # ESLint 配置
├── .prettierrc                 # Prettier 配置
├── tailwind.config.ts          # Tailwind 配置
├── tsconfig.json               # TypeScript 配置
├── next.config.ts              # Next.js 配置（如使用）
├── package.json
└── README.md
```

## 核心代码模板

### API 客户端

```typescript
// src/lib/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

export { apiClient };
export type { AxiosRequestConfig, AxiosResponse };
```

### Zustand Store

```typescript
// src/stores/useAuthStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/lib/api';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        const response = await apiClient.post('/auth/login', {
          email,
          password,
        });
        const { access_token, user } = response.data;
        set({
          user,
          token: access_token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      updateUser: (userData: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...userData } });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
);
```

### 通用 Hook

```typescript
// src/hooks/useApi.ts
import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: AxiosError) => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions<T> = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosError | null>(null);

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiFunction(...args);
        setData(result);
        options.onSuccess?.(result);
        return result;
      } catch (err) {
        const axiosError = err as AxiosError;
        setError(axiosError);
        options.onError?.(axiosError);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, options]
  );

  return { data, loading, error, execute };
}
```

### 基础组件

```tsx
// src/components/ui/Button/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:pointer-events-none disabled:opacity-50',
          {
            'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
            'bg-gray-200 text-gray-900 hover:bg-gray-300': variant === 'secondary',
            'border border-gray-300 bg-transparent hover:bg-gray-100': variant === 'outline',
            'bg-transparent hover:bg-gray-100': variant === 'ghost',
            'bg-red-600 text-white hover:bg-red-700': variant === 'danger',
          },
          {
            'h-8 px-3 text-sm': size === 'sm',
            'h-10 px-4 text-sm': size === 'md',
            'h-12 px-6 text-base': size === 'lg',
          },
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, type ButtonProps };
```

## 快速使用

```
# 创建 Next.js 项目
创建一个 Next.js 14 的 React 项目，用于电商后台管理

# 创建 Vite React 项目
用 Vite 创建一个 React 项目，技术栈：TypeScript + Zustand + Tailwind

# 添加功能模块
为项目添加用户管理模块，包含 CRUD 功能

# 生成组件
生成一个 DataTable 组件，支持排序、分页、筛选
```

## 参考资料

- 组件库参考: [references/component-patterns.md](references/component-patterns.md)
- 状态管理指南: [references/state-management.md](references/state-management.md)
