# Git Flow 详解

## 分支类型

```
main (master) ─────●──────────●──────────●──────────▶
                   │          ↑          ↑
                   │          │          │
develop ─────●─────●────●─────●────●─────●──────────▶
              ↑          ↑          ↑
              │          │          │
feature/*     │          │          │
              └──────────┘          │
                                    │
release/*                    ┌──────┘
                             ▼
                       ●─────●─────●
                       │           │
hotfix/*               └───────────┘
```

### main 分支
- 始终保持可发布状态
- 每个 commit 对应一个版本标签
- 只接受 release 和 hotfix 分支的合并

### develop 分支
- 开发主干，包含最新开发进度
- 从 main 分支创建
- 接受 feature 分支的合并

### feature/* 分支
- 从 develop 分支创建
- 开发完成后合并回 develop
- 命名：`feature/{ticket}-{desc}`

### release/* 分支
- 从 develop 分支创建
- 用于发布前的准备（版本号、文档、最后修复）
- 完成后同时合并到 main 和 develop
- 命名：`release/v{版本号}`

### hotfix/* 分支
- 从 main 分支创建
- 用于紧急修复生产问题
- 完成后同时合并到 main 和 develop
- 命名：`hotfix/{ticket}-{desc}`

## 完整流程示例

```bash
# 1. 初始化（只需一次）
git checkout -b develop main
git push -u origin develop

# 2. 开始新功能
git checkout develop
git pull origin develop
git checkout -b feature/PROJ-123-user-login develop

# 3. 开发中...
git add .
git commit -m "feat: implement login form"
git commit -m "feat: add login API integration"
git push origin feature/PROJ-123-user-login

# 4. 完成功能，合并到 develop
git checkout develop
git pull origin develop
git merge --no-ff feature/PROJ-123-user-login
git push origin develop
git branch -d feature/PROJ-123-user-login
git push origin --delete feature/PROJ-123-user-login

# 5. 准备发布
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 6. 发布准备（版本号、changelog等）
# ... 修改版本号 ...
git commit -m "chore: bump version to 1.2.0"
git push origin release/v1.2.0

# 7. 合并到 main 并打标签
git checkout main
git pull origin main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

# 8. 合并回 develop
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# 9. 清理
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0

# 10. 紧急修复
git checkout main
git pull origin main
git checkout -b hotfix/PROJ-789-security-fix

# ... 修复代码 ...
git commit -m "fix: patch security vulnerability"

# 11. 合并 hotfix
git checkout main
git merge --no-ff hotfix/PROJ-789-security-fix
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git push origin main --tags

git checkout develop
git merge --no-ff hotfix/PROJ-789-security-fix
git push origin develop

git branch -d hotfix/PROJ-789-security-fix
git push origin --delete hotfix/PROJ-789-security-fix
```

## --no-ff 的作用

`--no-ff`（no fast-forward）强制创建合并 commit，保留分支历史：

```
# 没有 --no-ff（快进合并）
A ── B ── C ── D ── E  (main)

# 有 --no-ff（合并 commit）
A ── B ── M ────────── E  (main)
         / \
    C ──D   (feature)
```

好处：
- 清晰看到功能分支的起止点
- 可以一键 revert 整个功能
- 保留分支上下文
