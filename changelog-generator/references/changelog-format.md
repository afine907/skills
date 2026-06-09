# Changelog Format Reference

## Keep a Changelog 规范

来源: https://keepachangelog.com/

### 核心原则

1. 人类可读，机器可解析
2. 版本号遵循 SemVer
3. 最新版本在最前面
4. 按 Changed/Added/Deprecated/Removed/Fixed/Security 分组

### 版本格式

```markdown
## [版本号] - YYYY-MM-DD
```

### 分组类型

| 分组 | 用途 | 说明 |
|------|------|------|
| Added | 新功能 | 本次新增的功能 |
| Changed | 已变更 | 已有功能的变更 |
| Deprecated | 即将移除 | 即将废弃的功能 |
| Removed | 已移除 | 本次移除的功能 |
| Fixed | 已修复 | Bug 修复 |
| Security | 安全 | 安全相关变更 |

### 完整示例

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-01-15

### Added
- User profile customization
- Dark mode support

### Changed
- Improved dashboard loading speed by 40%

### Fixed
- Fixed login timeout issue on mobile devices

### Security
- Updated authentication library to patch CVE-2026-1234

## [1.1.0] - 2026-01-01

### Added
- Export to CSV functionality

### Fixed
- Fixed date formatting in reports
```

## Conventional Commits 格式

来源: https://www.conventionalcommits.org/

### 格式

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type 与 Changelog 分组映射

| Commit Type | Changelog 分组 | Emoji |
|-------------|---------------|-------|
| feat | Added | 🚀 |
| fix | Fixed | 🐛 |
| perf | Changed (Performance) | ⚡ |
| refactor | Changed (Refactor) | ♻️ |
| docs | Changed (Documentation) | 📚 |
| style | Changed (Style) | 🎨 |
| test | Changed (Tests) | ✅ |
| build | Changed (Build) | 🏗️ |
| ci | Changed (CI/CD) | ⚙️ |
| chore | Changed (Chores) | 🧹 |
| revert | Removed | ⏪ |

### Breaking Changes

```
feat: add user authentication

BREAKING CHANGE: remove deprecated /api/v1/auth endpoint
```

在 Changelog 中映射为 `⚠️ Breaking Changes` 分组。

## 版本号语义

| 变更类型 | 版本增量 | 示例 |
|----------|----------|------|
| Breaking Change | MAJOR (X.0.0) | 1.2.3 → 2.0.0 |
| 新功能 (feat) | MINOR (0.X.0) | 1.2.3 → 1.3.0 |
| Bug 修复 (fix) | PATCH (0.0.X) | 1.2.3 → 1.2.4 |

## 平台差异

### GitHub Releases

- 在 GitHub 上创建 Release 时，可以选择将 Release Notes 同步到 CHANGELOG.md
- 使用 `gh release create` 命令自动生成 Release Notes

### GitLab

- 使用 `.gitlab/changelog.yml` 配置自动生成 Changelog
- 支持 `git log --format` 提取结构化信息
