# 技术方案模板

> 复制此模板，替换 `{占位符}` 内容即可使用。

---

# {功能名称} 技术方案

> 作者: {姓名}  
> 日期: {YYYY-MM-DD}  
> 状态: 草稿 / 评审中 / 已通过  
> 版本: v1.0

## 一、需求概述

### 1.1 业务背景

{2-3 句话描述业务背景和动机}

### 1.2 核心需求

1. {需求点1}
2. {需求点2}
3. {需求点3}

### 1.3 约束条件

- **性能**: {QPS 目标}，{延迟目标}
- **数据**: {数据规模}，{增长预期}
- **兼容**: {需要兼容的系统}
- **时间**: {截止日期}

## 二、方案设计

### 2.1 整体架构

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Client  │────▶│  API GW  │────▶│ Service │
└─────────┘     └─────────┘     └────┬────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              ┌─────────┐     ┌─────────┐     ┌─────────┐
              │  Cache   │     │   DB    │     │   MQ    │
              └─────────┘     └─────────┘     └─────────┘
```

### 2.2 核心流程

```
用户请求 → 参数校验 → 业务处理 → 数据持久化 → 返回响应
```

### 2.3 模块划分

| 模块 | 职责 | 接口 |
|------|------|------|
| {模块A} | {职责} | {对外接口} |
| {模块B} | {职责} | {对外接口} |

### 2.4 接口定义

**{接口名称}**

```
POST /api/v1/{resource}
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "field": "value"
}

Response (200):
{
  "data": {}
}

Error (400):
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "..."
  }
}
```

### 2.5 数据模型

```sql
CREATE TABLE {table_name} (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    -- 业务字段
    status      TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-正常, 1-删除',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{表说明}';
```

## 三、技术选型

| 组件 | 选型 | 理由 | 风险 |
|------|------|------|------|
| {组件} | {选型} | {为什么选这个} | {风险} |

## 四、非功能需求

### 4.1 性能

- 读: {延迟目标}，通过 {方案} 实现
- 写: {延迟目标}，通过 {方案} 实现

### 4.2 可用性

- SLA: {目标}
- 降级: {策略}

### 4.3 监控

- 指标: {关键指标}
- 告警: {告警规则}

## 五、风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| {风险} | 高/中/低 | 高/中/低 | {措施} |

## 六、里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 设计评审 | {日期} | 本文档 |
| 开发 | {日期} | 代码 |
| 测试 | {日期} | 测试报告 |
| 上线 | {日期} | 灰度发布 |

## 七、待确认

- [ ] {待确认项}
