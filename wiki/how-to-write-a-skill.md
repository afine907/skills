# 如何创建技能

## 创建新技能

使用 `/skill-creator` 命令创建技能。它会引导你完成：

1. 描述技能意图
2. 生成 SKILL.md 和 references/
3. 创建评估测试用例 (evals/evals.json)
4. 运行 with-skill / without-skill 对比测试
5. LLM-as-Judge 评分
6. 迭代优化

```bash
# 在 Claude Code 中直接调用
/skill-creator
```

## 技能目录结构

```
my-skill/
├── SKILL.md            # 必须 — 技能定义
├── references/         # 可选 — 详细参考文档
└── evals/              # 可选 — 评估测试用例
    └── evals.json
```

## SKILL.md 规范

详见 [验证机制](how-validation-works.md) 了解 frontmatter 字段规则和验证要求。

## 评估技能效果

详见 [技能效果评估](how-to-evaluate-skill-changes.md) 了解 with-skill vs without-skill 对比方法。
