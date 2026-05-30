---
name: ci-workflow
category: operations
description: |
  自然语言描述 → CI 配置文件（GitHub Actions / GitLab CI）+ 逐段解释 + 安全审查。
  适用场景：用户要求"写 CI 配置"、"配个 GitHub Actions/GitLab CI"、"自动构建/部署/发布流程"。
  触发关键词：/ci、ci/cd、github actions、gitlab ci、pipeline、workflow、自动构建、自动部署。
---

# CI Workflow — CI 配置生成 Agent

自然语言描述 → CI 配置文件 + 逐段解释 + 安全审查，一次输出。

不适用：Jenkins、CircleCI、Azure DevOps 等非 GitHub/GitLab 平台（不在当前覆盖范围）；本地构建部署（用 shell-command）；Dockerfile 编写（用 docker-essentials）；监控告警配置（用 log-analyzer）。


## Goal

自然语言描述 → CI 配置文件（GitHub Actions / GitLab CI）+ 逐段解释 + 安全审查


## Trigger

- 用户说"写 CI 配置"、"配个 GitHub Actions"、"配个 GitLab CI"
- 用户提到 ci/cd、pipeline、workflow、自动构建、自动部署
- 用户要求配置自动发布流程、PR 检查、安全扫描


## 工作流程

### 三条路径

```
路径A - 标准生成（用户描述需求）：
描述 → 识别平台 → 选构造策略 → 编写配置 → 逐段解释 → 安全审查

路径B - 审查/优化（用户给已有配置）：
读取配置 → 逐段解析 → 输出 review 报告 → 标注风险和优化点

路径C - 输入模糊（需求不清晰）：
追问具体平台、触发条件、技术栈、部署目标 → 回到路径A
```

## 快速使用

```
# 标准生成（路径A）
配个 GitHub Actions，Node.js 项目，npm 构建+测试

# 配置审查（路径B）
帮我审查这个 GitHub Actions 配置有没有安全问题：
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo ${{ secrets.PRODUCTION_KEY }}

# Docker CI（路径A）
配个 GitLab CI，Go 项目，Docker 构建+推送到仓库

# 发布流程（路径A）
配置自动发布流程：打 tag 自动构建并发布到 GitHub Release

# 模糊需求（路径C）
帮我配个 CI
```

## 平台识别

| 标志 | 平台 | 配置文件名 |
|------|------|-----------|
| 项目下有 `.github/workflows/` | GitHub Actions | `.github/workflows/*.yml` |
| 项目下有 `.gitlab-ci.yml` | GitLab CI | `.gitlab-ci.yml` |
| 用户提到 GitHub / Actions（已指明平台） | GitHub Actions | — |
| 用户提到 GitLab（已指明平台） | GitLab CI | — |
| 用户未指定 | 检测 `.github/workflows/` 或 `.gitlab-ci.yml`；均不存在则追问平台和需求 | — |

## 构造策略

| 场景 | 策略 | 关键点 |
|------|------|--------|
| **构建测试** | checkout → setup → deps → test → (lint) | 缓存依赖、并行 job、fail-fast |
| **Docker 构建推送** | login → buildx → cache → push | 多架构、layer caching、tag 策略 |
| **部署** | build → test → deploy | environment 审批、回滚策略、artifact 传递 |
| **Lint/格式检查** | 并行独立 job | 与构建解耦、fail-fast |
| **Release** | tag 触发 → build → release | GitHub Release / GitLab Release、changelog |
| **PR 自动检查** | 每次 PR 触发 | 状态检查、必过 job、自动合并规则 |
| **安全扫描** | 定时或 PR 触发 | CodeQL、secret 扫描、dependency review |
| **依赖更新** | 定时触发 | Dependabot / Renovate 配置 |
| **Monorepo** | workspace 识别 → 增量构建 → 按需部署 | Nx/Turborepo/pnpm workspace、触发过滤、缓存共享 |
| **Mobile（iOS/Android）** | 证书管理 → 构建 → 签名 → 发布 | Xcode/Gradle、Fastlane、代码签名、TestFlight/Play Store |

> 更多配置片段见 [references/patterns.md](references/patterns.md)，非标需求时翻查。

