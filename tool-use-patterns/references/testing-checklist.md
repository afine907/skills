# 工具集成测试清单

## 测试矩阵

### 正常路径测试

| # | 测试项 | 验证点 | 优先级 |
|---|--------|--------|--------|
| 1 | 工具正常调用 | 参数正确传递、返回值正确解析 | P0 |
| 2 | 可选参数默认值 | 缺省参数时使用默认值 | P0 |
| 3 | 并行调用 | 多工具并发无竞态 | P1 |
| 4 | 大响应处理 | 大响应不撑爆上下文 | P1 |

### 错误处理测试

| # | 测试项 | 验证点 | 优先级 |
|---|--------|--------|--------|
| 5 | 超时重试 | 超时后指数退避重试 | P0 |
| 6 | 限流处理 | 429 后退避重试 | P0 |
| 7 | 参数错误恢复 | 错误信息返回 LLM → LLM 修正参数 | P0 |
| 8 | 工具不可用 | 断路器触发 → 降级方案 | P0 |
| 9 | 持续失败 | 3 次失败后断路器打开 | P0 |
| 10 | 网络异常 | 连接超时/DNS 失败的处理 | P1 |

### 输出验证测试

| # | 测试项 | 验证点 | 优先级 |
|---|--------|--------|--------|
| 11 | Schema 验证 | 输出符合预期 JSON Schema | P0 |
| 12 | 空响应处理 | null/空数组不导致崩溃 | P0 |
| 13 | 部分响应 | 缺失字段被标记而非猜测 | P1 |
| 14 | 异常格式 | 非预期格式的优雅处理 | P1 |

### 幂等性测试

| # | 测试项 | 验证点 | 优先级 |
|---|--------|--------|--------|
| 15 | 相同幂等键 | 重复调用返回相同结果 | P0 |
| 16 | 不同幂等键 | 不同调用创建独立记录 | P0 |
| 17 | 重试幂等性 | 失败重试不产生重复副作用 | P0 |

### 安全测试

| # | 测试项 | 验证点 | 优先级 |
|---|--------|--------|--------|
| 18 | 参数注入 | 恶意参数被 Schema 拦截 | P0 |
| 19 | 路径穿越 | 文件操作的路径沙箱 | P0 |
| 20 | 权限边界 | 工具不能越权操作 | P0 |
| 21 | Prompt 注入 | 工具输出中的恶意内容不污染 Agent | P1 |

## 自动化测试脚本模板

```python
import pytest
from unittest.mock import patch, MagicMock

class TestToolIntegration:
    """工具集成测试套件"""

    def test_normal_call(self, tool, sample_input):
        """正常调用：参数正确传递，返回值正确解析"""
        result = tool.execute(sample_input)
        assert result.success is True
        assert "expected_field" in result.data

    def test_timeout_retry(self, tool, sample_input):
        """超时重试：第1次超时，第2次成功"""
        tool.execute = MagicMock(side_effect=[
            TimeoutError("request timed out"),
            {"success": True, "data": "ok"}
        ])
        result = tool.execute_with_retry(sample_input, max_retries=3)
        assert result.success is True
        assert tool.execute.call_count == 2

    def test_circuit_breaker(self, tool, sample_input):
        """断路器：连续3次失败后打开"""
        tool.execute = MagicMock(side_effect=ServiceError("unavailable"))
        for _ in range(3):
            tool.execute_with_retry(sample_input)
        assert tool.circuit_breaker.is_open is True

    def test_idempotency(self, tool, sample_input, idempotency_key):
        """幂等性：相同key返回相同结果"""
        result1 = tool.execute(sample_input, idempotency_key=idempotency_key)
        result2 = tool.execute(sample_input, idempotency_key=idempotency_key)
        assert result1.id == result2.id

    @pytest.mark.parametrize("malicious_input", [
        {"sql": "'; DROP TABLE users; --"},
        {"path": "../../../etc/passwd"},
        {"command": "rm -rf /"},
    ])
    def test_injection_defense(self, tool, malicious_input):
        """注入防御：恶意参数被拦截"""
        with pytest.raises(ValidationError):
            tool.execute(malicious_input)
```

## 测试执行建议

1. **Mock 测试优先** — 快速验证逻辑，CI 中每次 PR 运行
2. **集成测试定期** — 真实工具 + 沙箱环境，每日运行
3. **故障注入手动** — 模拟极端场景，发版前运行
4. **属性测试随机** — 发现边界条件，定期运行
