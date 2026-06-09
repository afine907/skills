# 配置检查清单

本文档提供 harness engineering 配置生成的完整检查清单。

## 项目扫描检查

### 技术栈检测

- [ ] 识别项目主要编程语言
- [ ] 识别使用的框架和库
- [ ] 识别构建工具和打包器
- [ ] 识别包管理器
- [ ] 识别现有代码质量工具（linters, formatters）
- [ ] 识别测试框架
- [ ] 识别 CI/CD 配置

### 现有配置检查

- [ ] 检查是否存在 CLAUDE.md
- [ ] 检查是否存在 .claude/ 目录
- [ ] 检查是否存在 .cursorrules 文件
- [ ] 检查是否存在 .editorconfig
- [ ] 检查是否存在 .gitignore
- [ ] 检查是否存在 README.md

## 配置文件生成检查

### CLAUDE.md 生成

- [ ] 包含项目概述
- [ ] 包含技术栈信息
- [ ] 包含开发命令（install, dev, build, test, lint）
- [ ] 包含项目结构说明
- [ ] 包含编码规范建议
- [ ] 文件格式正确，无语法错误

### .claude/rules/ 目录生成

- [ ] 创建 .claude/rules/ 目录
- [ ] 生成通用规则文件（code-style.md, git.md, documentation.md）
- [ ] 生成语言特定规则（typescript.md, python.md, go.md 等）
- [ ] 生成框架特定规则（react.md, api-design.md 等）
- [ ] 每个规则文件包含正确的 frontmatter（globs 字段）
- [ ] 规则内容具体明确，有示例

### .cursorrules 生成

- [ ] 合并所有 .claude/rules/ 中的规则
- [ ] 格式适合 Cursor IDE
- [ ] 无重复内容
- [ ] 文件编码正确（UTF-8）

## 代码质量套件配置检查

### JavaScript/TypeScript 项目

- [ ] ESLint 配置（.eslintrc.json 或 eslint.config.js）
- [ ] Prettier 配置（.prettierrc）
- [ ] EditorConfig 配置（.editorconfig）
- [ ] Husky + lint-staged 配置（.husky/, package.json 配置）
- [ ] TypeScript 配置（tsconfig.json）如果适用

### Python 项目

- [ ] Black 配置（pyproject.toml 或 setup.cfg）
- [ ] isort 配置（pyproject.toml 或 setup.cfg）
- [ ] flake8 或 ruff 配置
- [ ] mypy 配置（pyproject.toml 或 mypy.ini）
- [ ] pre-commit 配置（.pre-commit-config.yaml）

### Go 项目

- [ ] golangci-lint 配置（.golangci.yml）
- [ ] Makefile 包含 lint, test, build 命令
- [ ] Go 模块配置（go.mod, go.sum）

## 测试框架配置检查

### JavaScript/TypeScript 项目

- [ ] Jest 或 Vitest 配置
- [ ] 测试覆盖率配置
- [ ] 示例测试文件
- [ ] 测试脚本添加到 package.json

### Python 项目

- [ ] pytest 配置（pyproject.toml 或 pytest.ini）
- [ ] 测试覆盖率配置（pytest-cov）
- [ ] 示例测试文件
- [ ] 测试脚本添加到 Makefile 或 pyproject.toml

### Go 项目

- [ ] 标准测试文件结构
- [ ] 测试覆盖率配置
- [ ] 示例测试文件
- [ ] Makefile 包含 test 命令

## 团队共享检查

### Git 配置

- [ ] .gitignore 包含本地配置文件（如 .env.local）
- [ ] 配置文件纳入版本控制
- [ ] 提供 .env.example 示例文件

### 文档更新

- [ ] README.md 包含配置说明
- [ ] 添加贡献指南
- [ ] 添加配置文件说明

### 团队协作

- [ ] 配置文件可跨平台使用（Windows, macOS, Linux）
- [ ] 配置文件可跨 IDE 使用（VS Code, Cursor, Windsurf）
- [ ] 提供配置自定义指南

## 验证检查

### 语法验证

- [ ] 所有 JSON 文件语法正确
- [ ] 所有 YAML 文件语法正确
- [ ] 所有 Markdown 文件格式正确

### 功能验证

- [ ] 运行 linting 命令无错误
- [ ] 运行测试命令通过
- [ ] 运行构建命令成功

### 兼容性验证

- [ ] 配置在目标 IDE 中正常工作
- [ ] 配置在不同操作系统中正常工作
- [ ] 配置不与现有工具冲突

## 最终检查

- [ ] 所有生成的文件已保存
- [ ] 提供了配置使用说明
- [ ] 提供了配置自定义建议
- [ ] 提供了团队共享指南
- [ ] 更新了项目 README（如果需要）
