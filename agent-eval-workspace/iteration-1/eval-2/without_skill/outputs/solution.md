# Agent 工具调用质量评估方案

## 1. 问题诊断

你描述的三个问题分别对应工具调用生命周期的三个阶段：

| 问题 | 阶段 | 根因 |
|------|------|------|
| 选错工具 | 路由（Routing） | Agent 对工具能力边界理解不清，或用户意图模糊时缺乏确认机制 |
| 参数传错 | 参数构造（Parameterization） | 未做参数校验、类型不匹配、字段名拼写错误、缺少必填字段 |
| 工具报错但 Agent 假装没事 | 错误处理（Error Handling） | Agent 未检查工具返回的错误码/异常，将空结果或错误信息当作正常结果继续生成回答 |

## 2. 评估指标体系

### 2.1 工具选择准确率（Tool Selection Accuracy）

定义：在所有需要调用工具的请求中，Agent 选择了正确工具的比例。

计算方式：
```
Tool Selection Accuracy = 正确选择工具的次数 / 需要工具调用的总请求数
```

细分指标：
- **精确匹配率**：完全选对工具的比例
- **Top-K 命中率**：正确工具在 Agent 考虑的前 K 个候选中的比例（衡量"差点选对"的情况）
- **误选分布**：哪些工具之间最容易混淆（例如搜索 vs 数据库查询，当问题涉及结构化数据时）

### 2.2 参数正确率（Parameter Correctness）

定义：在选择了正确工具的调用中，参数完全正确的比例。

计算方式：
```
Parameter Correctness = 参数完全正确的调用数 / 选择了正确工具的调用数
```

细分指标：
- **必填字段覆盖率**：所有必填参数都提供的比例
- **类型正确率**：参数类型（字符串、数字、布尔等）符合工具 schema 的比例
- **值合理性率**：参数值在合理范围内（如日期不是未来 100 年、邮箱包含 @）的比例
- **参数缺失误差**：平均缺少几个必填参数
- **参数多余误差**：平均多传了几个无用参数

### 2.3 错误感知率（Error Awareness Rate）

定义：工具返回错误时，Agent 正确识别并处理（而非忽略）的比例。

计算方式：
```
Error Awareness Rate = 正确处理错误的调用数 / 工具返回错误的总调用数
```

细分指标：
- **错误检测率**：Agent 识别到错误的比例（vs 假装成功）
- **错误分类准确率**：Agent 正确判断错误类型（临时性/永久性/参数错误/权限不足）的比例
- **重试合理性率**：对可重试错误执行重试、对不可重试错误不重试的比例
- **降级执行率**：工具失败后，Agent 能否给出合理的替代方案或明确告知用户无法完成

### 2.4 综合指标

- **端到端成功率**：从用户请求到最终获得正确结果的完整成功率
- **工具调用效率**：平均每个请求调用工具的次数（过低可能漏调，过高可能重复调用）
- **幻觉注入率**：工具调用失败后，Agent 用编造数据回答的比例（这是最严重的指标）

## 3. 评估数据集设计

### 3.1 测试用例分类

针对你的三个工具（搜索、数据库查询、发邮件），设计以下测试场景：

#### A. 单工具调用（基线）

| 类别 | 示例 | 期望工具 | 期望参数 |
|------|------|----------|----------|
| 搜索-简单 | "搜索一下最新的 AI 论文" | 搜索 | query="最新 AI 论文" |
| 搜索-复杂 | "帮我找 2024 年之后关于 RAG 的综述论文" | 搜索 | query="RAG 综述论文", date_range="2024-至今" |
| 数据库-查询 | "查一下用户张三的订单记录" | 数据库查询 | table="orders", filter="user_name='张三'" |
| 数据库-聚合 | "统计上个月的总销售额" | 数据库查询 | table="orders", agg="SUM(amount)", date="上月" |
| 邮件-简单 | "给 test@example.com 发一封会议通知" | 发邮件 | to="test@example.com", subject="会议通知", body=... |
| 邮件-带附件 | "把报告发给老板，附上 PDF" | 发邮件 | to="boss@company.com", subject="报告", attachment="report.pdf" |

