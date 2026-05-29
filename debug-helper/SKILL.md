---
name: debug-helper
category: productivity
description: |
  结构化调试分析。固定 5 步分析框架：定位 → 上下文 → 假设 → 验证 → 修复。
---

# Debug Helper — 结构化调试 Agent

报错 + 代码 → 结构化分析 → 根因 + 修复方案。


## Goal

结构化调试分析。固定 5 步分析框架：定位 → 上下文 → 假设 → 验证 → 修复

## Trigger

当用户需要使用此技能时触发。

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
报错信息 → 定位(Step1) → 上下文(Step2) → 假设(Step3) → 验证(Step4) → 修复(Step5) → 验证修复(Step6)
                                                                                         │
                                                                               ┌─────────┴─────────┐
                                                                               │                   │
                                                                          修复成功             仍有问题
                                                                               │                   │
                                                                               ▼                   ▼
                                                                            完成 ✅          回 Step3 更新假设
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

| 错误类型 | 需收集信息 | 方法 |
|----------|-----------|------|
| **语言异常** | 出错表达式、相关变量值/类型、函数入参、前一步返回值 | `print(type(x))`、检查函数调用处的变量定义 |
| **堆栈跟踪** | 完整调用链（入口→出错行）、项目代码帧 vs 框架帧 | 框架帧通常包含 `site-packages/`、`node_modules/`、`runtime/` 等路径；剥去它们找到业务代码 |
| **HTTP 错误** | 请求方法、URL、headers、payload、响应体 | 查看请求构造处代码、API 文档对应接口 |
| **系统错误** | 内存/磁盘/连接数指标、近期变更、进程列表 | `free -h`、`df -h`、`dmesg`、`journalctl -n 50` |
| **编译错误** | 文件路径、符号名、语言版本、依赖版本 | 检查 `package.json`/`requirements.txt`、语法变更记录 |
| **测试失败** | 测试用例输入、期望值 vs 实际值、断言条件、mock 数据 | 查看测试 fixture、mock 返回值是否和真实行为一致 |

**兜底**：错误类型不在上述表中时，从错误文本提取错误码 + 关键词 → 直接进入 Step 3。

## Step 3: 生成假设

列出可能的根因，按概率从高到低排序：

```
假设 1（高概率）: <原因> — 基于<证据>
假设 2（中概率）: <原因> — 基于<证据>
假设 3（低概率）: <原因> — 基于<证据>
```

## Step 4: 验证方法

对每个假设给出验证方式，按错误类型分类：

| 错误类型 | 假设示例 | 验证方式 |
|----------|----------|----------|
| **语言异常** | 变量为 None | 在出错行前加 `print(type(x))` 或断点 |
|  | 字典缺 key | 检查数据来源是否有默认值、是否该用 `.get(key, default)` |
| **堆栈跟踪** | 调用链中某步返回异常值 | 逐帧检查返回值类型，找到第一个不符合预期的帧 |
|  | 异常被中间层吞掉 | 检查 try/except 是否有空 `except: pass` |
| **HTTP 错误** | 服务未启动 | `systemctl status service` 或 `curl localhost:port` |
|  | token/认证过期 | 手动 curl 测试 header 是否正确传递 |
| **系统错误** | 磁盘满 | `df -h` → `du -sh /* | sort -rh` 找大目录 |
|  | 内存泄露 | `free -h` → 对比多次采样看持续增长 |
| **编译错误** | 模块未安装 | 检查 `pip list` / `npm ls`、虚拟环境是否激活 |
|  | 语法变更 | 对比语言/框架版本 changelog |
| **测试失败** | mock 与真实行为不符 | 去掉 mock 运行一次真实调用对比结果 |
|  | fixture 数据过期 | 检查 fixture 是否随 schema 更新 |
| **不匹配已知类型** | — | 从错误文本提取特征后，用 `grep`/`journalctl` 搜索类似案例 |

## Step 5: 输出报告

按以下模板输出：

```markdown
## 调试分析

**错误**: <类型>
**位置**: <文件:行号>

### 调用链
<精简调用栈，剥去框架帧（含 site-packages/node_modules/runtime/ 等路径的帧）>

### 根因分析
| 假设 | 概率 | 验证方法 |
|------|------|----------|
| X | 高 | <验证> |
| Y | 中 | <验证> |
| Z | 低 | <验证> |

### 修复方案
<具体修改步骤或代码 diff>

### 影响范围
<修复会影响哪些模块/函数？有无副作用？>

### 防御建议
<如何防止同类问题：类型检查、单元测试、边界处理等>
```

## Step 6: 验证修复

修复方案实施后，验证修复是否生效：

1. **确认修改正确**：重新运行出错场景，确认不再触发原错误
2. **回归检查**：确认修改没有破坏相关功能
3. **如果仍有问题**：返回 Step 3，更新假设（排除已验证为否的路径），重新排序概率
4. **最多迭代 3 轮**，超过则标记为需人工介入

## 工作流程（完整）

```
报错信息 → 定位(Step1) → 上下文(Step2) → 假设(Step3) → 验证(Step4) → 修复(Step5) → 验证修复(Step6) → 若失败回 Step3
```

## 使用示例

### 示例：Python KeyError

```
用户输入：
报错了：
Traceback (most recent call last):
  File "app.py", line 42, in <module>
    result = process_data(None)
KeyError: 'user_id'

输出：
## 调试分析

**错误**: 语言异常（KeyError）
**位置**: app.py:42

### 调用链
app.py:42 <module> → process_data(None) → process_data 内部访问 dict key 'user_id'

### 根因分析
| 假设 | 概率 | 验证方法 |
|------|------|----------|
| process_data 入参为 None，内部尝试访问 None['user_id'] | 高 | 检查 process_data 函数第一行是否有入参检查 |
| 数据源返回了空 dict | 中 | 检查调用 process_data 前一步的数据获取逻辑 |
| key 名拼写错误 | 低 | 对比数据源字段名 |

### 修复方案
在 process_data 函数开头增加入参检查：
```python
def process_data(data):
    if data is None:
        return {}
    return data.get('user_id', '')
```

### 影响范围
仅 process_data 函数内部，不影响调用方接口

### 防御建议
- 使用 `.get(key, default)` 替代 `[key]` 访问 dict
- 对可能为 None 的入参加类型检查和默认值
```

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
