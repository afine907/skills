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
代码分析 → 结构识别 → 内容生成 → 格式化 → 输出文档
```

## 支持的文档类型

| 类型 | 输入 | 输出 |
|------|------|------|
| README | 项目目录 | README.md |
| API 文档 | 路由/控制器代码 | OpenAPI/Swagger |
| 架构文档 | 项目结构 | ARCHITECTURE.md |
| 变更日志 | Git 历史 | CHANGELOG.md |
| 贡献指南 | 项目配置 | CONTRIBUTING.md |
| 代码注释 | 函数/类代码 | 行内注释/Docstring |

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

详细 API 文档: [docs/api.md](docs/api.md)

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

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

[MIT License](LICENSE)

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