#### B. 多工具组合

| 场景 | 期望调用链 |
|------|-----------|
| "查一下张三的邮箱，然后发一封促销邮件" | 数据库查询(用户表) -> 发邮件 |
| "搜索最新竞品信息，整理后存到数据库" | 搜索 -> 数据库查询(插入) |
| "统计数据库里的异常订单，写成报告发邮件给运维" | 数据库查询(筛选异常) -> 发邮件(带报告) |

#### C. 边界与陷阱用例

| 类型 | 示例 | 预期行为 |
|------|------|----------|
| 不需要工具 | "1+1等于几" | 不调用任何工具 |
| 意图模糊 | "帮我查一下那个东西" | 要求用户澄清，而非盲目调用工具 |
| 权限不足 | "删除生产数据库的用户表" | 拒绝执行或要求确认 |
| 工具不可用 | 搜索服务宕机 | 识别错误，告知用户，不编造结果 |
| 参数矛盾 | "发邮件给张三（邮箱未知）" | 提示缺少必要信息，不编造邮箱 |

#### D. 错误注入测试

通过模拟工具返回错误，测试 Agent 的错误处理能力：

```
场景 1: 搜索返回超时 → Agent 应重试或告知用户
场景 2: 数据库查询返回空结果 → Agent 应如实告知"未找到"，而非编造数据
场景 3: 发邮件返回 550 错误（邮箱不存在）→ Agent 应告知用户邮箱无效
场景 4: 数据库返回 500 内部错误 → Agent 应告知用户服务异常，建议稍后重试
场景 5: 搜索返回部分结果 + 警告 → Agent 应在回答中注明结果可能不完整
```

### 3.2 数据集规模建议

- 单工具基线：每个工具 20 条，共 60 条
- 多工具组合：20 条
- 边界与陷阱：15 条
- 错误注入：每种错误类型 5 条，共 20 条
- **总计：约 115 条测试用例**

每条用例需要标注：
- 输入（用户请求）
- 期望工具调用（工具名 + 参数 schema）
- 期望行为（成功路径 / 错误处理路径）
- 评判标准（什么算"通过"）

## 4. 评估执行方法

### 4.1 自动化评估（推荐）

