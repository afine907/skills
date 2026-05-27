# Python Dockerfile Patterns

## FastAPI 多阶段构建

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# Run stage
FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Flask

```dockerfile
FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app/ ./app/
USER appuser
EXPOSE 8000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]
```

## 关键点

| 要点 | 说明 |
|------|------|
| `python:3.12-slim` | 精简镜像，~150MB |
| `--no-cache-dir` | 不缓存 pip 下载 |
| `useradd` | 非 root 用户运行 |
| `COPY pyproject.toml` 单独一层 | 利用 Docker 缓存 |

## .dockerignore

```
.git
.env
__pycache__
*.pyc
.pytest_cache
.venv
tests/
*.md
```
