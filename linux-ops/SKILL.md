---
name: linux-ops
description: |
  【Linux运维】Linux 服务器运维实战指南，包含进程管理、系统监控、网络诊断、日志分析、用户权限、故障排查。

  触发时机：
  - 用户要求"Linux命令"、"服务器运维"
  - 服务器出问题需要排查
  - 需要监控系统状态

  提供完整命令和排查流程。
category: reference
user-invocable: false
---

# Linux Ops — Linux 运维实战指南

Linux 服务器运维从日常操作到故障排查的完整指南。


## Goal

Linux 服务器运维实战指南，包含进程管理、系统监控、网络诊断、日志分析、用户权限、故障排查

## Trigger

- 用户要求"Linux命令"、"服务器运维"
  - 服务器出问题需要排查
  - 需要监控系统状态

## 工作流程

1. **评估严重程度** -- 判断是服务完全宕机还是性能下降。if 服务无法访问 -> 跳到步骤 2a（服务宕机排查）；if 响应缓慢 -> 跳到步骤 2b（性能排查）。同时检查是否为批量影响（单个服务 / 多个服务 / 整个主机）。
2a. **服务宕机排查** -- `systemctl status <service>` 确认服务状态。`journalctl -u <service> -n 100` 查看最近日志。`lsof -i :<port>` 检查端口占用。if 配置错误 -> 测试配置（如 `nginx -t`）并修复；if 资源耗尽 -> 转步骤 2b；if 依赖服务异常 -> 检查上游服务连通性。
2b. **性能降级排查** -- `top` / `htop` 检查 CPU 占用。`free -h` 检查内存使用。`df -h` 检查磁盘空间。`iostat -x 1 5` 检查磁盘 IO。`ss -s` 检查网络连接状态。if CPU 高 -> 找到高占用进程并评估是否可重启/kill。if 内存不足 -> 检查是否有内存泄漏进程（`ps aux --sort=-%mem`）。if 磁盘满 -> 转步骤 3 清理。
3. **根因定位与修复** -- 根据步骤 2 的发现选择修复策略。if 配置问题 -> 编辑配置文件 + `systemctl daemon-reload` + 重启服务。if 资源问题 -> kill 异常进程 / 清理磁盘 / 调整 ulimit。if 网络问题 -> 检查防火墙规则 / DNS 解析 / 路由配置。if 权限问题 -> 检查 SELinux/AppArmor 日志 + 调整权限。
4. **验证修复** -- 重新运行诊断命令确认问题已解决。检查服务日志确认无新错误。确认受影响的用户/客户端已恢复正常。
5. **后续加固** -- 配置监控告警防止再次发生。if 磁盘满 -> 配置 logrotate 定时清理。if 服务频繁崩溃 -> 配置 systemd 自动重启（`Restart=always`）。记录故障处理过程供后续参考。

## 进程管理

### 查看进程

```bash
# 基础查看
ps aux                                        # 所有进程
ps aux | grep nginx                           # 过滤进程
ps -ef --forest                               # 进程树
pstree -p                                     # 进程树（带PID）

# 详细信息
ps -o pid,ppid,user,%cpu,%mem,cmd -p 12345    # 指定字段
top -p 12345                                  # 实时监控指定进程
htop                                          # 交互式进程管理

# 查找进程
pgrep -a nginx                                # 按名称查找
pidof nginx                                   # 获取PID
lsof -i :80                                   # 查看端口占用
fuser -n tcp 80                               # 端口占用进程
```

### 进程控制

```bash
# 信号管理
kill -15 PID                                  # 优雅终止 (SIGTERM)
kill -9 PID                                   # 强制终止 (SIGKILL)
kill -HUP PID                                 # 重新加载配置
killall nginx                                 # 按名称终止
pkill -f "python app.py"                      # 按模式终止

# 后台运行
nohup ./app.py &                              # 后台运行
disown                                        # 断开终端关联
screen -S mysession                           # 创建 screen 会话
tmux new -s mysession                         # 创建 tmux 会话

# 优先级
nice -n 10 ./cpu-intensive.sh                 # 降低优先级
renice -n -5 -p PID                           # 调整优先级
```

### 服务管理 (systemd)

```bash
# 服务操作
systemctl start/stop/restart/status nginx     # 管理服务
systemctl enable/disable nginx                # 开机自启
systemctl list-units --type=service           # 列出服务
systemctl list-unit-files --type=service      # 列出所有服务文件

# 日志
journalctl -u nginx -f                        # 实时日志
journalctl -u nginx --since "1 hour ago"      # 最近1小时
journalctl -u nginx --since "2026-01-01"      # 指定日期
journalctl -p err                             # 错误级别日志

# 自定义服务
cat > /etc/systemd/system/myapp.service << EOF
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/start.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable myapp
```

