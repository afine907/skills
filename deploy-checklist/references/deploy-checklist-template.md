# 部署检查清单模板

本文档提供各类项目的部署检查清单模板，供 `/deploy-checklist` 技能生成清单时参考。根据项目类型和变更内容选择适用的检查项。

## 一、通用检查项（所有项目适用）

### 发布前准备

- [ ] 代码已合并到目标分支（main/master/release）
- [ ] CI/CD 流水线全部通过（构建、测试、Lint）
- [ ] Code Review 已完成并获得批准
- [ ] 版本号已更新（遵循语义化版本）
- [ ] CHANGELOG 已更新
- [ ] 发布说明已准备

### 配置与环境

- [ ] 环境变量差异已核对（staging vs production）
- [ ] 新增配置项有默认值或兼容处理
- [ ] 敏感信息通过密钥管理服务注入，未硬编码
- [ ] Feature Flag 已配置（如适用）

### 监控与告警

- [ ] 关键接口已添加监控指标（成功率、延迟 P99）
- [ ] 告警阈值已配置并验证
- [ ] 日志级别已确认（生产环境无 DEBUG 日志）
- [ ] 健康检查端点可用

### 部署策略

- [ ] 部署步骤已文档化
- [ ] 回滚方案已确认并测试
- [ ] 灰度/金丝雀发布策略已配置（如适用）
- [ ] 停机窗口已通知相关方（如需停机）

### 上线后验证

- [ ] 健康检查端点返回 200
- [ ] 核心功能冒烟测试通过
- [ ] 错误率无异常上升（对比上线前 30 分钟）
- [ ] 响应延迟无显著增加
- [ ] 日志无异常错误

---

## 二、Web 后端项目

### 接口兼容性

- [ ] API 变更是否向后兼容
- [ ] 新增接口是否有文档（Swagger/OpenAPI）
- [ ] 废弃接口是否已标记并通知调用方
- [ ] 接口返回格式是否一致

### 数据库

- [ ] 迁移脚本已在 staging 环境执行并验证
- [ ] 反向迁移（rollback）脚本已就绪
- [ ] 大表 DDL 是否使用 online 方式（如 `pt-online-schema-change`）
- [ ] 索引变更已评估对写入性能的影响
- [ ] 数据备份已完成

### 连接与资源

- [ ] 数据库连接池配置已确认
- [ ] 缓存失效策略已配置（Redis/Memcached）
- [ ] 消息队列消费者数量已调整
- [ ] 外部服务调用超时已配置

```bash
# 验证数据库迁移
python manage.py migrate --plan  # Django
alembic upgrade head --sql       # SQLAlchemy
flyway info                      # Flyway
```

---

## 三、Web 前端项目

### 构建与资源

- [ ] 构建产物大小与上次对比无异常增长（>20% 需确认）
- [ ] Source Map 已生成但未部署到公网
- [ ] 静态资源文件名包含 hash（缓存失效）
- [ ] CDN 缓存已刷新或配置了合适的 Cache-Control

### 兼容性

- [ ] 浏览器兼容性已确认（目标浏览器列表）
- [ ] 移动端适配已验证
- [ ] 第三方 SDK 版本兼容性已确认

### SEO 与性能

- [ ] meta 标签和 OG 标签已更新
- [ ] Core Web Vitals 无显著退化
- [ ] 首屏加载时间在可接受范围内

```bash
# 构建产物分析
npm run build -- --stats
npx webpack-bundle-analyzer stats.json

# CDN 缓存刷新（以 Cloudflare 为例）
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -d '{"purge_everything":true}'
```

---

## 四、移动端项目

### 版本与兼容

- [ ] 最低支持版本已确认（Android API Level / iOS Version）
- [ ] 热更新方案已准备（如 CodePush）
- [ ] 强制升级策略已配置
- [ ] 新权限申请已在 manifest/Info.plist 中声明

### 发布渠道

- [ ] 应用商店审核材料已准备（截图、描述、隐私政策）
- [ ] 灰度发布比例已设定
- [ ] 回退方案：热更新可回退，应用商店版本需等审核

---

## 五、微服务项目

### 服务间通信

- [ ] 服务发现配置已更新
- [ ] 服务间 API 契约兼容性已确认
- [ ] 调用链 tracing 已配置
- [ ] 熔断/降级策略已配置

### 部署顺序

- [ ] 服务部署顺序已确认（被依赖方先部署）
- [ ] 滚动更新策略已配置（maxUnavailable / maxSurge）
- [ ] Pod Disruption Budget 已设置

```yaml
# Kubernetes 滚动更新示例
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  minReadySeconds: 30
```

---

## 六、数据/ETL 项目

### 数据源与目标

- [ ] 数据源连接可用性已确认
- [ ] 输出目标写入权限已验证
- [ ] 数据量预估与资源匹配

### 任务调度

- [ ] 任务依赖顺序正确
- [ ] 幂等性已保证（重跑不会产生重复数据）
- [ ] 失败重试策略已配置
- [ ] 数据质量检查点已设置

---

## 七、基础库/SDK 项目

### 版本管理

- [ ] 遵循语义化版本（MAJOR.MINOR.PATCH）
- [ ] Breaking Change 已在 MAJOR 版本中标记
- [ ] 废弃 API 已标记 `@deprecated` 并提供替代方案
- [ ] 向下兼容性已确认

### 发布流程

- [ ] 包已发布到对应 registry（npm/PyPI/Maven）
- [ ] Release Notes 已发布
- [ ] 文档已更新

---

## 八、Hotfix 专项检查

紧急修复时使用最小化清单：

- [ ] 修复代码已确认无误（至少一人 Review）
- [ ] 回滚方案就绪（保留上一个版本的镜像/包）
- [ ] 监控重点关注相关指标
- [ ] 部署后立即验证修复效果
- [ ] 后续补充完整检查项

---

## 九、首次部署专项

首次部署到新环境时额外确认：

- [ ] 域名 DNS 已配置
- [ ] SSL/TLS 证书已签发并配置
- [ ] 生产环境资源已就绪（数据库、缓存、存储、队列）
- [ ] 监控和告警已配置
- [ ] 备份策略已设置并验证
- [ ] 安全基线已配置（防火墙、安全组、WAF）
- [ ] 运维文档已交付

---

## 部署时间线模板

```
T-60min  最终确认检查清单，通知相关人员
T-30min  开始部署流程
T-15min  执行数据库迁移（如有）
T-10min  部署应用
T-5min   健康检查通过
T-0      开始灰度（10% -> 50% -> 100%）
T+15min  确认核心指标正常
T+30min  确认部署完成，通知相关方
T+60min  监控无异常，收工
```
