# 团队共享指南

本文档提供 harness engineering 配置文件的团队共享最佳实践。

## 版本控制策略

### 纳入版本控制的文件

以下配置文件应该纳入版本控制，确保团队成员使用一致的配置：

**必须纳入：**
- `CLAUDE.md` - 项目级 Claude 配置
- `.claude/rules/` - Claude 规则文件目录
- `.cursorrules` - Cursor IDE 配置
- `.editorconfig` - 编辑器配置
- `.eslintrc.json` 或 `eslint.config.js` - ESLint 配置
- `.prettierrc` - Prettier 配置
- `pyproject.toml` - Python 项目配置（含 Black, isort, mypy 配置）
- `.golangci.yml` - Go 代码检查配置
- `Makefile` - 构建脚本（如果使用）

**可选纳入：**
- `.husky/` - Git hooks 目录
- `.lintstagedrc` - lint-staged 配置
- `jest.config.js` 或 `vitest.config.ts` - 测试配置
- `.github/workflows/` - CI/CD 配置

**绝不纳入：**
- `.env.local` 或其他本地环境文件
- `node_modules/` - 依赖目录
- `__pycache__/` - Python 缓存
- `.idea/` 或 `.vscode/` - IDE 本地配置（除非是共享设置）
- 任何包含敏感信息的文件

### .gitignore 模板

```gitignore
# 环境文件
.env
.env.local
.env.*.local

# 依赖
node_modules/
vendor/
venv/

# 构建输出
dist/
build/
*.pyc
__pycache__/

# IDE 本地配置
.idea/
.vscode/settings.json
*.swp
*.swo

# 操作系统文件
.DS_Store
Thumbs.db

# 测试覆盖率
coverage/
htmlcov/
.coverage

# 日志
*.log
npm-debug.log*

# 临时文件
tmp/
temp/
```

## 配置分发方式

### 方式一：Git 仓库（推荐）

最简单直接的方式，所有配置文件随代码一起版本控制：

```bash
# 克隆项目时自动获取配置
git clone <repository-url>

# 配置文件已在项目中
ls -la CLAUDE.md .claude/ .cursorrules
```

**优点：**
- 配置与代码同步更新
- 版本历史可追溯
- 无需额外工具

**缺点：**
- 所有成员必须更新到最新代码

### 方式二：共享配置仓库

对于多个项目共享相同配置，可以创建独立的配置仓库：

```bash
# 创建配置仓库
git clone https://github.com/your-org/shared-configs.git

# 在项目中引用配置
# 方式 A：复制配置文件
cp shared-configs/CLAUDE.md .
cp -r shared-configs/.claude .

# 方式 B：使用符号链接（推荐）
ln -s shared-configs/CLAUDE.md CLAUDE.md
ln -s shared-configs/.claude .claude
```

**优点：**
- 多个项目共享配置
- 配置更新一次，所有项目受益
- 可以有不同项目的配置变体

**缺点：**
- 需要维护额外仓库
- 符号链接在 Windows 上有限制

### 方式三：包管理器安装

如果配置以技能形式存在，可以使用包管理器安装：

```bash
# 使用 skills CLI
npx skills add https://github.com/your-org/shared-skills

# 或使用 npm 包
npm install --save-dev @your-org/eslint-config
```

**优点：**
- 标准化的安装流程
- 版本管理
- 自动更新

**缺点：**
- 需要发布配置包
- 学习曲线

## 配置更新流程

### 更新策略

1. **渐进式更新**：先更新核心配置，再更新可选配置
2. **向后兼容**：新配置不应破坏现有功能
3. **文档先行**：更新配置前先更新文档
4. **测试验证**：更新后运行测试确认无问题

### 更新流程

```bash
# 1. 拉取最新配置
git pull origin main

# 2. 检查配置变更
git diff HEAD~1 CLAUDE.md .claude/

# 3. 安装新依赖（如果需要）
npm install  # 或 pip install -r requirements.txt

# 4. 验证配置
npm run lint
npm test

# 5. 提交本地调整（如果有）
git add .
git commit -m "chore: update local config"
```

