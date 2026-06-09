---
name: harness-engineering-setup
description: |
  【Harness Engineering 搭建】为历史项目快速搭建 Claude Code harness engineering 环境。
  自动检测技术栈，生成 CLAUDE.md、.claude/rules、.cursorrules 等配置文件。
  触发时机：用户要求"搭建 harness"、"配置 Claude 规则"、"为团队制定标准配置"
category: productivity
---

# Harness Engineering Setup

为历史项目快速搭建 Claude Code harness engineering 环境，自动检测技术栈并生成标准化配置。

## Goal

帮助团队快速为没有 harness engineering 的历史项目搭建完整的 Claude Code 配置环境，包括：
- 自动检测项目技术栈（前端/后端/全栈，语言和框架）
- 生成项目级 CLAUDE.md 配置文件
- 创建 .claude/rules/ 目录结构和规则文件
- 生成 .cursorrules 文件以支持 Cursor IDE
- 配置通用代码质量套件（linting、formatting、testing）

## Trigger

当用户需要为项目搭建 Claude Code harness engineering 环境时触发。典型场景：
- "帮我搭建 harness"、"配置 Claude 规则"
- "这个项目没有 CLAUDE.md，帮我创建"
- "为团队制定标准配置"
- "初始化 Claude 环境"

## Workflow

### Step 1: 项目扫描与技术栈检测

首先分析目标项目，识别技术栈和现有配置：

```bash
# 检查项目根目录
ls -la

# 识别包管理器和依赖
cat package.json 2>/dev/null || cat requirements.txt 2>/dev/null || cat go.mod 2>/dev/null || cat Cargo.toml 2>/dev/null

# 检查现有配置文件
ls -la .claude/ 2>/dev/null || echo "No .claude directory"
ls -la .cursorrules 2>/dev/null || echo "No .cursorrules file"
ls -la CLAUDE.md 2>/dev/null || echo "No CLAUDE.md file"

# 检查是否为全栈项目（多语言/多框架）
ls -la frontend/ backend/ src/ api/ 2>/dev/null || echo "Checking for monorepo structure"
find . -maxdepth 2 -name "package.json" -o -name "requirements.txt" -o -name "go.mod" 2>/dev/null | head -10
```

**检测维度：**
- **语言**: JavaScript/TypeScript, Python, Go, Rust, Java, C# 等
- **框架**: React, Vue, Angular, Next.js, Express, FastAPI, Gin 等
- **构建工具**: Webpack, Vite, Turbopack, esbuild 等
- **包管理器**: npm, yarn, pnpm, pip, go mod, cargo 等
- **现有工具**: ESLint, Prettier, Black, pytest, Jest 等
- **项目结构**: 单体应用、全栈项目、monorepo

### Step 2: 配置生成决策

根据检测结果，确定需要生成的配置文件：

| 检测结果 | 生成内容 |
|----------|----------|
| 无 CLAUDE.md | 生成项目级 CLAUDE.md |
| 无 .claude/rules/ | 创建规则目录和基础规则文件 |
| 无 .cursorrules | 生成 Cursor IDE 兼容配置 |
| 无 linting 配置 | 推荐并配置代码检查工具 |
| 无 testing 配置 | 推荐并配置测试框架 |

**全栈项目特殊处理：**
- 如果检测到多个技术栈（如前端 + 后端），需要为每个部分分别生成配置
- 在 CLAUDE.md 中提供整体项目架构说明
- 为前后端分别生成规则文件，使用不同的 paths/globs 配置
- 确保 .cursorrules 包含所有技术栈的规则

### Step 3: 生成 CLAUDE.md

使用模板生成项目级 CLAUDE.md 文件：

```markdown
# CLAUDE.md

## 项目概述

{项目名称} - {简短描述}

## 技术栈

- **语言**: {检测到的语言}
- **框架**: {检测到的框架}
- **构建工具**: {构建工具}
- **包管理器**: {包管理器}

## 开发命令

```bash
# 安装依赖
{install_command}

# 开发模式
{dev_command}

# 构建
{build_command}

# 测试
{test_command}

# 代码检查
{lint_command}
```

## 项目结构

{根据检测到的框架，提供标准项目结构说明}

## 编码规范

{根据技术栈，提供编码规范建议}
```

### Step 4: 创建 .claude/rules/ 目录

根据技术栈生成对应的规则文件：

**通用规则（所有项目）：**
- `code-style.md` - 代码风格规范
- `git.md` - Git 工作流规范
- `documentation.md` - 文档规范
- `testing.md` - 测试规范

**语言特定规则：**
- `typescript.md` - TypeScript 规则（如果是 TS/JS 项目）
- `python.md` - Python 规则（如果是 Python 项目）
- `go.md` - Go 规则（如果是 Go 项目）

**框架特定规则：**
- `react.md` - React 规则（如果是 React 项目）
- `api-design.md` - API 设计规则（如果是后端服务）