## 系统监控

### CPU 监控

```bash
# 实时监控
top -o %CPU                                   # 按 CPU 排序
htop                                          # 交互式监控
mpstat -P ALL 1                               # 多核 CPU 使用

# 历史数据
sar -u 1 10                                   # CPU 使用率
vmstat 1 10                                   # 综合统计

# 进程 CPU
pidstat -p PID 1                              # 指定进程
ps aux --sort=-%cpu | head -10                # CPU 前10
```

### 内存监控

```bash
# 内存使用
free -h                                       # 内存概览
free -m -s 5                                  # 每5秒刷新

# 详细信息
cat /proc/meminfo                             # 内存详情
vmstat -s                                     # 内存统计

# 进程内存
ps aux --sort=-%mem | head -10                # 内存前10
pmap -x PID                                   # 进程内存映射

# 内存泄漏检测
valgrind --leak-check=full ./myapp
```

### 磁盘监控

```bash
# 磁盘空间
df -h                                         # 文件系统使用
df -i                                         # inode 使用
du -sh /var/log                               # 目录大小
du -ah / | sort -rh | head -20               # 大文件排行

# 磁盘 I/O
iostat -x 1 10                                # I/O 统计
iotop -o                                      # I/O 进程

# 查找大文件
find / -type f -size +100M 2>/dev/null       # 大于100M的文件
find / -type f -mtime +30 -delete             # 删除30天前的文件
```

## 网络诊断

### 连接状态

```bash
# 网络接口
ip addr                                       # IP 地址
ip route                                      # 路由表
ip link                                       # 网络接口

# 连接状态
ss -tunlp                                     # 监听端口
ss -s                                         # 连接统计
netstat -tunlp                                # 监听端口（旧）
netstat -an | grep ESTABLISHED | wc -l        # 活跃连接数

# 端口检查
lsof -i :80                                   # 端口占用
lsof -i -P -n | grep LISTEN                   # 所有监听端口
```

### 网络测试

```bash
# 连通性
ping -c 5 host                                # ICMP 测试
traceroute host                               # 路由追踪
mtr host                                      # 实时路由追踪

# DNS
nslookup domain                               # DNS 查询
dig domain                                    # 详细 DNS
dig +short domain                             # 简短输出

# HTTP 测试
curl -v https://example.com                   # HTTP 请求
curl -o /dev/null -s -w "%{time_total}\n" URL # 响应时间
wget --spider URL                             # 检测 URL

# 抓包
tcpdump -i eth0 port 80                       # 抓取80端口
tcpdump -i eth0 -w capture.pcap               # 保存到文件
```

## 日志分析

### 系统日志

```bash
# 日志位置
/var/log/syslog                               # 系统日志
/var/log/auth.log                             # 认证日志
/var/log/kern.log                             # 内核日志
/var/log/dmesg                                # 启动日志

# 日志查看
tail -f /var/log/syslog                       # 实时查看
tail -100 /var/log/syslog                     # 最后100行
grep "error" /var/log/syslog                  # 搜索错误
journalctl -xe                                # 查看最新日志

# 日志轮转
cat /etc/logrotate.conf                       # 轮转配置
logrotate -f /etc/logrotate.conf              # 强制轮转
```

### 应用日志分析

```bash
# Nginx 日志
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10  # IP 统计
awk '{print $9}' access.log | sort | uniq -c | sort -rn             # 状态码统计
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -10  # URL 统计

# 实时统计
tail -f access.log | awk '{print $1}' | uniq -c

# 错误日志
grep -i "error" /var/log/nginx/error.log
tail -f /var/log/nginx/error.log
```

## 用户权限

### 用户管理

```bash
# 用户操作
useradd -m -s /bin/bash username              # 创建用户
passwd username                               # 设置密码
userdel -r username                           # 删除用户
usermod -aG sudo username                     # 添加到 sudo 组

# 组管理
groupadd mygroup                              # 创建组
groupdel mygroup                              # 删除组
usermod -aG mygroup username                  # 添加用户到组
groups username                               # 查看用户组

# 查看用户
whoami                                        # 当前用户
who                                           # 登录用户
w                                             # 登录用户详情
last                                          # 登录历史
```

### 权限管理

```bash
# 文件权限
chmod 755 file                                # 设置权限
chmod u+x file                                # 添加执行权限
chmod -R 755 /path                            # 递归设置
chown user:group file                         # 修改所有者
chown -R user:group /path                     # 递归修改

# 特殊权限
chmod +s file                                 # SUID
chmod +g file                                 # SGID
chmod +t dir                                  # Sticky bit

# ACL 权限
setfacl -m u:user:rw file                     # 用户 ACL
setfacl -m g:group:rx file                    # 组 ACL
getfacl file                                  # 查看 ACL
```

