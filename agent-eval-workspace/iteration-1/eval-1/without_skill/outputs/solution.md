# Agent v1 vs v2 科学评估方案

## 1. 评估目标

对比两个版本的 Agent 性能：
- **v1**: 仅使用简单 system prompt
- **v2**: 在 v1 基础上增加 few-shot examples 和 tool use

评估维度：准确性、效率、稳定性、用户体验。

---

## 2. 评估指标体系

### 2.1 核心指标

| 指标 | 定义 | 计算方式 | 权重建议 |
|------|------|----------|----------|
| **任务完成率** | Agent 成功完成目标任务的比例 | 成功任务数 / 总任务数 | 30% |
| **答案准确率** | 输出结果与标准答案的匹配程度 | 正确答案数 / 总答案数 | 25% |
| **响应效率** | 完成任务所需的 token/步骤数 | 平均 token 消耗或步骤数 | 15% |
| **格式合规率** | 输出符合预期格式的比例 | 合规输出数 / 总输出数 | 10% |
| **错误恢复率** | 遇到错误后成功恢复的比例 | 恢复成功数 / 错误发生数 | 10% |
| **一致性** | 相同输入多次运行结果的稳定程度 | 结果标准差或变异系数 | 10% |

### 2.2 工具使用专项指标（v2 专属）

| 指标 | 定义 |
|------|------|
| **工具调用准确率** | 正确选择工具的比例 |
| **工具参数正确率** | 工具参数填写正确的比例 |
| **工具调用必要性** | 是否在需要时才调用工具（避免冗余调用） |
| **工具结果利用度** | 是否正确利用工具返回的结果 |

### 2.3 指标评分标准

```
任务完成率:
  - 完全成功: 1.0
  - 部分成功（完成主要目标但有小缺陷）: 0.7
  - 基本失败（仅完成少量要求）: 0.3
  - 完全失败: 0.0

答案准确率:
  - 精确匹配: 1.0
  - 语义等价（意思对但表述不同）: 0.8
  - 部分正确: 0.5
  - 错误: 0.0
```

---

## 3. 测试数据集设计

### 3.1 测试用例分类

```
测试数据集/
├── category_1_basic/          # 基础能力测试
│   ├── simple_qa.json         # 简单问答
│   ├── instruction_follow.json # 指令遵循
│   └── format_output.json     # 格式输出
├── category_2_intermediate/   # 中等难度
│   ├── multi_step.json        # 多步骤推理
│   ├── context_switch.json    # 上下文切换
│   └── edge_cases.json        # 边界情况
├── category_3_advanced/       # 高难度
│   ├── complex_reasoning.json # 复杂推理
│   ├── tool_integration.json  # 工具集成场景
│   └── error_handling.json    # 错误处理
└── category_4_adversarial/    # 对抗性测试
    ├── ambiguous.json         # 模糊指令
    ├── contradictory.json     # 矛盾要求
    └── injection.json         # 提示注入
```

### 3.2 测试用例格式

每个测试用例应包含：

```json
{
  "id": "test_001",
  "category": "basic_qa",
  "difficulty": "easy",
  "input": {
    "user_message": "用户输入内容",
    "context": "可选的上下文信息",
    "tools_available": ["tool_a", "tool_b"]
  },
  "expected": {
    "answer": "期望的答案",
    "should_use_tools": false,
    "expected_tools": [],
    "format": "json|text|markdown",
    "criteria": ["必须包含X", "不能包含Y"]
  },
  "metadata": {
    "tags": ["tag1", "tag2"],
    "max_tokens": 1000,
    "timeout_seconds": 30
  }
}
```

### 3.3 样本量建议

| 测试类型 | 最少样本量 | 建议样本量 | 说明 |
|----------|-----------|-----------|------|
| 每个子类别 | 20 | 50 | 确保统计显著性 |
| 总计基础测试 | 80 | 200 | 覆盖核心能力 |
| 总计进阶测试 | 60 | 150 | 覆盖边界情况 |
| 总计对抗测试 | 20 | 50 | 鲁棒性验证 |
| **总计** | **160** | **400** | - |

---

## 4. 评估流程

### 4.1 整体流程

