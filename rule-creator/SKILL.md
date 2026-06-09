---
name: rule-creator
category: development
description: Create Claude Code rules for .claude/rules/ directory. Trigger on "create a rule", "add a rule", "set up rules", or ".claude/rules".
---

# Rule Creator

A skill for creating Claude Code rules that help Claude understand and follow project-specific conventions.

## Goal

Help users create well-structured rule files in `.claude/rules/` that:
- Use proper YAML frontmatter with `paths` field for scoping
- Follow markdown formatting best practices
- Are organized by topic (testing, code-style, api-design, etc.)
- Load only when relevant, saving context budget

## When to Use This Skill

Trigger this skill when the user:
- Wants to create a new rule for Claude Code
- Mentions `.claude/rules/` directory
- Asks about setting up project conventions
- Wants to enforce coding standards
- Mentions "rule" in the context of Claude Code configuration

## Rule File Structure

Every rule file follows this format:

```markdown
---
paths: ["glob patterns"]
---

# Rule Title

Rule content in markdown...
```

### YAML Frontmatter

The `paths` field specifies which files trigger this rule:

```yaml
---
paths: ["src/**/*.ts", "tests/**/*.ts"]
---
```

**Glob Pattern Examples:**
- `**/*.ts` — All TypeScript files
- `src/**/*` — All files under src/
- `*.test.ts` — Test files in root
- `**/__tests__/**` — Files in __tests__ directories
- `!**/*.d.ts` — Exclude declaration files

### Without Frontmatter

Rules without `paths` load for **every edit** — use sparingly:

```markdown
# Global Rule

This applies to all files...
```

## Workflow

### Step 1: Understand Intent

Ask the user:
1. **What should this rule enforce?** (testing conventions, code style, API design, etc.)
2. **Which files should trigger it?** (file types, directories)
3. **Any specific conventions?** (naming, formatting, patterns)

### Step 2: Choose Template

Based on the topic, select an appropriate template from `references/templates/`:

| Topic | Template File | Use Case |
|-------|---------------|----------|
| Testing | `testing.md` | Test frameworks, naming, coverage |
| Code Style | `code-style.md` | Formatting, linting, naming |
| API Design | `api-design.md` | REST/GraphQL conventions |
| TypeScript | `typescript.md` | Type safety, patterns |
| Python | `python.md` | Python-specific conventions |
| Git | `git.md` | Commit messages, branching |
| Documentation | `documentation.md` | README, comments, docs |

### Step 3: Generate Rule

Create the rule file with:
1. Proper YAML frontmatter with `paths`
2. Clear, actionable instructions
3. Examples where helpful
4. Why each rule matters (not just what)

### Step 4: Save to Project

Save the rule to `.claude/rules/` in the project root:

```
your-project/
├── .claude/
│   ├── CLAUDE.md
│   └── rules/
│       └── your-rule.md
```

### Step 5: Verify (Optional)

If the user wants to verify the rule works:
1. Read a file that should match the `paths`
2. Check if Claude loads the rule
3. Verify the rule content is followed

## Writing Guidelines

### Be Clear and Specific

❌ Bad: "Write good tests"
✅ Good: "Each function must have at least one unit test using Jest. Test files use `.test.ts` extension."

### Explain Why

❌ Bad: "Use camelCase"
✅ Good: "Use camelCase for variables and functions because it's the TypeScript/JavaScript convention and improves readability."

### Keep It Focused

Each rule file should cover ONE topic. Split large rules into multiple files:
- `testing.md` — Test frameworks and patterns
- `testing-naming.md` — Test file and function naming
- `testing-coverage.md` — Coverage requirements

### Use Examples

Show, don't just tell:

```markdown
## Function Naming

Use descriptive names that explain what the function does:

✅ `calculateTotalPrice(items)`
✅ `fetchUserData(userId)`
❌ `calc(u)`
❌ `getData()`
```

## 输出模板

Claude 生成规则文件时，按以下格式输出：

```
## 规则文件报告

### 规则信息
- 文件名：{topic}.md
- 作用域：{paths glob patterns}
- 覆盖主题：{testing / code-style / api-design / ...}

### 生成文件内容
（展示完整的 .md 文件，包含 YAML frontmatter 和规则内容）

### 文件位置
.claude/rules/{topic}.md

### 后续步骤
1. 验证规则是否正确触发（编辑匹配 paths 的文件）
2. 如需调整作用域，修改 paths 字段
3. 如需添加更多规则，重复此流程
```

**端到端示例：**

用户输入：`为 TypeScript 项目添加测试规则`

Claude 输出以上模板，生成的 .md 文件内容为：

```markdown
---
paths: ["**/*.test.ts", "**/*.spec.ts", "tests/**/*.ts"]
---

# TypeScript 测试规范

## 框架与工具
- 使用 Vitest 作为测试运行器
- 使用 @vue/test-utils 或 @testing-library/react 测试组件

## 命名规范
- 测试文件：{模块名}.test.ts 或 {模块名}.spec.ts
- 测试函数：describe("模块名") > it("应该在...时...")

## 覆盖率要求
- 核心业务逻辑：80%+
- 工具函数：90%+
- UI 组件：关键交互路径
```

## 快速使用

```
# 创建测试规则
为项目添加 TypeScript 测试规范

# 创建代码风格规则
为 React 项目添加 ESLint 规则

# 创建 API 设计规则
为 REST API 项目添加接口规范

# 创建 Git 提交规则
为项目添加 commit message 规范
```

## 不适用

- 全局指令配置（CLAUDE.md）→ 直接编辑 CLAUDE.md 文件
- IDE / 编辑器设置（settings.json）→ 使用 Claude Code settings 配置
- 复杂多步骤工作流 → 使用 [task-loom](../task-loom/SKILL.md) 编排

## Edge Cases

### Multiple Path Patterns

When a rule applies to multiple file types:

```yaml
---
paths: ["src/**/*.ts", "tests/**/*.ts", "scripts/**/*.js"]
---
```

### Excluding Files

Use negation patterns:

```yaml
---
paths: ["src/**/*", "!src/**/*.d.ts", "!src/**/*.test.ts"]
---
```

### Complex Scoping

Combine patterns for precise control:

```yaml
---
paths: ["src/components/**/*.tsx", "src/pages/**/*.tsx"]
---
```

## Best Practices

1. **One topic per file** — Easier to maintain and load selectively
2. **Use paths frontmatter** — Avoid loading rules for every edit
3. **Be specific** — Vague rules get ignored
4. **Explain reasoning** — Help Claude understand why, not just what
5. **Include examples** — Show correct and incorrect patterns
6. **Keep it concise** — Rules should be quick to read and follow
7. **Version control** — Commit rules to git for team sharing

## Template Reference

For detailed templates, see `references/templates/` directory. Each template includes:
- YAML frontmatter example
- Recommended sections
- Common patterns
- Anti-patterns to avoid