### 配置冲突解决

当本地配置与远程配置冲突时：

```bash
# 查看冲突
git status

# 解决冲突（手动编辑文件）
vim CLAUDE.md

# 或使用合并工具
git mergetool

# 标记冲突已解决
git add CLAUDE.md

# 继续合并
git commit
```

## 团队协作规范

### 配置变更流程

1. **提出变更**：在 Issue 或 PR 中说明变更原因
2. **团队讨论**：重要变更需要团队讨论
3. **实施变更**：创建 PR，包含配置变更和文档更新
4. **代码审查**：至少一人审查配置变更
5. **合并部署**：合并后通知团队成员更新

### 变更文档

每次配置变更应该包含：

```markdown
## 变更说明

### 变更内容
- 更新了 ESLint 配置，添加了新的规则
- 修改了 Prettier 配置，统一缩进为 2 空格

### 变更原因
- 团队反馈代码风格不一致
- 为支持新的 TypeScript 特性

### 影响范围
- 所有 JavaScript/TypeScript 文件
- 需要运行 `npm install` 安装新依赖

### 迁移步骤
1. 拉取最新代码
2. 运行 `npm install`
3. 运行 `npm run lint --fix` 自动修复
4. 检查并手动修复剩余问题
```

### 团队培训

新成员加入时：

1. **配置说明**：在 README 中提供配置说明
2. **工具安装**：提供工具安装指南
3. **最佳实践**：分享编码和配置最佳实践
4. **常见问题**：维护常见问题解答

## 跨平台兼容

### Windows 兼容性

- 避免使用 Unix 特定路径（如 `/usr/local/bin`）
- 使用跨平台路径分隔符（`path.join()`）
- 测试 Windows 上的 Git hooks
- 提供 PowerShell 和 Bash 脚本

### macOS/Linux 兼容性

- 确保文件权限正确
- 测试符号链接功能
- 验证 shell 脚本兼容性

### IDE 兼容性

- **VS Code**：提供 `.vscode/extensions.json` 推荐扩展
- **Cursor**：确保 `.cursorrules` 格式正确
- **Windsurf**：兼容 Claude Code 规则格式
- **Vim/Emacs**：提供基本配置示例

## 配置效果评估

### 定期审查

每月或每季度审查配置效果：

1. **代码质量指标**：linting 错误数量、测试覆盖率
2. **团队反馈**：收集团队对配置的反馈
3. **工具更新**：检查依赖工具是否有重要更新
4. **最佳实践**：跟踪行业最佳实践变化

### 配置优化

根据审查结果优化配置：

- 移除未使用的规则
- 添加新发现的最佳实践
- 更新过时的配置
- 简化复杂配置

### 指标追踪

```bash
# 代码质量指标
npm run lint 2>&1 | grep -c "error"  # 错误数量
npm test -- --coverage  # 测试覆盖率

# 配置使用情况
git log --oneline -- CLAUDE.md .claude/  # 配置变更历史
git shortlog -sn -- .eslintrc.json  # 谁在修改配置
```

## 常见问题

### Q: 配置文件太大，影响 Git 性能？

A: 
- 使用 `.gitignore` 排除大文件
- 考虑使用 Git LFS 管理大配置文件
- 定期清理无用配置

### Q: 团队成员使用不同 IDE 怎么办？

A: 
- 提供通用配置（如 `.editorconfig`）
- 为每个 IDE 提供特定配置
- 使用配置仓库统一管理

### Q: 配置更新后成员不更新怎么办？

A: 
- 在 CI 中检查配置版本
- 定期发送更新通知
- 提供自动更新脚本

### Q: 如何处理实验性配置？

A: 
- 使用功能分支测试配置
- 提供配置开关
- 渐进式推广到全团队

## 参考资源

- Git 官方文档
- GitHub 最佳实践
- Conventional Commits
- EditorConfig 规范
