# Docker Compose

## 常用命令

```bash
docker compose up                           # 启动服务
docker compose up -d                        # 后台运行
docker compose up --build                   # 构建并启动
docker compose down                         # 停止服务
docker compose down -v                      # 同时删除卷
docker compose ps                           # 查看状态
docker compose logs -f web                  # 查看日志
docker compose exec web bash                # 进入容器
docker compose restart                      # 重启服务
docker compose pull                         # 拉取镜像
docker compose config                       # 查看配置
```

## docker-compose.yml 示例

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

## 常用模式

### 开发环境
```yaml
services:
  dev:
    image: node:20-alpine
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "3000:3000"
    command: npm run dev
```

### 数据库持久化
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pg_data:
```
