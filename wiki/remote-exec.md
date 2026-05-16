# Remote-Exec — 远程 SSH 命令执行

| 元数据 | 值 |
|--------|-----|
| 技能名 | `remote-exec` |
| SKILL.md | `remote-exec/SKILL.md` |
| 参考文档 | `remote-exec/references/install.md`, `remote-exec/references/examples.md` |

## 简介

`remote-exec` 允许 AI Agent 通过 SSH 连接到远程服务器并执行 bash 命令。密码通过 Python 变量传递，不在命令行暴露。

## 前置条件

```bash
# Agent 会自动安装，也可手动装
python3 -m pip install paramiko --break-system-packages
```

## 触发方式

用户在对话中提供：
- 服务器 IP / 域名
- SSH 端口（默认 22）
- 用户名
- 密码
- 要执行的命令

## Agent 执行流程

1. 确认 paramiko 已安装（如未安装则自动装）
2. 用 `exec` 工具运行内联 Python 脚本
3. Python 脚本用 paramiko 建立 SSH 连接
4. 执行命令，收集 stdout/stderr/exit code
5. 断开连接，返回结果

## 安全约束

- 密码仅存在于 Python 进程内存中
- 一次性连接，用完即断
- `rm -rf`、重启、防火墙变更等破坏性操作必须先确认
- 命令默认 60s 超时

## 示例

```
用户：连 192.168.1.100，root/abc123，帮我查下磁盘空间
Agent：确认后执行 df -h，返回结果
```

详见 [examples.md](../remote-exec/references/examples.md)