## 定时任务管理

### cron 定时任务

```bash
# 编辑定时任务
crontab -e                                # 编辑当前用户的 cron

# 查看定时任务
crontab -l                                # 列出当前用户的 cron
crontab -l -u username                    # 列出指定用户的 cron

# cron 表达式格式
# 分 时 日 月 周 命令
# 0 2 * * * /path/to/script.sh           # 每天凌晨 2 点
# 0 */4 * * * /path/to/script.sh         # 每 4 小时
# 0 9 * * 1-5 /path/to/script.sh         # 工作日 9 点
# 0 0 1 * * /path/to/script.sh           # 每月 1 号

# 常用示例
0 * * * * /path/to/hourly.sh             # 每小时
30 2 * * * /path/to/daily.sh             # 每天 2:30
0 0 * * 0 /path/to/weekly.sh             # 每周日
0 0 1 * * /path/to/monthly.sh            # 每月
```

### at 一次性任务

```bash
# 创建任务
echo "/path/to/script.sh" | at now + 1 hour    # 1 小时后执行
echo "/path/to/script.sh" | at 23:00           # 今晚 23 点
at now + 30 minutes                            # 交互式输入

# 查看任务
atq                                           # 列出队列中的任务
at -c 123                                     # 查看任务详情

# 删除任务
atrm 123                                      # 删除指定任务
```

### systemd timer（推荐）

```ini
# /etc/systemd/system/mytask.timer
[Unit]
Description=Run mytask daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
Unit=mytask.service

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/mytask.service
[Unit]
Description=My scheduled task

[Service]
Type=oneshot
ExecStart=/path/to/script.sh
```

```bash
systemctl enable --now mytask.timer          # 启用定时器
systemctl list-timers                       # 查看所有定时器
```

## 防火墙管理

### iptables

```bash
# 查看规则
iptables -L -n -v                           # 列出所有规则
iptables -L -n -v --line-numbers            # 带行号

# 基本规则
iptables -A INPUT -p tcp --dport 80 -j ACCEPT    # 允许 80 端口
iptables -A INPUT -p tcp --dport 443 -j ACCEPT   # 允许 443 端口
iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT    # 允许特定网段
iptables -A INPUT -j DROP                         # 拒绝其他

# 删除规则
iptables -D INPUT 3                          # 删除第 3 条规则
iptables -F                                  # 清空所有规则

# 保存规则
iptables-save > /etc/iptables/rules.v4       # 保存
iptables-restore < /etc/iptables/rules.v4    # 恢复
```

### firewalld（CentOS/RHEL）

```bash
# 查看状态
firewall-cmd --state
firewall-cmd --list-all

# 管理端口
firewall-cmd --add-port=80/tcp --permanent   # 添加端口
firewall-cmd --remove-port=80/tcp --permanent # 移除端口
firewall-cmd --reload                         # 重载配置

# 管理服务
firewall-cmd --add-service=http --permanent   # 允许 HTTP 服务
firewall-cmd --remove-service=http --permanent

# 管理区域
firewall-cmd --get-active-zones              # 查看活跃区域
firewall-cmd --zone=public --add-interface=eth0  # 添加接口到区域
```

### ufw（Ubuntu/Debian）

```bash
# 基本操作
ufw status verbose                         # 查看状态
ufw enable                                 # 启用防火墙
ufw disable                                # 禁用防火墙

# 规则管理
ufw allow 22/tcp                           # 允许 SSH
ufw allow 80,443/tcp                       # 允许 HTTP/HTTPS
ufw allow from 192.168.1.0/24              # 允许特定网段
ufw deny 3306                              # 拒绝 MySQL

# 删除规则
ufw delete allow 80/tcp                    # 删除规则
ufw status numbered                        # 带编号查看
ufw delete 3                               # 按编号删除
```

## 故障排查流程

### 系统响应慢

```bash
# 1. 检查 CPU
top -o %CPU
ps aux --sort=-%cpu | head -10

# 2. 检查内存
free -h
ps aux --sort=-%mem | head -10

# 3. 检查磁盘
df -h
iostat -x 1 5

# 4. 检查网络
ss -s
netstat -an | wc -l
```

### 服务无法启动

```bash
# 1. 查看服务状态
systemctl status myservice

# 2. 查看日志
journalctl -u myservice -n 100

# 3. 检查配置
myservice -t  # 测试配置

# 4. 检查依赖
ldd /usr/bin/myservice

# 5. 检查端口
lsof -i :PORT
```

### 磁盘空间不足

