# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of Claude Code skills - reusable prompt templates that extend Claude's capabilities. Each skill is a self-contained module with a `SKILL.md` file that defines its behavior.

Each skill has a `category` field in its SKILL.md frontmatter. See individual `*/SKILL.md` for details.

| Category | Phase |
|----------|-------|
| `requirements` | Product & Requirements |
| `development` | Architecture & Coding |
| `quality` | Code Quality & Testing |
| `source-control` | Version Control |
| `operations` | Deploy & Operate |
| `productivity` | Cross-phase Tools |
| `reference` | Reference Cards |

## Creating Skills

### Structure

```
my-skill/           # kebab-case directory name
  SKILL.md          # Required
  scripts/          # Optional: CLI tools
  references/       # Optional: templates, schemas
```

### SKILL.md

Must start with YAML frontmatter (all fields required):

```yaml
---
name: my-skill                    # Must match directory name
description: One-line trigger description for Claude to decide when to invoke.
category: productivity            # requirements|development|quality|source-control|operations|productivity|reference
---
```

Body sections (recommended): Title → Goal → Trigger conditions → Workflow → Best practices → Edge cases.

## High-Quality Skill Design Principles

These patterns are extracted from the highest-scoring skills (9+ points). Follow them to write skills that are genuinely useful, not just structurally complete.

### The 5 Dimensions That Matter

| Dimension | What It Means | Bad Example | Good Example |
|-----------|--------------|-------------|--------------|
| **Workflow** | Numbered steps with decision logic, not just an ASCII arrow diagram | `分析 → 设计 → 实现` | Step 1: 诊断 intake (ask 5 questions) → Step 2: 根据回答选择路径 A/B/C → Step 3: ... |
| **Edge Cases** | Specific if-then failure scenarios with concrete thresholds | "注意性能问题" | ">100K 行: 分批 1000 条/批, sleep 100ms; >1M 行: 用 gh-ost 在线工具" |
| **Decision Tables** | Multi-dimensional lookup matrices that eliminate ambiguity | 简单的两列对比表 | 3+ 列矩阵: 用户输入特征 → 推荐策略 → 具体命令 → 预期输出 |
| **Output Template** | Complete markdown template with placeholders + a filled example | "输出 JSON 格式" | 完整模板含所有字段 + 一个真实场景的 filled 版本 |
| **Not Applicable** | Explicit scope boundary with redirects to correct tools | 无 | "不支持 Jenkins → 用 shell-command; 不支持 Dockerfile → 用 docker-essentials" |

### 7 Design Patterns from Top Skills

**1. Diagnostic Intake (诊断入口)**
Don't jump straight to solutions. Start by asking 3-5 questions to understand context.
```
用户触发 → 问: 什么语言? 什么规模? 什么约束? → 根据答案路由到具体路径
```
Used by: debug-helper, ci-workflow, load-testing, test-strategy

**2. Multi-Path Routing (多路径路由)**
Instead of one linear flow, define 2-3 distinct paths based on user intent.
```
Path A: 标准生成（最常见）
Path B: 审查/优化已有内容
Path C: 输入模糊 → 先澄清再走 Path A
```
Used by: ci-workflow (3 paths), regex-buddy (3 paths)

**3. Iteration with Hard Limits (带硬限的迭代循环)**
For diagnostic/refinement tasks, define a loop with a hard ceiling and human fallback.
```
Step N: 执行 → 检查结果 → 不满意? → 回到 Step 2（最多 3 轮）→ 仍不满意? → 标记需人工介入
```
Used by: wo-yao-yan-pai (max 5), debug-helper (max 3)

**4. Decision Flowchart (决策流程图)**
Replace prose recommendations with ASCII branching diagrams.
```
需要 SSR? ──是──▶ Next.js
    │
    否
    ▼
需要边缘部署? ──是──▶ Hono
    │
    否
    ▼
Fastify
```
Used by: git-branch, load-testing, auth-patterns, mobile-service-creator

**5. Worked Example (端到端示例)**
Show a complete input→output cycle with realistic data, not just code snippets.
```
输入: "为 8 人团队设计分支策略，每周发布"
输出: [完整的分支计划文档，含策略选择理由、命名规范、保护规则、CI 配置]
```
Used by: debug-helper (Python KeyError), caching-strategy (电商缓存), auth-patterns (SaaS 平台)

**6. Safety Constraints (安全约束)**
For skills that execute actions, define explicit danger levels and confirmation flows.
```
绿色: 只读操作 → 直接执行
黄色: 修改操作 → 展示计划后执行
红色: 删除/破坏操作 → 要求用户确认
```
Used by: shell-command (danger levels), migration-helper (backup before migrate)

**7. Scope Boundary with Redirects (范围边界 + 重定向)**
Every skill should explicitly say what it does NOT do and where to go instead.
```
## 不适用
- Kubernetes 集群管理 → 使用 k8s-cluster
- Dockerfile 编写 → 使用 docker-essentials
- CI/CD 配置 → 使用 ci-workflow
```
Used by: ci-workflow, k8s-cluster, k8s-gen, and all 7.0+ skills

### Common Anti-Patterns

- **Reference dump**: Organized by topic (进程管理, 网络诊断, 日志分析) instead of by workflow steps
- **Code recipe collection**: Lots of code examples but no decision logic for when to use which
- **Missing intake**: Jumps from trigger to solution without understanding context
- **Vague edge cases**: "注意性能" instead of ">100K rows → batch size 1000"
- **No output template**: Skill generates something but doesn't define what the deliverable looks like
- **Hidden dependencies**: References other skills in `## 参考资料` instead of keeping them atomic

### Validate locally

```bash
python scripts/validate_skills.py
```

Checks: frontmatter fields, name-directory match, category validity, `[text](path)` links point to existing files.

## Running Tests

```bash
# Run all tests
pytest task-loom/tests/ -v

# Run specific test file
pytest task-loom/tests/test_dag_manager.py -v

# Run single test
pytest task-loom/tests/test_dag_manager.py::TestDAGManager::test_add_task -v
```

