# Docker 容器管理

## 运行容器

### 基本运行
```bash
docker run nginx
docker run -d nginx                          # 后台运行
docker run --name web nginx                  # 指定名称
```

### 端口映射
```bash
docker run -d -p 8080:80 nginx               # 映射端口
docker run -d -p 127.0.0.1:8080:80 nginx     # 绑定地址
```

### 环境变量
```bash
docker run -e MYSQL_ROOT_PASSWORD=secret mysql
docker run --env-file .env myapp
```

### 挂载卷
```bash
docker run -v /host/path:/container/path nginx
docker run -v $(pwd):/app myapp
docker run --mount type=bind,src=/host,dst=/container nginx
```

### 交互模式
```bash
docker run -it ubuntu bash
docker run -it --rm ubuntu bash              # 退出后删除
```

### 资源限制
```bash
docker run --memory=512m --cpus=1 nginx
docker run --memory=512m --memory-swap=1g nginx
```

## 管理容器

### 列出容器
```bash
docker ps                                    # 运行中的容器
docker ps -a                                 # 所有容器
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 生命周期管理
```bash
docker stop nginx
docker start nginx
docker restart nginx
docker pause nginx
docker unpause nginx
docker kill nginx
docker rm nginx
docker rm -f nginx                           # 强制删除运行中的
docker rm $(docker ps -aq)                   # 删除所有
```

### 进入容器
```bash
docker exec nginx ls /app
docker exec -it nginx bash
docker exec -u 0 -it nginx bash              # 以 root 进入
docker attach nginx
```

### 日志和调试
```bash
docker logs nginx
docker logs -f nginx                         # 实时跟踪
docker logs --tail 100 nginx
docker logs --since 1h nginx
docker top nginx
docker port nginx
docker diff nginx
docker stats --no-stream
```

### 复制文件
```bash
docker cp nginx:/etc/nginx/nginx.conf ./
docker cp ./app.conf nginx:/etc/nginx/conf.d/
```
