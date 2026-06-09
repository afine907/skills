---
name: load-testing
description: |
  【压力测试】设计和执行负载测试方案，包含测试场景设计、压测脚本生成、性能指标分析、瓶颈定位。

  触发时机：
  - 用户要求"压力测试"、"性能测试"、"压测"
  - 上线前需要评估系统容量
  - 性能优化需要数据支撑

  支持 JMeter/K6/Locust 脚本生成。
category: operations
---

# Load Testing — 压力测试技能

设计负载测试方案，生成压测脚本，分析性能瓶颈。


## Goal

设计和执行负载测试方案，包含测试场景设计、压测脚本生成、性能指标分析、瓶颈定位

## Trigger

- 用户要求"压力测试"、"性能测试"、"压测"
  - 上线前需要评估系统容量
  - 性能优化需要数据支撑

## 工作流程

```
需求分析 → 场景设计 → 工具选择 → 脚本生成 → 执行监控 → 结果分析 → 瓶颈定位
   │          │          │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼          ▼          ▼
 问诊问卷   用户模型   决策树     脚本模板   预热验证   指标分析   优化建议
 环境确认   负载模型   工具对比   数据配置   实时监控   阈值判断   优先级排序
```

### Step 1: 需求分析（Intake 问卷）

向用户确认以下关键信息：

| 问题 | 选项 | 影响 |
|------|------|------|
| 目标系统类型？ | REST API / GraphQL / WebSocket / gRPC / 混合 | 决定协议和工具 |
| 认证方式？ | 无 / API Key / JWT / OAuth2 / Session | 决定脚本认证逻辑 |
| 预期并发用户数？ | <100 / 100-1000 / 1000-10000 / >10000 | 决定工具和执行方式 |
| 预算限制？ | 免费 / <$10 / $10-100 / >$100 | 决定工具选择 |
| 测试环境？ | 本地 / 独立测试环境 / 预发布环境 | 决定网络和隔离策略 |
| 测试目标？ | 基准 / 容量 / 压力 / 浸泡 / 尖峰 | 决定负载模型 |
| 目标性能指标？ | P95<500ms / TPS>1000 / 错误率<1% | 决定断言阈值 |

### Step 2: 场景设计
- 设计用户行为模型（浏览→搜索→下单→支付）
- 确定负载模型（恒定/阶梯/脉冲）
- 设置断言阈值（P95<500ms, 错误率<1%, TPS>1000）

### Step 3: 工具选择

根据 intake 信息使用以下决策树选择工具：

```
目标系统协议？
    │
    ├── HTTP/REST API
    │     │
    │     ├── 团队熟悉 JavaScript？ ──是──▶ K6（推荐）
    │     │       │
    │     │       否
    │     │       ▼
    │     └── 团队熟悉 Python？ ──是──▶ Locust
    │             │
    │             否
    │             ▼
    │         JMeter（GUI 友好）
    │
    ├── WebSocket/gRPC
    │     └── K6（原生支持多种协议）
    │
    └── 混合协议
          └── K6 + 自定义扩展
```

| 工具 | 语言 | 学习曲线 | 分布式 | 适用场景 |
|------|------|---------|--------|---------|
| K6 | JavaScript | 低 | 云端免费 | HTTP API、CI/CD 集成 |
| Locust | Python | 低 | 多节点 | 复杂业务逻辑、Python 团队 |
| JMeter | XML/Java | 中 | 多节点 | 企业级、GUI 需求 |
| k6 Cloud | JavaScript | 低 | 托管 | 大规模、预算充足 |

### Step 4: 脚本生成
- 生成测试脚本（含认证、思考时间、数据驱动）
- 配置环境变量和测试数据

### Step 5: 执行与监控
- 预热测试（验证脚本正确性）
- 正式执行（监控服务端指标）
- 实时观察错误率和响应时间

### Step 6: 结果分析
- 分析性能指标（TPS、P50/P95/P99、错误率）
- 定位瓶颈（CPU/内存/IO/数据库/网络）
- 输出优化建议

## 测试类型

| 类型 | 目标 | 并发数 | 持续时间 |
|------|------|--------|----------|
| 基准测试 | 建立性能基线 | 1-10 | 5min |
| 负载测试 | 验证预期负载 | 预期并发 | 30min |
| 压力测试 | 找到系统极限 | 逐步增加 | 30-60min |
| 浸泡测试 | 检测内存泄漏 | 预期并发 | 4-24h |
| 尖峰测试 | 验证突发流量 | 突发峰值 | 5-10min |