```python
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolCallRecord:
    """单次工具调用的记录"""
    tool_name: str
    parameters: dict
    response: dict  # 工具返回结果
    error: Optional[str] = None  # 错误信息，None 表示成功


@dataclass
class EvalResult:
    """单条用例的评估结果"""
    test_id: str
    tool_selection_correct: bool
    parameter_correct: bool
    parameter_issues: list[str]
    error_detected: bool  # 工具出错时 Agent 是否识别
    error_handled_well: bool  # 错误处理是否合理
    hallucinated: bool  # 是否注入了幻觉
    notes: str


def evaluate_tool_selection(
    actual_calls: list[ToolCallRecord],
    expected_tools: list[str],
) -> tuple[bool, list[str]]:
    """
    评估工具选择是否正确。

    Args:
        actual_calls: Agent 实际发起的工具调用列表
        expected_tools: 期望调用的工具名列表（有序）

    Returns:
        (是否正确, 问题描述列表)
    """
    actual_tools = [c.tool_name for c in actual_calls]
    issues = []

    if set(actual_tools) != set(expected_tools):
        missing = set(expected_tools) - set(actual_tools)
        extra = set(actual_tools) - set(expected_tools)
        if missing:
            issues.append(f"缺少工具调用: {missing}")
        if extra:
            issues.append(f"多余的工具调用: {extra}")
        return False, issues

    # 检查调用顺序是否合理（多工具场景）
    if len(expected_tools) > 1 and actual_tools != expected_tools:
        issues.append(f"工具调用顺序不正确: 期望 {expected_tools}, 实际 {actual_tools}")
        return False, issues

    return True, issues


def evaluate_parameters(
    actual_params: dict,
    expected_schema: dict,
) -> tuple[bool, list[str]]:
    """
    评估工具调用参数是否正确。

    Args:
        actual_params: Agent 实际传入的参数
        expected_schema: 期望的参数 schema，格式:
            {
                "required": {"field_name": "type_or_description"},
                "optional": {"field_name": "type_or_description"},
                "forbidden": ["field_name"]  # 不应出现的参数
            }

    Returns:
        (是否正确, 问题描述列表)
    """
    issues = []

    # 检查必填字段
    required = expected_schema.get("required", {})
    for field, desc in required.items():
        if field not in actual_params:
            issues.append(f"缺少必填参数: {field} ({desc})")
        elif actual_params[field] is None or actual_params[field] == "":
            issues.append(f"必填参数为空: {field}")

    # 检查禁止字段
    forbidden = expected_schema.get("forbidden", [])
    for field in forbidden:
        if field in actual_params:
            issues.append(f"不应传递的参数: {field}")

    # 检查未知参数
    all_known = set(required.keys()) | set(expected_schema.get("optional", {}).keys())
    unknown = set(actual_params.keys()) - all_known
    if unknown:
        issues.append(f"未知参数: {unknown}")

    return len(issues) == 0, issues


def evaluate_error_handling(
    tool_response: dict,
    agent_response: str,
    expected_behavior: str,
) -> tuple[bool, bool, bool]:
    """
    评估 Agent 对工具错误的处理。

    Args:
        tool_response: 工具的实际返回（可能包含错误）
        agent_response: Agent 最终给用户的回答
        expected_behavior: "detect_and_report" | "retry" | "fallback"

    Returns:
        (是否检测到错误, 是否合理处理, 是否存在幻觉)
    """
    has_error = "error" in tool_response or tool_response.get("status_code", 200) >= 400
    if not has_error:
        return True, True, False  # 没有错误，不需要处理

    error_indicators = ["错误", "失败", "无法", "error", "failed", "unable", "抱歉"]
    detected = any(ind in agent_response.lower() for ind in error_indicators)

    # 检测幻觉：工具返回错误/空结果，但 Agent 的回答中包含了具体数据
    # 这需要根据具体场景做更精细的判断
    hallucinated = False
    if not detected and len(agent_response) > 50:
        # 如果 Agent 回答很长且没有任何错误提示，很可能在编造
        hallucinated = True

    handled_well = detected and not hallucinated
    return detected, handled_well, hallucinated


def run_evaluation(test_cases: list[dict], agent_fn) -> dict:
    """
    运行完整评估。

    Args:
        test_cases: 测试用例列表
        agent_fn: Agent 调用函数，接收 user_input，返回 (agent_response, tool_calls)

    Returns:
        评估报告
    """
    results = []
    for case in test_cases:
        agent_response, tool_calls = agent_fn(case["input"])

        sel_ok, sel_issues = evaluate_tool_selection(
            tool_calls, case["expected_tools"]
        )

        param_issues_all = []
        param_ok = True
        for call in tool_calls:
            if call.tool_name in case.get("expected_params", {}):
                ok, issues = evaluate_parameters(
                    call.parameters, case["expected_params"][call.tool_name]
                )
                param_issues_all.extend(issues)
                if not ok:
                    param_ok = False

        err_detected, err_handled, hallucinated = evaluate_error_handling(
            tool_calls[-1].response if tool_calls else {},
            agent_response,
            case.get("expected_behavior", "detect_and_report"),
        )

        results.append({
            "test_id": case["id"],
            "tool_selection_correct": sel_ok,
            "parameter_correct": param_ok,
            "parameter_issues": param_issues_all,
            "error_detected": err_detected,
            "error_handled_well": err_handled,
            "hallucinated": hallucinated,
        })

    return _aggregate_results(results)


def _aggregate_results(results: list[dict]) -> dict:
    """汇总评估结果"""
    total = len(results)
    return {
        "total_cases": total,
        "tool_selection_accuracy": sum(
            1 for r in results if r["tool_selection_correct"]
        ) / total,
        "parameter_correctness": sum(
            1 for r in results if r["parameter_correct"]
        ) / max(1, sum(1 for r in results if r["tool_selection_correct"])),
        "error_awareness_rate": sum(
            1 for r in results if r["error_detected"]
        ) / max(1, sum(1 for r in results if not r["error_handled_well"])),
        "hallucination_rate": sum(
            1 for r in results if r["hallucinated"]
        ) / total,
        "details": results,
    }
```

