# Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skills-blue)](https://claude.ai/code)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI-Codex-green)](https://openai.com/codex)
[![Cursor](https://img.shields.io/badge/Cursor-Agent-purple)](https://cursor.sh)
[![Windsurf](https://img.shields.io/badge/Windsurf-Agent-teal)](https://codeium.com/windsurf)

可复用的提示词模板集合，为 AI 编码 Agent 提供结构化能力扩展。支持 Claude Code、OpenAI Codex、Cursor、Windsurf 等编码 Agent。

## 技能列表

| 技能 | 描述 | 命令 |
|------|------|------|
| [**Loom**](loom/SKILL.md) | 项目编排引擎，专为大规模 PRD 项目设计 | `/loom init`, `/loom audit`, `/loom plan`, `/loom execute` |
| [**Commit**](commit/SKILL.md) | 智能 Git Commit 生成器，自动生成语义化提交消息 | `/commit`, `/commit --dry-run` |

### Loom - 项目编排引擎

专业级项目编排系统，专为大规模 PRD（10,000+ 行）多文档项目设计。

**核心特性**：
- 🔍 **审计优先** - 写代码前识别 PRD 中的逻辑缺陷和安全风险
- ⚙️ **状态机驱动** - INIT → AUDIT → PLAN → EXECUTE → VERIFY 结构化工作流
- ✅ **验证驱动** - 测试通过才算任务完成
- 📝 **上下文连续** - Ledger 系统实现跨任务知识传递

<details>
<summary>命令列表</summary>

| 命令 | 说明 |
|------|------|
| `/loom init <project> <prd_paths...>` | 初始化项目工作区 |
| `/loom audit` | 扫描 PRD 风险，生成审计报告 |
| `/loom plan` | 构建 DAG，分解任务 |
| `/loom execute [--task T_XXX]` | 按依赖顺序执行任务 |
| `/loom status` | 查看项目状态 |
| `/loom resume` | 从检查点恢复 |

</details>

### Commit - 智能 Git Commit 生成器

分析暂存区变更并自动生成符合 [Conventional Commits](https://www.conventionalcommits.org/) 规范的提交消息。

**核心特性**：
- 🤖 自动分析 `git diff --staged` 变更内容
- 📝 生成语义化 Commit Message (feat/fix/refactor/docs/style/test/chore)
- 🎯 自动识别影响范围 (scope)
- ✨ 自动添加 Co-Authored-By 标注

<details>
<summary>命令列表</summary>

| 命令 | 说明 |
|------|------|
| `/commit` | 分析暂存变更并生成 commit |
| `/commit -m "msg"` | 使用自定义消息提交 |
| `/commit --amend` | 修改上一次提交 |
| `/commit --dry-run` | 预览 commit message（不提交） |

</details>

## 快速安装

### 方式一：克隆到技能目录

```bash
# 克隆仓库
git clone git@github.com:afine907/skills.git

# 移动到 Claude Code 技能目录
mv skills ~/.claude/skills/
```

### 方式二：直接使用

```bash
# 克隆到任意目录
git clone git@github.com:afine907/skills.git

# 在 Claude Code 中使用完整路径
# /path/to/skills/loom/SKILL.md
```

### 验证安装

```bash
# 在 Claude Code 中执行
/loom status
/commit --dry-run
```

## 快速开始

### Loom 使用示例

```bash
# 1. 初始化项目
/loom init my-project docs/prd/*.md

# 2. 审计风险
/loom audit

# 3. 规划任务
/loom plan

# 4. 执行开发
/loom execute
```

### Commit 使用示例

```bash
# 暂存变更
git add .

# 生成并提交
/commit
```

## 目录结构

```
skills/
├── loom/
│   ├── SKILL.md            # 技能定义
│   ├── references/         # 参考文档 (风险分类、模板)
│   ├── scripts/            # Python 脚本 (DAG管理、风险扫描)
│   └── tests/              # 单元测试
├── commit/
│   └── SKILL.md            # 技能定义
├── CLAUDE.md               # Claude Code 项目指引
├── LICENSE
└── README.md
```

## 开发

```bash
# 运行测试
pytest loom/tests/ -v

# 运行单个测试
pytest loom/tests/test_dag_manager.py::TestDAGManager::test_add_task -v
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

Copyright (c) 2026 Skills Contributors
