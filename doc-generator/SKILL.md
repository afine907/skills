---
name: doc-generator
description: |
  【文档生成】从代码自动生成各类技术文档：API 文档、README、架构文档、变更日志、代码注释。

  触发时机：
  - 用户要求"生成文档"、"写README"、"生成API文档"
  - 项目缺少文档需要补充
  - 代码变更需要更新文档

  支持多种文档格式和输出方式。
category: productivity
---

# Doc Generator — 文档生成技能

从代码和项目结构自动生成专业级技术文档。


## Goal

从代码自动生成各类技术文档：API 文档、README、架构文档、变更日志、代码注释

## Trigger

- 用户要求"生成文档"、"写README"、"生成API文档"
  - 项目缺少文档需要补充
  - 代码变更需要更新文档

## 工作流程

```
诊断 → 类型选择 → 信息收集 → 内容生成 → 质量检查 → 格式化输出
  │       │          │          │          │          │
  ▼       ▼          ▼          ▼          ▼          ▼
现有文档  决策流程    输入源     模板填充    质量清单    最终文档
缺失分析  优先级排序   解析提取   代码示例    准确性验证  链接检查
```

### Step 1: 诊断（现状分析）

检查项目当前文档状态：

| 检查项 | 检查方式 | 结果 |
|--------|---------|------|
| README.md | 检查文件是否存在 | 存在 / 缺失 / 过期 |
| API 文档 | 检查 docs/ 目录或 OpenAPI 文件 | 存在 / 缺失 |
| 架构文档 | 检查 ARCHITECTURE.md 或 docs/architecture.md | 存在 / 缺失 |
| 变更日志 | 检查 CHANGELOG.md | 存在 / 缺失 |
| 代码注释 | 抽样检查核心函数 docstring | 充分 / 不足 / 缺失 |
| 贡献指南 | 检查 CONTRIBUTING.md | 存在 / 缺失 |
| 许可证 | 检查 LICENSE 文件 | 存在 / 缺失 |

输出：文档缺失清单 + 优先级排序

### Step 2: 文档类型选择

```
用户需求是什么？
    │
    ├── 需要项目介绍/入门？ ──是──▶ README
    │       │
    │       否
    │       ▼
    ├── 需要接口说明？ ──是──▶ API 文档
    │       │
    │       否
    │       ▼
    ├── 需要系统设计说明？ ──是──▶ 架构文档
    │       │
    │       否
    │       ▼
    ├── 需要变更记录？ ──是──▶ 变更日志
    │       │
    │       否
    │       ▼
    ├── 需要补充代码注释？ ──是──▶ Docstring 生成
    │       │
    │       否
    │       ▼
    └── 需要贡献指南？ ──是──▶ CONTRIBUTING.md
```

### Step 3: 信息收集
- README: 读取 package.json/pyproject.toml、目录结构、已有文档
- API 文档: 解析路由定义、请求/响应模型、注释
- 架构文档: 分析目录结构、依赖关系、模块划分
- 代码注释: 解析函数签名、参数、返回值

### Step 4: 内容生成
- 按模板结构填充内容
- 补充代码示例和使用说明
- 添加项目特定的信息（徽章、许可证、联系方式）

### Step 5: 质量检查

| 文档类型 | 必要部分 | 质量标准 |
|---------|---------|---------|
| README | 项目描述、快速开始、项目结构 | 描述 < 2 行、安装命令可复制、结构树完整 |
| API 文档 | 每个端点的请求/响应示例 | 示例可运行、状态码完整、错误响应有说明 |
| 架构文档 | 模块图、数据流图、技术选型理由 | 图表清晰、理由充分、与代码一致 |
| 变更日志 | 版本号、日期、变更分类 | 遵循 Keep a Changelog 格式 |
| Docstring | 功能描述、参数、返回值、异常、示例 | 参数有类型、示例可运行 |

### Step 6: 格式化与输出
- 检查 Markdown 格式（标题层级、代码块语言标记）
- 验证链接有效性（相对路径、API 端点）
- 输出到目标文件或预览
- IF 用户反馈不满意 THEN: 根据反馈重新生成对应部分

## 支持的文档类型

| 类型 | 输入 | 输出 |
|------|------|------|
| README | 项目目录 | README.md |
| API 文档 | 路由/控制器代码 | OpenAPI/Swagger |
| 架构文档 | 项目结构 | ARCHITECTURE.md |
| 变更日志 | Git 历史 | CHANGELOG.md |
| 贡献指南 | 项目配置 | `CONTRIBUTING.md` |
| 代码注释 | 函数/类代码 | 行内注释/Docstring |

