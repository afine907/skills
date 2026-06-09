# Harness Engineering Setup

为历史项目快速搭建 Claude Code harness engineering 环境的技能。

## 功能特性

- **自动检测项目技术栈**: 支持 JavaScript/TypeScript、Python、Go 等多种语言
- **智能配置生成**: 根据检测结果生成最合适的配置文件
- **全栈项目支持**: 为前后端分别生成配置，使用正确的 globs 配置
- **团队协作友好**: 包含 Git 规范、文档规范、测试规范等团队协作所需的配置

## 支持的技术栈

### 语言
- JavaScript/TypeScript
- Python
- Go
- Rust (基础支持)
- Java (基础支持)

### 框架
- React, Vue, Angular
- Next.js, Nuxt.js
- Express, Fastify, Hono
- FastAPI, Flask, Django
- Gin, Echo, Fiber

### 构建工具
- Webpack, Vite, Turbopack
- esbuild, Rollup
- Create React App

## 生成的配置文件

### CLAUDE.md
项目级 Claude Code 配置文件，包含：
- 项目概述和技术栈
- 开发命令（install, dev, build, test, lint）
- 项目结构说明
- 编码规范建议

### .claude/rules/
Claude Code 规则文件目录，包含：
- **code-style.md**: 代码风格规范
- **git.md**: Git 工作流规范
- **documentation.md**: 文档规范
- **testing.md**: 测试规范
- **typescript.md**: TypeScript 规则（如果是 TS 项目）
- **python.md**: Python 规则（如果是 Python 项目）
- **go.md**: Go 规则（如果是 Go 项目）
- **react.md**: React 规则（如果是 React 项目）
- **api-design.md**: API 设计规则（如果是后端服务）

### .cursorrules
Cursor IDE 兼容配置文件，合并所有规则。

## 使用方法

### 触发条件

当用户需要为项目搭建 Claude Code harness engineering 环境时触发：
- "帮我搭建 harness"
- "配置 Claude 规则"
- "为团队制定标准配置"
- "初始化 Claude 环境"

### 工作流程

1. **项目扫描**: 检测项目技术栈和现有配置
2. **配置决策**: 确定需要生成的配置文件
3. **生成 CLAUDE.md**: 生成项目级配置
4. **创建规则目录**: 生成 .claude/rules/ 目录和规则文件
5. **生成 .cursorrules**: 合并所有规则
6. **配置工具套件**: 推荐并配置代码质量工具
7. **验证与文档**: 验证配置并更新文档

## 示例

### React + TypeScript + Vite 项目

```bash
# 检测技术栈
cat package.json | grep -E "react|typescript|vite"

# 生成配置
# 会自动生成：
# - CLAUDE.md
# - .claude/rules/typescript.md
# - .claude/rules/react.md
# - .claude/rules/code-style.md
# - .cursorrules
```

### Python FastAPI 项目

```bash
# 检测技术栈
cat requirements.txt | grep -E "fastapi|uvicorn"

# 生成配置
# 会自动生成：
# - CLAUDE.md
# - .claude/rules/python.md
# - .claude/rules/api-design.md
# - .claude/rules/code-style.md
# - .cursorrules
```

### 全栈 Next.js + Go Gin 项目

```bash
# 检测技术栈
ls frontend/package.json backend/go.mod

# 生成配置
# 会自动生成：
# - CLAUDE.md (包含整体架构说明)
# - .claude/rules/typescript.md (globs: ["frontend/**/*.ts"])
# - .claude/rules/react.md (globs: ["frontend/**/*.tsx"])
# - .claude/rules/go.md (globs: ["backend/**/*.go"])
# - .claude/rules/api-design.md (globs: ["backend/**/*.go"])
# - .cursorrules (合并所有规则)
```

## 最佳实践

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

## 评估结果

### 第一轮测试
- **完整性**: 7/10
- **准确性**: 7/10
- **清晰度**: 8/10
- **实用性**: 7/10
- **总分**: 29/40

### 第二轮测试（优化后）
- **完整性**: 9/10 (+2)
- **准确性**: 9/10 (+2)
- **清晰度**: 9/10 (+1)
- **实用性**: 9/10 (+2)
- **总分**: 36/40 (+7)

**效果判断**: +24.1% 提升，技能有明显价值。

## 改进历史

### v1.0 (初始版本)
- 支持基础技术栈检测
- 生成 CLAUDE.md 和 .claude/rules/
- 支持 JavaScript/TypeScript、Python、Go

### v1.1 (优化版本)
- 改进全栈项目支持
- 优化 globs 配置
- 添加 testing.md 规则文件
- 提升代码质量（+7 分）

## 参考资源

- [规则文件模板](references/rule-templates.md)
- [配置检查清单](references/config-checklist.md)
- [团队共享指南](references/team-sharing.md)