```
┌─────────────────────────────────────────────────────────────┐
│                      评估流程                                │
├─────────────────────────────────────────────────────────────┤
│  1. 准备阶段                                                │
│     ├── 构建测试数据集                                       │
│     ├── 定义评估标准                                         │
│     ├── 搭建评估环境                                         │
│     └── 确定统计方法                                         │
│                                                             │
│  2. 执行阶段                                                │
│     ├── v1 运行全部测试用例（每用例 N 次）                    │
│     ├── v2 运行全部测试用例（每用例 N 次）                    │
│     └── 记录所有输出和元数据                                  │
│                                                             │
│  3. 评估阶段                                                │
│     ├── 自动化指标计算                                       │
│     ├── 人工抽样审核                                         │
│     ├── 统计显著性检验                                       │
│     └── 生成评估报告                                         │
│                                                             │
│  4. 分析阶段                                                │
│     ├── 指标对比分析                                         │
│     ├── 错误模式分析                                         │
│     ├── 成本效益分析                                         │
│     └── 最终结论与建议                                       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 详细执行步骤

#### 步骤 1: 准备阶段

```python
# 评估配置示例
eval_config = {
    "model": "gpt-4",  # 或其他被测模型
    "temperature": 0.0,  # 固定温度确保可复现
    "max_tokens": 2048,
    "num_runs_per_case": 3,  # 每个用例运行次数（用于计算一致性）
    "random_seed": 42,
    "timeout_seconds": 60,
    "eval_model": "gpt-4",  # 用于自动评估的模型
    "human_review_ratio": 0.1  # 人工审核比例
}
```

#### 步骤 2: 运行测试

```python
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TestResult:
    test_id: str
    version: str  # "v1" or "v2"
    run_number: int
    input_data: Dict[str, Any]
    output: str
    tools_used: List[str]
    token_count: int
    latency_ms: float
    success: bool
    error_message: str = ""

def run_evaluation(agent_v1, agent_v2, test_cases: List[Dict], config: Dict):
    """运行完整评估流程"""
    results = []

    for case in test_cases:
        for run in range(config["num_runs_per_case"]):
            # 运行 v1
            result_v1 = run_single_test(agent_v1, case, "v1", run)
            results.append(result_v1)

            # 运行 v2
            result_v2 = run_single_test(agent_v2, case, "v2", run)
            results.append(result_v2)

    return results

def run_single_test(agent, test_case: Dict, version: str, run_number: int) -> TestResult:
    """运行单个测试用例"""
    start_time = time.time()

    try:
        response = agent.run(
            message=test_case["input"]["user_message"],
            context=test_case["input"].get("context"),
            tools=test_case["input"].get("tools_available", [])
        )

        latency = (time.time() - start_time) * 1000

        return TestResult(
            test_id=test_case["id"],
            version=version,
            run_number=run_number,
            input_data=test_case["input"],
            output=response.content,
            tools_used=response.tools_called,
            token_count=response.total_tokens,
            latency_ms=latency,
            success=True
        )

    except Exception as e:
        return TestResult(
            test_id=test_case["id"],
            version=version,
            run_number=run_number,
            input_data=test_case["input"],
            output="",
            tools_used=[],
            token_count=0,
            latency_ms=(time.time() - start_time) * 1000,
            success=False,
            error_message=str(e)
        )
```

#### 步骤 3: 自动化评估

```python
from enum import Enum
from typing import Optional

class ScoreLevel(Enum):
    EXCELLENT = 1.0
    GOOD = 0.8
    PARTIAL = 0.5
    POOR = 0.2
    FAIL = 0.0

def evaluate_result(result: TestResult, expected: Dict, eval_model) -> Dict[str, float]:
    """对单个结果进行多维度评分"""
    scores = {}

    # 1. 任务完成度（使用 LLM-as-Judge）
    scores["task_completion"] = eval_task_completion(
        result.output, expected["answer"], eval_model
    )

    # 2. 准确性
    scores["accuracy"] = eval_accuracy(
        result.output, expected.get("criteria", []), eval_model
    )

    # 3. 格式合规性
    scores["format_compliance"] = eval_format(
        result.output, expected.get("format", "text")
    )

    # 4. 工具使用（仅 v2）
    if expected.get("should_use_tools"):
        scores["tool_usage"] = eval_tool_usage(
            result.tools_used,
            expected.get("expected_tools", []),
            expected.get("tool_params", {})
        )

    # 5. 效率（token 使用）
    scores["efficiency"] = eval_efficiency(
        result.token_count, expected.get("max_tokens", 2048)
    )

    return scores

