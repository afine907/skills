---
name: microservice-patterns
description: |
  【微服务模式】微服务架构设计模式，包含服务拆分、通信方式、数据管理、服务发现、熔断降级、链路追踪。

  触发时机：
  - 用户要求"微服务架构"、"服务拆分"
  - 需要设计分布式系统
  - 需要实现服务治理

  提供模式选择建议和代码实现。
category: development
user-invocable: false
---

# Microservice Patterns — 微服务设计模式

微服务架构的核心设计模式和最佳实践。


## Goal

微服务架构设计模式，包含服务拆分、通信方式、数据管理、服务发现、熔断降级、链路追踪

## Trigger

- 用户要求"微服务架构"、"服务拆分"
  - 需要设计分布式系统
  - 需要实现服务治理

## 工作流程

### Step 1: 领域分析 (Domain Analysis)

使用 DDD 限界上下文映射，识别核心域/支撑域/通用域：
- 列出所有业务能力（用户管理、订单处理、支付、库存...）
- 按业务领域分组，识别上下文边界
- 标注核心域（竞争力来源）、支撑域（辅助核心域）、通用域（可外购）

**成功标准**：完成限界上下文图，明确每个上下文的职责范围。

### Step 2: 服务边界定义 (Service Boundary)

为每个限界上下文定义服务：
- 单一职责：每个服务只负责一个业务领域
- 独立部署：服务可独立构建、测试、部署
- 明确 API：列出每个服务的 REST/gRPC 接口

### Step 3: 通信模式选择 (Communication)

| 交互类型 | 推荐方式 | 原因 |
|----------|----------|------|
| 实时查询（用户看订单详情） | 同步 HTTP/gRPC | 需要立即返回结果 |
| 异步通知（订单创建后通知库存） | 异步消息队列 | 解耦、削峰 |
| 事件广播（缓存刷新） | 发布/订阅 | 一对多通知 |

### Step 4: 数据策略 (Data Strategy)

每个服务独立数据库，识别跨服务数据查询需求：
- 服务内数据：直接查询本服务数据库
- 跨服务数据：使用 API 组合或 CQRS
- 读写比 > 10:1：考虑 CQRS 模式

### Step 5: 分布式事务 (Transactions)

识别需要跨服务事务的场景，应用 Saga 模式：
- 编排式 Saga：中央编排器协调流程
- 协同式 Saga：各服务通过事件自行协调
- 为每个步骤定义补偿操作

### Step 6: 韧性设计 (Resilience)

在每个服务边界添加保护措施：
- 熔断器（Circuit Breaker）：连续失败 5 次后熔断 60 秒
- 重试 + 退避：最多重试 3 次，指数退避
- 超时控制：每个远程调用设置超时
- 舱壁隔离：关键服务独立线程池

### Step 7: 可观测性 (Observability)

- 链路追踪：集成 OpenTelemetry，每条请求生成 trace ID
- 结构化日志：所有服务使用统一日志格式，包含 trace ID
- 指标监控：请求量、错误率、延迟 P99

### Step 8: 部署配置 (Deployment)

- 服务发现：使用 Consul/etcd/Nacos 注册服务
- API 网关：统一入口，路由、认证、限流
- 容器编排：Kubernetes 部署，Helm Chart 管理

## 服务拆分原则

### 拆分策略

| 策略 | 说明 | 示例 |
|------|------|------|
| 按业务领域 | DDD 限界上下文 | 用户服务、订单服务、商品服务 |
| 按子域 | 核心域/支撑域/通用域 | 订单(核心)、库存(支撑)、认证(通用) |
| 按变更频率 | 稳定/易变分离 | 基础数据 vs 业务逻辑 |
| 按团队 | 团队自治 | 每个团队负责一组服务 |

### 拆分反模式

| 反模式 | 问题 | 解决 |
|--------|------|------|
| 过早拆分 | 复杂度爆炸 | 先单体，后拆分 |
| 粒度过细 | 分布式单体 | 合并紧密耦合的服务 |
| 共享数据库 | 服务间强耦合 | 每个服务独立数据库 |

