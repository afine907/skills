---
name: mobile-service-creator
description: |
  【移动端脚手架】快速创建 React Native / Flutter 移动应用项目。

  触发时机：
  - 用户要求"创建移动应用"、"React Native项目"、"Flutter项目"
category: development
---

# Mobile Service Creator — 移动端脚手架

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

创建 React Native / Flutter 移动应用项目。

## Workflow

1. **选择框架** — React Native / Flutter / Expo
2. **初始化项目** — 创建项目结构
3. **配置导航** — 路由、Tab 导航、Stack 导航
4. **集成工具** — 状态管理、网络请求、存储
5. **适配平台** — iOS/Android 差异处理

## 框架选择

| 场景 | 推荐 | 理由 |
|------|------|------|
| Web 团队转移动端 | React Native + Expo | JS/TS，复用 React 经验 |
| 原生性能要求高 | Flutter | 自绘引擎，性能好 |
| 快速原型 | Expo | 零配置，快速预览 |

## React Native + Expo 项目结构

```
my-mobile-app/
├── app/                    # Expo Router 页面
│   ├── (tabs)/             # Tab 导航
│   │   ├── index.tsx       # 首页
│   │   ├── explore.tsx     # 发现
│   │   └── _layout.tsx     # Tab 布局
│   ├── _layout.tsx         # 根布局
│   └── [id].tsx            # 动态路由
├── components/             # 通用组件
├── hooks/                  # 自定义 Hooks
├── services/               # API 服务
├── stores/                 # 状态管理
├── utils/                  # 工具函数
├── app.json                # Expo 配置
└── package.json
```

## 核心代码模板

### API 请求

```typescript
// services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = AsyncStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
```

### 状态管理 (Zustand)

```typescript
// stores/user.ts
import { create } from 'zustand'

interface UserStore {
  user: User | null
  setUser: (user: User) => void
  logout: () => void
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}))
```

### 导航配置

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router'

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="[id]" options={{ title: '详情' }} />
    </Stack>
  )
}
```

## Example

```
用户: 创建一个 React Native 电商 App

输出:
1. npx create-expo-app@latest shop --template tabs
2. 配置 Zustand 状态管理
3. 创建 Tab: 首页、分类、购物车、我的
4. 集成 axios API 请求
5. 添加 react-native-reanimated 动画
6. EAS Build 配置 (iOS + Android)
```

## 参考

