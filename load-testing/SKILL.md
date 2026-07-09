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
需求分析 → 场景设计 → 脚本生成 → 执行监控 → 结果分析 → 瓶颈定位
```

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

## Example

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
