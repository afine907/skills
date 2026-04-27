---
name: linux-ops
description: Linux 运维常用命令速查，覆盖进程管理、日志分析、网络诊断、性能监控。
homepage: https://www.kernel.org/
metadata: {"clawdbot":{"emoji":"🐧","requires":{"bins":["bash"]}}}
---

# Linux Operations

Linux 运维命令速查手册。

## 进程管理

### 查看进程
```bash
# 查看所有进程
ps aux
ps -ef

# 查找进程
ps aux | grep nginx
pgrep nginx
pgrep -f "python app.py"

# 进程树
pstree
pstree -p  # 显示 PID

# 动态监控
top
htop  # 更友好，需安装
```

### 管理进程
```bash
# 后台运行
nohup python app.py &
nohup python app.py > output.log 2>&1 &

# 终止进程
kill PID
kill -9 PID  # 强制

# 批量终止
pkill nginx
killall nginx
kill $(pgrep -f "python app.py")
```

### 系统服务
```bash
# systemctl (systemd)
systemctl status nginx
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl enable nginx  # 开机启动

# 查看服务日志
journalctl -u nginx
journalctl -u nginx -f  # 实时
journalctl -u nginx --since "1 hour ago"
```

## 内存管理

### 查看内存
```bash
# 内存使用
free -h

# 详细内存信息
cat /proc/meminfo

# 进程内存排序
ps aux --sort=-%mem | head
top -o %MEM
```

## 磁盘管理

### 查看磁盘
```bash
# 磁盘使用
df -h

# 目录大小
du -sh /var/log
du -h --max-depth=1 /var

# 查找大文件
find / -type f -size +100M 2>/dev/null
du -ah / | sort -rh | head -20

# 磁盘分区
lsblk
fdisk -l
```

### 磁盘操作
```bash
# 挂载
mount /dev/sdb1 /mnt/data

# 卸载
umount /mnt/data

# 检查磁盘
fsck /dev/sdb1
```

## 网络诊断

### 网络信息
```bash
# 网络接口
ip addr
ip link

# 路由表
ip route

# DNS
nslookup example.com
dig example.com
```

### 连接检查
```bash
# 测试连通性
ping example.com
ping -c 5 example.com

# 端口检查
nc -zv example.com 80

# 网络连接
netstat -tuln  # 监听端口
ss -tuln

# 查看进程端口
netstat -tlnp
lsof -i :80
```

### 网络追踪
```bash
# 路由追踪
traceroute example.com
mtr example.com

# 抓包
tcpdump -i eth0
tcpdump -i eth0 port 80
tcpdump -i eth0 -w capture.pcap
```

### 网络配置
```bash
# 防火墙 (ufw)
ufw status
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## 日志分析

### 系统日志
```bash
# 系统日志位置
/var/log/syslog      # Debian/Ubuntu
/var/log/messages    # CentOS/RHEL
/var/log/auth.log    # 认证日志

# 查看日志
tail -f /var/log/syslog
tail -100 /var/log/syslog

# 搜索日志
grep "error" /var/log/syslog
grep -i "error\|fail" /var/log/syslog
```

### 日志分析技巧
```bash
# 实时监控
tail -f /var/log/nginx/access.log | grep "404\|500"

# 统计 IP 访问
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head

# 统计 HTTP 状态码
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```

## 性能监控

### CPU
```bash
# CPU 使用率
top
htop
mpstat

# CPU 信息
lscpu
cat /proc/cpuinfo
nproc  # CPU 核心数

# CPU 负载
cat /proc/loadavg
uptime
```

### I/O 性能
```bash
# I/O 统计
iostat
iostat -x 1

# I/O 监控
iotop

# 查看打开的文件
lsof
lsof -p PID
```

## 用户管理

### 用户操作
```bash
# 查看用户
whoami
id
cat /etc/passwd

# 创建用户
useradd username
useradd -m -s /bin/bash username
adduser username  # 交互式

# 删除用户
userdel username
userdel -r username  # 同时删除 home 目录

# 修改密码
passwd
passwd username
```

### 组管理
```bash
# 查看组
groups
groups username

# 创建组
groupadd groupname

# 用户组操作
gpasswd -a user group  # 添加用户到组
gpasswd -d user group  # 从组删除用户
```

### 权限管理
```bash
# 查看权限
ls -la

# 修改权限
chmod 755 file
chmod +x file

# 修改所有者
chown user file
chown user:group file
chown -R user:group directory/

# ACL
getfacl file
setfacl -m u:user:rwx file
```

## 定时任务

### crontab
```bash
# 编辑定时任务
crontab -e

# 查看定时任务
crontab -l

# 格式: 分 时 日 月 周 命令
# 示例:
* * * * * command           # 每分钟
*/5 * * * * command         # 每 5 分钟
0 * * * * command           # 每小时
0 0 * * * command           # 每天零点
0 0 * * 0 command           # 每周日零点
0 0 1 * * command           # 每月 1 号零点
```

## 文件操作

### 查找文件
```bash
# 按名称查找
find /path -name "*.py"
find /path -iname "*.py"  # 忽略大小写

# 按类型查找
find /path -type f  # 文件
find /path -type d  # 目录

# 按大小查找
find /path -size +100M

# 按时间查找
find /path -mtime -7  # 7 天内修改

# 快速查找
locate filename
sudo updatedb
```

### 文件处理
```bash
# 搜索内容
grep "pattern" file
grep -r "pattern" /path  # 递归
grep -i "pattern" file   # 忽略大小写

# 文件统计
wc file        # 行数、字数、字节数
wc -l file     # 只显示行数

# 排序去重
sort file
sort -r file   # 逆序
uniq file      # 去重
uniq -c file   # 去重并计数
```

### 压缩解压
```bash
# tar
tar -cvf archive.tar files/
tar -czvf archive.tar.gz files/
tar -xvf archive.tar
tar -xzvf archive.tar.gz

# zip/unzip
zip archive.zip files/
zip -r archive.zip directory/
unzip archive.zip
```

## 系统信息

```bash
# 系统版本
uname -a
cat /etc/os-release

# 运行时间
uptime

# 环境变量
env
echo $PATH
export VAR=value
```

## 故障排查流程

1. **检查进程**: `ps aux | grep xxx`
2. **检查端口**: `netstat -tlnp` / `ss -tlnp`
3. **检查日志**: `journalctl -u xxx -f`
4. **检查资源**: `top` / `free -h` / `df -h`
5. **检查网络**: `ping` / `curl -v` / `nc`
6. **检查防火墙**: `ufw status`

## 文档

- Linux 手册: `man command`
- TLDR: `tldr command`
- Linux 命令速查: https://cheatography.com/davechild/cheat-sheets/linux-command-line/
