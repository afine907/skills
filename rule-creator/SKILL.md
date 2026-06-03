---
name: rule-creator
description: Create Claude Code rules for .claude/rules/ directory. Use this skill when the user wants to create, add, or set up rules for Claude Code, including testing rules, code style rules, API design rules, or any project-specific conventions. Trigger on phrases like "create a rule", "add a rule", "set up rules", "Claude Code rules", ".claude/rules", or when discussing project conventions that should be enforced.
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
