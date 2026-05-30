# 技术文章写作指南

## 文章结构

### 标准结构

```markdown
# 标题

> 一句话摘要，概括文章核心价值

## 背景

为什么写这篇文章？解决什么问题？

## 核心内容

### 概念解释

用通俗语言解释技术概念

### 实现步骤

1. 步骤一
2. 步骤二
3. 步骤三

### 代码示例

```python
# 带注释的代码示例
def example():
    pass
```

## 实战案例

完整的实际应用场景

## 常见问题

Q: 问题1
A: 解答1

## 总结

核心要点回顾

## 参考资料

- [链接1](url1)
- [链接2](url2)
```

## 写作原则

### 清晰性

- 使用简单句，避免长句
- 专业术语首次出现时解释
- 使用类比帮助理解

### 实用性

- 提供可运行的代码示例
- 包含实际应用场景
- 给出常见问题解答

### 结构性

- 使用标题层级清晰组织
- 每个章节有明确目的
- 使用列表和表格提高可读性

## 代码示例规范

### Python 示例

```python
# 文件名: example.py
# 描述: 简短说明

def function_name(param: str) -> dict:
    """函数文档字符串

    Args:
        param: 参数说明

    Returns:
        返回值说明

    Raises:
        ValueError: 异常说明
    """
    # 实现步骤说明
    result = process(param)
    return {"result": result}
```

### JavaScript 示例

```javascript
// 文件名: example.js
// 描述: 简短说明

/**
 * 函数说明
 * @param {string} param - 参数说明
 * @returns {Object} 返回值说明
 */
function functionName(param) {
  // 实现步骤说明
  const result = process(param);
  return { result };
}
```

### Bash 示例

```bash
#!/bin/bash
# 描述: 简短说明

# 步骤1: 说明
command1

# 步骤2: 说明
command2
```

## 常见错误

### 避免的问题

1. **代码不完整** - 确保代码可运行
2. **缺少上下文** - 解释代码的用途
3. **格式混乱** - 使用一致的代码风格
4. **链接失效** - 验证所有链接有效

### 改进建议

1. 添加错误处理
2. 包含输入验证
3. 提供多个示例
4. 解释边界情况
