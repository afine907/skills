# Prompt CI/CD 流水线配置

## GitHub Actions 配置

### 基础流水线

```yaml
name: Prompt Regression Tests

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'evals/**'

concurrency:
  group: prompt-regression-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint prompt templates
        run: python prompts/scripts/lint_prompts.py prompts/

  regression:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        prompt_type: [system, templates]
    steps:
      - uses: actions/checkout@v4
      - name: Run regression tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python prompts/scripts/run_evals.py \
            --prompt-dir prompts/${{ matrix.prompt_type }}/ \
            --eval-set evals/test-cases.json \
            --baseline evals/baselines/current.json \
            --threshold 0.85 \
            --runs 5

  security:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python prompts/scripts/run_evals.py \
            --eval-set evals/security/injection-tests.json \
            --threshold 0.95

  compare:
    needs: [regression, security]
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - name: Compare with baseline
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python prompts/scripts/compare_versions.py \
            --current evals/results/current.json \
            --baseline evals/baselines/current.json \
            --output evals/regressions/${{ github.sha }}.json
```

### 关键配置说明

**Path-scoped triggers：**
```yaml
on:
  pull_request:
    paths:
      - 'prompts/**'  # 仅 Prompt 文件变更触发
```
只有修改了 prompts/ 目录下的文件才会触发流水线，避免无关 PR（如 CSS 修改）浪费 Judge Token。

**Concurrency control：**
```yaml
concurrency:
  group: prompt-regression-${{ github.head_ref }}
  cancel-in-progress: true
```
同一 PR 的多次 push 只运行最新的，避免资源浪费。

**Matrix sharding：**
```yaml
strategy:
  matrix:
    prompt_type: [system, templates]
```
按 Prompt 类型分片并行运行，加速流水线。

## GitLab CI 配置

```yaml
prompt-regression:
  stage: test
  rules:
    - changes:
        - prompts/**/*
        - evals/**/*
  script:
    - python prompts/scripts/lint_prompts.py prompts/
    - python prompts/scripts/run_evals.py
        --prompt-dir prompts/
        --eval-set evals/test-cases.json
        --baseline evals/baselines/current.json
        --threshold 0.85
  artifacts:
    paths:
      - evals/results/
      - evals/regressions/
```

## Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: prompt-lint
        name: Lint prompt templates
        entry: python prompts/scripts/lint_prompts.py
        language: system
        files: 'prompts/.*\.md$'
        pass_filenames: true
```

## 部署阶段配置

### 灰度发布

```yaml
deploy-staging:
  needs: [regression, security, compare]
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy to staging
      run: |
        # 部署新 Prompt 版本到灰度环境
        python prompts/scripts/deploy.py \
          --version ${{ github.sha }} \
          --environment staging \
          --traffic-percent 5
    - name: Monitor quality
      run: |
        # 监控灰度环境的质量指标
        python prompts/scripts/monitor.py \
          --duration 30m \
          --threshold 0.85
```

### 全量发布

```yaml
deploy-production:
  needs: deploy-staging
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Promote to production
      run: |
        python prompts/scripts/deploy.py \
          --version ${{ github.sha }} \
          --environment production \
          --traffic-percent 100
```

### 回滚

```yaml
rollback:
  runs-on: ubuntu-latest
  if: failure()
  steps:
    - name: Rollback to previous version
      run: |
        python prompts/scripts/deploy.py \
          --version ${{ github.event.before }} \
          --environment production \
          --traffic-percent 100
```
