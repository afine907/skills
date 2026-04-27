---
name: docker-essentials
description: Docker 容器管理速查。当需要：(1) 运行/管理 Docker 容器 (2) 构建镜像 (3) 网络和卷管理 (4) Docker Compose 操作 (5) 排查容器问题时使用。
---

# Docker Essentials

Docker 核心命令速查指南。

## 快速参考

### 容器操作
```bash
# 运行容器
docker run -d -p 8080:80 --name web nginx
docker run -it ubuntu bash                    # 交互模式
docker run -v $(pwd):/app myapp               # 挂载卷

# 管理容器
docker ps -a                                  # 列出所有容器
docker stop/start/restart nginx               # 停止/启动/重启
docker rm -f nginx                            # 删除容器
docker exec -it nginx bash                    # 进入容器
docker logs -f nginx                          # 查看日志
```

### 镜像操作
```bash
docker build -t myapp:1.0 .                   # 构建镜像
docker images                                 # 列出镜像
docker rmi nginx                              # 删除镜像
docker image prune                            # 清理悬空镜像
```

### 网络和卷
```bash
docker network create mynet                   # 创建网络
docker volume create mydata                   # 创建卷
docker run --network mynet -v mydata:/data app
```

### Docker Compose
```bash
docker compose up -d                          # 启动服务
docker compose down                           # 停止服务
docker compose logs -f web                    # 查看日志
docker compose exec web bash                  # 进入容器
```

## 详细参考

- **镜像管理**: [references/images.md](references/images.md) - 镜像构建、导出导入、清理
- **容器管理**: [references/containers.md](references/containers.md) - 端口映射、资源限制、调试
- **网络卷管理**: [references/network-volumes.md](references/network-volumes.md) - 网络模式、数据持久化
- **Compose**: [references/compose.md](references/compose.md) - 完整 docker-compose.yml 示例
- **故障排查**: [references/troubleshooting.md](references/troubleshooting.md) - 常见问题解决

## 最佳实践

- 使用 `.dockerignore` 排除不必要文件
- 多阶段构建减小镜像体积
- 使用特定版本标签，避免 `latest`
- 单一职责：一个容器一个进程
- 健康检查 `HEALTHCHECK`

## 文档

- 官方文档: https://docs.docker.com/
- Docker Hub: https://hub.docker.com/