## API Gateway

微服务架构的统一入口，提供路由、认证、限流、协议转换等功能。

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| Kong | 基于 Nginx、插件丰富 | 通用 API 网关 |
| APISIX | 高性能、动态配置 | 高并发场景 |
| Spring Cloud Gateway | 响应式、Spring 生态 | Spring Cloud 项目 |

### 核心功能

- **路由转发**: 根据路径/Header 转发到后端服务
- **认证授权**: 集中处理 JWT/OAuth2 认证
- **限流熔断**: 保护后端服务
- **协议转换**: HTTP ↔ gRPC 转换
- **请求聚合**: 合并多个后端服务的响应

## 通信模式

### 同步通信 (HTTP/gRPC)

```
服务A ──HTTP/gRPC──▶ 服务B
       ◀──Response──
```

| 方式 | 优势 | 适用场景 |
|------|------|----------|
| REST | 简单、通用 | 对外 API、CRUD |
| gRPC | 高性能、强类型 | 内部服务通信、流式 |
| GraphQL | 灵活查询 | BFF 层、前端聚合 |

### 异步通信 (消息队列)

```
服务A ──Publish──▶ 消息队列 ──Consume──▶ 服务B
```

| 方式 | 优势 | 适用场景 |
|------|------|----------|
| 事件驱动 | 解耦、可扩展 | 状态变更通知 |
| 命令队列 | 削峰填谷 | 异步任务处理 |
| 发布/订阅 | 一对多广播 | 缓存刷新、日志收集 |

### 同步实现示例

```python
# gRPC 服务定义
# user.proto
syntax = "proto3";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
}

message GetUserRequest {
  string id = 1;
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
}

# gRPC 客户端
import grpc
from user_pb2_grpc import UserServiceStub
from user_pb2 import GetUserRequest

class UserClient:
    def __init__(self, host: str):
        self.channel = grpc.insecure_channel(host)
        self.stub = UserServiceStub(self.channel)
    
    def get_user(self, user_id: str):
        request = GetUserRequest(id=user_id)
        return self.stub.GetUser(request)
```

## 数据管理

### 每服务一数据库

```
用户服务 ──▶ 用户数据库 (PostgreSQL)
订单服务 ──▶ 订单数据库 (MySQL)
商品服务 ──▶ 商品数据库 (MongoDB)
```

### CQRS（命令查询职责分离）

将读写操作分离到不同的模型和数据库，适用于读写比例差异大的场景。

```
写操作 (Command):
  用户请求 → 命令服务 → 写数据库 → 发布事件

读操作 (Query):
  用户请求 → 查询服务 → 读数据库（反规范化）
                  ↑
            事件消费 → 更新读库
```

**适用场景**:
- 读写比例 > 10:1
- 查询复杂度远高于写入
- 需要不同的读写优化策略

### Saga 模式 (分布式事务)

```
创建订单流程:
1. 订单服务: 创建订单 (PENDING)
2. 库存服务: 预扣库存
3. 支付服务: 扣款
4. 订单服务: 更新订单状态 (PAID)

补偿流程 (任一步骤失败):
3. 支付服务: 退款
2. 库存服务: 恢复库存
1. 订单服务: 取消订单
```

```python
# Saga 编排器
class OrderSaga:
    def __init__(self):
        self.steps = [
            SagaStep(
                action=self.create_order,
                compensation=self.cancel_order
            ),
            SagaStep(
                action=self.reserve_inventory,
                compensation=self.release_inventory
            ),
            SagaStep(
                action=self.process_payment,
                compensation=self.refund_payment
            ),
        ]
    
    async def execute(self, order_data):
        completed = []
        
        for step in self.steps:
            try:
                result = await step.action(order_data)
                completed.append(step)
            except Exception as e:
                # 补偿已完成的步骤
                for completed_step in reversed(completed):
                    await completed_step.compensation(order_data)
                raise SagaFailedError(str(e))
```

