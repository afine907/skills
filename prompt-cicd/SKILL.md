---
name: prompt-cicd
description: |
  【Prompt CI/CD】Prompt 即代码：版本控制、回归测试、A/B 对比、部署流水线。触发时机：用户说"prompt 版本管理"、"prompt 测试"、"prompt CI/CD"时。
category: development
---

# Prompt CI/CD — Prompt 即代码管理

将 Prompt 视为第一类代码制品，提供完整的生命周期管理。

> **核心洞察：** 没有自动测试套件能捕获过时的 Prompt。没有编译器告诉你业务逻辑不一致。当系统变化时，Prompt 必须由理解模型推理模式和系统新行为的人手动更新。这是最脆弱的架构模式。


## Goal

将 Prompt 作为代码管理：版本控制、回归测试、A/B 对比、部署流水线。解决"Prompt 即架构"风险

## Trigger

- 用户说"prompt 版本管理"、"prompt 测试"、"prompt CI/CD"、"prompt 回归"
  - Prompt 是关键业务逻辑，需要变更管理
  - 团队需要协作开发 Prompt
  - Prompt 变更需要测试后才能部署

## 工作流程

```
提取 Prompt → 版本管理 → 构建测试套件 → 搭建回归流水线 → 部署+回滚
```

## Step 1: Prompt 盘点与提取

### 发现 Prompt 的位置

Prompt 通常散落在代码库各处：

| 位置 | 形式 | 提取策略 |
|------|------|---------|
| 源代码内联 | 字符串常量、模板字符串 | 提取到独立文件 |
| 配置文件 | JSON/YAML 中的字段 | 保留结构，提取 Prompt 部分 |
| 环境变量 | `SYSTEM_PROMPT` 等 | 替换为文件引用 |
| 数据库 | 动态加载的 Prompt | 导出为版本管理文件 |
| 前端代码 | 用户可见的 Prompt 模板 | 提取到共享目录 |

### 关键性分级

| 级别 | 定义 | 管理方式 |
|------|------|---------|
| **Critical** | 直接影响输出质量的核心 Prompt（系统提示、角色定义） | 完整回归测试 + A/B 对比 |
| **Important** | 影响特定功能的 Prompt（工具描述、格式约束） | 回归测试 |
| **Low** | 辅助性 Prompt（提示文本、错误消息） | 基本格式检查 |

## Step 2: 版本控制目录结构

```
prompts/
├── system/
│   ├── v1/
│   │   ├── system.md              # 系统提示正文
│   │   ├── tool-descriptions.md   # 工具描述
│   │   └── metadata.json          # 模型、温度、max_tokens
│   └── v2/
│       ├── system.md
│       ├── tool-descriptions.md
│       └── metadata.json
├── templates/
│   ├── customer-support.md
│   ├── data-analysis.md
│   └── code-generation.md
├── evals/
│   ├── test-cases.json            # 测试用例集
│   ├── baselines/                 # 基线评分
│   │   ├── v1-scores.json
│   │   └── v2-scores.json
│   └── regressions/               # 回归记录
│       └── 2026-05-29-v1-to-v2.json
├── changelog.md                   # Prompt 变更日志
└── README.md                      # 目录说明和使用指南
```

### metadata.json 格式

```json
{
  "version": "v2",
  "model": "claude-sonnet-4",
  "temperature": 0.7,
  "max_tokens": 4096,
  "created": "2026-05-29",
  "author": "team-name",
  "criticality": "critical",
  "changelog": "改进了工具选择的准确性，增加了错误处理指导"
}
```

## Step 3: 回归测试套件

### 测试用例类型

| 类型 | 目的 | 数量建议 |
|------|------|---------|
| **黄金测试** | 已知正确的输入/输出对 | Critical Prompt 10+ 个 |
| **格式合规** | 输出符合预期 Schema | 每种输出格式 3+ 个 |
| **安全测试** | 拒绝有害请求 | 10+ 个攻击向量 |
| **性能基准** | 延迟和 Token 消耗 | 每个模板 3+ 个 |
| **边界情况** | 极端输入处理 | 每类边界 2+ 个 |

### 测试用例格式

```json
{
  "test_id": "prompt-regression-001",
  "prompt_version": "v2",
  "input": "用户的输入",
  "expected_properties": {
    "contains": ["必须包含的关键词"],
    "not_contains": ["不能包含的内容"],
    "format": "json | markdown | plain",
    "max_tokens": 500,
    "safety": "must_refuse | must_comply"
  },
  "scoring_rubric": {
    "relevance": "回答是否相关",
    "accuracy": "信息是否准确",
    "tone": "语气是否符合品牌"
  },
  "pass_threshold": 0.85
}
```

### 回归测试执行

```
对每个 Prompt 版本变更:
  1. 运行黄金测试 → 验证核心行为未退化
  2. 运行格式测试 → 验证输出格式未变化
  3. 运行安全测试 → 验证安全防线未削弱
  4. 运行性能测试 → 验证延迟和成本未恶化
  5. 与基线对比 → 生成回归报告
```

## Step 4: A/B 对比框架

### 对比维度

| 维度 | 评估方式 | 权重 |
|------|---------|------|
| **输出质量** | LLM-as-Judge 评分 | 40% |
| **格式合规** | 自动 Schema 验证 | 20% |
| **安全性** | 安全测试通过率 | 20% |
| **性能** | 延迟 + Token 消耗 | 10% |
| **成本** | 每调用成本 | 10% |

### 统计显著性

