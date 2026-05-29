# 工具组合编排模式

## 模式 1：顺序流水线

最简单的组合模式，每步依赖前一步的输出。

```
Tool_A(output) → Tool_B(output) → Tool_C(result)
```

**适用场景：** 数据获取 → 处理 → 存储

**实现要点：**
- 每步将输出传入下一步的输入
- 任一步失败时记录已完成步骤的状态
- 设置总步骤硬上限（代码级）

```python
def pipeline(tools: list, initial_input, max_steps=10):
    result = initial_input
    for i, tool in enumerate(tools[:max_steps]):
        try:
            result = tool.execute(result)
            log_step(i, tool.name, result, success=True)
        except ToolError as e:
            log_step(i, tool.name, error=e, success=False)
            # 决定：重试、降级、或中止
            result = handle_failure(tool, result, e)
            if result is None:
                break
    return result
```

## 模式 2：并行扇出

多个无依赖的工具同时执行，结果合并。

```
         ┌→ Tool_A → result_a ─┐
input →  ├→ Tool_B → result_b ─┼→ merge(results)
         └→ Tool_C → result_c ─┘
```

**适用场景：** 多数据源聚合、并行搜索、批量处理

**实现要点：**
- 使用 asyncio.gather 或线程池并发执行
- 单个工具失败不阻塞其他工具
- 合并结果时标记失败的工具

```python
import asyncio

async def fan_out(tools: list, input_data):
    tasks = [tool.execute(input_data) for tool in tools]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    merged = {}
    for tool, result in zip(tools, results):
        if isinstance(result, Exception):
            merged[tool.name] = {"error": str(result)}
        else:
            merged[tool.name] = result
    return merged
```

## 模式 3：条件分支

根据前一步的结果选择不同的工具路径。

```
input → Tool_A
         ├── 成功 → Tool_B(success_input)
         └── 失败 → Tool_C(fallback_input)
```

**适用场景：** 有降级方案的工具调用、A/B 策略选择

**实现要点：**
- 分支条件要明确（基于返回值而非异常）
- 每个分支都有明确的工具和参数
- 记录走了哪个分支（可观测性）

```python
def conditional_branch(input_data):
    result_a = tool_a.execute(input_data)

    if result_a.success:
        log_branch("success_path")
        return tool_b.execute(result_a.data)
    else:
        log_branch("fallback_path")
        return tool_c.execute(input_data)
```

## 模式 4：补偿回滚（Saga 模式）

多步写入操作中，后续步骤失败时需要回滚前面已完成的步骤。

```
Tool_A → Tool_B → Tool_C 失败
  ↓         ↓
补偿 A ← 补偿 B
```

**适用场景：** 多步写入操作、跨服务事务

**实现要点：**
- 每个工具注册补偿动作后再执行
- 补偿动作按逆序执行
- 补偿失败时记录并告警（不能无限重试）
- 不可补偿的操作（发邮件、发布内容）需要在执行前额外确认

```python
class Saga:
    def __init__(self):
        self.compensations = []

    def execute(self, tool, input_data, compensation):
        try:
            result = tool.execute(input_data)
            self.compensations.append((compensation, input_data))
            return result
        except Exception as e:
            self.rollback()
            raise

    def rollback(self):
        for comp, data in reversed(self.compensations):
            try:
                comp(data)
            except Exception as e:
                log_compensation_failure(comp, data, e)
                # 补偿失败，告警但继续
```

## 模式选择决策表

| 维度 | 顺序流水线 | 并行扇出 | 条件分支 | 补偿回滚 |
|------|-----------|---------|---------|---------|
| 依赖关系 | 强依赖 | 无依赖 | 条件依赖 | 强依赖 |
| 执行方式 | 串行 | 并行 | 串行 | 串行 |
| 失败处理 | 中止/重试 | 隔离失败 | 走降级分支 | 回滚已执行 |
| 适用场景 | 数据流水线 | 聚合查询 | 策略选择 | 多步写入 |
| 复杂度 | 低 | 中 | 中 | 高 |
