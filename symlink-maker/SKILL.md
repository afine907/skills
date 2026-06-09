---
name: symlink-maker
description: Cross-platform symlink creation for files and directories (Windows/macOS/Linux). Handles permission fallbacks, cross-drive paths, and idempotent linking.
category: productivity
---

# Symlink Maker — 跨平台符号链接创建 Agent

## Goal

跨平台创建文件/目录的符号链接，自动处理平台差异（Windows junction fallback、跨驱动器绝对路径、权限问题），支持幂等操作和安全删除。

## Trigger

用户提到以下任一关键词时触发：
- 创建符号链接 / create symlink / soft link / 软链接
- 链接目录 / link directory / symlink folder
- 文件夹快捷方式 / directory junction
- 多个项目共享同一配置目录
- 跨项目复用 rules / shared config via symlink

## 工作流程

```
检测平台 → 选择链接类型 → 处理路径 → 执行链接 → 验证结果
```

### Step 1: 检测平台与权限

| 平台 | 目录链接 | 文件链接 | 权限要求 |
|------|---------|---------|---------|
| Windows (开发者模式) | Symlink (相对路径) | Symlink (相对路径) | 需要开发者模式 |
| Windows (无开发者模式) | Junction (绝对路径) | Symlink (降级) | 无特殊权限 |
| macOS / Linux | Symlink (相对路径) | Symlink (相对路径) | 无特殊权限 |

判断逻辑：
1. 检测 `platform.system()`
2. Windows 下尝试 symlink，若 `PermissionError` 自动降级为 Junction
3. 跨驱动器（如 `C:` → `D:`）使用绝对路径

### Step 2: 选择链接类型

| 场景 | 推荐类型 | 原因 |
|------|---------|------|
| 目录 → 目录 | Junction (Windows) / Symlink (Unix) | 目录链接最常用 |
| 文件 → 文件 | Symlink | Junction 仅支持目录 |
| 跨驱动器 | Symlink (绝对路径) | Junction 必须绝对路径 |
| 同驱动器内 | Symlink (相对路径) | 可随项目移动 |

### Step 3: 处理路径

- **相对路径优先**：使用 `os.path.relpath()` 计算链接目标，确保项目移动后链接仍有效
- **跨驱动器降级**：Windows 下 `C:\project` → `D:\shared` 时自动使用绝对路径
- **父目录自动创建**：链接路径的父目录不存在时自动 `makedirs`

### Step 4: 执行链接

```bash
# 创建链接
python <skill-dir>/scripts/create_link.py <source> <link_path>

# 删除链接
python <skill-dir>/scripts/create_link.py --remove <link_path>
```

脚本特性：
- **幂等**：重复执行不会覆盖已正确的链接
- **自动清理**：目标链接已存在但指向错误时，自动删除旧链接再创建
- **安全删除**：区分 symlink（`os.remove`）和 junction（`os.rmdir`）

### Step 5: 验证结果

执行后检查：
1. 链接路径是否存在（`os.path.exists(link_path)`）
2. 链接指向是否正确（`os.readlink(link_path)` 匹配预期）
3. 链接类型是否符合预期（symlink vs junction）

## 输出模板

```
[created] .opencode/rules -> ../.claude/rules (symlink)
[reused]  .opencode/rules (already correct)
[removed] .opencode/rules (was -> ../.claude/rules)
[skip]    .opencode/rules is not a link
```

**端到端交互示例：**

用户输入：`为我的项目创建符号链接`

Claude 的完整交互流程：
1. 检测平台 → Windows/macOS/Linux
2. 询问需求 → 源路径和目标路径
3. 推荐链接类型 → 根据多维度决策表
4. 执行创建 → 调用脚本
5. 验证结果 → 输出操作报告

## 链接类型决策表

| 源类型 | 目标类型 | 平台 | 同驱动器 | 推荐链接类型 | 路径策略 |
|--------|---------|------|---------|-------------|---------|
| 目录 | 目录 | Windows | 是 | Junction | 相对路径 |
| 目录 | 目录 | Windows | 否 | Symlink | 绝对路径 |
| 目录 | 目录 | macOS/Linux | - | Symlink | 相对路径 |
| 文件 | 文件 | 任意 | - | Symlink | 相对路径 |
| 目录 | 目录 | Windows (无权限) | - | Junction | 绝对路径 |

## 使用示例

```bash
# 示例 1: 共享 Claude 和 OpenCode 的 rules 目录
python <skill-dir>/scripts/create_link.py ".claude/rules" ".opencode/rules"
# 输出: [created] .opencode/rules -> ../.claude/rules (symlink)

# 示例 2: 幂等执行（已存在则跳过）
python <skill-dir>/scripts/create_link.py ".claude/rules" ".opencode/rules"
# 输出: [reused] .opencode/rules (already correct)

# 示例 3: 删除链接
python <skill-dir>/scripts/create_link.py --remove ".opencode/rules"
# 输出: [removed] .opencode/rules (was -> ../.claude/rules)

# 示例 4: 跨驱动器（Windows）
python <skill-dir>/scripts/create_link.py "D:\shared\config" "C:\project\.config"
# 输出: [created] C:\project\.config -> D:\shared\config (symlink)
```

## Edge Cases

| 场景 | 处理方式 |
|------|---------|
| 源路径不存在 | 警告但仍创建链接（`WARNING: source does not exist`） |
| 目标链接已存在但指向错误 | 自动删除旧链接，创建新链接 |
| 目标链接已存在且正确 | 跳过，输出 `[reused]` |
| 目标路径不是链接（是普通文件/目录） | 报错，不覆盖 |
| 跨驱动器（Windows） | 自动使用绝对路径 |
| 权限不足（Windows 无开发者模式） | 自动降级为 Junction |
| 链接目标是目录 vs 文件 | 自动设置 `target_is_directory` 参数 |

## 注意事项

1. **Windows Junction 限制**：Junction 只能链接目录，不能链接文件
2. **相对路径优势**：优先使用相对路径，项目移动后链接仍有效
3. **幂等安全**：可重复执行，不会产生副作用
4. **不要链接敏感目录**：避免链接包含密钥、token 的目录到不安全位置
5. **删除时区分类型**：脚本自动处理 symlink vs junction 的删除差异

## 不适用

- 需要权限管理的硬链接 → 使用操作系统原生 `mklink /H`
- 需要网络共享链接 → 使用 SMB/NFS 挂载
- 需要原子性批量链接 → 使用脚本循环调用