def eval_task_completion(output: str, expected_answer: str, eval_model) -> float:
    """使用 LLM 评估任务完成度"""
    prompt = f"""
    请评估以下输出是否完成了预期任务。

    预期答案: {expected_answer}
    实际输出: {output}

    评分标准:
    - 1.0: 完全正确，与预期答案语义等价
    - 0.7: 基本正确，有小的表述差异但核心信息正确
    - 0.5: 部分正确，包含部分正确信息但有明显遗漏或错误
    - 0.2: 大部分错误，仅包含少量正确信息
    - 0.0: 完全错误或无关

    请只返回一个 0-1 之间的数字分数。
    """

    response = eval_model.generate(prompt)
    try:
        return float(response.strip())
    except ValueError:
        return 0.0

def eval_tool_usage(actual_tools: List[str], expected_tools: List[str], 
                    expected_params: Dict) -> float:
    """评估工具使用正确性"""
    if not expected_tools:
        return 1.0 if not actual_tools else 0.5  # 不需要工具时，未调用得满分

    # 工具选择正确性
    expected_set = set(expected_tools)
    actual_set = set(actual_tools)

    if not expected_set:
        return 1.0

    # 计算召回率和精确率
    true_positives = len(expected_set & actual_set)
    recall = true_positives / len(expected_set) if expected_set else 0
    precision = true_positives / len(actual_set) if actual_set else 0

    # F1 分数
    if precision + recall == 0:
        return 0.0
    f1 = 2 * (precision * recall) / (precision + recall)

    return f1
```

#### 步骤 4: 统计分析

```python
import numpy as np
from scipy import stats
from typing import Tuple

def statistical_analysis(results_v1: List[Dict], results_v2: List[Dict]) -> Dict:
    """执行统计显著性检验"""

    analysis = {}

    for metric in ["task_completion", "accuracy", "efficiency", "format_compliance"]:
        scores_v1 = [r["scores"][metric] for r in results_v1 if metric in r["scores"]]
        scores_v2 = [r["scores"][metric] for r in results_v2 if metric in r["scores"]]

        if not scores_v1 or not scores_v2:
            continue

        # 描述性统计
        analysis[metric] = {
            "v1": {
                "mean": np.mean(scores_v1),
                "std": np.std(scores_v1),
                "median": np.median(scores_v1),
                "n": len(scores_v1)
            },
            "v2": {
                "mean": np.mean(scores_v2),
                "std": np.std(scores_v2),
                "median": np.median(scores_v2),
                "n": len(scores_v2)
            }
        }

        # 独立样本 t 检验（正态分布）
        t_stat, p_value = stats.ttest_ind(scores_v1, scores_v2)

        # Mann-Whitney U 检验（非参数，不假设正态分布）
        u_stat, u_p_value = stats.mannwhitneyu(scores_v1, scores_v2, alternative='two-sided')

        # 效应量（Cohen's d）
        pooled_std = np.sqrt(
            (np.std(scores_v1)**2 + np.std(scores_v2)**2) / 2
        )
        cohens_d = (np.mean(scores_v2) - np.mean(scores_v1)) / pooled_std if pooled_std > 0 else 0

        analysis[metric]["statistical_tests"] = {
            "t_test": {"statistic": t_stat, "p_value": p_value},
            "mann_whitney_u": {"statistic": u_stat, "p_value": u_p_value},
            "cohens_d": cohens_d,
            "effect_size_interpretation": interpret_effect_size(cohens_d)
        }

        # 置信区间
        ci = stats.t.interval(
            0.95,
            len(scores_v1) + len(scores_v2) - 2,
            loc=np.mean(scores_v2) - np.mean(scores_v1),
            scale=stats.sem(scores_v2 - scores_v1[:len(scores_v2)])
        )
        analysis[metric]["confidence_interval_95"] = ci

    return analysis

