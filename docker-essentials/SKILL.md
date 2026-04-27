---
name: docker-essentials
description: Docker 容器管理基础命令和最佳实践，覆盖镜像、容器、网络、卷管理。
homepage: https://www.docker.com/
metadata: {"clawdbot":{"emoji":"🐳","requires":{"bins":["docker"]}}}
---

# Docker Essentials

Docker 容器管理核心命令速查。

## 镜像管理

### 查找和拉取
```bash
# 搜索镜像
docker search nginx
docker search --limit 5 nginx

# 拉取镜像
docker pull nginx
docker pull nginx:1.25-alpine
docker pull python:3.12-slim

# 列出本地镜像
docker images
docker image ls

# 查看镜像详情
docker image inspect nginx

# 查看镜像历史
docker history nginx

# 导出/导入镜像
docker save -o nginx.tar nginx:latest
docker load -i nginx.tar
```

### 构建镜像
```bash
# 从 Dockerfile 构建
docker build -t myapp:1.0 .
docker build -t myapp:1.0 -f Dockerfile.prod .

# 构建时传递参数
docker build --build-arg NODE_ENV=production -t myapp .

# 不使用缓存构建
docker build --no-cache -t myapp .

# 多平台构建
docker buildx build --platform linux/amd64,linux/arm64 -t myapp .
```

### 清理镜像
```bash
# 删除镜像
docker rmi nginx
docker rmi -f $(docker images -q)  # 删除所有

# 删除悬空镜像 (none tag)
docker image prune

# 删除所有未使用的镜像
docker image prune -a
```

## 容器管理

### 运行容器
```bash
# 基本运行
docker run nginx
docker run -d nginx  # 后台运行
docker run --name web nginx

# 端口映射
docker run -d -p 8080:80 nginx
docker run -d -p 127.0.0.1:8080:80 nginx

# 环境变量
docker run -e MYSQL_ROOT_PASSWORD=secret mysql
docker run --env-file .env myapp

# 挂载卷
docker run -v /host/path:/container/path nginx
docker run -v $(pwd):/app myapp
docker run --mount type=bind,src=/host,dst=/container nginx

# 交互模式
docker run -it ubuntu bash
docker run -it --rm ubuntu bash  # 退出后删除

# 资源限制
docker run --memory=512m --cpus=1 nginx
docker run --memory=512m --memory-swap=1g nginx
```

### 列出容器
```bash
# 运行中的容器
docker ps
docker container ls

# 所有容器（包括停止的）
docker ps -a

# 只显示 ID
docker ps -q

# 格式化输出
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker ps --format "{{.Names}}: {{.Status}}"
```

### 管理容器
```bash
# 停止/启动
docker stop nginx
docker start nginx
docker restart nginx

# 暂停/恢复
docker pause nginx
docker unpause nginx

# 杀死容器
docker kill nginx

# 删除容器
docker rm nginx
docker rm -f nginx  # 强制删除运行中的
docker rm $(docker ps -aq)  # 删除所有

# 查看容器信息
docker inspect nginx
docker stats nginx

# 查看资源使用
docker stats --no-stream
```

### 进入容器
```bash
# 执行命令
docker exec nginx ls /app
docker exec -it nginx bash

# 附加到容器
docker attach nginx

# 以 root 进入
docker exec -u 0 -it nginx bash
```

### 日志和调试
```bash
# 查看日志
docker logs nginx
docker logs -f nginx  # 实时跟踪
docker logs --tail 100 nginx
docker logs --since 1h nginx

# 导出容器
docker export nginx > nginx.tar

# 查看进程
docker top nginx

# 查看端口映射
docker port nginx

# 查看文件变更
docker diff nginx
```

## 网络管理

### 网络操作
```bash
# 列出网络
docker network ls

# 创建网络
docker network create mynet
docker network create --driver bridge mynet
docker network create --subnet=172.20.0.0/16 mynet

# 连接容器到网络
docker network connect mynet nginx
docker network disconnect mynet nginx

# 查看网络详情
docker network inspect mynet

# 删除网络
docker network rm mynet

# 清理未使用的网络
docker network prune
```