## 测试场景设计

### 场景模板

```yaml
test_scenario:
  name: {场景名称}
  description: {场景描述}
  
  # 负载模型
  load_model:
    type: {constant/ramp-up/step/spike}
    target_vus: {目标虚拟用户数}
    ramp_up_time: {爬坡时间}
    hold_time: {持续时间}
    ramp_down_time: {下降时间}
  
  # 测试接口
  endpoints:
    - name: {接口名称}
      method: {GET/POST/PUT/DELETE}
      url: {接口地址}
      headers:
        Content-Type: application/json
        Authorization: Bearer ${token}
      body: |
        {
          "field": "${dynamic_value}"
        }
      think_time: {思考时间(秒)}
      weight: {权重(%)}
  
  # 断言
  assertions:
    - type: response_time
      condition: p95 < 500ms
    - type: error_rate
      condition: < 1%
    - type: throughput
      condition: > 1000 req/s
  
  # 测试数据
  test_data:
    source: {csv/api/generated}
    file: {data.csv}
    strategy: {sequential/random/unique}
```

### 常见场景

| 场景 | 描述 | 关注指标 |
|------|------|----------|
| 秒杀抢购 | 瞬间高并发写入 | TPS、错误率、库存一致性 |
| 商品列表 | 高并发读取 | 响应时间、缓存命中率 |
| 下单支付 | 复杂业务流程 | 端到端延迟、事务成功率 |
| 文件上传 | 大文件传输 | 上传速度、内存使用 |
| 搜索查询 | 复杂查询 | 查询延迟、数据库负载 |

## 脚本生成

### K6 脚本模板

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const latency = new Trend('latency');

// 测试配置
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // 爬坡到 50 VU
    { duration: '5m', target: 50 },   // 保持 50 VU
    { duration: '2m', target: 100 },  // 爬坡到 100 VU
    { duration: '5m', target: 100 },  // 保持 100 VU
    { duration: '2m', target: 0 },    // 降到 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% 请求 < 500ms
    errors: ['rate<0.01'],             // 错误率 < 1%
  },
};

