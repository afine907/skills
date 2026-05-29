---
name: go-service-creator
category: development
description: |
  Go 微服务脚手架生成器。自然语言描述 → 完整 Go 项目目录。
  触发场景：用户要求"创建 Go 服务"、"初始化 Go 项目"、"搭建 Go 后端"、"生成 Go 微服务"。
  关键词：go service, golang, gin, echo, fiber, go backend, go api, go microservice。
---

# Go Service — Go 微服务脚手架生成

自然语言描述 → 完整 Go 项目目录（代码 + 配置 + Dockerfile + Makefile），一次输出。

不适用：纯 CLI 工具（用 shell-command）；Go 库/包开发（非服务）；已有项目的重构。


## Goal

Go 微服务脚手架生成器。自然语言描述 → 完整 Go 项目目录

## Trigger

当用户需要使用此技能时触发。

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
描述需求 → 选择框架 → 确认配置 → 生成项目 → 验证构建
```

### Step 1: 收集需求

从用户描述中提取：
- **服务名称**：用于目录名和 module 名
- **框架偏好**：Gin（默认）/ Echo / Fiber
- **端口**：默认 8080
- **数据库**：MySQL / PostgreSQL / SQLite / 无
- **功能模块**：用户提到的业务实体

如果信息不足，询问 1-2 个关键问题（框架、端口），不要过度追问。

### Step 2: 选择框架

| 框架 | 适用场景 | 特点 |
|------|----------|------|
| **Gin** (默认) | 通用 API 服务 | 性能好，生态丰富，社区最大 |
| **Echo** | 需要丰富中间件 | 轻量，API 设计优雅 |
| **Fiber** | 极致性能 | Express 风格，基于 fasthttp |

读取对应的模板文件获取代码模式：
- Gin → [references/gin-template.md](references/gin-template.md)
- Echo → [references/echo-template.md](references/echo-template.md)
- Fiber → [references/fiber-template.md](references/fiber-template.md)

### Step 3: 生成项目文件

标准目录布局（参考 [references/project-layout.md](references/project-layout.md)）：

```
<service-name>/
├── cmd/
│   └── server/
│       └── main.go              # 入口：路由注册 + graceful shutdown
├── internal/
│   ├── config/
│   │   └── config.go            # 配置管理（envconfig）
│   ├── handler/
│   │   └── <entity>.go          # HTTP handlers
│   ├── model/
│   │   └── <entity>.go          # 数据模型
│   └── service/
│       └── <entity>.go          # 业务逻辑
├── go.mod
├── go.sum
├── Makefile                     # build / test / run / lint
├── Dockerfile                   # 多阶段构建
├── .env.example
└── README.md
```

**必生成文件**：
1. `cmd/server/main.go` — 路由注册、中间件、graceful shutdown
2. `internal/config/config.go` — 环境变量配置
3. `internal/handler/*.go` — 每个实体一个 handler 文件
4. `internal/model/*.go` — 数据模型
5. `internal/service/*.go` — 业务逻辑层
6. `go.mod` — module 定义和依赖
7. `Makefile` — 常用命令
8. `Dockerfile` — 多阶段构建（参考 [references/dockerfile-patterns.md](references/dockerfile-patterns.md)）
9. `.env.example` — 环境变量模板
10. `README.md` — 项目说明和启动方式

### Step 4: 验证

生成完成后执行：
```bash
cd <service-name> && go mod tidy
```

报告生成结果：文件列表、启动方式、下一步建议。

## 输出格式

完成后输出：

```markdown
## 项目已生成

**服务**: <name>
**框架**: <gin/echo/fiber>
**端口**: <port>

### 文件结构
<tree>

### 启动方式

    make run
    # 或
    go run cmd/server/main.go

### 下一步
- 修改 internal/handler/ 添加业务逻辑
- 配置 .env 文件
- 运行 make test 执行测试
```
