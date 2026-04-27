# Docker 故障排查

## 查看容器状态

```bash
# 查看容器退出原因
docker inspect --format='{{.State.ExitCode}}' nginx
docker inspect --format='{{.State.Error}}' nginx

# 查看容器事件
docker events --filter container=nginx

# 实时监控资源
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 查看层大小
docker history --human nginx
```

## 常见问题

### 容器无法启动
```bash
# 查看日志
docker logs nginx

# 查看详细信息
docker inspect nginx

# 交互调试
docker run -it --entrypoint bash nginx
```

### 网络问题
```bash
# 检查网络
docker network inspect bridge

# 测试连通性
docker exec nginx ping db

# 查看端口映射
docker port nginx
```

### 磁盘空间不足
```bash
# 查看磁盘使用
docker system df

# 清理未使用资源
docker system prune
docker system prune --volumes
docker system prune -a
```

### 权限问题
```bash
# 以 root 进入
docker exec -u 0 -it nginx bash

# 查看用户
docker exec nginx whoami
```

## 清理命令

```bash
# 清理所有未使用的资源
docker system prune

# 同时清理卷
docker system prune --volumes

# 同时清理镜像
docker system prune -a

# 只清理特定类型
docker container prune
docker image prune
docker volume prune
docker network prune
```