def interpret_effect_size(d: float) -> str:
    """解释 Cohen's d 效应量"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"
```

---

## 5. 评估执行方案

### 5.1 运行策略

```python
class EvaluationRunner:
    def __init__(self, config: Dict):
        self.config = config
        self.results = []

    def run_full_evaluation(self, agent_v1, agent_v2, test_dataset: List[Dict]):
        """执行完整评估"""

        # 1. 随机打乱测试顺序（避免顺序偏差）
        import random
        random.seed(self.config["random_seed"])
        shuffled_dataset = test_dataset.copy()
        random.shuffle(shuffled_dataset)

        # 2. 分批次运行（避免 API 限流）
        batch_size = self.config.get("batch_size", 10)
        for i in range(0, len(shuffled_dataset), batch_size):
            batch = shuffled_dataset[i:i+batch_size]
            self._run_batch(agent_v1, agent_v2, batch)

            # 批次间暂停
            if i + batch_size < len(shuffled_dataset):
                time.sleep(self.config.get("batch_delay_seconds", 1))

        return self.results

    def _run_batch(self, agent_v1, agent_v2, batch: List[Dict]):
        """运行单个批次"""
        for case in batch:
            for run in range(self.config["num_runs_per_case"]):
                # v1 运行
                result_v1 = self._execute_test(agent_v1, case, "v1", run)
                self.results.append(result_v1)

                # v2 运行
                result_v2 = self._execute_test(agent_v2, case, "v2", run)
                self.results.append(result_v2)

                # 记录进度
                self._log_progress(case["id"], run)
```

### 5.2 并行执行（可选，加速大规模评估）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_parallel_evaluation(agent_v1, agent_v2, test_cases: List[Dict], 
                           max_workers: int = 5) -> List[TestResult]:
    """并行执行评估（注意 API 并发限制）"""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for case in test_cases:
            for run in range(config["num_runs_per_case"]):
                # 提交 v1 任务
                futures.append(
                    executor.submit(run_single_test, agent_v1, case, "v1", run)
                )
                # 提交 v2 任务
                futures.append(
                    executor.submit(run_single_test, agent_v2, case, "v2", run)
                )

        # 收集结果
        for future in as_completed(futures):
            try:
                result = future.result(timeout=config["timeout_seconds"])
                results.append(result)
            except Exception as e:
                print(f"Task failed: {e}")

    return results
```

---

## 6. 结果分析与报告

### 6.1 报告结构

```python
def generate_evaluation_report(analysis_results: Dict, raw_results: List[Dict]) -> str:
    """生成评估报告"""

    report = """
# Agent 评估报告: v1 vs v2

## 执行摘要

| 指标 | v1 均值 | v2 均值 | 提升幅度 | p 值 | 效应量 | 结论 |
|------|---------|---------|----------|------|--------|------|
"""

    for metric, data in analysis_results.items():
        v1_mean = data["v1"]["mean"]
        v2_mean = data["v2"]["mean"]
        improvement = ((v2_mean - v1_mean) / v1_mean) * 100 if v1_mean > 0 else 0
        p_value = data["statistical_tests"]["t_test"]["p_value"]
        effect_size = data["statistical_tests"]["cohens_d"]
        effect_interp = data["statistical_tests"]["effect_size_interpretation"]

        # 判断是否显著
        significance = "显著" if p_value < 0.05 else "不显著"
        conclusion = f"{significance} ({effect_interp})"

        report += f"| {metric} | {v1_mean:.3f} | {v2_mean:.3f} | {improvement:+.1f}% | {p_value:.4f} | {effect_size:.2f} | {conclusion} |\n"

    report += """

## 详细分析

### 1. 任务完成率
{task_completion_analysis}

### 2. 答案准确率
{accuracy_analysis}

### 3. 响应效率
{efficiency_analysis}

### 4. 工具使用分析（v2 专项）
{tool_usage_analysis}

## 错误模式分析

### v1 常见错误
{v1_error_patterns}

### v2 常见错误
{v2_error_patterns}

## 成本效益分析

| 维度 | v1 | v2 | 差异 |
|------|----|----|------|
| 平均 Token 消耗 | {v1_tokens} | {v2_tokens} | {token_diff} |
| 平均延迟 | {v1_latency}ms | {v2_latency}ms | {latency_diff} |
| API 调用成本 | ${v1_cost} | ${v2_cost} | ${cost_diff} |

## 结论与建议

{conclusion}

## 附录

