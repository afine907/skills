---
name: symlink-maker
description: |
  【符号链接】创建文件或目录的符号链接，跨平台支持 Windows/macOS/Linux。
  触发时机：用户说"创建软链接"、"ln -s"、"mklink"。
  自动检测操作系统，选择合适的链接方式。
category: productivity
---

# Symlink Maker — 符号链接创建工具

跨平台创建文件或目录的符号链接，自动处理 Windows/macOS/Linux 差异。

## Goal

帮助用户快速创建符号链接，无需记忆不同操作系统的命令差异。

## Trigger

当用户需要：
- 创建文件或目录的符号链接
- 在不同位置共享配置文件
- 链接 node_modules 或其他依赖目录

## Workflow

```
检测操作系统 → 验证源路径 → 选择链接方式 → 创建链接 → 验证结果
```

## 跨平台差异

| 操作系统 | 文件链接 | 目录链接 | 需要管理员 |
|----------|----------|----------|------------|
| Windows | `mklink` | `mklink /J` (junction) | 文件链接需要 |
| macOS/Linux | `ln -s` | `ln -s` | 不需要 |

## 使用方式

### 命令行使用

```bash
# 使用脚本创建
python <skill-dir>/scripts/create_link.py "<source>" "<link_path>"

# 示例：文件链接
python <skill-dir>/scripts/create_link.py "D:/project/config.json" "C:/Users/me/Desktop/config.json"

# 示例：目录链接
python <skill-dir>/scripts/create_link.py "D:/shared/assets" "D:/my-project/assets"
```

### 手动创建

```bash
# Windows - 文件链接（需要管理员）
mklink "C:\link\to\file.txt" "C:\source\file.txt"

# Windows - 目录链接（junction，不需要管理员）
mklink /J "C:\link\to\dir" "C:\source\dir"

# macOS/Linux
ln -s /source/file /link/to/file
ln -s /source/dir /link/to/dir
```

## 常见场景

### 共享配置文件

```bash
# 将 .gitconfig 链接到多台机器共享的位置
python create_link.py "D:/shared/.gitconfig" "C:/Users/me/.gitconfig"

# 链接 VS Code 设置
python create_link.py "D:/shared/vscode/settings.json" "C:/Users/me/AppData/Roaming/Code/User/settings.json"
```

### 项目依赖链接

```bash
# 链接 node_modules 到另一个项目
python create_link.py "D:/shared/node_modules" "D:/my-project/node_modules"

# 链接 Python 虚拟环境
python create_link.py "D:/shared/.venv" "D:/my-project/.venv"
```

## 注意事项

### 链接验证

创建链接后，务必验证：
- 链接是否正确创建
- 源路径是否可访问
- 链接是否指向正确位置

```bash
# Windows
dir link_path
fsutil reparsepoint query link_path

# macOS/Linux
ls -la link_path
readlink link_path
```

### 常见问题

1. **权限不足** - Windows 文件链接需要管理员权限，使用 junction 替代
2. **源路径不存在** - 链接会创建但指向空位置（broken symlink）
3. **相对路径** - 建议使用绝对路径避免路径解析问题
4. **备份重要** - 创建链接前备份目标位置的现有文件

## 参考资料

- Windows mklink: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mklink
- Linux ln: https://man7.org/linux/man-pages/man1/ln.1.html
