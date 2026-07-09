---
name: monorepo-manager
description: |
  【Monorepo管理】设计和管理 Monorepo 项目结构，包含工作空间配置、依赖管理、构建优化。

  触发时机：
  - 用户要求"Monorepo"、"多包管理"、"workspace配置"
  - 需要将多个项目合并到一个仓库
category: development
---

# Monorepo Manager — Monorepo 管理

设计和管理 Monorepo 项目，实现代码共享和高效构建。

## Workflow

1. **评估需求** — 是否真的需要 Monorepo
2. **选择工具** — pnpm workspace / Turborepo / Nx / Lerna
3. **设计结构** — packages/ 目录划分、共享代码
4. **配置构建** — 依赖拓扑、增量构建、缓存
5. **配置 CI** — 只构建变更的包

## 方案对比

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| pnpm workspace | 原生支持、速度快 | Node.js 项目 |
| Turborepo | 构建编排、远程缓存 | 大型前端项目 |
| Nx | 依赖图、增量构建 | 全栈项目 |
| Lerna | 版本管理、发布 | npm 包发布 |

## pnpm workspace 配置

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```json
// package.json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint"
  }
}
```

## 目录结构

```
my-monorepo/
├── apps/
│   ├── web/              # 前端应用
│   ├── api/              # 后端服务
│   └── admin/            # 管理后台
├── packages/
│   ├── ui/               # 共享 UI 组件
│   ├── utils/            # 共享工具函数
│   ├── config/           # 共享配置 (eslint, tsconfig)
│   └── types/            # 共享类型定义
├── pnpm-workspace.yaml
├── turbo.json
└── package.json
```

## Turborepo 配置

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {}
  }
}
```

## Example

```
用户: 将 3 个独立项目合并为 Monorepo

输出:
1. 创建 monorepo 结构: apps/ + packages/
2. 配置 pnpm workspace
3. 提取共享代码到 packages/shared
4. 配置 Turborepo 构建编排
5. CI: 只构建 pnpm --filter ...[origin/master] 变更的包
```

## 参考

- Turborepo: [references/turborepo.md](references/turborepo.md)
- pnpm workspace: [references/pnpm-workspace.md](references/pnpm-workspace.md)
