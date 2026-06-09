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
user-invocable: false
---

# Docker Essentials — Docker 实战指南

Docker 容器管理从入门到实战的完整指南。


## Goal

Docker 容器管理实战指南，包含容器操作、镜像构建、网络配置、数据卷管理、Docker Compose、故障排查

## Trigger

- 用户要求"Docker命令"、"容器管理"
  - 需要编写 Dockerfile
  - 容器出问题需要排查

## 工作流程

1. **确定部署模式** -- 评估项目需求：单个容器（简单 Web 服务 / CLI 工具）还是多服务（Web + DB + Cache）？if 单容器 -> 使用 `docker run` + 手写 Dockerfile 流程（步骤 2）；if 多服务 -> 使用 Docker Compose 流程（步骤 2'）。
2. **编写 Dockerfile** -- 选择精简基础镜像（`alpine` / `distroless`）。if 构建阶段包含开发依赖 -> 使用多阶段构建分离构建和运行环境。先复制依赖文件（`package*.json`、`requirements.txt`），再 `RUN install`，最后复制源码以利用缓存。添加 `HEALTHCHECK` 指令。
2'. **编写 docker-compose.yml** -- 定义所有服务及其依赖关系。使用 `depends_on` + `condition: service_healthy` 确保启动顺序。为需要持久化的数据声明 named volumes。为服务间通信创建自定义 bridge network。添加 healthcheck 确保服务就绪。
3. **构建和本地测试** -- `docker build -t myapp:1.0 .` 构建镜像。`docker run -d -p 8080:80 myapp:1.0` 启动容器。验证服务响应正常（`curl http://localhost:8080`）。
4. **镜像优化** -- if 镜像体积过大 -> 检查 `docker history myapp:1.0` 查看各层大小。使用 `.dockerignore` 排除不需要的文件（`node_modules`、`.git`、`__pycache__`）。合并 RUN 层减少层数。删除构建时依赖（`--only=production`）。
5. **部署** -- if 单机部署 -> `docker compose up -d`；if 需要集群编排 -> 使用 Kubernetes 或 Docker Swarm。配置容器自动重启（`restart: unless-stopped`）。确认所有容器的 healthcheck 通过。
6. **监控和故障排查** -- `docker stats` 监控资源使用。`docker logs -f <container>` 查看日志。if 容器反复重启 -> `docker inspect <container>` 检查退出码。定期执行 `docker system prune` 清理无用资源。

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

## 多平台构建（BuildKit/buildx）

### 设置 buildx

```bash
# 创建构建器
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# 列出构建器
docker buildx ls
```

### 多平台构建

```bash
# 构建多平台镜像
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:1.0 .

# 推送到仓库
docker buildx build --platform linux/amd64,linux/arm64 \
  -t registry.example.com/myapp:1.0 \
  --push .

# 构建并加载到本地
docker buildx build --platform linux/amd64 -t myapp:1.0 --load .
```

### Dockerfile 多平台兼容

