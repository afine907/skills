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
---

# Linux Ops — Linux 运维实战指南

Linux 服务器运维从日常操作到故障排查的完整指南。

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

## 参考资料

- 进程管理: [references/process.md](references/process.md)
- 系统资源: [references/system.md](references/system.md)
- 网络诊断: [references/network.md](references/network.md)
- 日志分析: [references/logs.md](references/logs.md)
- 用户权限: [references/users.md](references/users.md)