```bash
# 1. 查看使用情况
df -h

# 2. 查找大目录
du -sh /* | sort -rh | head -10
du -sh /var/* | sort -rh | head -10

# 3. 查找大文件
find / -type f -size +100M 2>/dev/null

# 4. 清理日志
journalctl --vacuum-size=100M
find /var/log -name "*.gz" -delete

# 5. 清理包管理器
apt autoremove
yum clean all
```

## 快速使用

```
# 排查 CPU 占用高
服务器 CPU 占用100%，帮我排查

# 查找大文件
磁盘空间不足，帮我找出大文件

# 分析日志
分析 Nginx 访问日志，找出最频繁的 IP

# 配置服务
帮我配置一个 systemd 服务
```

## Edge Cases / 常见陷阱

| 场景 | 现象 | 诊断方法 | 解决方案 |
|------|------|----------|----------|
| 非 root 执行命令被拒绝 | `Permission denied` 或 `Operation not permitted` | 检查当前用户和文件权限 `ls -la` | 使用 `sudo` 执行需要特权的命令；检查文件属主 `chown`；检查 sudoers 配置 |
| systemctl 命令不存在 | `systemctl: command not found` | 检查系统是否使用 systemd `cat /proc/1/comm` | 老系统使用 `service` 命令 + `/etc/init.d/` 脚本；最小化容器可能需要安装 systemd |
| journalctl 无日志输出 | `--since` 过滤后无结果 | 检查日志存储配置 `journalctl --disk-usage` | 调整 journald 配置 `/etc/systemd/journald.conf` 中的 `SystemMaxUse`；使用文件日志路径代替 |
| 磁盘 100% 满无法写日志 | 新日志无法写入，排查陷入死循环 | 使用只读命令 `df -h`、`du` 检查 | `journalctl --vacuum-size=50M` 释放日志空间；`find /tmp -type f -mtime +1 -delete` 清理临时文件 |
| SSH 密钥认证失败 | 用户创建后 SSH 密钥认证不工作 | 检查 `~/.ssh` 目录权限（应为 700）和 `authorized_keys` 权限（应为 600） | `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`；检查 sshd_config 中的 `PubkeyAuthentication yes` |
| SELinux/AppArmor 阻止操作 | 服务运行正常但无法绑定端口或访问文件 | `ausearch -m avc` (SELinux) 或 `aa-status` (AppArmor) | 使用 `setenforce 0` 临时禁用（调试用）；生成正确的 SELinux 策略 `audit2allow` |
| systemd 服务启动后立即退出 | `systemctl status` 显示 `inactive (dead)` | `journalctl -u <service>` 查看退出原因 | 检查 ExecStart 路径是否正确；检查 User 权限；添加 `Type=simple` 或 `Type=forking` |
| 文件描述符耗尽 | `Too many open files` 错误 | `cat /proc/sys/fs/file-nr` 检查当前使用量 | 调整 `/etc/security/limits.conf` 或 systemd 的 `LimitNOFILE=` |
| SSH 连接超时 | 建立连接时卡住 | `ssh -vvv host` 查看连接过程 | 检查防火墙规则；检查 DNS 反向解析；调整 `/etc/ssh/sshd_config` 中的 `UseDNS no` |
| cron 定时任务未执行 | 预期的任务没有运行 | 检查 `/var/log/syslog` 或 `journalctl -u cron` | 确认 crontab 格式正确；确认脚本有执行权限；确认脚本中的环境变量（cron 环境极简） |

## 不适用场景

| 场景 | 原因 | 建议使用 |
|------|------|----------|
| Docker 容器内部运维 | 本技能针对宿主机，非容器内操作 | 使用 docker-essentials 技能 |
| Kubernetes 集群管理 | 本技能覆盖单机，非集群编排 | 使用 k8s-cluster 技能 |
| macOS 系统运维 | macOS 使用 launchctl、brew services 等不同命令体系 | 使用 macOS 专用运维工具 |
| Windows Server 运维 | Windows 使用 PowerShell、WMI 等不同体系 | 使用 PowerShell 技能 |
| 云基础设施管理（AWS/GCP/Azure） | 本技能不覆盖云平台 CLI 和 API | 使用对应云平台的 CLI 工具（aws-cli、gcloud、az） |
| 配置管理自动化（Ansible/Terraform） | 本技能面向手动操作，非自动化编排 | 使用 Ansible/Terraform 技能 |
| 安全扫描 / 漏洞管理 | 本技能不覆盖系统安全审计 | 使用 security-scanning 技能 |

## 参考资料

- 进程管理: [references/process.md](references/process.md)
- 系统资源: [references/system.md](references/system.md)
- 网络诊断: [references/network.md](references/network.md)
- 日志分析: [references/logs.md](references/logs.md)
- 用户权限: [references/users.md](references/users.md)
