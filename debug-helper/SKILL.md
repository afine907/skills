---
name: debug-helper
description: |
  结构化调试分析。固定 5 步分析框架：定位 → 上下文 → 假设 → 验证 → 修复。
  适用场景：
  - 用户贴错误信息 / 堆栈 / traceback
  - 用户要求"帮我看下这个报错"、"debug 一下"、"为什么会报错"
  - remote-exec 执行后返回了错误输出
  - CI/CD 失败日志分析

  不适用：需求讨论、代码审查、性能优化（分别用 requirements-analyzer、wo-yao-yan-pai、performance-profiling）。
---

# Debug Helper — 结构化调试 Agent

报错 + 代码 → 结构化分析 → 根因 + 修复方案。

## 工作流程

```
报错信息 → 定位(Step1) → 上下文(Step2) → 假设(Step3) → 验证(Step4) → 修复(Step5)
```

## Step 1: 定位

识别错误类型和发生位置：

| 错误类型 | 特征 | 提取关键信息 |
|----------|------|-------------|
| **语言异常** | `TypeError`, `KeyError`, `NullPointerException` | 异常类型 + 行号 + 出错表达式 |
| **堆栈跟踪** | `Traceback`, `at ...`, `stack trace` | 入口函数 → 调用链 → 出错行 |
| **HTTP 错误** | `4xx`, `5xx`, `Connection refused` | 状态码 + 请求 URL + 响应体 |
| **系统错误** | `OOM`, `Segfault`, `Disk full` | 错误码 + 系统资源指标 |
| **编译错误** | `SyntaxError`, `undefined`, `cannot find` | 文件 + 行号 + 符号名 |
| **测试失败** | `FAILED`, `AssertionError`, `expected X got Y` | 测试名 + 期望值 + 实际值 |

## Step 2: 上下文关联

根据错误类型收集相关上下文：

```
# 语言异常 → 关联变量值、函数入参、对象状态
# 堆栈跟踪 → 关联完整调用链（不要只看最后一行）
# HTTP 错误 → 关联请求方法、headers、payload
# 系统错误 → 关联资源使用情况（内存、磁盘、连接数）
# 编译错误 → 关联依赖版本、语法变更
```

## Step 3: 生成假设

列出可能的根因，按概率从高到低排序：

```
假设 1（高概率）: <原因> — 基于<证据>
假设 2（中概率）: <原因> — 基于<证据>
假设 3（低概率）: <原因> — 基于<证据>
```

## Step 4: 验证方法

对每个假设给出验证方式：

| 假设 | 验证方式 |
|------|----------|
| 变量为 None | 在出错行前加 `print(type(x))` 或断点 |
| 索引越界 | 检查列表长度和访问下标 |
| 服务未启动 | `systemctl status service` 或 `curl localhost:port` |

## Step 5: 输出报告

按以下模板输出：

```markdown
## 🐛 调试分析

**错误**: <类型>
**位置**: <文件:行号>

### 调用链
<精简调用栈，去除框架内部帧>

### 根因分析
| 假设 | 概率 | 验证方法 |
|------|------|----------|
| X | 高 | <验证> |
| Y | 中 | <验证> |
| Z | 低 | <验证> |

### 修复方案
<具体修改步骤或代码 diff>

### 防御建议
<如何防止同类问题：类型检查、单元测试、边界处理等>
```

## 快速使用

```
# 贴错误信息分析
报错了：
Traceback (most recent call last):
  File "app.py", line 42, in <module>
    result = process_data(None)
KeyError: 'user_id'

# 配合 remote-exec
远程执行：journalctl -u app -n 50 --no-pager
分析上面的输出，找根因

# CI 失败日志
帮我看下这个 CI 报错
```

## 参考资料

- 常见错误模式: [references/patterns.md](references/patterns.md)
