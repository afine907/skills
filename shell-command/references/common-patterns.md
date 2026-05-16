# 常用 Shell 命令对照表

按场景分类，描述 → 命令的快速映射。仅在用户需求不匹配常见模式时翻查。

## 文件操作

| 场景 | 命令 |
|------|------|
| 查看目录内容 | `ls -lh` / `ls -la`（含隐藏） |
| 递归查看 | `ls -lhR` |
| 查找文件 | `find /path -name "*.py"` |
| 按大小查找 | `find / -size +100M -size -1G` |
| 按时间查找 | `find . -mtime -7`（7天内修改） |
| 目录大小 | `du -sh /path` |
| 各子目录大小 | `du -ah /path \| sort -rh \| head -10` |
| 磁盘使用 | `df -h` |
| 磁盘 inode | `df -i` |
| 复制文件 | `cp source dest` |
| 复制目录 | `cp -r source dest` |
| 移动/重命名 | `mv source dest` |
| 创建软链接 | `ln -s target link_name` |
| 递归删除目录 | `rm -rf /path`（🟡 需确认） |
| 统计文件数 | `ls -1 \| wc -l` |

## 内容搜索

| 场景 | 命令 |
|------|------|
| 搜索文件内容 | `grep -r "pattern" /path` |
| 忽略大小写 | `grep -ri "pattern" /path` |
| 显示上下文 | `grep -C 3 "pattern" file` |
| 只列出文件名 | `grep -rl "pattern" /path` |
| 正则搜索 | `grep -E "pattern" file` |
| 反向匹配 | `grep -v "exclude" file` |

## 进程管理

| 场景 | 命令 |
|------|------|
| 查看所有进程 | `ps aux` / `ps -ef` |
| 按名称搜索进程 | `ps aux \| grep nginx` |
| 进程树 | `pstree` / `ps auxf` |
| 杀进程 | `kill PID`（🟡 需确认） |
| 强制杀 | `kill -9 PID`（🟡 需额外确认） |
| 按名称杀 | `pkill -f name`（🟡 需确认） |
| 进程实时监控 | `top` / `htop` |
| 查看端口占用 | `lsof -i :80` / `ss -tlnp \| grep :80` |

## 网络诊断

| 场景 | 命令 |
|------|------|
| 连通性测试 | `ping -c 5 host` |
| HTTP 测试 | `curl -v http://host` |
| 查看响应头 | `curl -I http://host` |
| 查看监听端口 | `ss -tlnp` / `netstat -tuln` |
| 查看连接状态 | `ss -tun` / `netstat -tun` |
| DNS 查询 | `dig domain` / `nslookup domain` |
| 路由跟踪 | `traceroute host` / `tracert host` |
| 下载文件 | `wget url` / `curl -O url` |

## 文本处理

| 场景 | 命令 |
|------|------|
| 查看文件 | `cat file` / `less file` |
| 查看头尾 | `head -n 20 file` / `tail -n 20 file` |
| 实时跟踪 | `tail -f file` |
| 提取列 | `awk '{print $1, $3}' file` |
| 排序 | `sort file` / `sort -rn`（数字逆序） |
| 去重 | `sort file \| uniq` / `uniq -c`（计数） |
| 统计频率 | `awk '{print $1}' log \| sort \| uniq -c \| sort -rn` |
| 替换文本 | `sed 's/old/new/g' file` |

## 系统信息

| 场景 | 命令 |
|------|------|
| 内存使用 | `free -h` / `free -m` |
| 系统负载 | `uptime` / `top -bn1` |
| CPU 信息 | `lscpu` / `nproc` |
| 内核版本 | `uname -a` |
| 发行版 | `cat /etc/os-release` |
| 启动时间 | `uptime -s` |
| 系统日志 | `journalctl -n 50 --no-pager` |
| 实时日志 | `journalctl -f` |

## 权限管理

| 场景 | 命令 |
|------|------|
| 查看权限 | `ls -l file` |
| 修改权限 | `chmod 755 file` / `chmod +x script.sh` |
| 修改所有者 | `chown user:group file` |
| 查看当前用户 | `whoami` |
| 查看登录用户 | `who` / `w` |

## Docker

| 场景 | 命令 |
|------|------|
| 查看运行容器 | `docker ps` |
| 查看所有容器 | `docker ps -a` |
| 查看镜像 | `docker images` |
| 查看日志 | `docker logs -f container_name` |
| 进入容器 | `docker exec -it container_name bash` |
| 查看资源使用 | `docker stats` |
| 清理未用资源 | `docker system prune`（🟡 需确认） |

## Git

| 场景 | 命令 |
|------|------|
| 仓库状态 | `git status` |
| 查看 diff | `git diff` / `git diff --staged` |
| 提交历史 | `git log --oneline -10` |
| 查看分支 | `git branch -a` |
| 查某行历史 | `git log -p -- file.py` |
| 查看 blame | `git blame file.py` |
