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

1. **选择框架** — Next.js / Vite + React / CRA
2. **配置项目** — TypeScript, ESLint, Tailwind
3. **设计结构** — 目录规范、路由、状态管理
4. **集成工具** — 测试、构建、部署
5. **生成代码** — 组件、页面、API 层

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
  headers: 
## Example

```
用户: 创建一个 Next.js 14 管理后台项目

输出:
1. npx create-next-app@latest admin --typescript --tailwind --app
2. 配置 Zustand 状态管理
3. 创建 /dashboard, /users, /settings 路由
4. 集成 axios API 客户端
5. 添加 ESLint + Prettier 配置
```
