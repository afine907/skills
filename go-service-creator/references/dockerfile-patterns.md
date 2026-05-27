# Go Dockerfile Patterns

## 多阶段构建（推荐）

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o server cmd/server/main.go

# Run stage
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
```

## 关键点

| 要点 | 说明 |
|------|------|
| `CGO_ENABLED=0` | 禁用 CGO，生成纯静态二进制 |
| `-ldflags="-s -w"` | 去掉调试信息，减小体积 |
| `go mod download` | 单独一层利用 Docker 缓存 |
| `alpine` 基础镜像 | 最终镜像只有 ~10MB |
| `ca-certificates` | HTTPS 请求需要 |

## .dockerignore

```
.git
.env
*.md
Makefile
tmp/
vendor/
```
