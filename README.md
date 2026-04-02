# Skills

Claude Code 技能集合，提供高效的开发工作流增强工具。

## 技能列表

### [Loom](loom/SKILL.md) - 项目编排引擎

专业级项目编排系统，专为大规模 PRD（10,000+ 行）多文档项目设计。

**核心价值**：
- **审计优先** - 写代码前识别逻辑缺陷
- **状态机驱动** - 结构化工作流管理
- **验证驱动** - 测试通过才算完成
- **上下文连续** - Ledger 系统实现跨任务知识传递

**命令**：

| 命令 | 说明 |
|------|------|
| `/loom init <project> <prd_paths...>` | 初始化项目工作区 |
| `/loom audit` | 扫描 PRD 风险，生成审计报告 |
| `/loom plan` | 构建 DAG，分解任务 |
| `/loom execute [--task T_XXX]` | 按依赖顺序执行任务 |
| `/loom status` | 查看项目状态 |
| `/loom resume` | 从检查点恢复 |

---

### [Commit](commit/SKILL.md) - 智能 Git Commit 生成器

分析暂存区变更并自动生成符合规范的 commit message。

**核心功能**：
- **自动分析** - 分析 `git diff --staged` 变更内容
- **语义化消息** - 生成 Conventional Commits 规范消息
- **范围检测** - 自动识别影响模块/组件
- **多文件支持** - 统一处理多文件变更

**命令**：

| 命令 | 说明 |
|------|------|
| `/commit` | 分析暂存变更并生成 commit |
| `/commit -m "message"` | 使用自定义消息提交 |
| `/commit --amend` | 修改上一次提交 |
| `/commit --dry-run` | 预览 commit message（不提交） |

## 安装

将技能目录放置在 Claude Code 技能路径下，即可通过 `/技能名` 调用。

## 目录结构

```
skills/
├── loom/                    # 项目编排引擎
│   ├── SKILL.md            # 技能定义
│   ├── references/         # 参考文档
│   ├── scripts/            # 辅助脚本
│   └── tests/              # 测试文件
├── commit/                  # Commit 生成器
│   └── SKILL.md            # 技能定义
└── README.md               # 本文件
```

## 许可证

[MIT License](LICENSE)

Copyright (c) 2026 Skills Contributors
