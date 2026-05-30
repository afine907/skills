# Turborepo 参考指南

## 概述

Turborepo 是一个高性能的 JavaScript/TypeScript 项目构建系统，专为 Monorepo 设计。

## 安装

```bash
# 使用 pnpm
pnpm add -Dw turbo

# 使用 npm
npm install -D turbo

# 使用 yarn
yarn add -D turbo
```

## 配置

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"],
      "inputs": ["src/**"],
      "outputMode": "full"
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**", "test/**"]
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

### 任务依赖

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]  // 依赖包的 build 任务
    },
    "test": {
      "dependsOn": ["build"]   // 依赖当前包的 build
    },
    "deploy": {
      "dependsOn": ["build", "test"]  // 依赖 build 和 test
    }
  }
}
```

## 命令

### 基础命令

```bash
# 运行所有包的 build 任务
turbo build

# 运行指定包
turbo build --filter=@monorepo/web

# 运行多个包
turbo build --filter=@monorepo/web --filter=@monorepo/api

# 依赖链
turbo build --filter=...@monorepo/web  # web 及其所有依赖

# 并行运行
turbo build --concurrency=10

# 不使用缓存
turbo build --force
```

### 过滤器

```bash
# 按包名过滤
turbo build --filter=@monorepo/web

# 按目录过滤
turbo build --filter=./apps/*

# 依赖过滤
turbo build --filter=...@monorepo/web    # web 及依赖
turbo build --filter=@monorepo/web...    # web 及被依赖

# 变更过滤
turbo build --filter=...[HEAD^1]         # 变更的包及依赖
turbo build --filter=...[main]           # 相对 main 的变更
```

## 缓存

### 本地缓存

```bash
# 默认缓存位置
.turbo/cache/

# 查看缓存
turbo build --dry-run

# 清理缓存
turbo clean
```

### 远程缓存

```bash
# 登录
turbo login

# 链接到远程缓存
turbo link

# 运行（自动使用远程缓存）
turbo build
```

### 缓存命中

```bash
# 查看缓存状态
turbo build --dry-run

# 输出示例
@monorepo/web:build: cache hit, replaying output
@monorepo/api:build: cache miss, executing
@monorepo/utils:build: cache hit, replaying output
```

## 工作区配置

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
    "lint": "turbo lint"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

## CI/CD 集成

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - run: pnpm install --frozen-lockfile
      - run: turbo build --filter=...[HEAD^1]
      - run: turbo test --filter=...[HEAD^1]
```

## 性能优化

### 减少缓存大小

```json
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"],  // 只缓存必要的输出
      "inputs": ["src/**"]     // 只监听必要的输入
    }
  }
}
```

### 并行执行

```bash
# 增加并发数
turbo build --concurrency=50%

# 限制并发
turbo build --concurrency=4
```

## 官方文档

- https://turbo.build/docs