```dockerfile
# 使用 TARGETARCH 变量
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder
ARG TARGETARCH
WORKDIR /app
COPY . .
RUN npm ci && npm run build

FROM node:20-alpine
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

## Docker 系统配置（daemon.json）

```json
{
  "data-root": "/data/docker",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "registry-mirrors": [
    "https://mirror.example.com"
  ],
  "insecure-registries": [],
  "default-address-pools": [
    {"base": "172.17.0.0/12", "size": 24}
  ],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
```

```bash
# 重启 Docker 使配置生效
systemctl restart docker

# 查看配置
docker info | grep -A 5 "Docker Root Dir"
```

## 镜像扫描与安全

```bash
# Docker Scout（推荐）
docker scout cves myapp:latest             # 扫描漏洞
docker scout recommendations myapp:latest  # 安全建议

# Trivy（开源工具）
trivy image myapp:latest                   # 扫描镜像
trivy image --severity HIGH,CRITICAL myapp:latest  # 仅高危

# Grype（开源工具）
grype myapp:latest                         # 扫描镜像
```

## 安全最佳实践

1. **非 root 运行**: `USER node`
2. **只读文件系统**: `--read-only`
3. **限制能力**: `--cap-drop ALL --cap-add NET_BIND_SERVICE`
4. **扫描漏洞**: `docker scout cves myapp`
5. **使用签名镜像**: Docker Content Trust
6. **最小权限**: 只暴露必要端口
7. **多阶段构建**: 减少攻击面
8. **固定基础镜像版本**: 避免使用 `latest` 标签

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

## Edge Cases / 常见陷阱

| 场景 | 现象 | 诊断方法 | 解决方案 |
|------|------|----------|----------|
| 容器反复重启 | `docker ps` 显示重启计数递增 | `docker inspect <container>` 查看 `ExitCode`；`docker logs <container>` 查看退出原因 | exit code 1 = 应用错误，检查日志；exit code 137 = OOM killed，增加 `--memory`；exit code 1 = 配置错误，检查环境变量 |
| 端口冲突 | `Bind for 0.0.0.0:80 failed: port is already allocated` | `docker port <container>` 查看端口映射；`lsof -i :80` 找到占用进程 | 更换宿主机端口（`-p 8080:80`）；停掉冲突容器；修改 host 绑定地址 |
| 卷挂载权限被拒绝 | 容器内无法写入挂载的目录 | `ls -la` 检查宿主机目录权限；`docker exec` 检查容器内 UID/GID | 使用 `--user $(id -u):$(id -g)` 指定 UID/GID；或在 Dockerfile 中 `chown` 目标目录 |
| 构建缓存失效 | 每次构建都要重新安装依赖 | 检查 Dockerfile 中 COPY 指令顺序和 .dockerignore 配置 | 确保依赖文件（package.json、requirements.txt）在源码之前 COPY；检查 .dockerignore 是否排除了不该排除的文件 |
| Compose 服务间无法通信 | `docker compose exec web ping api` 失败 | `docker network inspect <network>` 检查容器是否在同一网络；确认使用**服务名**而非 localhost | 所有需要互通的服务必须加入同一自定义网络；使用服务名作为主机名 |
| 磁盘被 Docker 耗尽 | `No space left on device` | `docker system df` 查看 Docker 磁盘占用 | `docker system prune -a --volumes` 清理；配置 daemon.json 限制日志大小（`max-size`、`max-file`） |
| Windows Docker Desktop 路径问题 | 挂载的卷内容为空或路径错误 | 确认 Docker Desktop 设置中共享了对应磁盘 | 在 Docker Desktop Settings > Resources > File Sharing 中添加共享路径；使用 `//c/` 格式而非 `C:\` |
| 多阶段构建产物未复制 | 运行时镜像缺少必要的文件 | `docker run --rm <image> ls /app` 检查文件是否存在 | 确认 `COPY --from=builder` 指令的源路径和目标路径正确；确认构建阶段确实生成了所需文件 |
| 容器内 DNS 解析失败 | 容器无法解析外部域名 | `docker exec <container> cat /etc/resolv.conf` 检查 DNS 配置 | 检查宿主机 DNS；在 daemon.json 中配置 `dns` 字段；检查是否有自定义网络 DNS 限制 |
| Docker Desktop 在 WSL2 中性能差 | 文件操作（如 `npm install`）极慢 | 确认项目目录是否在 Linux 文件系统内 | 将项目放在 WSL2 的 ext4 文件系统中（`~/projects/`）而非 `/mnt/c/`；使用 Docker Desktop 的 WSL2 后端集成 |

## 不适用场景

| 场景 | 原因 | 建议使用 |
|------|------|----------|
| Kubernetes 集群编排 | 本技能覆盖单机 Docker，非集群编排 | 使用 k8s-cluster 技能 |
| CI/CD 流水线构建 | 本技能不覆盖 CI/CD 集成配置 | 使用 ci-workflow 技能 |
| Podman 容器管理 | Podman CLI 虽类似但有差异（无 daemon、rootless 默认） | 参考 Podman 官方文档 |
| Docker Swarm 集群 | 本技能仅覆盖基本 Swarm 命令，不深入 | 考虑迁移到 Kubernetes 或参考 Swarm 文档 |
| 容器安全扫描 | 本技能不覆盖漏洞扫描和安全审计 | 使用 security-scanning 技能 |
| 微服务架构设计 | 本技能关注 Docker 操作，非架构设计 | 使用 architecture-decision 技能 |
| 服务器运维（宿主机） | 本技能聚焦容器内操作，非宿主机管理 | 使用 linux-essentials 技能 |

## 参考资料

- 镜像管理: [references/images.md](references/images.md)
- 容器管理: [references/containers.md](references/containers.md)
- 网络卷管理: [references/network-volumes.md](references/network-volumes.md)
- Compose: [references/compose.md](references/compose.md)
- 故障排查: [references/troubleshooting.md](references/troubleshooting.md)
