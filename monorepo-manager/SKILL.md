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


## Goal

设计和管理 Monorepo 项目结构，包含工作空间配置、依赖管理、构建优化、版本管理

## Trigger

- 用户要求"Monorepo"、"多包管理"、"workspace配置"
  - 需要将多个项目合并到一个仓库
  - 需要优化 Monorepo 构建性能

## 工作流程

### Step 1: 评估现有项目 (Assess)

分析待迁移的项目，收集关键信息：
- 列出所有待合并的项目（名称、语言、框架、依赖）
- 识别共享代码（工具函数、类型定义、UI 组件）
- 评估项目间依赖关系（是否存在循环依赖）
- 统计包数量和团队规模

**诊断命令**：
```bash
# 扫描各项目的依赖
find . -name "package.json" -not -path "*/node_modules/*" -exec cat {} \; | jq '.dependencies | keys[]' | sort | uniq -c | sort -rn
```

**成功标准**：完成项目清单，明确共享代码范围，无循环依赖。

### Step 2: 选择工具 (Choose Tool)

根据项目特征应用决策表：

| 团队规模 | 项目数 | 推荐工具 | 原因 |
|----------|--------|----------|------|
| < 5人 | < 5个 | pnpm workspace | 轻量、足够 |
| 5-20人 | 5-15个 | Turborepo | 缓存高效、配置简单 |
| > 20人 | > 15个 | Nx | 增量构建、代码生成 |
| 需发布 npm 包 | 任意 | Lerna + pnpm | 版本管理强 |

### Step 3: 脚手架搭建 (Scaffold)

生成目录结构，按照项目结构模板创建 `apps/` 和 `packages/` 目录。

### Step 4: 配置工作空间 (Configure)

- 配置 `pnpm-workspace.yaml`
- 配置根 `package.json` 和构建工具（turbo.json）
- 配置 TypeScript 项目引用
- 设置依赖版本 catalog（统一版本管理）

### Step 5: 迁移包 (Migrate)

增量迁移包到 monorepo：
1. 先迁移共享包（无外部依赖的优先）
2. 再迁移应用包
3. 更新包间引用（`workspace:*` 协议）
4. 每次迁移后验证构建

### Step 6: 验证 (Validate)

```bash
# 全量构建
pnpm build

# 全量测试
pnpm test

# 检查缓存命中率
pnpm build  # 第二次运行应命中缓存
```

**成功标准**：全量构建通过，测试通过，缓存命中率 > 80%。

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

## 输出模板

```markdown
# Monorepo 搭建方案

## 项目概览
- **Monorepo 名称**: {monorepo-name}
- **包含包数**: {n} 个应用 + {m} 个共享包
- **选择工具**: {tool-name}
- **选择理由**: {rationale}

## 目标包清单

| 包名 | 类型 | 路径 | 依赖 |
|------|------|------|------|
| {app-name} | 应用 | apps/{app-name} | @monorepo/ui, @monorepo/utils |
| {lib-name} | 共享包 | packages/{lib-name} | 无 |

## 依赖策略
- **版本管理**: {统一版本 / 独立版本}
- **依赖提升**: {是 / 否}
- **共享依赖**: {react, typescript, ...}

## 构建流水线
- **构建工具**: {turbo / nx}
- **缓存策略**: {本地缓存 / 远程缓存}
- **增量构建**: {启用 / 禁用}

## CI/CD 配置
- **平台**: {GitHub Actions / GitLab CI}
- **流水线阶段**: install → build → test → lint → deploy

## 验证清单
- [ ] 全量构建通过
- [ ] 全量测试通过
- [ ] 缓存命中率 > 80%
- [ ] 包间引用正确解析
- [ ] TypeScript 项目引用正常
```

**填写示例**（电商平台）：

```markdown
# Monorepo 搭建方案

## 项目概览
- **Monorepo 名称**: ecommerce-platform
- **包含包数**: 3 个应用 + 3 个共享包
- **选择工具**: Turborepo
- **选择理由**: 团队 8 人，前端 Next.js 项目，Tb 缓存高效

## 目标包清单

| 包名 | 类型 | 路径 | 依赖 |
|------|------|------|------|
| web | 应用 | apps/web | @monorepo/ui, @monorepo/utils, @monorepo/types |
| admin | 应用 | apps/admin | @monorepo/ui, @monorepo/utils |
| api | 应用 | apps/api | @monorepo/utils, @monorepo/types |
| ui | 共享包 | packages/ui | react |
| utils | 共享包 | packages/utils | 无 |
| types | 共享包 | packages/types | 无 |

## 依赖策略
- **版本管理**: 统一版本（pnpm catalog）
- **依赖提升**: 是
- **共享依赖**: react ^18.2.0, typescript ^5.3.0, vitest ^1.0.0

## 构建流水线
- **构建工具**: Turborepo
- **缓存策略**: 远程缓存（Vercel）
- **增量构建**: 启用

## CI/CD 配置
- **平台**: GitHub Actions
- **流水线阶段**: install → build → test → lint → deploy

## 验证清单
- [x] 全量构建通过
- [x] 全量测试通过
- [ ] 缓存命中率 > 80%（需运行多次）
- [x] 包间引用正确解析
- [x] TypeScript 项目引用正常
```

## Edge Cases

1. **循环依赖检测**：如果发现包 A 依赖包 B 且 B 依赖包 A，则需要将共享代码提取到独立的包 C，让 A 和 B 都依赖 C。使用 `pnpm why <package>` 或 `madge --circular` 检测。
2. **跨包类型兼容失败**：如果共享包 A 的 TypeScript 类型与应用包 B 的 tsconfig 不兼容（如 `strict` 模式不一致），则统一使用根 tsconfig 的 `strict: true`，并在共享包中导出完整类型定义。
3. **构建缓存损坏**：如果构建缓存导致产物不一致（如缓存了旧的依赖产物），则清除缓存并重建：`rm -rf node_modules/.cache && pnpm build --force`。
4. **pnpm workspace catalog 版本冲突**：如果 catalog 中声明的版本与某个包的 `package.json` 版本冲突，则运行 `pnpm install --no-frozen-lockfile` 让 pnpm 自动解决，并更新 lockfile。
5. **CI/CD 流水线变慢**：如果 monorepo 的 CI 构建时间超过 10 分钟，使用 Turborepo 的 `--filter` 选项只构建变更的包：`turbo build --filter=...[HEAD^1]`，或配置远程缓存。
6. **添加非 Node.js 包**：如果需要在 monorepo 中添加 Python/Go 等非 Node.js 包，使用 `pnpm workspace` 的 `packages` 字段添加路径，但不要共享 `package.json` 构建流程，为该包创建独立的构建脚本。

## 不适用

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 单个小型项目 | monorepo 带来不必要的复杂度 | 使用单仓库，无需 workspace |
| 团队无代码共享需求 | 包之间没有共享代码，monorepo 无优势 | 使用多仓库，各自独立部署 |
| 异构技术栈（不兼容构建系统） | 不同语言的构建系统无法统一 | 使用多仓库或 git submodule |

**重定向**：
- 对于单包项目优化，使用常规的项目结构和构建配置即可。
- 对于需要跨仓库代码共享的场景，考虑使用 npm 私有包或 Git Submodule。

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