### A. 测试用例统计
- 总用例数: {total_cases}
- v1 有效结果: {v1_valid}
- v2 有效结果: {v2_valid}

### B. 统计检验详情
{statistical_details}
"""

    return report
```

### 6.2 可视化分析

```python
import matplotlib.pyplot as plt
import seaborn as sns

def create_visualizations(analysis_results: Dict, output_dir: str):
    """生成可视化图表"""

    # 1. 指标对比柱状图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    metrics = list(analysis_results.keys())
    for idx, metric in enumerate(metrics[:4]):
        ax = axes[idx // 2][idx % 2]

        v1_scores = analysis_results[metric]["v1"]["mean"]
        v2_scores = analysis_results[metric]["v2"]["mean"]

        bars = ax.bar(["v1", "v2"], [v1_scores, v2_scores], 
                      color=["#3498db", "#2ecc71"])

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}', ha='center', va='bottom')

        ax.set_title(metric)
        ax.set_ylim(0, 1.1)
        ax.set_ylabel("Score")

    plt.tight_layout()
    plt.savefig(f"{output_dir}/metrics_comparison.png", dpi=150)
    plt.close()

    # 2. 分数分布箱线图
    fig, ax = plt.subplots(figsize=(10, 6))

    data_to_plot = []
    labels = []

    for metric in metrics:
        # 假设我们有原始分数数据
        v1_raw = get_raw_scores(metric, "v1")
        v2_raw = get_raw_scores(metric, "v2")
        data_to_plot.extend([v1_raw, v2_raw])
        labels.extend([f"{metric}\nv1", f"{metric}\nv2"])

    ax.boxplot(data_to_plot, labels=labels)
    ax.set_title("Score Distribution by Metric and Version")
    ax.set_ylabel("Score")

    plt.tight_layout()
    plt.savefig(f"{output_dir}/score_distribution.png", dpi=150)
    plt.close()

    # 3. 按难度级别分析
    fig, ax = plt.subplots(figsize=(10, 6))

    difficulties = ["easy", "medium", "hard"]
    v1_by_diff = []
    v2_by_diff = []

    for diff in difficulties:
        v1_score = get_mean_score_by_difficulty(diff, "v1")
        v2_score = get_mean_score_by_difficulty(diff, "v2")
        v1_by_diff.append(v1_score)
        v2_by_diff.append(v2_score)

    x = np.arange(len(difficulties))
    width = 0.35

    ax.bar(x - width/2, v1_by_diff, width, label='v1', color='#3498db')
    ax.bar(x + width/2, v2_by_diff, width, label='v2', color='#2ecc71')

    ax.set_xlabel('Difficulty Level')
    ax.set_ylabel('Mean Score')
    ax.set_title('Performance by Difficulty Level')
    ax.set_xticks(x)
    ax.set_xticklabels(difficulties)
    ax.legend()

    plt.tight_layout()
    plt.savefig(f"{output_dir}/performance_by_difficulty.png", dpi=150)
    plt.close()
```

---

## 7. 决策框架

### 7.1 综合评分

```python
def calculate_composite_score(analysis_results: Dict, weights: Dict[str, float]) -> Dict:
    """计算加权综合得分"""

    composite_scores = {"v1": 0.0, "v2": 0.0}

    for metric, weight in weights.items():
        if metric in analysis_results:
            composite_scores["v1"] += analysis_results[metric]["v1"]["mean"] * weight
            composite_scores["v2"] += analysis_results[metric]["v2"]["mean"] * weight

    return composite_scores

# 权重配置
weights = {
    "task_completion": 0.30,
    "accuracy": 0.25,
    "efficiency": 0.15,
    "format_compliance": 0.10,
    "tool_usage": 0.10,
    "consistency": 0.10
}
```

### 7.2 决策规则

```python
def make_decision(analysis_results: Dict, composite_scores: Dict) -> Dict:
    """基于评估结果做出决策"""

    decision = {
        "recommendation": None,
        "confidence": None,
        "reasoning": [],
        "conditions": []
    }

    v1_score = composite_scores["v1"]
    v2_score = composite_scores["v2"]
    improvement = v2_score - v1_score

    # 规则 1: 统计显著性
    significant_improvements = 0
    for metric, data in analysis_results.items():
        if data["statistical_tests"]["t_test"]["p_value"] < 0.05:
            if data["v2"]["mean"] > data["v1"]["mean"]:
                significant_improvements += 1

    # 规则 2: 效应量
    large_effects = 0
    for metric, data in analysis_results.items():
        if data["statistical_tests"]["effect_size_interpretation"] in ["medium", "large"]:
            large_effects += 1

    # 规则 3: 成本效益
    token_increase = analysis_results.get("efficiency", {}).get("v2", {}).get("mean", 0) - \
                     analysis_results.get("efficiency", {}).get("v1", {}).get("mean", 0)

    # 决策逻辑
    if improvement > 0.1 and significant_improvements >= 2:
        decision["recommendation"] = "ADOPT_V2"
        decision["confidence"] = "HIGH"
        decision["reasoning"].append(f"v2 综合得分提升 {improvement:.1%}")
        decision["reasoning"].append(f"{significant_improvements} 个指标有统计显著提升")

    elif improvement > 0.05 and significant_improvements >= 1:
        decision["recommendation"] = "CONDITIONALLY_ADOPT_V2"
        decision["confidence"] = "MEDIUM"
        decision["reasoning"].append(f"v2 有一定提升但幅度有限")
        decision["conditions"].append("建议进一步优化 few-shot examples")

    elif improvement < -0.05:
        decision["recommendation"] = "KEEP_V1"
        decision["confidence"] = "HIGH"
        decision["reasoning"].append("v2 表现不如 v1")

    else:
        decision["recommendation"] = "NEED_MORE_DATA"
        decision["confidence"] = "LOW"
        decision["reasoning"].append("两个版本差异不明显")

    return decision
```

### 7.3 决策矩阵

| 场景 | 综合提升 | 统计显著 | 效应量 | 成本增加 | 建议 |
|------|----------|----------|--------|----------|------|
| A | >10% | >=2 指标 | 中/大 | <20% | 全面采用 v2 |
| B | >10% | >=2 指标 | 中/大 | >20% | 评估成本效益后决定 |
| C | 5-10% | >=1 指标 | 小/中 | 任意 | 有条件采用，持续优化 |
| D | <5% | 不显著 | 微小 | 任意 | 保持 v1，收集更多数据 |
| E | 负值 | 显著下降 | 任意 | 任意 | 保持 v1，分析 v2 失败原因 |

---

## 8. 实施检查清单

### 8.1 评估前准备

- [ ] 确定评估目标和成功标准
- [ ] 构建测试数据集（至少 160 个用例）
- [ ] 定义评估指标和权重
- [ ] 准备 v1 和 v2 的 Agent 实现
- [ ] 搭建评估环境和监控
- [ ] 确定人工审核人员和流程

### 8.2 评估执行

- [ ] 设置固定的随机种子和温度参数
- [ ] 运行完整测试套件（每用例至少 3 次）
- [ ] 记录所有输出、元数据和错误
- [ ] 执行自动化指标计算
- [ ] 进行人工抽样审核（至少 10% 的结果）

### 8.3 结果分析

- [ ] 计算各指标的描述性统计
- [ ] 执行统计显著性检验（t 检验和 Mann-Whitney U）
- [ ] 计算效应量（Cohen's d）
- [ ] 生成置信区间
- [ ] 分析错误模式和失败案例
- [ ] 进行成本效益分析

### 8.4 报告与决策

- [ ] 生成完整的评估报告
- [ ] 创建可视化图表
- [ ] 形成明确的决策建议
- [ ] 记录改进建议和后续计划
- [ ] 与相关方沟通评估结果

---

## 9. 注意事项与最佳实践

### 9.1 避免常见陷阱

1. **评估偏差**
   - 确保测试数据集覆盖各种场景，避免选择偏差
   - 使用盲评（评估者不知道结果来自哪个版本）
   - 随机化测试顺序，避免顺序效应

2. **样本量不足**
   - 每个子类别至少 20 个用例
   - 每个用例运行至少 3 次以计算一致性
   - 总样本量应足够进行统计检验（建议 160+）

3. **指标选择偏差**
   - 不要只看单一指标，使用多维度评估
   - 平衡准确性与效率的权衡
   - 考虑实际业务场景的需求

4. **过拟合测试集**
   - 保留独立的验证集
   - 避免根据测试结果反复调整 Agent
   - 使用交叉验证（如果样本量允许）

### 9.2 确保可复现性

```python
# 记录完整的评估配置
eval_manifest = {
    "timestamp": datetime.now().isoformat(),
    "config": eval_config,
    "test_dataset_hash": hashlib.md5(json.dumps(test_dataset).encode()).hexdigest(),
    "agent_v1_config": agent_v1.get_config(),
    "agent_v2_config": agent_v2.get_config(),
    "environment": {
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependencies": get_installed_packages()
    }
}

# 保存到文件
with open("eval_manifest.json", "w") as f:
    json.dump(eval_manifest, f, indent=2)
```

### 9.3 持续改进

评估不是一次性的活动。建议：

1. 建立持续评估机制，定期重新评估
2. 收集真实用户反馈，补充自动化评估
3. 根据评估结果迭代优化 Agent
4. 扩展测试数据集，覆盖新发现的边界情况
5. 尝试不同的 few-shot examples 组合，找到最优方案

---

## 10. 快速启动脚本

```python
#!/usr/bin/env python3
"""Agent 评估快速启动脚本"""

import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Agent v1 vs v2 评估工具")
    parser.add_argument("--config", type=str, default="eval_config.json",
                       help="评估配置文件路径")
    parser.add_argument("--dataset", type=str, default="test_dataset.json",
                       help="测试数据集路径")
    parser.add_argument("--output", type=str, default="eval_results",
                       help="输出目录")
    parser.add_argument("--quick", action="store_true",
                       help="快速模式（减少样本量）")

    args = parser.parse_args()

    # 加载配置
    with open(args.config) as f:
        config = json.load(f)

    # 加载数据集
    with open(args.dataset) as f:
        dataset = json.load(f)

    # 快速模式调整
    if args.quick:
        config["num_runs_per_case"] = 1
        dataset = dataset[:50]  # 只使用前 50 个用例
        print("Running in quick mode with reduced sample size")

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 初始化 Agent
    agent_v1 = initialize_agent_v1(config)
    agent_v2 = initialize_agent_v2(config)

    # 运行评估
    print("Starting evaluation...")
    runner = EvaluationRunner(config)
    results = runner.run_full_evaluation(agent_v1, agent_v2, dataset)

    # 分析结果
    print("Analyzing results...")
    results_v1 = [r for r in results if r.version == "v1"]
    results_v2 = [r for r in results if r.version == "v2"]
    analysis = statistical_analysis(results_v1, results_v2)

    # 生成报告
    print("Generating report...")
    report = generate_evaluation_report(analysis, results)

    # 保存结果
    with open(output_dir / "report.md", "w") as f:
        f.write(report)

    with open(output_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    # 生成可视化
    create_visualizations(analysis, str(output_dir))

    # 输出决策
    composite_scores = calculate_composite_score(analysis, weights)
    decision = make_decision(analysis, composite_scores)

    print("\n" + "="*50)
    print("EVALUATION COMPLETE")
    print("="*50)
    print(f"\nRecommendation: {decision['recommendation']}")
    print(f"Confidence: {decision['confidence']}")
    print(f"\nReasoning:")
    for reason in decision["reasoning"]:
        print(f"  - {reason}")
    if decision["conditions"]:
        print(f"\nConditions:")
        for condition in decision["conditions"]:
            print(f"  - {condition}")

    print(f"\nFull report saved to: {output_dir / 'report.md'}")

if __name__ == "__main__":
    main()
```

---

## 11. 总结

本评估方案提供了：

1. **科学的指标体系** - 多维度评估，避免单一指标偏差
2. **严谨的统计方法** - 显著性检验和效应量分析
3. **完整的执行流程** - 从数据准备到决策输出
4. **实用的工具代码** - 可直接使用的评估框架
5. **明确的决策规则** - 基于数据的客观决策

通过这套方案，你可以：
- 客观量化 v2 相比 v1 的提升幅度
- 判断提升是否具有统计显著性
- 分析 v2 的优势和不足
- 做出数据驱动的版本选择决策

**关键成功因素**：
- 足够的样本量（160+ 测试用例）
- 多次运行计算一致性（每用例 3+ 次）
- 多维度指标综合评估
- 结合人工审核验证自动评估结果
