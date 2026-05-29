# 应急响应手册

本文档提供常见故障场景的应急处置 Playbook，供 `/incident-response` 技能在事故处理中参考。每个场景包含现象识别、排查步骤和处置方案。

## 一、通用排查流程

### 排查顺序（黄金信号）

```
延迟 (Latency) → 流量 (Traffic) → 错误 (Errors) → 饱和度 (Saturation)
```

### 快速诊断命令

```bash
# 服务健康检查
curl -s http://localhost:8080/health | jq .

# 查看最近部署
kubectl rollout history deployment/my-app -n production

# 查看 Pod 状态
kubectl get pods -n production -l app=my-app

# 查看最近日志
kubectl logs -n production -l app=my-app --tail=100 --since=10m

# 查看资源使用
kubectl top pods -n production -l app=my-app

# 查看系统负载
uptime && free -h && df -h
```

---

## 二、常见故障场景 Playbook

### 场景 1: 服务完全不可用（P0）

**现象**：
- 所有请求返回 5xx 或超时
- 健康检查失败
- 监控大面积告警

**排查步骤**：

```bash
# 1. 检查服务是否存活
kubectl get pods -n production -l app=my-app

# 2. 检查 Pod 事件
kubectl describe pods -n production -l app=my-app | grep -A5 Events

# 3. 检查最近部署
kubectl rollout history deployment/my-app -n production

# 4. 检查资源配额
kubectl describe resourcequota -n production
```

**处置方案**（按优先级）：

| 优先级 | 操作 | 命令 |
|--------|------|------|
| 1 | 回滚最近部署 | `kubectl rollout undo deployment/my-app -n production` |
| 2 | 扩容副本 | `kubectl scale deployment/my-app --replicas=10 -n production` |
| 3 | 重启 Pod | `kubectl rollout restart deployment/my-app -n production` |

---

### 场景 2: 错误率飙升（P0/P1）

**现象**：
- 5xx 错误率突然升高
- 部分请求成功，部分失败
- 可能伴随延迟升高

**排查步骤**：

```bash
# 1. 确认错误类型
kubectl logs -n production -l app=my-app --tail=200 | grep -i "error\|exception" | sort | uniq -c | sort -rn

# 2. 检查是否有新部署
git log --oneline -5

# 3. 检查依赖服务状态
curl -s http://dependency-service:8080/health

# 4. 检查数据库连接
kubectl exec -it deploy/my-app -n production -- python -c "import db; db.ping()"
```

**常见原因与处置**：

| 原因 | 识别特征 | 处置 |
|------|----------|------|
| 新部署引入 Bug | 错误在部署后立即出现 | 回滚 |
| 依赖服务异常 | 错误包含 connection refused/timeout | 检查依赖服务，启用降级 |
| 数据库连接池耗尽 | 错误包含 "connection pool" | 扩容连接池或重启服务 |
| 内存 OOM | Pod 重启，OOMKilled 状态 | 扩容内存或增加副本 |

---

### 场景 3: 延迟升高（P1/P2）

**现象**：
- P99 延迟显著升高
- 用户反馈"变慢了"
- 可能没有明显错误

**排查步骤**：

```bash
# 1. 确认延迟分布
# 查看监控面板的 P50/P95/P99 延迟

# 2. 检查慢查询
kubectl exec -it deploy/my-app -n production -- \
  cat /var/log/slow-query.log | tail -20

# 3. 检查资源饱和度
kubectl top pods -n production -l app=my-app

# 4. 检查外部依赖延迟
time curl -s http://external-api.example.com/health
```

**常见原因与处置**：

| 原因 | 处置 |
|------|------|
| 数据库慢查询 | 优化查询 / 添加索引 / 读写分离 |
| 外部 API 变慢 | 设置超时 / 启用熔断 / 使用缓存 |
| 资源不足（CPU/内存） | 扩容 |
| 缓存失效 | 预热缓存 / 检查缓存配置 |

---

### 场景 4: 数据库故障（P0）

**现象**：
- 数据库连接失败
- 查询超时
- 数据不一致

**排查步骤**：

