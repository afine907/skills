---
name: self-improve
description: >
  用户纠正AI时的经验固化。当用户说"记住这个"、"这个不对"、"以后别这样"、"写到规则里"、"记一下"时触发。
  诊断"为什么会执行不对"（CLAUDE.md缺规则/rules写得不好/没有记忆），将结构化教训写入正确位置，
  确保错误不贰过。也适用于复盘、总结经验、记录教训等场景。
---

# Self-Improve — 经验固化

## 目标

当用户纠正AI时，记录这次纠正过程，确保未来会话不再犯同样的错误。

## 触发时机

用户说出以下任一关键词时触发：
- 记住这个、记一下、以后注意、别再犯
- 写到规则里、这个不对、别这样做
- 复盘、总结经验、记录教训、retrospective

## 执行流程

**重要：所有写入操作优先使用当前项目目录（如 `d:\Code\jojo-code\.claude\`），而非全局目录（`~/.claude/`）**

### Step 1: 解析用户意图

从当前对话上下文中提取：
- 用户想记住什么？（错误现象 / 正确做法 / 规则）
- 用户给出了什么具体信息？

### Step 2: 诊断"为什么会执行不对"

检查以下位置，找出根因：

| 位置 | 检查内容 |
|------|----------|
| 项目 CLAUDE.md | 是否缺少这条规则？ |
| 项目 .claude/rules/ | 是否有规则但写得不够清晰？ |
| 全局 .claude/memory/ | 是否有记忆但没被触发？ |
| Skill 定义 | 是否 skill 没有覆盖这个场景？ |
| 代码本身 | 是否是代码设计问题？ |

输出诊断结果：
- 根因是什么（CLAUDE.md缺规则 / rules写得不好 / 没有记忆...）
- 应该写入哪个位置

### Step 3: 提取结构化教训

使用以下格式提取教训（每条控制在 5 行以内）：

```markdown
### [简短标题]
- **错误**: 描述发生了什么
- **原因**: 根本原因分析
- **正确做法**: 标准操作流程
- **场景**: 适用条件
- **来源**: 日期
```

### Step 3.5: 去重检查

写入前执行以下检查：
1. 读取项目 CLAUDE.md，搜索是否有相似条目
2. 读取 `.claude/rules/` 下所有文件，搜索是否有相似条目
3. 如果找到相似内容 → 更新现有条目，而非新增
4. 如果未找到 → 新增到对应位置

### Step 4: 写入对应位置

根据诊断结论选择写入位置。详见 [references/write-locations.md](references/write-locations.md)。

写入时使用对应格式模板，详见 [references/rules-templates.md](references/rules-templates.md)。

**格式要求**：
- 始终加载规则：无 frontmatter
- 懒加载规则：使用 `globs` + `alwaysApply: false`
- 参考官方文档：https://code.claude.com/docs/zh-CN/memory#使用-clauderules-组织规则

### Step 5: 记录本次复盘会话

将复盘过程写入项目 `.claude/retrospectives/` 目录。

1. 创建目录（如不存在）：`mkdir -p .claude/retrospectives/`
2. 生成文件名：`YYYY-MM-DD-<简短描述>.md`
3. 使用复盘模板写入，详见 [references/retrospective-template.md](references/retrospective-template.md)

### Step 6: 确认写入成功

- 告诉用户根因是什么
- 告诉用户写入了哪个文件
- 展示写入的内容
- 告诉用户未来如何自动应用这条规则

## 输出示例

### 示例 1：通用规则（始终加载）

```markdown
## 诊断结果

用户说："记住这个：以后用 asyncio.to_thread 而不是 run_in_executor"

**根因**: CLAUDE.md 中没有关于异步执行的规则

**写入位置**: `.claude/rules/general.md`（无 globs，始终加载）

## 写入内容

### 异步任务执行
- **错误**: 使用 `asyncio.get_event_loop().run_in_executor()`
- **原因**: 这是旧写法，Python 3.12+ 已废弃
- **正确做法**: 使用 `asyncio.to_thread()` 执行同步代码
- **场景**: 在 async handler 中需要调用同步函数时
- **来源**: 2026-05-23

---
```

### 示例 2：专项规则（懒加载）

```markdown
## 诊断结果

用户说："记住：CI 中 Node.js 要用 22 版本"

**根因**: `.claude/rules/` 缺少 CI/CD 相关规则

**写入位置**: `.claude/rules/ci-cd.md`（使用 globs 懒加载）

## 写入内容

文件内容：
---
description: "CI/CD 相关规则"
globs: [".github/workflows/*.yml", "Makefile"]
alwaysApply: false
---

### Node.js 版本
- **错误**: pnpm install 失败
- **原因**: pnpm 11+ 需要 Node.js >= 22.13
- **正确做法**: 使用 `node-version: '22'`
- **场景**: CI 中使用 pnpm 时
- **来源**: 2026-05-30

---
```

## 与其他 Skill 的协作

- **验牌 (wo-yao-yan-pai)**: 验牌发现问题后，可以用 self-improve 记录教训
- **commit**: 提交前的检查清单可以引用 self-improve 积累的经验

## 注意事项

1. **去重**: 写入前必须执行 Step 3.5 去重检查，避免重复
2. **精简**: 每条教训控制在 5 行以内，太长没人看
3. **可操作**: "正确做法"必须是具体的命令或步骤，不是抽象建议
4. **溯源**: 标注来源（日期），方便追溯
5. **格式正确**: 使用 `globs` 字段（不是 `paths`），格式为 JSON 数组：
   ```yaml
   globs: ["**/*.ts", "**/*.tsx"]
   alwaysApply: false
   ```