// 测试逻辑
export default function () {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.TOKEN}`,
    },
  };

  // 请求1: 获取列表
  const listRes = http.get('http://localhost:8000/api/v1/items', params);
  check(listRes, {
    'list status is 200': (r) => r.status === 200,
    'list has items': (r) => JSON.parse(r.body).data.length > 0,
  });
  errorRate.add(listRes.status !== 200);
  latency.add(listRes.timings.duration);

  sleep(1);

  // 请求2: 获取详情
  const itemId = JSON.parse(listRes.body).data[0].id;
  const detailRes = http.get(
    `http://localhost:8000/api/v1/items/${itemId}`,
    params
  );
  check(detailRes, {
    'detail status is 200': (r) => r.status === 200,
  });

  sleep(2);
}
```

### Locust 脚本模板

```python
from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """登录获取 token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def list_items(self):
        """获取列表（权重3）"""
        with self.client.get(
            "/api/v1/items",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def create_item(self):
        """创建资源（权重1）"""
        self.client.post(
            "/api/v1/items",
            headers=self.headers,
            json={
                "name": "test item",
                "description": "load test"
            }
        )
```

## 性能指标

### 关键指标

| 指标 | 含义 | 健康范围 |
|------|------|----------|
| TPS/QPS | 每秒事务/查询数 | 业务预期的 1.5-2 倍 |
| P50 响应时间 | 50% 请求的延迟 | < 200ms |
| P95 响应时间 | 95% 请求的延迟 | < 500ms |
| P99 响应时间 | 99% 请求的延迟 | < 1000ms |
| 错误率 | 失败请求占比 | < 0.1% |
| CPU 使用率 | 服务器 CPU | < 70% |
| 内存使用率 | 服务器内存 | < 80% |
| 数据库连接数 | 连接池使用 | < 80% |

### 瓶颈定位

| 现象 | 可能瓶颈 | 排查方向 |
|------|----------|----------|
| TPS 上不去，CPU 低 | IO 瓶颈 | 数据库慢查询、网络延迟 |
| TPS 上不去，CPU 高 | CPU 瓶颈 | 计算密集、GC 频繁 |
| 响应时间波动大 | 资源竞争 | 锁等待、连接池耗尽 |
| 错误率随并发上升 | 容量不足 | 连接数、队列溢出 |
| 内存持续增长 | 内存泄漏 | 对象未释放、缓存无限增长 |

## Edge Cases

- **目标系统不可达**
  - IF 网络不通 THEN: 先验证网络连通性（ping / telnet），确认防火墙规则
  - IF 认证 token 失效 THEN: 手动获取新 token，更新脚本中的 token 变量
  - IF 需要 VPN THEN: 确认 VPN 连接状态，从 VPN 内网发起测试

- **限流 API**
  - IF 目标有每 IP 限流 THEN: 设计多账号轮换策略（N 个测试账号轮流使用）
  - IF 限流阈值 < 100 req/min THEN: 降低并发到限流阈值以下，增加测试持续时间
  - IF 目标在负载均衡器后面 THEN: 从多个源 IP 发起请求，避免单 IP 限流
  - IF 无法绕过限流 THEN: 使用阶梯式增加（从限流阈值的 50% 开始，逐步增加）

- **成本控制**
  - IF 预算 < $10 THEN: 使用本地 K6/Locust，限制最大 50 VU，持续时间 < 10min
  - IF 预算 $10-100 THEN: 使用 K6 云端执行，限制 100 VU 上限，持续时间 < 30min
  - IF 预算 > $100 THEN: 可使用大规模云端执行，但仍需设置 VU 和时长上限
  - 始终设置: `max_vu_limit` 和 `max_duration` 防止意外超支

- **测试数据不足**
  - IF 需要大量唯一数据 THEN: 使用 Faker 生成动态数据（避免缓存命中）
  - IF 测试用户数 > 1000 THEN: 生成 CSV 测试数据文件，使用 data-driven 模式
  - IF 需要特定数据分布 THEN: 按比例生成（80% 读/20% 写、90% 普通用户/10% VIP）

- **非 HTTP 协议**
  - IF WebSocket THEN: 使用 K6 WebSocket 扩展或 Locust WebSocket 用户
  - IF gRPC THEN: 使用 K6 gRPC 协议支持或 ghz（专用 gRPC 压测工具）
  - IF MQTT THEN: 使用 MQTT 压测工具（如 mqtt-stresser）
  - IF 混合协议 THEN: 多工具并行，分别测试各协议端点

- **目标系统正在生产运行**
  - IF 无法使用独立测试环境 THEN: 在低峰期执行，限制负载不超过生产容量的 50%
  - IF 必须在生产测试 THEN: 仅做基准和轻量级负载测试，不做压力/浸泡测试
  - IF 数据会被污染 THEN: 使用测试前创建/测试后清理的策略，或隔离测试数据

## 不适用

**范围边界：** 本技能设计和执行负载测试，分析系统在压力下的表现。不负责容量规划（基础设施采购）、应用级代码性能分析（profiling）或安全渗透测试。

- 云端基础设施成本分析 → 使用 [cost-optimization](../cost-optimization/SKILL.md)
- 应用级代码性能分析 → 使用 performance-profiling
- 安全渗透测试 → 使用 [security-scan](../security-scan/SKILL.md)

### 适用场景矩阵

| 测试目标 | 推荐测试类型 | 推荐工具 | 推荐负载模型 | 关键指标 |
|---------|-------------|---------|-------------|---------|
| 建立性能基线 | 基准测试 | K6 | 恒定（预期并发） | P50/P95 响应时间 |
| 验证系统容量 | 负载测试 | K6/Locust | 阶梯递增 | TPS 上限、错误率拐点 |
| 找到系统极限 | 压力测试 | K6 | 阶梯递增（超过预期） | 系统崩溃点、恢复时间 |
| 检测内存泄漏 | 浸泡测试 | Locust | 恒定（预期并发 x 1.5） | 内存增长趋势 |
| 验证突发流量 | 尖峰测试 | K6 | 脉冲（0→峰值→0） | 峰值错误率、恢复时间 |
| CI/CD 集成 | 基准测试 | K6 | 恒定（小规模） | 与基线的偏差百分比 |

## 快速使用

```
# 设计压测方案
帮我为商品列表接口设计压测方案

# 生成 K6 脚本
为以下接口生成 K6 压测脚本：[粘贴接口文档]

# 分析压测结果
分析以下压测结果，找出瓶颈：[粘贴结果]

# 制定容量规划
根据业务量（日活100万）制定服务器容量规划
```

## 参考资料

- K6 脚本模板: [references/k6-templates.md](references/k6-templates.md)
- 性能指标参考: [references/metrics.md](references/metrics.md)