### 网络模式
```bash
# bridge (默认)
docker run -d --network bridge nginx

# host (共享主机网络)
docker run -d --network host nginx

# none (无网络)
docker run -d --network none nginx

# 自定义网络
docker run -d --network mynet --name app1 myapp
docker run -d --network mynet --name app2 myapp
# app1 和 app2 可以通过容器名互相访问
```

## 卷管理

### 数据卷操作
```bash
# 列出卷
docker volume ls

# 创建卷
docker volume create mydata

# 查看卷详情
docker volume inspect mydata

# 使用卷
docker run -v mydata:/app/data myapp

# 删除卷
docker volume rm mydata

# 清理未使用的卷
docker volume prune
```

### 绑定挂载 vs 卷
```bash
# 绑定挂载 (适合开发)
docker run -v $(pwd)/src:/app/src myapp

# 命名卷 (适合生产)
docker run -v mydata:/data myapp

# 匿名卷
docker run -v /data myapp
```

## Docker Compose

### 基本命令
```bash
# 启动服务
docker compose up
docker compose up -d  # 后台运行

# 构建并启动
docker compose up --build

# 停止服务
docker compose down
docker compose down -v  # 同时删除卷

# 查看状态
docker compose ps
docker compose logs
docker compose logs -f web

# 执行命令
docker compose exec web bash

# 重启服务
docker compose restart
docker compose restart web

# 拉取镜像
docker compose pull

# 查看配置
docker compose config
docker compose config --services
```

### docker-compose.yml 示例
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - api
    networks:
      - frontend

  api:
    build: ./api
    environment:
      - DATABASE_URL=postgres://db:5432/mydb
    depends_on:
      - db
    networks:
      - frontend
      - backend

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend

networks:
  frontend:
  backend:

volumes:
  pgdata:
```

## 清理命令

```bash
# 清理所有未使用的资源
docker system prune

# 同时清理卷
docker system prune --volumes

# 同时清理镜像
docker system prune -a

# 查看磁盘使用
docker system df

# 实时事件
docker events
```

## 常用模式

### 开发环境
```bash
# 热重载开发
docker run -d \
  --name dev \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:20-alpine \
  npm run dev
```

### 数据库
```bash
# MySQL 持久化
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=secret \
  -v mysql_data:/var/lib/mysql \
  -p 3306:3306 \
  mysql:8

# PostgreSQL 持久化
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -v pg_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine

# Redis 持久化
docker run -d \
  --name redis \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes
```

### 多容器应用
```bash
# 创建网络
docker network create appnet

# 启动数据库
docker run -d --name db --network appnet \
  -e POSTGRES_PASSWORD=secret postgres

# 启动应用
docker run -d --name app --network appnet \
  -e DATABASE_URL=postgres://db:5432/mydb \
  -p 8080:8080 myapp
```

## 故障排查

```bash
# 查看容器退出原因
docker inspect --format='{{.State.ExitCode}}' nginx
docker inspect --format='{{.State.Error}}' nginx

# 查看容器事件
docker events --filter container=nginx

# 实时监控资源
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 复制文件
docker cp nginx:/etc/nginx/nginx.conf ./
docker cp ./app.conf nginx:/etc/nginx/conf.d/

# 查看层大小
docker history --human nginx
```

## 最佳实践

- 使用 `.dockerignore` 排除不必要文件
- 多阶段构建减小镜像体积
- 使用特定版本标签，避免 `latest`
- 非 root 用户运行容器
- 单一职责原则，一个容器一个进程
- 健康检查 `HEALTHCHECK`
- 使用 Docker Compose 管理多容器应用
- 定期清理未使用的资源

## 文档

- 官方文档: https://docs.docker.com/
- Docker Hub: https://hub.docker.com/
- Dockerfile 最佳实践: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Compose 规范: https://compose-spec.io/
