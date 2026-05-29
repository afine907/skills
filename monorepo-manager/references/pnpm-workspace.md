# pnpm Workspace 参考指南

## 概述

pnpm workspace 是 pnpm 内置的 Monorepo 管理功能，支持在一个仓库中管理多个包。

## 配置

### pnpm-workspace.yaml

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'
```

### 根 package.json

```json
{
  "name": "monorepo",
  "private": true,
  "scripts": {
    "dev": "pnpm -r run dev",
    "build": "pnpm -r run build",
    "test": "pnpm -r run test"
  },
  "devDependencies": {
    "typescript": "^5.3.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

## 命令

### 安装依赖

```bash
# 安装所有依赖
pnpm install

# 安装到指定包
pnpm --filter @monorepo/web add react

# 安装到根目录
pnpm -w add -D typescript

# 安装工作区内包
pnpm --filter @monorepo/web add @monorepo/utils
```

### 运行脚本

```bash
# 运行所有包的脚本
pnpm -r run build

# 运行指定包
pnpm --filter @monorepo/web run build

# 并行运行
pnpm -r --parallel run dev

# 运行根脚本
pnpm run build
```

### 过滤器

```bash
# 按包名
pnpm --filter @monorepo/web run build

# 按目录
pnpm --filter ./apps/* run build

# 依赖链
pnpm --filter ...@monorepo/web run build    # web 及依赖
pnpm --filter @monorepo/web... run build    # web 及被依赖

# 变更的包
pnpm --filter "[origin/main]" run build
```

## 包间依赖

### 引用工作区包

```json
{
  "dependencies": {
    "@monorepo/utils": "workspace:*",
    "@monorepo/types": "workspace:*"
  }
}
```

### 版本协议

```json
{
  "dependencies": {
    "@monorepo/utils": "workspace:*",     // 任何版本
    "@monorepo/utils": "workspace:^1.0.0", // 兼容 1.x
    "@monorepo/utils": "workspace:~1.0.0"  // 兼容 1.0.x
  }
}
```

## 依赖管理

### 统一版本 (Catalog)

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'

catalog:
  react: ^18.2.0
  typescript: ^5.3.0
  vitest: ^1.0.0
```

```json
// packages/ui/package.json
{
  "dependencies": {
    "react": "catalog:"
  }
}
```

### 依赖提升

```ini
# .npmrc
shamefully-hoist=true
strict-peer-dependencies=false
```

## TypeScript 项目引用

### 根 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true
  },
  "references": [
    { "path": "./apps/web" },
    { "path": "./apps/api" },
    { "path": "./packages/ui" }
  ]
}
```

### 包 tsconfig.json

```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "references": [
    { "path": "../utils" }
  ]
}
```

## 发布

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

```bash
# 使用 pnpm 版本
pnpm version patch -r
pnpm version minor -r
pnpm version major -r
```

## CI/CD

```yaml
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
      - run: pnpm -r run build
      - run: pnpm -r run test
```

## 官方文档

- https://pnpm.io/workspaces
