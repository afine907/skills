# Docker 镜像管理

## 镜像操作

### 搜索和拉取
```bash
docker search nginx
docker pull nginx:1.25-alpine
docker pull python:3.12-slim
```

### 列出和查看
```bash
docker images
docker image ls
docker image inspect nginx
docker history nginx
```

### 构建镜像
```bash
docker build -t myapp:1.0 .
docker build -t myapp:1.0 -f Dockerfile.prod .
docker build --build-arg NODE_ENV=production -t myapp .
docker build --no-cache -t myapp .
docker buildx build --platform linux/amd64,linux/arm64 -t myapp .
```

### 导出导入
```bash
docker save -o nginx.tar nginx:latest
docker load -i nginx.tar
```

### 删除镜像
```bash
docker rmi nginx
docker rmi -f $(docker images -q)
docker image prune          # 删除悬空镜像
docker image prune -a       # 删除所有未使用的镜像
```