### 缓存策略选择

| 场景 | 缓存目标 | 有效 key |
|------|----------|----------|
| **npm** | `~/.npm`（`actions/setup-node` 内置 cache 自动管理） | `${{ runner.os }}-npm-${{ hashFiles('package-lock.json') }}` |
| **pnpm/yarn** | `~/.local/share/pnpm` / `$(yarn cache dir)` | `${{ runner.os }}-pkgmgr-${{ hashFiles('pnpm-lock.yaml') }}` |
| **pip/poetry** | `~/.cache/pip` | `${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}` |
| **maven/gradle** | `~/.m2/repository` | `${{ runner.os }}-maven-${{ hashFiles('pom.xml') }}` |
| **go** | `~/go/pkg/mod` | `${{ runner.os }}-go-${{ hashFiles('go.sum') }}` |
| **docker layer** | BuildKit cache | `type=gha` / `type=registry` |

## 输出模板

````markdown
```yaml
<CI 配置文件内容>
```

**平台**: GitHub Actions / GitLab CI
**目标文件**: `.github/workflows/<name>.yml` / `.gitlab-ci.yml`
**说明**: <一句话解释配置作用>
**关键设计**: [配置中的关键决策及原因，如缓存策略、并发控制、触发条件等]

### 逐段解释
| 配置段 | 含义 |
|--------|------|
| <段名> | <用途说明> |

### 安全审查
| 检查项 | 状态 | 说明 |
|--------|------|------|
| <检查项> | ✅ 通过 / ⚠️ 警告 / 🔴 拒绝 | <说明> |

### 使用建议
- <dry-run / 测试建议>
- <维护提示>
````

## 安全检查

| 检查项 | 风险等级 | 处理方式 |
|--------|----------|----------|
| 明文密码/token/密钥硬编码 | 🔴 拒绝 | 必须使用 Secrets（`${{ secrets.XXX }}` / `$CI_JOB_TOKEN`） |
| `pull_request_target` + checkout PR 代码 | 🔴 拒绝 | 恶意 PR 可窃取 secrets |
| `pull_request_target` 中 `persist-credentials` 未禁用 | 🔴 拒绝 | GITHUB_TOKEN 在后续步骤仍可用，PR 脚本可窃取 |
| 自托管 runner + `pull_request` 触发 | 🟡 警告 | PR 代码在 runner 上执行任意代码，建议仅用于受信任分支 |
| `GITHUB_TOKEN` 权限设为 `write-all` | 🟡 警告 | 限制到最小必要权限 |
| 缺少依赖缓存 | 🟡 警告 | 建议配置缓存可减少 50%+ 构建时间 |
| 缺少并发控制 | 🟡 警告 | 建议设置 `concurrency` + `cancel-in-progress` |
| 缺少超时限制 | 🟡 警告 | 建议设置 `timeout-minutes` 防止 runaway job |
| secrets 作用域设为全局 | 🟡 警告 | 建议限制到 environment 级别 |
| CI 脚本含 `sudo` / 系统修改 | 🟡 警告 | 确认 CI 环境是否需要 root 权限 |
| 未指定 `if:` 条件的事件触发 | 🟢 提示 | 建议按分支/路径过滤减少不必要运行 |
| artifact 无保留期 | 🟢 提示 | 建议设置 `retention-days` |
| 缺少 fail-fast 策略 | 🟢 提示 | 矩阵构建建议启用 fail-fast |
| 缺少 OIDC 配置 | 🟢 提示 | 云部署建议使用 OIDC 替代静态密钥 |

## 最佳实践

| 规则 | 说明 |
|------|------|
| **最小权限** | token 权限只给 job 需要的最小范围 |
| **缓存优先** | 包管理器、Docker layer 都配置缓存 |
| **显式超时** | 每个 job 都设置 `timeout-minutes` |
| **并发控制** | 同一 PR/分支的重复运行自动取消 |
| **触发过滤** | `paths` / `paths-ignore` 避免无关触发 |
| **环境隔离** | 敏感部署用 `environment` + 审批 |
| **版本 pin** | actions 用 `@sha` 或主版本号（`@v4`），不用 `@main` |
