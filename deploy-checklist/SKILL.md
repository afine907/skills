---
name: deploy-checklist
category: operations
description: |
  Generate pre-deployment checklist based on project type and environment. Covers database, config, monitoring, backup, and rollback.
  Use when:
  - User says "部署前检查"、"发版检查"、"deploy checklist"、"预发布检查"
  - Before a production deployment
  - User is about to cut a release

  Do NOT use: when user has already deployed and needs post-incident troubleshooting and runbook guidance.
---

# Deploy Checklist — 部署检查清单 Agent

项目类型 + 变更描述 → 预发布检查清单。

## 工作流程

```
识别项目类型 → 分析变更 → 生成检查清单 → 逐项确认
```

## Step 1: 识别项目类型

根据用户描述或代码仓库特征确定项目类型：

| 项目类型 | 特征识别 |
|----------|----------|
| **Web 后端** | Spring Boot, Django, FastAPI, Flask, Gin, Express, NestJS |
| **Web 前端** | React, Vue, Angular, Next.js, Nuxt |
| **移动端** | Android, iOS, React Native, Flutter |
| **微服务** | docker-compose.yml, Kubernetes 配置, service mesh |
| **数据/ETL** | Spark, Airflow, data pipeline 脚本 |
| **基础库/SDK** | npm package, PyPI package, maven artifact |
| **静态站点** | Hugo, Jekyll, Astro, 纯 HTML |

**如果无法识别**：让用户选择项目类型。

## Step 2: 分析变更

从用户描述或 git 变更中提取关键信息：

```bash
# 获取最近 commit 了解变更内容
git log --oneline -10

# 获取提交数，动态决定 diff 范围
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
DIFF_RANGE="HEAD~5"
if [ "$COMMIT_COUNT" -lt 5 ]; then
  DIFF_RANGE="HEAD~$COMMIT_COUNT"
fi

# 检查是否有数据库迁移
git diff --name-only "$DIFF_RANGE" | grep -iE "migration|migrate|schema|sql|alembic"

# 检查依赖变更
git diff "$DIFF_RANGE" -- package.json requirements.txt go.mod 2>/dev/null

# 检查配置变更
git diff "$DIFF_RANGE" -- .env.example config/*.yml 2>/dev/null
```

## Step 3: 生成检查清单

按领域分块生成，只包含与项目类型和变更相关的检查项：

### 通用检查

- [ ] 代码已合并到目标分支
- [ ] CI/CD 流水线通过
- [ ] Code Review 已完成
- [ ] 版本号已更新
- [ ] CHANGELOG 已更新

### 数据库变更检查

仅在检测到 migration/schema 变更时包含：

- [ ] 迁移脚本已测试（staging 环境执行过）
- [ ] 反向迁移（rollback）脚本已就绪
- [ ] 大表迁移确认锁表影响（ALTER TABLE 是否 online DDL）
- [ ] 数据备份已完成
- [ ] 迁移顺序：先 schema 后数据

### 配置检查

- [ ] 环境变量差异核对（staging vs production）
- [ ] 敏感信息未硬编码（密码、token、密钥）
- [ ] 新配置项有默认值或兼容处理
- [ ] 特性开关（feature flag）已配置

### 监控与可观测性

- [ ] 关键接口已添加监控（成功率、延迟）
- [ ] 新增依赖/服务已添加到健康检查
- [ ] 告警阈值已配置
- [ ] 日志级别已确认（debug level 是否关闭）

### 部署与回滚

- [ ] 部署步骤已文档化
- [ ] 回滚方案已确认
- [ ] 灰度发布策略（如有）已配置
- [ ] 停机窗口（如需）已通知相关方

### 项目特定检查

| 项目类型 | 额外检查项 |
|----------|-----------|
| Web 后端 | 接口兼容性（是否改 API 签名）、数据库连接池配置、缓存失效策略 |
| Web 前端 | 构建产物大小对比、CDN 缓存刷新、SEO/OG 标签、资源加载性能 |
| 移动端 | 版本兼容性（API level / iOS version）、强制升级策略 |
| 微服务 | 服务发现配置、调用链 tracing、服务间契约兼容性 |
| 数据/ETL | 数据源可用性、输出目标权限、任务依赖顺序 |
| 基础库/SDK | 语义化版本、废弃 API 标记、向下兼容性确认 |

### 上线后验证

- [ ] 健康检查端点返回 200
- [ ] 核心功能冒烟测试通过
- [ ] 错误率无上升（对比上线前 30 分钟）
- [ ] 延迟无显著增加
- [ ] 日志无异常错误

## Step 4: 交互式确认

生成清单后逐项提醒用户确认：

```
已生成部署检查清单，共 <N> 项。
建议逐项确认后部署。如某项不适用，请标注 N/A。
```

**对于高风险项**（数据库迁移、配置变更、Breaking Change）：
使用 ⚠️ 标记并额外提示。

## Edge Cases

### 首次部署
```
首次部署到生产环境，额外确认：
- [ ] 域名 DNS 已配置
- [ ] SSL 证书已签发
- [ ] 生产环境资源（DB、缓存、存储）已就绪
- [ ] 监控和告警已配置
- [ ] 备份策略已设置
```

### 紧急修复（hotfix）
```
紧急热修复部署，最小化检查清单：
- [ ] 修复的代码确认无误
- [ ] 回滚方案就绪（保留上一个版本的镜像/包）
- [ ] 监控重点关注相关指标
- [ ] 部署后立即验证
常规检查项可在部署后补充。
```

### 无 git 仓库
用户直接提供项目类型描述时，跳过 git 分析步骤，直接基于项目类型生成通用清单。