```bash
# 1. 检查数据库连接
mysql -h $DB_HOST -u $DB_USER -p -e "SELECT 1"

# 2. 检查连接数
mysql -e "SHOW STATUS LIKE 'Threads_connected'"

# 3. 检查慢查询
mysql -e "SHOW PROCESSLIST"

# 4. 检查磁盘空间
df -h /var/lib/mysql
```

**处置方案**：

| 场景 | 处置 |
|------|------|
| 主库故障 | 切换到从库，提升为主库 |
| 连接池耗尽 | 杀掉空闲连接，扩容连接池 |
| 磁盘满 | 清理日志/临时表，扩容磁盘 |
| 慢查询阻塞 | 杀掉长时间运行的查询 |

```bash
# 杀掉长时间查询
mysql -e "SELECT * FROM information_schema.processlist WHERE time > 60"
mysql -e "KILL <process_id>"

# 切换主从（以 MySQL 为例）
# 1. 停止应用写入
# 2. 确认从库数据同步完成
# 3. 提升从库为主库
# 4. 更新应用数据库连接配置
# 5. 恢复应用写入
```

---

### 场景 5: 磁盘空间不足（P1/P2）

**现象**：
- 写入失败
- 日志停止记录
- 服务异常

**排查步骤**：

```bash
# 1. 确认磁盘使用
df -h

# 2. 查找大文件
du -sh /* | sort -rh | head -10
du -sh /var/log/* | sort -rh | head -10

# 3. 检查 Docker 空间
docker system df
```

**处置方案**：

```bash
# 清理日志
find /var/log -name "*.log" -mtime +7 -delete

# 清理 Docker
docker system prune -f
docker volume prune -f

# 清理临时文件
rm -rf /tmp/*
```

---

### 场景 6: 内存泄漏（P2）

**现象**：
- 内存使用持续增长
- Pod 频繁 OOMKilled 重启
- 服务周期性不可用

**排查步骤**：

```bash
# 1. 查看内存使用趋势
kubectl top pods -n production -l app=my-app

# 2. 查看 OOM 事件
kubectl get events -n production --field-selector reason=OOMKilling

# 3. 分析堆转储（Java）
jmap -dump:live,format=b,file=heap.bin <pid>

# 4. 分析内存快照（Node.js）
node --inspect app.js
# 然后用 Chrome DevTools 连接分析
```

**处置方案**：
- 短期：增加内存限制或增加副本数
- 中期：分析内存快照定位泄漏点
- 长期：修复代码中的内存泄漏

---

## 三、应急通信模板

### 事故通报（内部）

```
[事故通报] {服务名} - {P级别}

现象：{用户/系统观察到的症状}
影响：{受影响的用户数/功能}
状态：排查中 / 处置中 / 已恢复
负责人：{姓名}
下次更新：{时间}
```

### 事故通报（外部/用户）

```
尊敬的用户：

我们发现 {功能/服务} 出现异常，技术团队正在紧急处理中。
预计恢复时间：{时间}（如有）

给您带来不便，深表歉意。
```

### 恢复通报

```
[恢复通报] {服务名} - {P级别}

事故时间：{开始时间} - {结束时间}，持续 {时长}
根因：{简要原因}
处置：{采取的措施}
后续：{改进计划}

服务已恢复正常运行。
```

---

## 四、应急工具箱

### 常用诊断工具

| 工具 | 用途 | 命令示例 |
|------|------|----------|
| `curl` | HTTP 请求测试 | `curl -v http://service/health` |
| `ping`/`traceroute` | 网络连通性 | `traceroute db.internal` |
| `netstat`/`ss` | 端口和连接 | `ss -tlnp \| grep 8080` |
| `top`/`htop` | 系统资源 | `top -bn1 \| head -20` |
| `strace` | 系统调用追踪 | `strace -p <pid> -e trace=network` |
| `tcpdump` | 网络抓包 | `tcpdump -i eth0 port 8080` |

### 常用 K8s 诊断

```bash
# 查看 Pod 详情
kubectl describe pod <pod-name> -n production

# 进入 Pod 调试
kubectl exec -it <pod-name> -n production -- /bin/sh

# 查看 Pod 日志（前一个容器）
kubectl logs <pod-name> -n production --previous

# 临时调试容器
kubectl debug -it <pod-name> -n production --image=busybox
```
