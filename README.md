<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-%E2%9C%94%EF%B8%8F-blue?style=flat-square&logo=claude&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Cursor-%E2%9C%94%EF%B8%8F-purple?style=flat-square&logo=cursor&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Windsurf-%E2%9C%94%EF%B8%8F-teal?style=flat-square&logo=windsurf&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/OpenClaw-%E2%9C%94%EF%B8%8F-orange?style=flat-square&labelColor=1a1a2e" />
  <br>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/afine907/skills?style=flat-square&labelColor=1a1a2e&color=white" />
  </a>
  <a href="https://github.com/afine907/skills">
    <img src="https://img.shields.io/github/stars/afine907/skills?style=flat-square&labelColor=1a1a2e&color=yellow" />
  </a>
  <a href="https://github.com/afine907/skills/pulls">
    <img src="https://img.shields.io/github/issues-pr/afine907/skills?style=flat-square&labelColor=1a1a2e&color=white" />
  </a>
</p>

<br>

<h1 align="center">🎰 AI Skills</h1>

<p align="center">
  <b>从验牌到上线，一键打通 AI 编码全流程</b><br>
  代码审查 · 需求拆解 · Commit 生成 · 技术写作 · 项目编排
</p>

<p align="center">
  <b>🇨🇳 中文</b> · <a href="README_EN.md">🇬🇧 English</a>
</p>

<br>

---

# 📖 这是什么？

一组可复用的 [技能](SKILL_CATEGORIES.md)（prompt 模板），专为 AI 编码 Agent 设计。每个技能是一个独立的 `SKILL.md`，把模糊指令变成结构化、可重复的工作流。

**支持平台：** Claude Code · Cursor · Windsurf · OpenClaw · 任何支持 `/commands` 的 Agent

**覆盖完整 SDLC：** 需求 → 架构 → 开发 → 质量 → 版本控制 → 部署 → 运维

<br>

---

# ⚡ 快速安装

```bash
# 一键全装
npx skills add https://github.com/afine907/skills

# 只装单个技能
npx skills add https://github.com/afine907/skills --skill wo-yao-yan-pai
```

然后在 Agent 里输入 `/skill-name` 或直接说技能名即可。

<br>

---

# 🃏 主角技 · 我要验牌

> **AI 写的代码你敢直接用？先验一验。**

<p align="center">
  <a href="wo-yao-yan-pai/SKILL.md">
    <img src="https://img.shields.io/badge/🔥_我要验牌-点击查看完整技能-red?style=for-the-badge&labelColor=1a1a2e" />
  </a>
</p>

你是「**赌侠**」还是「**小瘪三**」？拉出来验验就知道。

```
写完代码 → 🔍 多维审查 → 📊 生成报告 → 🎯 判定
                                           ↓
                              ┌────────────┴────────────┐
                              │                         │
                      小瘪三 （有问题）           赌侠 （稳了）
                              │                         │
                              ▼                         │
                          擦皮鞋 🧹                  ✅ 通关
                              │                         │
                              ▼                         │
                        Bug Fix                        │
                              │                         │
                              └────── 🔄 最多5轮 ────────┘
```

```bash
# 写完代码，直接说：
我要验牌

# Agent 自动干活，你只管等结果
# 🎯 判定 → 小瘪三→擦皮鞋→再审 | 赌侠→通关
```

### 🔬 审什么？

| 维度 | 查什么 |
|------|--------|
| 🏗️ 代码质量 | 可读性、命名规范、函数复杂度、重复代码 |
| 🐛 潜在 Bug | 边界条件、空指针、并发安全、异常处理 |
| ⚡ 性能 | 算法复杂度、内存泄漏、无用计算 |
| 🔒 安全 | SQL注入、XSS、敏感信息泄露 |
| 📐 最佳实践 | 设计模式、错误处理、测试覆盖 |

### 💯 评分体系

| 分数 | 判词 | 怎么办 |
|------|------|--------|
| 90-100 | 🏆 **赌侠** | 代码牛逼，直接上线 |
| 70-89 | 🔧 **接近赌侠** | 小问题，擦完就好 |
| 50-69 | 🧹 **小瘪三** | 中等以上问题已自动修复 |
| 0-49 | 🚨 **严重小瘪三** | 得大修，建议人工介入 |

### 🧠 为什么叫「我要验牌」？

> 「我要验牌」是网络热梗，源自赌场验牌的动作。
> 用在代码审查上就是——你 AI 生成的代码，我得先验验成色。
> 配上「赌侠」「小瘪三」「擦皮鞋」的赌场话语体系，
> 让无聊的 code review 变成一场有梗的博弈。🎲

直接在 Agent 里说「我要验牌」或 `/wo-yao-yan-pai` 即可触发。

<br>

---

# 🗂️ 技能牌组一览 (67个技能)

