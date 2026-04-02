# Commit - 智能 Git Commit 生成器

分析暂存区变更并自动生成符合 [Conventional Commits](https://www.conventionalcommits.org/) 规范的提交消息。

## 核心特性

- 🤖 自动分析 `git diff --staged` 变更内容
- 📝 生成语义化 Commit Message
- 🎯 自动识别影响范围 (scope)
- ✨ 支持多文件变更聚合

## 命令

| 命令 | 说明 |
|------|------|
| `/commit` | 分析暂存变更并生成 commit |
| `/commit -m "msg"` | 使用自定义消息提交 |
| `/commit --amend` | 修改上一次提交 |
| `/commit --dry-run` | 预览 commit message（不提交） |

## 工作流程

### Step 1: 预检查

```bash
# 验证 git 仓库
git rev-parse --is-inside-work-tree

# 检查暂存变更
git diff --staged --quiet

# 获取暂存文件
git diff --staged --name-only
```

**如果没有暂存变更**：检查 `git status`，提示用户先暂存。

### Step 2: 分析变更

```bash
git diff --staged
git diff --staged --stat
```

**分析重点**：

1. **变更类型检测**
   - 新文件 → `feat`
   - 修改文件 → 根据内容判断
   - 删除文件 → `refactor` 或 `chore`

2. **语义类型分类**
   - `feat`: 新功能
   - `fix`: Bug 修复
   - `refactor`: 重构（不改变行为）
   - `docs`: 文档
   - `style`: 格式化
   - `test`: 测试
   - `chore`: 构建、依赖、工具
   - `perf`: 性能优化
   - `ci`: CI/CD 配置
   - `build`: 构建系统

3. **范围识别**
   - 从文件路径提取：`src/auth/login.ts` → scope: `auth`

### Step 3: 生成 Commit Message

**格式**：
```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**规则**：
- 标题使用祈使语气："add" 而非 "added"
- 结尾不加句号
- 标题最多 50 字符
- 正文每行最多 72 字符
- 页脚：`BREAKING CHANGE:`、`Closes #123`、`Fixes #456`

**示例**：

```bash
# 简单功能
feat(auth): add JWT token refresh mechanism

# Bug 修复（带正文）
fix(payment): handle duplicate callback correctly

Payment callback was processing duplicates due to missing idempotency
check. Added unique constraint on (order_id, callback_id).

Fixes #234

# 多文件变更
feat(api): add user profile endpoints

- Add GET /api/users/:id/profile endpoint
- Add PUT /api/users/:id/profile endpoint
- Add profile image upload support

# 破坏性变更
refactor(db)!: migrate from MySQL to PostgreSQL

BREAKING CHANGE: Database migration required. Run `npm run migrate`
before upgrading.
```

### Step 4: 执行提交

```bash
git commit -m "type(scope): subject" [-m "optional body"]
```

**验证**：
```bash
git log -1 --oneline
git show HEAD --stat
```

## 最佳实践

**推荐**：
- ✅ 生成前分析所有暂存变更
- ✅ 使用祈使语气
- ✅ 标题控制在 50 字符内
- ✅ 复杂变更添加正文说明
- ✅ 关联相关 Issue
- ✅ 将相关变更放在一个 commit

**避免**：
- ❌ 没有暂存变更就提交
- ❌ 在一个 commit 混入不相关变更
- ❌ 使用过去时
- ❌ 标题结尾加句号
- ❌ 包含敏感信息
- ❌ 跳过 pre-commit hooks（除非明确要求）

## 边界情况

### 无暂存变更

```bash
git status
# 提示："没有暂存变更。是否暂存所有变更？"
```

### 空仓库（初始提交）

```bash
git rev-parse HEAD 2>/dev/null || git commit -m "chore: initial commit"
```

### 大型 Diff（>500行）

```bash
git diff --staged --stat
git diff --staged --unified=1
# 建议拆分为多个 commit
```

### 合并冲突

```bash
git status | grep "both modified"
git commit -m "merge: resolve conflicts in <files>"
```

## Hooks 集成

- **pre-commit**: 自动运行
- **commit-msg**: 自动运行
- 如果 hooks 失败：报告错误，建议修复
- 仅在明确要求时使用 `--no-verify`
