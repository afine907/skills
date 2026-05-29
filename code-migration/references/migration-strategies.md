# Migration Strategies Reference

## 策略对比

| 策略 | 风险 | 停机时间 | 复杂度 | 适用场景 |
|------|------|----------|--------|----------|
| 绞杀者模式 | 低 | 无 | 高 | 大型系统、持续交付 |
| 大爆炸模式 | 高 | 长 | 低 | 小型项目、差异大 |
| 并行运行模式 | 低 | 无 | 中 | 高可靠性要求 |

## 绞杀者模式详解

### 架构图

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   / 负载均衡器   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ 新服务 A  │  │ 新服务 B  │  │ 旧系统    │
        │ (已迁移)  │  │ (迁移中)  │  │ (待迁移)  │
        └──────────┘  └──────────┘  └──────────┘
```

### 实施步骤

```yaml
阶段 1: 准备
  - 分析系统边界
  - 识别迁移单元
  - 建立路由层
  - 设置监控

阶段 2: 迁移
  - 选择第一个迁移单元
  - 开发新服务
  - 配置路由规则
  - 测试验证
  - 切流上线

阶段 3: 清理
  - 下线旧服务
  - 清理代码
  - 更新文档
  - 总结复盘
```

### 路由配置示例

```nginx
# Nginx 路由配置
upstream legacy {
    server legacy-app:8080;
}

upstream new_service_a {
    server new-service-a:8080;
}

upstream new_service_b {
    server new-service-b:8080;
}

server {
    listen 80;

    # 已迁移的服务
    location /api/users {
        proxy_pass http://new_service_a;
    }

    location /api/orders {
        proxy_pass http://new_service_b;
    }

    # 未迁移的服务
    location /api/ {
        proxy_pass http://legacy;
    }
}
```

## 大爆炸模式详解

### 执行清单

```markdown
## 迁移前
- [ ] 完成所有代码迁移
- [ ] 完成所有测试
- [ ] 准备回滚方案
- [ ] 通知所有相关方
- [ ] 选择低峰期执行

## 迁移中
- [ ] 停止旧系统
- [ ] 执行数据库迁移
- [ ] 部署新系统
- [ ] 运行冒烟测试
- [ ] 验证核心功能

## 迁移后
- [ ] 监控系统指标
- [ ] 处理用户反馈
- [ ] 记录问题和解决方案
```

### 回滚脚本

```bash
#!/bin/bash
# rollback.sh

echo "Starting rollback..."

# 1. 停止新系统
docker-compose -f docker-compose.new.yml down

# 2. 恢复数据库
psql -U postgres -d mydb < backup/rollback.sql

# 3. 启动旧系统
docker-compose -f docker-compose.old.yml up -d

# 4. 验证
curl -f http://localhost:8080/health || exit 1

echo "Rollback completed successfully"
```

## 并行运行模式详解

### 比对系统

```python
class ParallelRunner:
    def __init__(self, old_system, new_system):
        self.old_system = old_system
        self.new_system = new_system
    
    async def execute(self, request):
        # 并行执行
        old_task = asyncio.create_task(self.old_system.process(request))
        new_task = asyncio.create_task(self.new_system.process(request))
        
        old_result = await old_task
        new_result = await new_task
        
        # 比对结果
        is_consistent = self.compare(old_result, new_result)
        
        # 记录差异
        if not is_consistent:
            self.log_difference(request, old_result, new_result)
        
        # 返回旧系统结果（迁移期间）
        return old_result
    
    def compare(self, old_result, new_result):
        # 自定义比对逻辑
        return old_result == new_result
```

### 流量镜像

```yaml
# Istio 流量镜像配置
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
    - my-service
  http:
    - route:
        - destination:
            host: my-service-v1
            subset: stable
          weight: 100
      mirror:
        host: my-service-v2
        subset: canary
      mirrorPercentage:
        value: 100.0
```

## 渐进式迁移检查清单

### 代码迁移

```markdown
## 准备阶段
- [ ] 代码分析工具运行完成
- [ ] 依赖兼容性检查通过
- [ ] 测试覆盖率达标（>80%）
- [ ] 迁移计划文档编写完成
- [ ] 团队培训完成

## 执行阶段
- [ ] 每个模块迁移后测试通过
- [ ] 代码审查完成
- [ ] 集成测试通过
- [ ] 性能测试无下降
- [ ] 安全扫描通过

## 收尾阶段
- [ ] 旧代码清理完成
- [ ] 文档更新完成
- [ ] 监控配置更新
- [ ] 团队复盘完成
```

### 数据库迁移

```markdown
## 准备阶段
- [ ] 数据备份完成
- [ ] 迁移脚本测试通过
- [ ] 回滚脚本准备就绪
- [ ] 性能影响评估完成
- [ ] 停机时间窗口确认

## 执行阶段
- [ ] 执行迁移脚本
- [ ] 数据一致性验证
- [ ] 应用层适配完成
- [ ] 功能测试通过

## 收尾阶段
- [ ] 旧表/字段清理
- [ ] 索引优化
- [ ] 性能监控确认
- [ ] 文档更新
```

## 风险评估矩阵

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 数据丢失 | 低 | 高 | 完整备份、并行验证 |
| 性能下降 | 中 | 中 | 性能测试、渐进式迁移 |
| 功能缺失 | 中 | 高 | 完整测试、特性对比 |
| 第三方依赖 | 高 | 中 | 提前评估、寻找替代 |
| 团队技能 | 中 | 中 | 培训、外部支持 |

## 迁移工具推荐

### 代码迁移

| 工具 | 用途 | 语言 |
|------|------|------|
| 2to3 | Python 2→3 | Python |
| futurize | 渐进式 Python 迁移 | Python |
| ts-migrate | JS→TS 迁移 | JavaScript |
| jscodeshift | 代码转换 | JavaScript |
| ng-migrate | Angular 迁移 | TypeScript |

### 数据库迁移

| 工具 | 用途 | 支持数据库 |
|------|------|------------|
| Prisma | Schema 迁移 | PostgreSQL, MySQL, SQLite |
| Alembic | 数据库迁移 | SQLAlchemy 支持的数据库 |
| Flyway | 数据库迁移 | 多种数据库 |
| Knex.js | 数据库迁移 | PostgreSQL, MySQL, SQLite |
| golang-migrate | 数据库迁移 | 多种数据库 |

### 依赖分析

| 工具 | 用途 |
|------|------|
| npm-check | 检查 npm 依赖 |
| pipdeptree | Python 依赖树 |
| depcheck | 未使用依赖检测 |
| retire.js | 安全漏洞检测 |

## 迁移后优化

### 性能优化

```yaml
检查清单:
  - 数据库查询优化
  - 缓存策略调整
  - 代码热点优化
  - 资源配置调整
  - CDN 配置更新
```

### 监控配置

```yaml
监控项:
  - 错误率
  - 响应时间
  - 资源使用率
  - 数据库性能
  - 用户行为指标

告警规则:
  - 错误率 > 1%
  - P99 延迟 > 500ms
  - CPU 使用率 > 80%
  - 内存使用率 > 90%
```