```
对同一测试集运行两个版本:
  每个用例运行 5 次 → 计算通过率
  配对比较 → 计算置信区间
  if 置信区间完全低于零 → 新版本存在回归
  if 置信区间完全高于零 → 新版本有改进
  if 置信区间包含零 → 无显著差异
```

### 对比报告模板

```markdown
# Prompt A/B 对比报告

## 版本对比
- 版本 A：v1（当前生产版本）
- 版本 B：v2（候选版本）
- 测试用例数：50
- 每用例运行次数：5

## 结果摘要

| 维度 | v1 均分 | v2 均分 | 差值 | 95% CI | 结论 |
|------|--------|--------|------|--------|------|
| 输出质量 | 8.2 | 8.5 | +0.3 | [+0.1, +0.5] | 改进 ✓ |
| 格式合规 | 95% | 93% | -2% | [-5%, +1%] | 无显著差异 |
| 安全性 | 98% | 98% | 0% | [-2%, +2%] | 无显著差异 |
| 延迟 | 1.8s | 2.1s | +0.3s | [+0.1, +0.5] | 退化 ⚠️ |

## 结论
v2 在输出质量上有显著改进，但延迟略有增加。建议部署 v2 但监控延迟指标。
```

## Step 5: 部署流水线

### CI/CD 阶段

```
PR 提交
  → [Pre-commit] Lint Prompt 模板（格式检查、无硬编码密钥）
  → [PR Gate] 运行回归测试 + 与基线对比
  → [Staging] 用真实 LLM 运行完整测试套件
  → [灰度发布] 5% 流量使用新版本
  → [监控] 对比新旧版本的质量指标
  → [全量发布] 或 [回滚]
```

### CI 配置模板（GitHub Actions）

```yaml
name: Prompt Regression Tests
on:
  pull_request:
    paths:
      - 'prompts/**'

jobs:
  prompt-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run prompt regression suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/run_prompt_evals.py \
            --prompt-dir prompts/ \
            --eval-set evals/test-cases.json \
            --baseline evals/baselines/current.json \
            --threshold 0.85
```

### 关键配置

- **Path-scoped triggers** — 仅 Prompt 文件变更才触发评估，节省 Judge Token
- **Concurrency control** — 同一 PR 的多次 push 取消之前的运行
- **Matrix sharding** — 按 Prompt 类型分片并行运行

## Step 6: 回滚与热修复

### 回滚流程

```
检测到生产环境质量退化
  → 确认退化原因（Prompt 变更 vs 模型变化 vs 数据变化）
  → 如果是 Prompt 变更:
    → 回滚到上一个已验证版本
    → 验证回滚后质量恢复
    → 分析退化原因
    → 修复后重新走完整流水线
```

### 紧急热修复

```
如果需要紧急修复:
  1. 从当前生产版本创建热修复分支
  2. 最小化修改（只修复问题，不做其他改动）
  3. 运行核心黄金测试（非完整套件）
  4. 部署到灰度环境
  5. 验证后全量发布
  6. 后续补充完整测试
```

## 快速使用

```
用户：我们的客服 Prompt 经常被修改，每次修改都担心会退化
助手：使用 /prompt-cicd 建立 Prompt 版本管理、回归测试和部署流水线
```

## 输出模板

Claude 生成 Prompt 管理方案时，按以下格式输出：

```
## Prompt CI/CD 方案报告

### Prompt 盘点
| Prompt 名称 | 位置 | 关键性 | 当前版本 |
|-------------|------|--------|---------|
| system-prompt | 源代码内联 | Critical | 无版本管理 |
| ... | ... | ... | ... |

### 目录结构
（展示 prompts/ 目录结构）

### 测试套件
- 黄金测试用例数：{N}
- 格式测试用例数：{N}
- 安全测试用例数：{N}

### CI 流水线
（展示 GitHub Actions YAML 配置）

### 部署流程
PR → 回归测试 → Staging → 灰度发布 → 全量发布

### 后续步骤
1. 从源代码中提取 Prompt 到 prompts/ 目录
2. 为每个 Critical Prompt 编写黄金测试用例
3. 配置 CI 流水线
4. 设置灰度发布策略
```

**端到端示例：**

用户输入：`我们的客服 Prompt 经常被修改，每次修改都担心会退化`

Claude 输出以上模板，包含 Prompt 目录结构、metadata.json 格式、回归测试用例模板、GitHub Actions CI 配置、A/B 对比报告模板等。

## 不适用

- 单次 Prompt 调试 → 直接修改即可，不需要 CI/CD
- 非 LLM 系统的配置管理 → 使用传统 CI/CD 工具（Jenkins / GitHub Actions 标准流水线）
- Prompt 数量少于 5 个 → 简单版本管理（git commit + tag）即可

## 边界情况

- **多模型 Prompt** — 同一 Prompt 需要在多个模型上测试（Claude、GPT、Gemini）
- **动态 Prompt** — 运行时根据条件组装的 Prompt，需要测试各种组合
- **Prompt 链** — 多个 Prompt 串联执行，需要测试端到端流程
- **带运行时变量的 Prompt** — 模板中的变量需要在测试时填充

## 与其他技能的协作

- `prompt-engineering` — 用此技能设计的 Prompt 进入 prompt-cicd 管理
- `agent-eval` — 回归测试框架与评估框架共享测试用例和评分标准
- `ci-workflow` — 流水线模板扩展 CI 模式到 Prompt 专用门禁
- `test-generator` — 自动为 Prompt 生成测试用例的模式