**全栈项目规则生成：**
对于全栈项目，需要为前后端分别生成规则文件：

```markdown
---
globs: ["frontend/src/**/*.ts", "frontend/src/**/*.tsx"]
---

# 前端规则（TypeScript/React）
...
```

```markdown
---
globs: ["backend/**/*.go"]
---

# 后端规则（Go）
...
```

每个规则文件使用标准 frontmatter 格式：

```markdown
---
globs: ["src/**/*.ts", "tests/**/*.ts"]
---

# 规则标题

规则内容...
```

### Step 5: 生成 .cursorrules

将 .claude/rules/ 中的规则合并为单个 .cursorrules 文件，用于 Cursor IDE 兼容：

```bash
# 合并所有规则文件
cat .claude/rules/*.md > .cursorrules
```

### Step 6: 配置通用套件

根据检测到的现有工具，推荐并配置：

**代码质量：**
- ESLint + Prettier (JavaScript/TypeScript)
- Black + isort (Python)
- gofmt + golangci-lint (Go)

**测试框架：**
- Jest + React Testing Library (React)
- Vitest (现代前端)
- pytest (Python)
- go test (Go)

**Git hooks：**
- husky + lint-staged (JavaScript)
- pre-commit (Python)

### Step 7: 验证与文档

生成完成后：
1. 验证所有配置文件语法正确
2. 运行一次 linting 和测试确认配置生效
3. 更新项目 README 添加配置说明
4. 提供团队共享指南

## Best Practices

### 规则文件设计
- **单一职责**: 每个规则文件只覆盖一个主题
- **路径作用域**: 使用 `globs` frontmatter 控制规则加载范围
- **具体明确**: 规则要具体，避免笼统的"写好代码"
- **解释 why**: 说明规则背后的原因，不只是 what
- **示例驱动**: 提供正确和错误的示例

### 配置管理
- **版本控制**: 将所有配置文件纳入 Git
- **团队共享**: 通过 .gitignore 排除本地配置
- **渐进式**: 先添加基础规则，再逐步完善
- **可维护**: 定期审查和更新规则

### 跨平台兼容
- **Claude Code**: 使用 .claude/rules/ 目录
- **Cursor IDE**: 使用 .cursorrules 文件
- **Windsurf**: 兼容 Claude Code 规则格式
- **通用**: 确保规则在不同 IDE 中一致

## Edge Cases

### 1. 多技术栈项目（全栈项目）
对于全栈项目（如 Next.js + Python, React + Go Gin），需要为前后端分别生成规则：

**检测策略：**
```bash
# 检查前端目录
ls -la frontend/ client/ src/ 2>/dev/null | grep -E "package.json|tsconfig.json"

# 检查后端目录
ls -la backend/ server/ api/ 2>/dev/null | grep -E "requirements.txt|go.mod|pyproject.toml"

# 检查 monorepo 结构
ls -la packages/ 2>/dev/null
```

**配置生成策略：**
- **CLAUDE.md**: 生成项目级配置，包含整体架构说明
- **.claude/rules/**: 为每个技术栈生成独立的规则文件
  - 前端规则：使用 `frontend/**/*.ts`, `frontend/**/*.tsx` 路径
  - 后端规则：使用 `backend/**/*.py`, `backend/**/*.go` 路径
- **.cursorrules**: 合并所有规则，确保覆盖所有技术栈

**示例结构：**
```
project/
├── CLAUDE.md                    # 项目级配置
├── .claude/
│   └── rules/
│       ├── code-style.md        # 通用规则
│       ├── git.md               # 通用规则
│       ├── typescript.md        # 前端规则 (globs: ["frontend/**/*.ts"])
│       ├── react.md             # 前端规则 (globs: ["frontend/**/*.tsx"])
│       ├── go.md                # 后端规则 (globs: ["backend/**/*.go"])
│       └── api-design.md        # 后端规则 (globs: ["backend/**/*.go"])
└── .cursorrules                 # 合并所有规则
```

### 2. 单体仓库 (Monorepo)
使用 workspace 配置，为每个子项目生成独立规则：
```
packages/
├── frontend/
│   ├── CLAUDE.md
│   └── .claude/rules/
└── backend/
    ├── CLAUDE.md
    └── .claude/rules/
```

### 3. 已有部分配置
如果项目已有部分配置文件，采用增量更新策略：
- 保留现有配置，只添加缺失部分
- 合并而非覆盖现有规则
- 提供配置迁移建议

### 4. 自定义规则需求
支持用户在生成后自定义：
- 提供规则模板库
- 支持从现有项目导入规则
- 提供规则效果评估工具

## References

- [规则文件模板](references/rule-templates.md) - 各技术栈的规则模板
- [配置检查清单](references/config-checklist.md) - 配置生成的检查清单
- [团队共享指南](references/team-sharing.md) - 配置文件的团队共享最佳实践