## 服务发现

### 注册中心

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| Consul | 健康检查、KV 存储 | 通用 |
| etcd | 强一致性、K8s 使用 | Kubernetes |
| Nacos | 配置管理、阿里开源 | Spring Cloud |
| Eureka | Netflix、简单（已停止维护） | Spring Cloud |

### 客户端发现

```python
# Consul 服务发现
import consul

class ServiceDiscovery:
    def __init__(self):
        self.consul = consul.Consul()
    
    def register(self, name: str, host: str, port: int):
        self.consul.agent.service.register(
            name=name,
            service_id=f"{name}-{host}-{port}",
            address=host,
            port=port,
            check=consul.Check.http(f"http://{host}:{port}/health", interval="10s")
        )
    
    def discover(self, name: str) -> tuple:
        _, services = self.consul.health.service(name, passing=True)
        if not services:
            raise ServiceNotFoundError(name)
        service = random.choice(services)
        return service['Service']['Address'], service['Service']['Port']
```

## 熔断降级

### 熔断器模式

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"        # 正常
    OPEN = "open"            # 熔断
    HALF_OPEN = "half_open"  # 半开

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit is open")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise
```

## 链路追踪

### OpenTelemetry 集成

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# 初始化（推荐使用 OTLP 导出器，兼容 Jaeger/Zipkin/任何 OTLP 后端）
provider = TracerProvider()
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# 使用
async def create_order(order_data):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.amount", order_data["amount"])
        
        # 调用其他服务
        with tracer.start_as_current_span("call_inventory_service"):
            await inventory_service.reserve(order_data["items"])
        
        with tracer.start_as_current_span("call_payment_service"):
            await payment_service.charge(order_data["amount"])
```

## Edge Cases

1. **网络分区（Network Partition）**：服务之间网络不通时，必须实现超时 + 重试 + 熔断的组合。设置合理的超时时间（如 3 秒），重试 3 次（指数退避），连续失败 5 次后触发熔断，避免级联故障。
2. **服务版本冲突**：API 变更时使用 URL 路径版本化（`/v1/users`、`/v2/users`），同时支持 N-1 个版本。新版本上线后至少保留旧版本 2 个发布周期，通过 API 网关的路由规则灰度切换。
3. **级联故障（Cascading Failure）**：当下游服务变慢或不可用时，上游服务的线程池会被耗尽。在每个服务边界设置熔断器和舱壁隔离（Bulkhead），限制对每个下游服务的并发调用数。
4. **数据不一致窗口**：跨服务查询存在最终一致性延迟。为每个跨服务查询标注可接受的延迟时间（如"订单列表最多延迟 5 秒"），并在 UI 上标注"数据可能不是最新的"。
5. **死信队列处理**：消息消费失败 3 次后路由到死信队列（DLQ）。设置 DLQ 监控告警，定期人工检查并处理：重试、修复数据、或丢弃。不要让消息无限重试。
6. **数据库迁移协调**：使用 Expand-Contract 模式：(1) Expand：新增字段，旧代码仍可运行；(2) 迁移数据；(3) Contract：删除旧字段。绝不直接修改已有字段，确保向后兼容。

## 输出模板

```markdown
# 微服务架构设计文档（ADR）

## 决策背景
- **系统规模**: {预估用户量、QPS}
- **团队规模**: {人数}
- **现有架构**: {单体 / 已有微服务}

## 服务划分

| 服务名 | 职责 | 领域类型 | 数据库 | API 数量 |
|--------|------|----------|--------|----------|
| {user-service} | 用户管理 | 核心域 | PostgreSQL | {n} |
| {order-service} | 订单处理 | 核心域 | MySQL | {n} |
| {payment-service} | 支付 | 支撑域 | PostgreSQL | {n} |

## 通信设计

| 交互 | 发起方 | 接收方 | 方式 | 协议 |
|------|--------|--------|------|------|
| 查询用户 | API Gateway | user-service | 同步 | gRPC |
| 订单创建 | order-service | payment-service | 异步 | Kafka |
| 库存扣减 | order-service | inventory-service | 同步 | gRPC |

## 数据策略
- **数据库隔离**: 每个服务独立数据库
- **跨服务查询**: {API 组合 / CQRS}
- **分布式事务**: {Saga 编排 / Saga 协同}

## 韧性设计
- **熔断**: 连续 {n} 次失败，熔断 {m} 秒
- **重试**: 最多 {n} 次，指数退避
- **超时**: {n}ms

## 部署架构
- **容器编排**: Kubernetes
- **服务发现**: {Consul / etcd / Nacos}
- **API 网关**: {Kong / APISIX}
- **链路追踪**: OpenTelemetry + Jaeger
```

