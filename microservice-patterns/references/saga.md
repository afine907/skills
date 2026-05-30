# Saga 模式详解

## 概述

Saga 是一种管理分布式事务的模式，将长事务分解为一系列本地事务，每个本地事务有对应的补偿操作。

## 两种实现方式

### 1. 协调式 Saga (Choreography)

每个服务监听事件并决定下一步操作。

```
订单服务 ──OrderCreated──▶ 库存服务
    ▲                          │
    │                    InventoryReserved
    │                          │
    ▼                          ▼
支付服务 ◀──PaymentRequested── 支付服务
    │
    PaymentCompleted
    │
    ▼
订单服务 ──OrderConfirmed──▶ 通知服务
```

**优点**：简单、松耦合
**缺点**：逻辑分散、难以追踪

### 2. 编排式 Saga (Orchestration)

中央协调器控制整个流程。

```
Saga 编排器
    │
    ├──1. 创建订单──▶ 订单服务
    │
    ├──2. 预扣库存──▶ 库存服务
    │
    ├──3. 处理支付──▶ 支付服务
    │
    └──4. 确认订单──▶ 订单服务
```

**优点**：逻辑集中、易于理解
**缺点**：编排器可能成为瓶颈

## 实现示例

### Python 实现

```python
from dataclasses import dataclass
from typing import Callable, Any
import asyncio

@dataclass
class SagaStep:
    name: str
    action: Callable
    compensation: Callable

class SagaOrchestrator:
    def __init__(self):
        self.steps: list[SagaStep] = []
    
    def add_step(self, step: SagaStep):
        self.steps.append(step)
    
    async def execute(self, context: dict) -> dict:
        completed_steps = []
        
        for step in self.steps:
            try:
                result = await step.action(context)
                context[step.name] = result
                completed_steps.append(step)
            except Exception as e:
                # 执行补偿操作
                for completed_step in reversed(completed_steps):
                    await completed_step.compensation(context)
                raise SagaFailedError(f"Step {step.name} failed: {e}")
        
        return context

# 使用示例
async def create_order(context):
    order = await order_service.create(context['order_data'])
    return order

async def cancel_order(context):
    await order_service.cancel(context['create_order']['id'])

async def reserve_inventory(context):
    await inventory_service.reserve(context['create_order']['items'])

async def release_inventory(context):
    await inventory_service.release(context['create_order']['items'])

async def process_payment(context):
    await payment_service.charge(context['create_order']['total'])

async def refund_payment(context):
    await payment_service.refund(context['process_payment']['transaction_id'])

# 组装 Saga
saga = SagaOrchestrator()
saga.add_step(SagaStep("create_order", create_order, cancel_order))
saga.add_step(SagaStep("reserve_inventory", reserve_inventory, release_inventory))
saga.add_step(SagaStep("process_payment", process_payment, refund_payment))

# 执行
result = await saga.execute({"order_data": order_data})
```

### TypeScript 实现

```typescript
interface SagaStep<T> {
  name: string;
  execute: (context: T) => Promise<T>;
  compensate: (context: T) => Promise<void>;
}

class SagaOrchestrator<T> {
  private steps: SagaStep<T>[] = [];
  
  addStep(step: SagaStep<T>): this {
    this.steps.push(step);
    return this;
  }
  
  async execute(context: T): Promise<T> {
    const completedSteps: SagaStep<T>[] = [];
    
    for (const step of this.steps) {
      try {
        context = await step.execute(context);
        completedSteps.push(step);
      } catch (error) {
        // 补偿
        for (const completed of completedSteps.reverse()) {
          await completed.compensate(context);
        }
        throw new Error(`Saga failed at step ${step.name}: ${error}`);
      }
    }
    
    return context;
  }
}
```

## 状态机实现

```python
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    INVENTORY_RESERVED = "inventory_reserved"
    PAYMENT_PROCESSED = "payment_processed"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class OrderSaga:
    def __init__(self, order):
        self.order = order
        self.transitions = {
            OrderStatus.PENDING: {
                'reserve_inventory': OrderStatus.INVENTORY_RESERVED,
                'cancel': OrderStatus.CANCELLED,
            },
            OrderStatus.INVENTORY_RESERVED: {
                'process_payment': OrderStatus.PAYMENT_PROCESSED,
                'release_inventory': OrderStatus.CANCELLED,
            },
            OrderStatus.PAYMENT_PROCESSED: {
                'confirm': OrderStatus.CONFIRMED,
                'refund': OrderStatus.CANCELLED,
            },
        }
    
    async def transition(self, action):
        current = self.order.status
        if action not in self.transitions.get(current, {}):
            raise InvalidTransition(f"{current} -> {action}")
        
        new_status = self.transitions[current][action]
        await self._execute_action(action)
        self.order.status = new_status
```

## 错误处理

### 补偿策略

1. **立即补偿**：失败后立即执行所有补偿
2. **重试后补偿**：重试几次后再补偿
3. **人工介入**：关键操作失败时通知人工处理

### 幂等性

所有操作和补偿必须是幂等的：

```python
async def reserve_inventory(context):
    reservation_id = context.get('reservation_id')
    if reservation_id:
        # 已经预留过，跳过
        return {'reservation_id': reservation_id}
    
    # 创建新的预留
    result = await inventory_service.reserve(context['items'])
    context['reservation_id'] = result['id']
    return result
```

## 最佳实践

1. **保持简单**：每个 Saga 不超过 5-7 个步骤
2. **幂等操作**：所有操作支持重复执行
3. **超时处理**：为每个步骤设置超时
4. **日志记录**：记录每个步骤的执行和补偿
5. **监控告警**：失败时及时通知
6. **测试充分**：测试正常流程和各种失败场景

## 参考资料

- Saga Pattern: https://microservices.io/patterns/data/saga.html
- Distributed Sagas: https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf
