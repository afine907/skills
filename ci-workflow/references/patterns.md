# CI 配置模式大全

按平台分类的常见 CI 配置片段。仅在用户需求不匹配常见模式时翻查。

---

## GitHub Actions

### 基础工作流骨架

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# 并发控制：同一 PR/分支的重复运行自动取消
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15           # 防止 runaway job
    permissions:                  # 最小权限
      contents: read
      checks: write

    steps:
      - uses: actions/checkout@v4
      - name: Setup
        run: echo "ready"
```

### 触发事件组合

| 事件 | 常用过滤 | 说明 |
|------|----------|------|
| `push` | `branches: [main]`、`paths: ['src/**']` | 代码推送 |
| `pull_request` | `branches: [main]` | PR 事件 |
| `pull_request_target` | ❌ 高危，需手动确认 | 有 secrets 上下文，避免 checkout PR 代码 |
| `workflow_dispatch` | — | 手动触发 |
| `schedule` | `cron: '0 2 * * *'` | 定时触发 |
| `release` | `types: [published]` | 发布事件 |
| `workflow_call` | — | 工作流复用 |

### Node.js 构建测试

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
      fail-fast: true              # 任一失败即停止全部

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm               # 自动缓存 ~/.npm

      - run: npm ci                # ci 比 install 更严格，锁定版本
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

### Python 构建测试

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip               # 自动缓存 pip

      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=./ --cov-report=xml
      - uses: codecov/codecov-action@v5
        with:
          file: ./coverage.xml
```

### Docker 构建推送

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write              # 推送到 ghcr.io 需要

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha      # GitHub Actions cache
          cache-to: type=gha,mode=max
```

### 部署到云平台

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment:
      name: production
      url: https://example.com

    # OIDC 认证（推荐替代静态密钥）
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/deploy-role
          aws-region: us-east-1

      - run: |
          echo "Deploy steps here"
          # deploy.sh
```

### 多 job 依赖编排

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint                    # 依赖 lint 完成
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test

  deploy:
    runs-on: ubuntu-latest
    needs: [lint, test]           # 依赖多个 job
    if: github.ref == 'refs/heads/main'
    steps:
      - run: echo "Deploy"
```

### 矩阵构建（多维度）

```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: [18, 20]
        include:                   # 额外组合
          - os: ubuntu-latest
            node: 22
        exclude:                   # 排除组合
          - os: windows-latest
            node: 18
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci && npm test
```

### Artifact 传递

```yaml
jobs:
  build:
    steps:
      - run: mkdir dist && echo "build output" > dist/output.txt
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 7        # 设置保留期

  test:
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/
      - run: cat dist/output.txt
```

### 条件执行

```yaml
steps:
  # 按分支条件
  - if: github.ref == 'refs/heads/main'
    run: echo "on main"

  # 按 PR 标签
  - if: contains(github.event.pull_request.labels.*.name, 'safe-to-deploy')
    run: echo "deploy"

  # 按文件变更路径
  - if: steps.changed-files.outputs.any_changed == 'true'
    run: echo "files changed"

  # 失败时仍执行
  - if: always()
    run: echo "always run"

  # 前一步失败时执行
  - if: failure()
    run: echo "previous step failed"
```

### Reusable Workflow

```yaml
# .github/workflows/ci.yml（被调用方）
on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      NPM_TOKEN:
        required: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

```yaml
# .github/workflows/main.yml（调用方）
jobs:
  call-ci:
    uses: ./.github/workflows/ci.yml
    with:
      node-version: '20'
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## GitLab CI

### 基础 pipeline 骨架

```yaml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  key: $CI_COMMIT_REF_SLUG
  paths:
    - .cache/pip/

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

### Node.js 构建测试

```yaml
image: node:20-alpine

cache:
  key: $CI_COMMIT_REF_SLUG
  paths:
    - node_modules/

before_script:
  - npm ci

lint:
  stage: lint
  script:
    - npm run lint

test:
  stage: test
  script:
    - npm test
  coverage: '/All files\s*\|\s*(\d+\.\d+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 7 days
```

### Docker 构建推送

```yaml
docker-build:
  stage: build
  image: docker:27-cli
  services:
    - docker:27-dind                     # Docker-in-Docker

  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""

  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY

  script:
    - docker buildx create --use
    - docker buildx build
        --cache-from type=registry,ref=$CI_REGISTRY_IMAGE:cache
        --cache-to type=registry,ref=$CI_REGISTRY_IMAGE:cache,mode=max
        --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
        --tag $CI_REGISTRY_IMAGE:latest
        --push .
```

### 多 job 依赖（needs）

```yaml
lint:
  stage: lint
  script: npm run lint

test:
  stage: test
  script: npm test

build:
  stage: build
  needs: [lint, test]            # 依赖 lint 和 test，无需等整个 stage
  script: npm run build

deploy:
  stage: deploy
  needs: [build]
  script: echo "deploy"
  environment: production
  only:
    - main
```

### Rules 条件控制

```yaml
job:
  rules:
    # 只在 main 分支或 MR 时运行
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

    # 按文件路径过滤
    - changes:
        - src/**/*
        - Dockerfile
      when: always

    # 定时任务跳过
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: never
```

### 手动部署 + 审批

```yaml
deploy-staging:
  stage: deploy
  script: echo "Deploy to staging"
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

deploy-production:
  stage: deploy
  script: echo "Deploy to production"
  environment:
    name: production
    url: https://example.com
  when: manual                     # 手动触发
  only:
    - main
```

### Includes（配置复用）

```yaml
# .gitlab-ci.yml
include:
  - local: ci/lint.yml
  - local: ci/test.yml
  - template: SAST.gitlab-ci.yml  # 使用 GitLab 官方模板
```

```yaml
# ci/lint.yml（被引入文件）
lint-eslint:
  stage: lint
  image: node:20-alpine
  script:
    - npm ci
    - npm run lint
```

---

## 安全配置参考

### GitHub Actions 权限最小化

| 场景 | 所需 permissions |
|------|-----------------|
| 只读代码 | `contents: read` |
| 创建 PR 评论 | `contents: read`, `issues: write` |
| 推送到容器注册表 | `contents: read`, `packages: write` |
| 部署（OIDC） | `contents: read`, `id-token: write` |
| 创建 Release | `contents: write` |

### 常见 Secrets 命名

| Secret 名 | 用途 | 建议作用域 |
|-----------|------|-----------|
| `DOCKER_USERNAME` / `DOCKER_PASSWORD` | Docker Registry 登录 | repository |
| `PRODUCTION_SSH_KEY` | 生产服务器 SSH | environment: production |
| `CLOUD_PROVIDER_TOKEN` | 云平台 API Token | environment |
| `NPM_TOKEN` | NPM 发布 Token | repository |

### 禁止模式（🚫 常见错误）

```yaml
# 🚫 禁止：硬编码密钥
- run: curl -H "Authorization: Bearer xxxxx" ...

# ✅ 正确：使用 Secrets
- run: curl -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" ...

# 🚫 禁止：pull_request_target 直接 checkout PR
on: pull_request_target
jobs:
  build:
    steps:
      - uses: actions/checkout@v4    # 会 checkout PR 的代码！
      - run: npm ci && npm test       # PR 开发者可篡改脚本

# ✅ 安全：仅用 pull_request_target 做 metadata 操作
on: pull_request_target
jobs:
  label:
    steps:
      - uses: actions/labeler@v5     # 只读 PR metadata，不 checkout
```