**填写示例**（电商平台）：

```markdown
# 微服务架构设计文档（ADR）

## 决策背景
- **系统规模**: 预估 100 万用户，峰值 QPS 5000
- **团队规模**: 15 人（3 个小组）
- **现有架构**: 单体应用，准备拆分

## 服务划分

| 服务名 | 职责 | 领域类型 | 数据库 | API 数量 |
|--------|------|----------|--------|----------|
| user-service | 用户注册、认证、信息管理 | 核心域 | PostgreSQL | 8 |
| product-service | 商品管理、搜索 | 核心域 | MySQL + Elasticsearch | 12 |
| order-service | 订单创建、查询、状态管理 | 核心域 | MySQL | 10 |
| payment-service | 支付处理、退款 | 支撑域 | PostgreSQL | 6 |
| inventory-service | 库存管理、扣减 | 支撑域 | MySQL | 5 |
| notification-service | 消息推送（邮件/短信） | 通用域 | MongoDB | 3 |

## 通信设计

| 交互 | 发起方 | 接收方 | 方式 | 协议 |
|------|--------|--------|------|------|
| 查询用户 | API Gateway | user-service | 同步 | gRPC |
| 查询商品 | API Gateway | product-service | 同步 | gRPC |
| 订单创建 | order-service | payment-service | 异步 | Kafka |
| 订单创建 | order-service | inventory-service | 同步 | gRPC |
| 支付完成 | payment-service | notification-service | 异步 | Kafka |

## 数据策略
- **数据库隔离**: 每个服务独立数据库
- **跨服务查询**: API 组合（API Gateway 聚合）
- **分布式事务**: Saga 编排（订单创建流程）

## 韧性设计
- **熔断**: 连续 5 次失败，熔断 60 秒
- **重试**: 最多 3 次，指数退避（100ms, 200ms, 400ms）
- **超时**: 3000ms

## 部署架构
- **容器编排**: Kubernetes
- **服务发现**: Nacos
- **API 网关**: APISIX
- **链路追踪**: OpenTelemetry + Jaeger
```

## 不适用

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 团队 < 5 人 | 微服务的运维开销超出团队承受能力 | 模块化单体（Modular Monolith） |
| 日请求量 < 10k | 单体完全能承受，微服务增加不必要的复杂度 | 单体 + 模块化设计 |
| 需要强一致性（全系统） | 分布式事务复杂度极高 | 单体 + 本地事务 |
| 早期创业阶段 | 应先验证产品市场契合度 | 单体快速迭代 |

**重定向**：
- 单体架构优化：考虑模块化单体（Modular Monolith），内部按模块划分，但保持单一部署单元。
- 容器化部署：如果只需要容器化但不需要微服务拆分，使用 Docker Compose 编排单体应用即可。

```
# 设计微服务架构
为电商平台设计微服务架构

# 实现服务间通信
实现 gRPC 服务间调用

# 实现分布式事务
使用 Saga 模式实现订单创建流程

# 添加熔断降级
为服务调用添加熔断器

# 配置链路追踪
集成 OpenTelemetry 链路追踪
```

## 参考资料

- 微服务模式: [references/patterns.md](references/patterns.md)
- Saga 模式: [references/saga.md](references/saga.md)
