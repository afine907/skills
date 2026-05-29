---
name: security-scan
description: |
  【安全扫描】对代码进行安全漏洞扫描，检测 OWASP Top 10、硬编码密钥、不安全配置、依赖漏洞等安全问题。

  触发时机：
  - 用户要求"安全检查"、"安全扫描"、"检查安全漏洞"
  - 代码提交前的安全自查
  - 安全审计前的预检

  纯静态分析，不执行代码，不发送网络请求。
category: quality
---

# Security Scan — 安全扫描技能

对代码进行系统性安全扫描，输出漏洞报告和修复建议。


## Goal

对代码进行安全漏洞扫描，检测 OWASP Top 10、硬编码密钥、不安全配置、依赖漏洞等安全问题

## Trigger

- 用户要求"安全检查"、"安全扫描"、"检查安全漏洞"
  - 代码提交前的安全自查
  - 安全审计前的预检

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
代码分析 → 模式匹配 → 漏洞分类 → 风险评估 → 输出报告
```

## 扫描维度

### 1. OWASP Top 10 检测

| 漏洞类型 | 检测模式 |
|----------|----------|
| A01 失效的访问控制 | 缺少权限检查的端点、IDOR 漏洞 |
| A02 加密失败 | 弱加密算法（MD5/SHA1）、明文存储 |
| A03 注入 | SQL 拼接、命令拼接、XSS 未转义 |
| A04 不安全设计 | 缺少速率限制、无审计日志 |
| A05 安全配置错误 | 默认密码、调试模式开启、CORS 过宽 |
| A06 过期组件 | 已知漏洞的依赖版本 |
| A07 认证失败 | Session 固定、JWT 未验证签名 |
| A08 数据完整性 | 未校验的数据反序列化 |
| A09 日志监控不足 | 安全事件未记录 |
| A10 SSRF | 未限制的服务端请求 |

### 2. 硬编码敏感信息

```python
# 检测模式
password = "xxx"           # 硬编码密码
api_key = "sk-..."         # API 密钥
secret = "..."             # 密钥
token = "eyJ..."           # JWT Token
AWS_ACCESS_KEY = "AKIA..." # 云服务密钥
connection_string = "..."  # 数据库连接串
```

### 3. 不安全代码模式

| 语言 | 不安全模式 | 安全替代 |
|------|-----------|----------|
| Python | `eval(input())` | `ast.literal_eval()` |
| Python | `pickle.loads()` | `json.loads()` |
| Python | `subprocess.shell=True` | `subprocess.run([...])` |
| Python | `os.system()` | `subprocess.run()` |
| JavaScript | `innerHTML = user_input` | `textContent` 或 sanitize |
| JavaScript | `eval()` | `JSON.parse()` 或安全替代 |
| SQL | `f"SELECT * FROM {table}"` | 参数化查询 |
| Shell | `$user_input` 拼接 | 引号包裹 + 校验 |

### 4. 依赖安全

检查依赖文件中的已知漏洞：
- `requirements.txt` / `pyproject.toml`（Python）
- `package.json` / `package-lock.json`（Node.js）
- `go.sum`（Go）
- `pom.xml` / `build.gradle`（Java）

### 5. 配置安全

| 检查项 | 不安全配置 |
|--------|-----------|
| CORS | `Access-Control-Allow-Origin: *` |
| HTTPS | 允许 HTTP 明文传输 |
| Cookies | 缺少 Secure/HttpOnly/SameSite |
| Headers | 缺少安全头（CSP, X-Frame-Options） |
| Debug | 生产环境开启 debug 模式 |

## 输出报告格式

```markdown
# 安全扫描报告

## 扫描概览
- 扫描时间：{时间}
- 扫描范围：{文件列表}
- 风险评级：{高/中/低}

## 漏洞统计

| 风险等级 | 数量 | 状态 |
|----------|------|------|
| 🔴 高危 | {n} | 需立即修复 |
| 🟠 中危 | {n} | 建议尽快修复 |
| 🟡 低危 | {n} | 建议修复 |
| 🔵 信息 | {n} | 可选改进 |

## 漏洞详情

### 🔴 [高危] {漏洞标题}
- **类型**: {OWASP 分类}
- **文件**: `{file}:{line}`
- **CWE**: CWE-{编号}
- **漏洞描述**: {详细描述}
- **攻击场景**: {可能的攻击方式}
- **影响**: {被利用后的后果}
- **修复建议**:
  - {具体修复步骤}
- **修复代码**:
```code
// 不安全代码
{原始代码}

// 安全代码
{修复后代码}
```

## 修复优先级建议
1. {最紧急的修复项}
2. {次紧急的修复项}
...

## 安全加固建议
- {整体安全改进建议}
```

## 快速使用

```
# 扫描当前项目
扫描当前项目的安全漏洞

# 扫描指定文件
扫描 src/auth/ 目录的安全问题

# 只检查硬编码密钥
检查代码中是否有硬编码的密钥

# 检查依赖安全
检查 requirements.txt 中的已知漏洞

# 安全审计
对这个项目做一次完整的安全审计
```

## 扫描原则

1. **零误报优先** — 宁可漏报，不要误报
2. **上下文感知** — 同一代码在不同上下文风险不同
3. **给出修复** — 每个漏洞必须附带修复建议
4. **风险排序** — 高危优先，不要淹没在低危问题中
5. **不执行代码** — 纯静态分析，不运行任何代码