## 文档类型选择决策表

### 按项目成熟度选择

| 项目阶段 | 优先文档 | 次要文档 | 可选文档 |
|---------|---------|---------|---------|
| 新项目（< 1月） | README、LICENSE | CONTRIBUTING | — |
| 成长期（1-6月） | README、API 文档、代码注释 | 架构文档、CONTRIBUTING | 变更日志 |
| 成熟期（> 6月） | 全部文档 | — | 高级架构文档 |
| 遗留系统维护 | README、架构文档 | API 文档 | 变更日志 |

### 按受众选择

| 目标受众 | 推荐文档 | 内容重点 | 语言风格 |
|---------|---------|---------|---------|
| 新开发者 | README、CONTRIBUTING | 快速开始、环境搭建、开发规范 | 友好、步骤清晰 |
| API 使用者 | API 文档 | 端点说明、请求/响应示例 | 精确、示例驱动 |
| 架构师/TL | 架构文档 | 系统设计、模块关系、技术选型 | 专业、有深度 |
| 项目经理 | README（精简版） | 功能列表、部署状态、进度 | 简洁、非技术 |
| 开源贡献者 | CONTRIBUTING、README | 贡献流程、代码规范、社区规则 | 友好、鼓励参与 |

### 质量评分标准

| 维度 | 评分标准 | 1分 | 3分 | 5分 |
|------|---------|-----|-----|-----|
| 完整性 | 必要部分是否齐全 | 缺失 > 50% | 缺失 < 20% | 全部齐全 |
| 准确性 | 内容是否与代码一致 | 多处不一致 | 少量不一致 | 完全一致 |
| 可读性 | 结构是否清晰 | 无组织 | 有基本结构 | 层次分明+示例 |
| 可操作性 | 读者能否直接行动 | 无法执行 | 需要猜测 | 可直接复制执行 |
| 时效性 | 是否反映最新状态 | 严重过期 | 部分过期 | 与代码同步 |

## README 生成

### 模板结构

```markdown
# {项目名称}

{一句话描述}

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-{version}-green.svg)]()

## 功能特性

- ✅ {特性1}
- ✅ {特性2}
- ✅ {特性3}

## 快速开始

### 前置要求

- {运行环境要求}
- {依赖工具}

### 安装

```bash
# 克隆项目
git clone {repo_url}
cd {project}

# 安装依赖
{install_command}

# 配置环境
cp .env.example .env
# 编辑 .env 文件

# 启动服务
{start_command}
```

### 验证

```bash
# 运行测试
{test_command}

# 健康检查
curl http://localhost:{port}/health
```

## 使用说明

### {功能1}

```{language}
{代码示例}
```

### {功能2}

```{language}
{代码示例}
```

## 项目结构

```
{project}/
├── src/              # 源代码
│   ├── {module1}/    # {说明}
│   └── {module2}/    # {说明}
├── tests/            # 测试代码
├── docs/             # 文档
├── scripts/          # 脚本工具
├── {config_files}    # 配置文件
└── README.md         # 本文件
```

## API 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/{resource} | 获取列表 |
| POST | /api/v1/{resource} | 创建资源 |
| GET | /api/v1/{resource}/{id} | 获取详情 |
| PUT | /api/v1/{resource}/{id} | 更新资源 |
| DELETE | /api/v1/{resource}/{id} | 删除资源 |

详细 API 文档: `docs/api.md`

## 开发指南

### 开发环境

```bash
# 安装开发依赖
{dev_install_command}

# 启动开发服务
{dev_start_command}
```

### 代码规范

- {规范1}
- {规范2}

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 杂务
```

## 部署

### Docker

```bash
docker build -t {image_name} .
docker run -p {port}:{port} {image_name}
```

### 手动部署

```bash
{deploy_commands}
```

## 常见问题

### Q: {问题1}
A: {答案1}

### Q: {问题2}
A: {答案2}

## 贡献指南

请阅读 `CONTRIBUTING.md`

## 许可证

`MIT License`

## 联系方式

- {联系方式}
```

## API 文档生成

从代码注释/路由定义提取 API 信息：

```python
# 输入：FastAPI 路由
@router.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    """创建新用户
    
    - **email**: 用户邮箱（必填，唯一）
    - **name**: 用户昵称（必填，2-50字符）
    - **role**: 用户角色（可选，默认 user）
    """
    pass

# 输出：API 文档
## POST /api/v1/users

创建新用户

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "张三",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "张三",
  "role": "user",
  "created_at": "2026-01-01T00:00:00Z"
}
```
```

## 代码注释生成