> 详见 [SKILL_CATEGORIES.md](SKILL_CATEGORIES.md) 完整 SDLC 阶段图，含使用指南和互补技能推荐。

按软件工程生命周期分类展示。

### 📋 需求阶段 (3个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 📋 **requirements-analyzer** | 模糊需求 → 结构化文档 | 产品经理、技术方案 |
| 📐 **tech-spec** | 需求 → 技术方案设计（架构、API、数据模型） | 技术负责人、架构师 |
| 📖 **user-story** | 需求 → 用户故事 + 验收标准 + 故事点估算 | 产品经理、Scrum Master |

### 🏗️ 开发阶段 (25个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 🧵 **task-loom** | 万字 PRD 秒变代码 | 项目启动、大需求拆解 |
| 🔌 **api-design** | 业务需求 → RESTful API + OpenAPI 规范 | 后端开发、API 设计 |
| 🕸️ **graphql-design** | 需求 → GraphQL Schema + DataLoader 优化 | GraphQL 项目 |
| 🔐 **auth-patterns** | JWT/OAuth2/RBAC/MFA 认证授权实现 | 需要登录系统的项目 |
| ⚡ **caching-strategy** | 缓存方案设计（Redis/穿透/击穿/雪崩防护） | 高并发系统 |
| 🚩 **feature-flag** | 功能开关 + 灰度发布 + A/B 测试 | 需要精细发布的团队 |
| 🌍 **i18n-helper** | 多语言国际化方案（React/Vue/Python） | 国际化项目 |
| 📱 **react-service-creator** | React 项目脚手架（Next.js/Vite/Zustand） | 前端项目启动 |
| 🐹 **go-service-creator** | Go 微服务脚手架（Gin/Echo/Fiber） | Go 后端项目 |
| 🐍 **python-service-creator** | Python 后端脚手架（FastAPI/Flask） | Python 后端项目 |
| 📡 **websocket-service** | WebSocket 实时通信（聊天/推送/通知） | 实时应用 |
| 🔄 **microservice-patterns** | 微服务模式（Saga/服务发现/熔断降级） | 分布式系统 |
| 📦 **monorepo-manager** | Monorepo 管理（Turborepo/pnpm workspace） | 多包项目 |
| 🛠️ **cli-tool-creator** | CLI 工具开发（Python Typer/Node Commander） | 命令行工具 |
| 📐 **typescript-service-creator** | TypeScript 后端脚手架（Express/Hono/Fastify） | TS 后端项目 |
| 🍃 **vue-service-creator** | Vue 3/Nuxt 3 前端脚手架 | Vue 前端项目 |
| 📱 **mobile-service-creator** | React Native/Flutter 移动端脚手架 | 移动应用开发 |
| 🔄 **data-pipeline** | ETL 管道设计（Airflow/dbt） | 数据工程 |
| 🔄 **code-migration** | 框架迁移方案（Python2→3/JS→TS） | 代码迁移 |
| 🎭 **api-mocking** | API Mock 服务（前后端并行开发） | 前端独立开发 |
| 🌱 **database-seeding** | 数据库种子数据生成（Faker/Factory） | 开发测试环境 |
| 💾 **database-ops** | 数据库设计与运维（Schema/索引/迁移） | 数据库相关 |
| 🎯 **prompt-cicd** | Prompt 版本管理 + 回归测试 + A/B 对比 | Prompt 工程师 |
| 🔧 **tool-use-patterns** | AI Agent 工具集成模式 | Agent 开发者 |

### ✅ 质量阶段 (9个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 🃏 **wo-yao-yan-pai** | 代码审查 → 报告 → 自动修复 | 所有用 AI 写代码的人 |
| 🔍 **code-review** | 多维度代码审查（正确性/安全/性能/可维护性） | Code Review |
| 🔒 **security-scan** | 安全漏洞扫描（OWASP Top 10/硬编码密钥） | 安全审计 |
| ♿ **accessibility-audit** | 无障碍审计（WCAG 2.1/ARIA/键盘导航） | 前端无障碍 |
| 🧠 **explain-code** | 代码结构 + 设计质量分析 | 接手老项目、写文档 |
| 🧪 **test-generator** | 代码写完自动生成测试 | 追求测试覆盖率的团队 |
| 📊 **test-strategy** | 测试策略设计（测试金字塔/覆盖率目标） | 测试负责人 |
| 🤖 **agent-eval** | AI Agent 输出质量评估 | Agent 开发者 |
| 🛡️ **agent-security** | AI Agent 安全模式 | Agent 开发者 |

