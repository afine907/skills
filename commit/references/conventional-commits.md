# Conventional Commits 规范参考

本文档是 Conventional Commits 规范的速查手册，供 `/commit` 技能生成提交信息时参考。

## 规范格式

```
<type>[optional scope][optional !]: <subject>

[optional body]

[optional footer(s)]
```

## Type 类型

| Type | 说明 | 使用场景 |
|------|------|----------|
| `feat` | 新功能 | 用户可感知的新特性 |
| `fix` | 修复 | Bug 修复 |
| `docs` | 文档 | 仅文档变更 |
| `style` | 格式 | 不影响代码逻辑的格式调整（空格、缩进、分号等） |
| `refactor` | 重构 | 既不修复 bug 也不添加功能的代码变更 |
| `perf` | 性能 | 提升性能的代码变更 |
| `test` | 测试 | 添加或修正测试 |
| `build` | 构建 | 构建系统或外部依赖变更 |
| `ci` | CI/CD | CI 配置文件和脚本变更 |
| `chore` | 杂项 | 不修改 src 或 test 的其他变更 |
| `revert` | 回滚 | 回滚之前的提交 |

## Scope 范围

范围是可选的，用括号包裹，标识变更影响的模块：

```
feat(auth): add OAuth2 login
fix(payment): prevent double charge
refactor(api)!: change response format
```

常见范围命名规则：
- 使用模块名：`auth`, `user`, `order`, `payment`
- 使用层级名：`controller`, `service`, `repository`
- 使用技术层：`api`, `db`, `cache`, `config`
- 多个范围用逗号分隔：`feat(auth, user): ...`

## Breaking Changes

两种标记方式：

```
# 方式一：感叹号
feat(api)!: change response format

BREAKING CHANGE: API response now wraps data in { data: ... } object.
```

```
# 方式二：仅 footer
feat(api): change response format

BREAKING CHANGE: API response now wraps data in { data: ... } object.
```

Breaking Change 必须出现在 type 后的 `!` 或 footer 中，会导致 MINOR 版本号升级（0.x 时）或 MAJOR 版本号升级（1.x 时）。

## Subject 编写规则

```bash
# 正确：祈使语气，首字母小写，无句号
feat(auth): add JWT token refresh

# 错误示例
feat(auth): Added JWT token refresh.   # 过去式 + 有句号
feat(auth): Adds JWT token refresh.    # 第三人称
feat(auth): 添加 JWT 刷新机制          # 中文（建议统一用英文）
```

规则总结：
1. 使用祈使语气（"add" 而非 "added"）
2. 首字母小写
3. 末尾不加句号
4. 不超过 50 个字符

## Body 编写规则

```bash
fix(auth): handle expired refresh token

The refresh token was not being validated for expiration,
causing stale tokens to be accepted indefinitely.

Added explicit expiry check before token rotation.
```

规则总结：
1. 与 subject 之间空一行
2. 使用祈使语气说明"为什么"和"怎么做"
3. 每行不超过 72 个字符
4. 可以使用多段落

## Footer 编写规则

```bash
# 关联 Issue
fix(auth): prevent session fixation

Fixes #123
Closes #456

# 多个 Issue
fix(auth): prevent session fixation

Fixes #123, Fixes #456

# Co-author
feat(api): add rate limiting

Co-Authored-By: Name <email@example.com>

# 破坏性变更
refactor(db)!: migrate to PostgreSQL

BREAKING CHANGE: MySQL is no longer supported. Run migration script.
```

## 完整示例

### 简单功能
```
feat(user): add avatar upload endpoint
```

### 带详细说明的修复
```
fix(payment): prevent duplicate callback processing

Payment gateway was sending duplicate webhook callbacks during
network retries. Added idempotency check using (order_id, callback_id)
as unique constraint.

Fixes #234
```

### 破坏性变更
```
refactor(api)!: standardize error response format

BREAKING CHANGE: Error responses now follow RFC 7807 format.
Clients parsing error responses must update accordingly.

Before: { "error": "message" }
After:  { "type": "...", "title": "...", "status": 400, "detail": "..." }
```

### 多文件重构
```
refactor(auth): extract token logic to dedicated service

- Move token generation to TokenService
- Move token validation to TokenService
- Add unit tests for TokenService

No behavior change expected.
```

## 常见错误对照

| 错误写法 | 正确写法 | 原因 |
|----------|----------|------|
| `feat: Add feature` | `feat: add feature` | 首字母小写 |
| `fix: bug fixed.` | `fix: resolve race condition` | 祈使语气 + 无句号 + 具体描述 |
| `update user profile` | `feat(user): update profile` | 缺少 type 和 scope |
| `feat(auth): 新增登录` | `feat(auth): add login` | 统一用英文 |
| `feat(auth): fix login bug` | `fix(auth): resolve login timeout` | type 与内容不匹配 |

## 工具链集成

```bash
# commitlint - 校验提交信息格式
npx commitlint --edit .git/COMMIT_EDITMSG

# commitizen - 交互式提交
npx cz

# standard-version - 自动生成 CHANGELOG
npx standard-version
```

## 语义化版本映射

| 提交类型 | 版本变更 | 示例 |
|----------|----------|------|
| `fix` | PATCH (0.0.x) | `fix(auth): ...` -> 1.0.1 |
| `feat` | MINOR (0.x.0) | `feat(auth): ...` -> 1.1.0 |
| `BREAKING CHANGE` | MAJOR (x.0.0) | `feat(auth)!: ...` -> 2.0.0 |
| `chore`, `docs`, `style` 等 | 不触发版本 | 无版本变更 |
