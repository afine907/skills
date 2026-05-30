---
name: docker-essentials
description: |
  【Docker速查】Docker 容器管理实战指南，包含容器操作、镜像构建、网络配置、数据卷管理、Docker Compose、故障排查。

  触发时机：
  - 用户要求"Docker命令"、"容器管理"
  - 需要编写 Dockerfile
  - 容器出问题需要排查

  提供完整命令和最佳实践。
category: reference
---

# Docker Essentials — Docker 实战指南

Docker 容器管理从入门到实战的完整指南。


## Goal

Docker 容器管理实战指南，包含容器操作、镜像构建、网络配置、数据卷管理、Docker Compose、故障排查

## Trigger

- 用户要求"Docker命令"、"容器管理"
  - 需要编写 Dockerfile
  - 容器出问题需要排查

## 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| 镜像 (Image) | 只读模板 | 类 (Class) |
| 容器 (Container) | 运行实例 | 对象 (Instance) |
| 仓库 (Registry) | 镜像存储 | npm/PyPI |
| 卷 (Volume) | 持久化存储 | 外接硬盘 |
| 网络 (Network) | 容器通信 | 局域网 |

## 容器操作

### 生命周期管理

```bash
# 创建并启动
docker run -d -p 8080:80 --name web nginx
docker run -it ubuntu bash                    # 交互模式
docker run --rm ubuntu echo "hello"           # 运行后删除

# 管理
docker ps                                     # 运行中的容器
docker ps -a                                  # 所有容器
docker start/stop/restart web                 # 启停容器
docker rm -f web                              # 强制删除
docker container prune                        # 删除所有停止的容器

# 进入容器
docker exec -it web bash                      # 交互式 shell
docker exec web cat /etc/nginx/nginx.conf     # 执行命令

# 查看日志
docker logs -f web                            # 实时日志
docker logs --tail 100 web                    # 最后100行
docker logs --since 1h web                    # 最近1小时
```

### 资源限制

```bash
# CPU 限制
docker run --cpus=1.5 myapp                   # 限制1.5核
docker run --cpu-shares=512 myapp             # 相对权重

# 内存限制
docker run --memory=512m myapp                # 限制512MB
docker run --memory=1g --memory-swap=2g myapp # 内存+交换

# 查看资源使用
docker stats                                  # 实时监控
docker stats --no-stream                      # 单次快照
```

## 镜像操作

### 构建镜像

```dockerfile
# Dockerfile 最佳实践
FROM node:20-alpine AS builder                # 使用精简基础镜像
WORKDIR /app
COPY package*.json ./                         # 先复制依赖文件
RUN npm ci --only=production                  # 安装依赖（利用缓存）
COPY . .                                      # 复制源代码
RUN npm run build

FROM node:20-alpine AS runtime                # 多阶段构建
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000/health
USER node                                     # 非 root 运行
CMD ["node", "dist/index.js"]
```

### 镜像管理

```bash
# 构建
docker build -t myapp:1.0 .
docker build -t myapp:1.0 -f Dockerfile.prod .
docker build --no-cache -t myapp:1.0 .

# 标签
docker tag myapp:1.0 myapp:latest
docker tag myapp:1.0 registry.example.com/myapp:1.0

# 推送/拉取
docker push registry.example.com/myapp:1.0
docker pull nginx:1.25

# 导出/导入
docker save myapp:1.0 > myapp.tar
docker load < myapp.tar

# 清理
docker image prune                            # 删除悬空镜像
docker image prune -a                         # 删除所有未使用
docker system prune -a                        # 清理所有未使用资源
```

## 网络配置

### 网络类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| bridge | 默认，容器间通信 | 单机多容器 |
| host | 共享主机网络 | 高性能需求 |
| none | 无网络 | 安全隔离 |
| overlay | 跨主机通信 | Docker Swarm |

```bash
# 网络管理
docker network create mynet                   # 创建桥接网络
docker network create --driver overlay swarm-net  # 创建 overlay 网络
docker network ls                             # 列出网络
docker network inspect mynet                  # 查看详情
docker network connect mynet web              # 连接容器到网络
docker network disconnect mynet web           # 断开连接

# 使用自定义网络
docker run -d --name web --network mynet nginx
docker run -d --name api --network mynet myapp
# web 和 api 可以通过容器名互相访问
```

## 数据卷管理

```bash
# 命名卷
docker volume create mydata
docker run -v mydata:/data nginx
docker volume ls
docker volume inspect mydata
docker volume rm mydata

# 绑定挂载
docker run -v $(pwd)/html:/usr/share/nginx/html nginx
docker run -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx

# tmpfs 挂载（内存）
docker run --tmpfs /app/temp nginx
```

## Docker Compose

### 完整示例

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
    networks:
      - app-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    networks:
      - app-net

volumes:
  pgdata:

networks:
  app-net:
```

### Compose 命令

```bash
# 基础操作
docker compose up -d                          # 后台启动
docker compose down                           # 停止并删除
docker compose down -v                        # 同时删除卷
docker compose ps                             # 查看状态
docker compose logs -f web                    # 查看日志
docker compose exec web bash                  # 进入容器

# 构建
docker compose build                          # 构建所有服务
docker compose build --no-cache web           # 无缓存构建
docker compose up -d --build                  # 构建并启动

# 扩缩容
docker compose up -d --scale web=3            # 扩展到3个实例

# 环境变量
docker compose --env-file .env.prod up -d     # 指定环境文件
```

## 故障排查

### 常见问题

```bash
# 容器无法启动
docker logs web                               # 查看日志
docker inspect web                            # 查看详细信息
docker events                                 # 查看事件

# 容器内网络问题
docker exec web ping api                      # 测试连通性
docker exec web curl http://api:3000/health   # 测试 HTTP
docker exec web cat /etc/resolv.conf          # 检查 DNS

# 磁盘空间不足
docker system df                              # 查看使用情况
docker system prune -a --volumes              # 清理所有

# 性能问题
docker stats                                  # 资源使用
docker top web                                # 进程列表
```

### 调试技巧

```bash
# 使用 debug 镜像
docker run -it --network mynet nicolaka/netshoot

# 查看容器文件系统
docker diff web                               # 文件变更
docker cp web:/app/logs ./logs                # 复制文件

# 导出容器状态
docker export web > web.tar
```

## 安全最佳实践

1. **非 root 运行**: `USER node`
2. **只读文件系统**: `--read-only`
3. **限制能力**: `--cap-drop ALL --cap-add NET_BIND_SERVICE`
4. **扫描漏洞**: `docker scout cves myapp`
5. **使用签名镜像**: Docker Content Trust
6. **最小权限**: 只暴露必要端口

## 快速使用

```
# 编写 Dockerfile
为 Node.js 项目编写多阶段构建的 Dockerfile

# 配置 Docker Compose
为 Web + DB + Redis 配置 docker-compose.yml

# 排查容器问题
容器启动失败，帮我排查原因

# 优化镜像
优化这个 Dockerfile 减小镜像体积
```

## 参考资料

- 镜像管理: [references/images.md](references/images.md)
- 容器管理: [references/containers.md](references/containers.md)
- 网络卷管理: [references/network-volumes.md](references/network-volumes.md)
- Compose: [references/compose.md](references/compose.md)
- 故障排查: [references/troubleshooting.md](references/troubleshooting.md)