### 🔗 版本控制 (6个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| ✍️ **commit** | 再也不用想 commit message | 追求整洁 Git 历史 |
| 🔍 **commit-diff-analyzer** | 两个 commit 改了啥一眼看穿 | Code Review、Debug |
| 📝 **pr-description** | git diff → 结构化 PR 描述 + gh CLI 创建 | PR 提交流程、团队协作 |
| 📜 **changelog-generator** | Git 标签 → Keep a Changelog 格式 | 发版准备、版本管理 |
| 🌿 **git-branch** | Git 分支策略（Git Flow/Trunk-Based） | 团队 Git 规范 |
| 🔀 **git-workflow** | 一键 Git 工作流（branch→stage→commit→push→PR） | 日常 Git 操作 |

### 🖥️ 运维阶段 (11个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| ⚙️ **ci-workflow** | 描述 → CI 配置文件（GitHub Actions/GitLab CI） | CI/CD 配置 |
| 🖥️ **remote-exec** | SSH 远程执行命令 | 服务器运维 |
| 📊 **log-analyzer** | 日志结构化分析，异常自动发现 | 线上排查 |
| ✅ **deploy-checklist** | 项目类型 → 预发布检查清单 | 发版准备 |
| 🚨 **incident-response** | 事故分级 → 应急处置 → RCA 复盘报告 | On-call、SRE |
| 🔥 **load-testing** | 压力测试设计 + K6/Locust 脚本生成 | 性能测试 |
| 🚚 **migration-helper** | 数据迁移方案 + 校验脚本 + 回滚策略 | 数据库迁移 |
| ☸️ **k8s-cluster** | Kubernetes 集群管理配置 | K8s 运维 |
| 📦 **k8s-gen** | K8s 部署配置生成 | K8s 部署 |
| 📈 **llm-observability** | AI Agent 可观测性（决策追踪/成本监控） | Agent 运维 |
| 💰 **cost-optimization** | 云成本优化 + AI Token 成本追踪 | 成本管控 |

### ✍️ 效率工具 (8个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 📝 **technical-article-writer** | 自动搜索 + 写技术文章 | 写博客、写文档 |
| 🔧 **shell-command** | 中文描述 → shell 命令 + 安全确认 | 日常终端操作 |
| 🐛 **debug-helper** | 结构化 5 步调试分析 | 排查报错、CI 失败 |
| 🔤 **regex-buddy** | 描述 → 正则 + 逐段解释 + 测试用例 | 数据提取、格式校验 |
| 🎯 **prompt-engineering** | 任务描述 → 高质量 LLM prompt | 技能创建、AI 工作流 |
| 📓 **meeting-notes** | 会议录音 → 结构化会议纪要 | 团队同步、每日站会 |
| 📄 **doc-generator** | 代码 → 文档（README/API/架构/注释） | 文档补充 |
| 🧠 **self-improve** | AI 纠错经验固化 | 持续改进 |

### 📚 参考速查 (5个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 🌐 **api-debug** | API 调试实战（curl/httpie/状态码/jq） | 接口调试 |
| 🐳 **docker-essentials** | Docker 容器管理速查 | 容器操作 |
| 🐧 **linux-ops** | Linux 运维速查（进程/网络/日志） | 服务器运维 |
| ⚡ **performance-profiling** | 性能分析（Python/Node/DB/系统） | 性能优化 |
| 🧪 **python-testing** | Python 测试速查（pytest/mock/fixtures） | Python 测试 |

<br>

---

# 🧠 为什么要用这个仓库？

1. **告别临时 prompt** — 「帮我审查这段代码」这种 prompt 每个开发者都在写，但效果天差地别。这些模板经过实战打磨。
2. **质量稳定** — 同一个 prompt 每次跑出同等级的结果，不受模型状态影响。
3. **自动化闭环** — 审查 → 修复 → 再审，不用手动介入。
4. **免费开源** — MIT 协议，随便用随便改。
5. **跨平台** — Claude Code、Cursor、Windsurf、OpenClaw 都能用。

<br>

---

# 🤝 贡献指南

欢迎 PR！三条规矩：

1. **一个技能 = 一个目录**，放好 `SKILL.md`
2. **纯提示词模板**，不放代码依赖
3. **一个技能只干一件事**

```bash
skills/
└── 你的技能名/
    ├── SKILL.md          # 必选
    └── references/       # 可选参考文档
```

觉得有用的话，点个 ⭐ 让更多人看见！

<br>

---

# 🌟 Star History

<a href="https://www.star-history.com/#afine907/skills&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=afine907/skills&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=afine907/skills&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=afine907/skills&type=Date" width="600" />
 </picture>
</a>

<br>

---

<p align="center">
  <a href="https://github.com/afine907/skills/issues/new">🐛 报 Bug</a>
  ·
  <a href="https://github.com/afine907/skills/pulls">🔧 提 PR</a>
  ·
  <a href="LICENSE">📄 MIT 协议</a>
</p>

<p align="center">
  <sub>Built with 🎰 by <a href="https://github.com/afine907">afine907</a></sub>
</p>
