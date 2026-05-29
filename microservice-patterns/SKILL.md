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
---

# Microservice Patterns — 微服务设计模式

微服务架构的核心设计模式和最佳实践。


## Goal

微服务架构设计模式，包含服务拆分、通信方式、数据管理、服务发现、熔断降级、链路追踪

## Trigger

- 用户要求"微服务架构"、"服务拆分"
  - 需要设计分布式系统
  - 需要实现服务治理

## Workflow

```
输入 → 处理 → 输出
```
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
| Eureka | Netflix、简单 | Spring Cloud |

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
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# 初始化
provider = TracerProvider()
jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
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

## 快速使用

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