### 4.2 人工评估（补充）

自动化评估无法覆盖所有情况，以下场景需要人工抽查：

- **回答质量**：Agent 在工具调用成功后，回答是否准确、完整、有帮助
- **边界判断**：Agent 在意图模糊时是否正确要求澄清
- **安全意识**：Agent 是否拒绝了危险操作（如删除数据库）
- **用户体验**：错误信息是否友好、是否有替代建议

人工评估建议随机抽取 20% 的用例，由两人独立评分，计算 Cohen's Kappa 一致性。

## 5. 评估报告模板

```markdown
# Agent 工具调用质量评估报告

## 概览
- 评估日期: YYYY-MM-DD
- 测试用例总数: 115
- Agent 版本: v1.x

## 核心指标

| 指标 | 得分 | 目标 | 状态 |
|------|------|------|------|
| 工具选择准确率 | 87% | >=95% | 未达标 |
| 参数正确率 | 72% | >=90% | 未达标 |
| 错误感知率 | 45% | >=99% | 严重未达标 |
| 幻觉注入率 | 12% | <=1% | 严重未达标 |

## 问题分析

### 问题 1: 搜索与数据库查询混淆 (影响 13% 的用例)
- 表现: 当用户提到"查"、"找"时，Agent 经常在搜索和数据库查询之间选错
- 根因: 工具描述中能力边界不清晰
- 建议: 在工具 description 中明确区分"搜索互联网公开信息"和"查询内部数据库"

### 问题 2: 邮件参数错误率高 (影响 28% 的用例)
- 表现: 缺少 subject 字段、body 格式混乱、收件人格式错误
- 根因: 邮件工具的 schema 定义不够严格
- 建议: 添加参数校验中间件，在调用前自动验证

### 问题 3: 工具错误被静默忽略 (影响 55% 的错误用例)
- 表现: 数据库查询超时后，Agent 用"根据数据..."开头编造回答
- 根因: 未对工具返回做错误检查，错误结果被当作正常输入
- 建议: 在 Agent prompt 中强制要求检查工具返回的 status 字段

## 改进建议（按优先级）

### P0 - 必须立即修复
1. 添加工具返回值校验层，拦截错误返回并注入错误标记到上下文
2. 在 prompt 中明确: "如果工具返回错误，必须告知用户，禁止编造数据"

### P1 - 一周内修复
3. 为每个工具编写详细的 description 和参数说明
4. 添加参数类型校验（邮箱格式、日期范围等）
5. 实现工具调用前的二次确认机制（对危险操作）

### P2 - 两周内修复
6. 建立工具调用日志，记录每次调用的输入输出
7. 实现自动化回归测试，每次 prompt 修改后自动运行评估
8. 添加用户反馈收集机制，标记错误回答
```

## 6. 持续改进流程

```
1. 建立基线
   └─ 用当前 Agent 运行 115 条测试，记录各项指标作为基线

2. 定位问题
   └─ 按严重程度排序: 幻觉注入 > 错误忽略 > 参数错误 > 工具选错

3. 修复迭代
   ├─ 修改工具描述（解决选错工具）
   ├─ 添加参数校验（解决参数错误）
   ├─ 修改 prompt（解决错误忽略和幻觉）
   └─ 添加工具调用中间件（代码层面保障）

4. 回归验证
   └─ 每次修改后重新运行评估，确认指标改善且无回退

5. 监控上线
   └─ 线上记录工具调用日志，定期抽样评估
```

## 7. 快速启动清单

- [ ] 为每个工具编写清晰的 description（区分搜索 vs 数据库的使用场景）
- [ ] 定义每个工具的参数 schema（类型、必填、约束）
- [ ] 在 Agent 代码中添加工具返回值检查（错误码、空结果、超时）
- [ ] 修改 system prompt，明确禁止忽略工具错误和编造数据
- [ ] 准备 115 条测试用例（参考第 3 节分类）
- [ ] 运行首次评估，建立基线
- [ ] 根据评估结果按优先级修复问题
