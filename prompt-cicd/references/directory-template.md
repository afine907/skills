# Prompt 仓库标准目录结构

## 完整目录结构

```
prompts/
├── README.md                      # 目录说明、使用指南、贡献规范
├── changelog.md                   # Prompt 变更日志（Keep a Changelog 格式）
│
├── system/                        # 系统提示
│   ├── v1/
│   │   ├── system.md              # 系统提示正文
│   │   ├── tool-descriptions.md   # 工具描述
│   │   ├── constraints.md         # 行为约束
│   │   └── metadata.json          # 版本元数据
│   └── v2/
│       ├── system.md
│       ├── tool-descriptions.md
│       ├── constraints.md
│       └── metadata.json
│
├── templates/                     # 功能模板
│   ├── customer-support.md
│   ├── data-analysis.md
│   ├── code-generation.md
│   └── summarization.md
│
├── evals/                         # 评估测试
│   ├── test-cases.json            # 测试用例集
│   ├── expected-outputs.json      # 预期输出（可选）
│   ├── baselines/                 # 基线评分
│   │   ├── v1-scores.json
│   │   └── v2-scores.json
│   ├── regressions/               # 回归记录
│   │   └── 2026-05-29-v1-to-v2.json
│   └── security/                  # 安全测试
│       ├── injection-tests.json
│       └── pii-tests.json
│
├── scripts/                       # 工具脚本
│   ├── run_evals.py               # 运行评估
│   ├── compare_versions.py        # 版本对比
│   └── lint_prompts.py            # Prompt Lint
│
└── .github/                       # CI/CD 配置
    └── workflows/
        └── prompt-regression.yml
```

## README.md 模板

```markdown
# Prompt Management

本目录管理所有 LLM Prompt 的版本、测试和部署。

## 目录结构

- `system/` — 系统提示，按版本组织
- `templates/` — 功能模板
- `evals/` — 测试用例和基线
- `scripts/` — 工具脚本

## 变更流程

1. 在对应版本目录下修改 Prompt
2. 更新 metadata.json 的 changelog
3. 运行回归测试：`python scripts/run_evals.py`
4. 提交 PR，等待 CI 通过
5. 合并后自动部署到灰度环境

## 版本命名

- 主版本：v1, v2, v3...（重大变更）
- 热修复：v1.1, v1.2...（小修复）

## 关键性分级

- **Critical** — 系统提示，完整回归测试 + A/B 对比
- **Important** — 功能模板，回归测试
- **Low** — 辅助文本，基本格式检查
```

## metadata.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "model", "created", "criticality"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^v[0-9]+(\\.[0-9]+)?$",
      "description": "版本号"
    },
    "model": {
      "type": "string",
      "description": "目标模型"
    },
    "temperature": {
      "type": "number",
      "minimum": 0,
      "maximum": 2,
      "default": 0.7
    },
    "max_tokens": {
      "type": "integer",
      "minimum": 1,
      "default": 4096
    },
    "created": {
      "type": "string",
      "format": "date"
    },
    "author": {
      "type": "string"
    },
    "criticality": {
      "type": "string",
      "enum": ["critical", "important", "low"]
    },
    "changelog": {
      "type": "string"
    },
    "parent_version": {
      "type": "string",
      "description": "基于哪个版本创建"
    }
  }
}
```
