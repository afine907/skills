---
name: monorepo-manager
description: |
  【Monorepo管理】设计和管理 Monorepo 项目结构，包含工作空间配置、依赖管理、构建优化、版本管理。

  触发时机：
  - 用户要求"Monorepo"、"多包管理"、"workspace配置"
  - 需要将多个项目合并到一个仓库
  - 需要优化 Monorepo 构建性能

  支持 Turborepo/Nx/Lerna/pnpm workspace。
category: development
---

# Monorepo Manager — Monorepo 管理技能

设计和管理 Monorepo 项目，实现代码共享和高效构建。

## 工具选型

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| Turborepo | 轻量、缓存、Vercel 维护 | Next.js/前端项目 |
| Nx | 功能全面、增量构建 | 大型企业项目 |
| Lerna | 版本管理、发布 | npm 包发布 |
| pnpm workspace | 原生支持、高效 | 任何 Node.js 项目 |

## 项目结构

```
monorepo/
├── apps/                    # 应用
│   ├── web/                 # 前端应用
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── api/                 # 后端服务
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── admin/               # 管理后台
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── packages/                # 共享包
│   ├── ui/                  # UI 组件库
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── utils/               # 工具函数
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── config/              # 共享配置
│   │   ├── eslint/
│   │   ├── tsconfig/
│   │   └── package.json
│   └── types/               # 类型定义
│       ├── src/
│       └── package.json
├── scripts/                 # 构建脚本
├── package.json             # 根 package.json
├── pnpm-workspace.yaml      # pnpm 工作空间配置
├── turbo.json               # Turborepo 配置
├── tsconfig.json            # 根 TypeScript 配置
└── .gitignore
```

## 配置文件

### pnpm-workspace.yaml

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### 根 package.json

```json
{
  "name": "monorepo",
  "private": true,
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "test": "turbo test",
    "lint": "turbo lint",
    "clean": "turbo clean"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "typescript": "^5.3.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "clean": {
      "cache": false
    }
  }
}
```

### 根 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "references": [
    { "path": "./apps/web" },
    { "path": "./apps/api" },
    { "path": "./packages/ui" },
    { "path": "./packages/utils" }
  ]
}
```

## 包间依赖

### 引用共享包

```json
// apps/web/package.json
{
  "name": "@monorepo/web",
  "dependencies": {
    "@monorepo/ui": "workspace:*",
    "@monorepo/utils": "workspace:*",
    "@monorepo/types": "workspace:*"
  }
}
```

### TypeScript 项目引用

```json
// apps/web/tsconfig.json
{
  "extends": "@monorepo/config/tsconfig/base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "references": [
    { "path": "../../packages/ui" },
    { "path": "../../packages/utils" }
  ]
}
```

## 依赖管理

### 统一版本

```json
// pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'

// 根 package.json 使用 catalog
{
  "pnpm": {
    "catalog": {
      "react": "^18.2.0",
      "typescript": "^5.3.0",
      "vitest": "^1.0.0"
    }
  }
}

// packages/ui/package.json
{
  "dependencies": {
    "react": "catalog:"
  }
}
```

### 依赖提升

```json
// .npmrc
shamefully-hoist=true
strict-peer-dependencies=false
```

## 构建优化

### 增量构建

```bash
# 只构建变更的包
turbo build --filter=...[HEAD^1]

# 构建指定包及其依赖
turbo build --filter=@monorepo/web

# 构建所有包
turbo build
```

### 远程缓存

```json
// turbo.json
{
  "remoteCache": {
    "signature": true
  }
}
```

```bash
# 登录 Turborepo 远程缓存
npx turbo login
npx turbo link
```

## 版本管理

### 统一版本

```bash
# 使用 changesets
pnpm add -Dw @changesets/cli
pnpm changeset init

# 创建变更集
pnpm changeset

# 更新版本
pnpm changeset version

# 发布
pnpm changeset publish
```

### 独立版本

```json
// lerna.json
{
  "version": "independent",
  "npmClient": "pnpm",
  "command": {
    "publish": {
      "conventionalCommits": true
    }
  }
}
```

## CI/CD 配置

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - run: pnpm test
      - run: pnpm lint
```

## 快速使用

```
# 创建 Monorepo
创建一个 Monorepo 项目，包含前端、后端和共享包

# 添加新包
在 Monorepo 中添加一个新的共享工具包

# 优化构建
优化 Monorepo 的构建性能

# 配置 CI/CD
为 Monorepo 配置 GitHub Actions CI/CD
```

## 参考资料

- Turborepo 文档: [references/turborepo.md](references/turborepo.md)
- pnpm workspace: [references/pnpm-workspace.md](references/pnpm-workspace.md)
