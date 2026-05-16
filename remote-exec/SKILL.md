---
name: remote-exec
description: |
  【远程执行】通过 SSH 在远程服务器上执行 bash 命令。

  触发时机：
  - 用户提供远程服务器 IP/域名、用户名、密码
  - 用户要求在远程机器上执行操作（查日志、部署、监控、排查问题等）

  使用流程：
  1. 获取或要求用户提供连接信息：host, port(默认22), user, password
  2. 用 Python paramiko 连接远程服务器
  3. 执行命令并返回结果
  4. 断开连接

  安全规则：
  - 密码仅存在 Python 进程内存中，用完即弃
  - 破坏性操作（rm -rf、重启、关防火墙等）必须先问用户
  - 首次连接自动信任主机（AutoAddPolicy）
  - 命令建议加超时，防止卡死
category: operations
---

# Remote Exec — 远程服务器命令执行 Agent

## 前置检查

在执行前，确保 paramiko 已安装：

```bash
python3 -c "import paramiko" 2>/dev/null || \
  python3 -m pip install paramiko --break-system-packages
```

## 连接模板

用 `exec` 工具执行内联 Python 脚本。**不要将密码写到文件里**。

### 基础执行

```python
import paramiko, sys, json

host, port, user, password, command = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, user, password, timeout=30)

stdin, stdout, stderr = client.exec_command(command, timeout=60)
exit_code = stdout.channel.recv_exit_status()

out = stdout.read().decode()
err = stderr.read().decode()
client.close()

result = {"exit_code": exit_code, "stdout": out, "stderr": err}
print(json.dumps(result))
```

### 需要 PTY 的场景（sudo、交互式命令）

```python
import paramiko, sys, json

host, port, user, password, command = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, user, password, timeout=30)

channel = client.get_transport().open_session()
channel.get_pty()
channel.exec_command(command)

# 如果是 sudo，需要发送密码
if 'sudo' in command:
    channel.send(password + '\n')

channel.settimeout(60)
exit_code = channel.recv_exit_status()
out = channel.recv(65536).decode()
client.close()

result = {"exit_code": exit_code, "stdout": out}
print(json.dumps(result))
```

### 批量命令

```python
import paramiko, sys, json

host, port, user, password = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
commands = sys.argv[5:]  # 多个命令依次传入

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, user, password, timeout=30)

results = []
for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    exit_code = stdout.channel.recv_exit_status()
    results.append({
        "command": cmd,
        "exit_code": exit_code,
        "stdout": stdout.read().decode(),
        "stderr": stderr.read().decode()
    })

client.close()
print(json.dumps(results))
```

### 通过 SSH 传文件（小文件用 base64）

```python
import paramiko, sys, base64, json

host, port, user, password = sys.argv[1:5]
# remote_path = sys.argv[5], base64_content = sys.argv[6]

transport = paramiko.Transport((host, port))
transport.connect(username=user, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

# 上传
# content = base64.b64decode(sys.argv[6])
# with sftp.open(remote_path, 'w') as f:
#     f.write(content)

# 下载
with sftp.open(sys.argv[5], 'r') as f:
    content = base64.b64encode(f.read()).decode()

sftp.close()
transport.close()
print(json.dumps({"file": sys.argv[5], "content": content}))
```

## 安全规则

### 🚫 必须确认的操作（ask before run）

- `rm -rf`、`dd`、`mkfs` 等不可逆操作
- 重启服务/系统（`reboot`, `shutdown`, `systemctl restart critical-service`）
- 防火墙变更（`iptables`, `ufw`, `firewall-cmd`）
- 修改关键配置（`/etc/` 下的系统配置）
- 停止/卸载关键服务

### ✅ 可以直接执行的操作

- 查看日志（`tail`, `journalctl`, `cat log`）
- 系统状态（`df -h`, `free -m`, `top -bn1`, `ps aux`）
- 文件列表（`ls`, `find`, `du -sh`）
- 网络诊断（`ping`, `curl`, `ss -tlnp`, `netstat`）
- 只读查询（`cat config`, `grep`, `awk`）
- 进程管理（`kill` 需要确认，`ps` 不需要）

### 连接安全

- 每次连接用 `timeout` 参数（默认 30s 连接超时，60s 命令超时）
- 连接用完即关（`client.close()`）
- 密码用 Python 变量传，不在命令行暴露
- 限制 `exec` 工具的 `timeout` 参数防止无限等待

## 执行方式

使用 `exec` 工具运行 Python 脚本：

```bash
python3 -c '
import paramiko, sys, json
...内联脚本...
' <host> <port> <user> <password> <command>
```

> 密码是第 4 个参数，会被 `exec` 传到 Python 进程的 `sys.argv[4]`，不会出现在 `ps` 进程列表中。
>
> ⚠️ `exec` 工具在 GitHub Actions CI 或其他公开日志中可能会记录完整命令，包括密码参数。建议在自托管的 OpenClaw 或本地环境使用。

## 常见场景

### 查日志

```
远程：tail -n 100 /var/log/nginx/error.log
远程：journalctl -u nginx --no-pager -n 50
```

### 磁盘 / 内存

```
远程：df -h
远程：free -h
远程：du -sh /var/log/*
```

### 部署检查

```
远程：systemctl status app
远程：docker ps | grep my-app
远程：curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health
```

### 错误排查

```
远程：ping -c 3 google.com
远程：ss -tlnp | grep :80
远程：cat /var/log/syslog | grep ERROR | tail -20
```
