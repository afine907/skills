# 技能效果评估

本文档介绍如何测试技能是否真正有效 — 使用自动化评估和 LLM-as-Judge 评分。

## 为什么要评估？

技能是提示模板。修改一个提示可能改善某方面，同时破坏另一方面。没有评估就是在猜。有了评估就有数据。

**核心问题：** 使用技能后的输出是否比不使用时更好？

## 评估方法论

### with-skill vs without-skill 对比

每次评估比较两种配置：

| 配置 | 做法 |
|------|------|
| **with-skill** | 代理先读 SKILL.md，再完成任务 |
| **without-skill** | 代理不读技能，直接完成同一任务（基线） |

如果 with-skill 评分没有更高，说明技能没有帮助。

### 测试用例结构

测试用例放在每个技能目录的 `evals/evals.json` 中：

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 0,
      "prompt": "用自然语言描述的用户任务",
      "expected_output": "输出应包含的内容",
      "files": []
    }
  ]
}
```

**编写好的测试用例：**
- 使用真实场景，不要用玩具例子
- 任务要具体到可以客观评估
- 包含测试技能价值的边界情况

### 断言

断言定义了"好输出"长什么样。每个 eval 的元数据中包含断言：

```json
{
  "text": "has_retry_strategy",
  "description": "包含指数退避的重试逻辑"
}
```

**编写有区分力的断言：**

差的断言（两种配置都能通过）：
```
"has_error_handling" — 太模糊，任何合格的回答都会包含错误处理
```

好的断言（只有 with-skill 能通过）：
```
"has_circuit_breaker_code" — 需要具体的断路器实现代码，
而不是仅仅提到这个概念
```

目标是编写技能独有的断言，而不是任何好回答都会包含的东西。

## 评估流程

### 第 1 步：创建评估测试用例

```bash
mkdir -p my-skill/evals
cat > my-skill/evals/evals.json << 'EOF'
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 0,
      "prompt": "具体任务描述",
      "expected_output": "好输出应包含的内容",
      "files": []
    }
  ]
}
EOF
```

### 第 2 步：运行 with-skill 和 without-skill

为每个 eval 启动两个代理：
- **with-skill**：读取 `my-skill/SKILL.md`，然后完成任务
- **without-skill**：不读技能，直接完成任务

输出保存到：
```
my-skill-workspace/iteration-1/eval-0/
├── eval_metadata.json
├── with_skill/outputs/solution.md
└── without_skill/outputs/solution.md
```

### 第 3 步：用断言评分

对每个 eval，检查每条断言在两种输出中的表现：

```json
{
  "eval_id": 0,
  "with_skill": {
    "assertions": [
      {"text": "has_retry_strategy", "passed": true, "evidence": "指数退避，3次重试"}
    ],
    "pass_rate": 1.0
  },
  "without_skill": {
    "assertions": [
      {"text": "has_retry_strategy", "passed": false, "evidence": "未提及重试逻辑"}
    ],
    "pass_rate": 0.0
  }
}
```

### 第 4 步：聚合基准数据

将所有 eval 评分合并为基准摘要：

```json
{
  "run_summary": {
    "with_skill": {"pass_rate": {"mean": 1.0, "stddev": 0.0}},
    "without_skill": {"pass_rate": {"mean": 0.6, "stddev": 0.1}},
    "delta": {"pass_rate": "+0.40"}
  }
}
```

### 第 5 步：用 eval viewer 审查

生成 HTML 页面来对比审查输出：

```bash
python skill-creator/eval-viewer/generate_review.py \
  my-skill-workspace/iteration-1 \
  --skill-name "my-skill" \
  --benchmark my-skill-workspace/iteration-1/benchmark.json \
  --static my-skill-workspace/iteration-1/viewer.html
```

## 统计注意事项

LLM 输出是非确定性的。单次运行不能证明什么。

**最佳实践：**
- 每个测试用例运行 3-5 次
- 报告均值 ± 标准差，不要只报告单次值
- 使用行为属性检查，不要用精确字符串匹配
- 5 次运行中 +20% 通过率是有意义的；一次完美运行不算

## LLM-as-Judge

对于主观质量维度（连贯性、完整性），使用 LLM 作为评判者：

```
给定任务：{task_description}
给定输出：{agent_output}

按以下维度评分：
1. 完整性 (0-10)：是否覆盖了任务的所有方面？
2. 准确性 (0-10)：信息是否正确？
3. 清晰度 (0-10)：结构是否清晰，易于理解？

返回 JSON：{"completeness": N, "accuracy": N, "clarity": N}
```

**校准：** 先用 5-10 个已知好/差的输出测试评判者。如果评分不符合预期，调整评分标准。

## 效果判断

| 通过率差距 | 解读 |
|-----------|------|
| +30% 以上 | 技能非常有效 |
| +10% ~ +30% | 技能有明显价值 |
| +0% ~ +10% | 边际收益 — 考虑复杂度是否值得 |
| 0% | 技能无效 — 重新设计或移除 |
| 负数 | 技能有害 — 立即移除 |
