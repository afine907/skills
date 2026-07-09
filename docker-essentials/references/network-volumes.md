# Docker 网络和卷管理

## 网络管理

### 网络操作
```bash
docker network ls
docker network create mynet
docker network create --driver bridge mynet
docker network create --subnet=172.20.0.0/16 mynet
docker network inspect mynet
docker network connect mynet nginx
docker network disconnect mynet nginx
docker network rm mynet
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

# 自定义网络 - 容器可通过名称互访
docker run -d --network mynet --name app1 myapp
docker run -d --network mynet --name app2 myapp
```

## 卷管理

### 数据卷操作
```bash
docker volume ls
docker volume create mydata
docker volume inspect mydata
docker volume rm mydata
docker volume prune

# 使用卷
docker run -v mydata:/app/data myapp
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