### Python Docstring (Google Style)

```python
def process_order(order_id: str, action: str) -> OrderResult:
    """处理订单操作。
    
    根据指定的动作对订单进行处理，支持提交、取消、退款等操作。
    
    Args:
        order_id: 订单唯一标识符，格式为 UUID
        action: 操作类型，可选值: submit, cancel, refund
    
    Returns:
        OrderResult: 包含处理结果的对象
            - success (bool): 是否成功
            - message (str): 结果描述
            - order (Order): 更新后的订单对象
    
    Raises:
        OrderNotFoundError: 订单不存在时抛出
        InvalidActionError: 操作不合法时抛出
        OrderStateError: 订单状态不允许该操作时抛出
    
    Examples:
        >>> result = process_order("123e4567-e89b-12d3-a456-426614174000", "submit")
        >>> print(result.success)
        True
    
    Note:
        该操作是幂等的，重复执行相同操作不会产生副作用。
    """
    pass
```

## Edge Cases

- **无 README 项目**
  - IF 存在 package.json THEN: 从中提取名称、描述、依赖、脚本，自动生成 README
  - IF 存在 pyproject.toml THEN: 从中提取项目元数据，自动生成 README
  - IF 无配置文件 THEN: 扫描目录结构推断语言和框架，生成基础 README 并标注"需人工补充"

- **API 文档缺失**
  - IF 代码有路由定义（FastAPI/Express/Flask） THEN: 从路由装饰器/定义逆向生成 OpenAPI 规范
  - IF 代码有 docstring/注释 THEN: 从注释提取参数和返回值，生成文档
  - IF 注释不足 THEN: 生成框架文档（占位），标注"需补充请求/响应示例"

- **多语言项目**
  - IF 项目包含多种语言 THEN: 按语言分别生成文档，最后生成跨语言架构视图
  - IF 语言间有接口 THEN: 重点文档化接口边界的数据格式和协议

- **文档过期**
  - IF 发现文档与代码不一致 THEN: 生成差异报告（具体哪些部分过期）
  - IF 用户选择更新 THEN: 按差异报告逐项更新，保留用户自定义内容
  - IF 无法自动判断 THEN: 列出可疑部分，让用户确认

- **私有仓库**
  - IF 项目为私有 THEN: 跳过仓库 URL 生成，使用相对路径引用所有文件
  - IF README 包含徽章 THEN: 使用内部 badge 服务或移除外部徽章
  - IF 有内部文档链接 THEN: 使用相对路径（./docs/api.md）而非绝对 URL

- **代码注释不足**
  - IF 函数无 docstring 但有类型注解 THEN: 从类型注解生成基础 docstring
  - IF 函数无任何文档信息 THEN: 从函数名和参数名推断用途，生成草稿并标注"需验证"
  - IF 类无 docstring THEN: 从方法列表推断类职责，生成基础文档

## 不适用

**范围边界：** 本技能从代码和项目结构自动生成技术文档，不进行深度代码逻辑分析、不生成变更日志（自动从 Git 提取）、不编写用户故事或需求文档。

- 自动生成变更日志 → 使用 [changelog-generator](../changelog-generator/SKILL.md)
- 深度代码分析 → 使用 [explain-code](../explain-code/SKILL.md)
- 用户故事/需求文档 → 使用 [user-story](../user-story/SKILL.md)

### 适用场景矩阵

| 用户意图 | 推荐文档类型 | 推荐入口 |
|---------|-------------|---------|
| 项目缺少 README | README.md | Step 1 诊断 → Step 2 类型选择 → Step 3-6 |
| 需要 API 文档 | API 文档 / OpenAPI | Step 3 信息收集（路由解析） |
| 需要架构说明 | 架构文档 | Step 3 信息收集（目录分析） |
| 代码注释不全 | Docstring 补充 | Step 3 信息收集（函数解析） |
| 需要贡献指南 | CONTRIBUTING.md | Step 4 内容生成（模板填充） |
| 文档需要更新 | 增量更新 | Step 1 诊断（差异分析）→ Step 5-6 |

## 快速使用

```
# 生成 README
根据当前项目生成 README.md

# 生成 API 文档
从 FastAPI 路由生成 API 文档

# 补充代码注释
为这个函数生成 Docstring：[粘贴代码]

# 生成架构文档
分析项目结构，生成架构文档

# 生成变更日志
根据最近的 Git 提交生成 CHANGELOG
```

## 参考资料

- README 模板: [references/readme-template.md](references/readme-template.md)
- Docstring 规范: [references/docstring-guide.md](references/docstring-guide.md)
