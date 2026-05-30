# 开发者指南

本项目的工作原理 — 技能如何创建、验证和评估。

## 指南

| 指南 | 内容 |
|------|------|
| [如何创建技能](how-to-write-a-skill.md) | 使用 /skill-creator 创建，目录结构，SKILL.md 规范 |
| [验证机制](how-validation-works.md) | validate_skills.py 检查项，CI 流水线，常见错误修复 |
| [技能效果评估](how-to-evaluate-skill-changes.md) | with-skill vs without-skill 对比，断言设计，LLM-as-Judge，基准聚合 |

## 快速参考

```bash
# 验证所有技能
python scripts/validate_skills.py

# 运行测试
pytest tests/ -v

# 创建新技能
/skill-creator

# 评估技能效果
# 1. 创建 evals/evals.json
# 2. 运行 with-skill 和 without-skill 代理
# 3. 用断言评分
# 4. 聚合基准数据
# 5. 用 eval viewer 审查结果
```
