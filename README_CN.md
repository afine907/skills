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
  <a href="README.md">🇬🇧 English Version (more formal)</a>
</p>

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

<details>
<summary><b>⚡ 30 秒安装</b></summary>

```bash
# 一键全装
npx skills add https://github.com/afine907/skills

# 只装我要验牌
npx skills add https://github.com/afine907/skills --skill wo-yao-yan-pai

# 然后在 Claude Code / Cursor / Windsurf / OpenClaw 里
# 说一句「我要验牌」就能用
```
</details>

<br>

---

# 🗂️ 技能牌组一览 (61个技能)

按软件工程生命周期分类展示。

### 📋 需求阶段 (3个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 📋 **requirements-analyzer** | 模糊需求 → 结构化文档 | 产品经理、技术方案 |
| 📐 **tech-spec** | 需求 → 技术方案设计（架构、API、数据模型） | 技术负责人、架构师 |
| 📖 **user-story** | 需求 → 用户故事 + 验收标准 + 故事点估算 | 产品经理、Scrum Master |

### 🏗️ 开发阶段 (19个)
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
| 🎭 **api-mocking** | API Mock 服务（前后端并行开发） | 前端独立开发 |
| 🌱 **database-seeding** | 数据库种子数据生成（Faker/Factory） | 开发测试环境 |
| 💾 **database-ops** | 数据库设计与运维（Schema/索引/迁移） | 数据库相关 |
| 🎯 **prompt-cicd** | Prompt 版本管理 + 回归测试 + A/B 对比 | Prompt 工程师 |
| 🔧 **tool-use-patterns** | AI Agent 工具集成模式 | Agent 开发者 |

### ✅ 质量阶段 (8个)
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

### 🖥️ 运维阶段 (9个)
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

### ✍️ 效率工具 (9个)
| 技能 | 一句话 | 适合谁 |
|------|--------|--------|
| 📝 **technical-article-writer** | 自动搜索 + 写技术文章 | 写博客、写文档 |
| 🔧 **shell-command** | 中文描述 → shell 命令 + 安全确认 | 日常终端操作 |
| 🐛 **debug-helper** | 结构化 5 步调试分析 | 排查报错、CI 失败 |
| 🔤 **regex-buddy** | 描述 → 正则 + 逐段解释 + 测试用例 | 数据提取、格式校验 |
| 🎯 **prompt-engineering** | 任务描述 → 高质量 LLM prompt | 技能创建、AI 工作流 |
| 📓 **meeting-notes** | 会议录音 → 结构化会议纪要 | 团队同步、每日站会 |
| 📄 **doc-generator** | 代码 → 文档（README/API/架构/注释） | 文档补充 |
| 🔗 **symlink-maker** | 跨平台符号链接创建 | 文件管理 |
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

# 🎯 各技能详解

## 🧵 [Task-Loom](task-loom/SKILL.md) — 项目编排引擎

```
/task-loom init my-project docs/prd.md
/task-loom audit     → 风险扫描，P0 问题提前暴露
/task-loom plan      → DAG 任务图，依赖一目了然
/task-loom execute   → 按依赖顺序生成代码
```

**痛点**：万字 PRD 直接喂给 LLM，上下文窗口炸了，重要需求遗漏了。
**解法**：Task-Loom 把大需求拆成 DAG 依赖图，按拓扑序分批生成。复杂项目一把梭。

## ✍️ [Commit](commit/SKILL.md) — Commit 生成器

```bash
git add .
/commit   # → feat(auth): add JWT token refresh with refresh rotation
```

**痛点**：每次写 commit message 都要想半天，要不就写个 "fix bug" 糊弄。
**解法**：自动分析 diff，按 Conventional Commits 规范生成消息，semantic-release 直接过。

## 🔍 [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md)

```bash
/commit-diff-analyzer <sha1> <sha2>
```

**痛点**：Code Review 时「这俩 commit 到底改了啥」——最常问也最烦的问题。
**解法**：结构化对比，分类展示变更，一眼看出影响范围。

## 📝 [PR-Description](pr-description/SKILL.md) — PR 描述生成器

```bash
/pr-description  # 自动分析当前分支 diff，生成 PR 描述
```

**痛点**：提 PR 时写不出好的描述，要么太短（"fix bug"），要么太长（没人看）。

**解法**：分析分支级别的 git diff，按模块归组生成结构化 PR 描述（Summary + Changes + Breaking Changes + Test Plan）。可选通过 `gh pr create` 直接创建 PR，内置认证检查和推送确认。

## 📜 [Changelog-Generator](changelog-generator/SKILL.md) — 更新日志生成器

```bash
/changelog-generator v1.0.0..HEAD
```

**痛点**：发版前总要手动整理 changelog，或者干脆不写。

**解法**：读取 git 标签/提交范围，按 Conventional Commits 的 type（feat/fix/refactor 等）分组输出 Keep a Changelog 格式。自动检测 Breaking Change 并建议版本号增量。

## 🧠 [Explain-Code](explain-code/SKILL.md)

```bash
/explain-code src/auth/
```

**痛点**：接手老项目，打开一个目录几百个文件，不知道从哪看起。
**解法**：分析代码结构、依赖关系、设计模式，生成人能看懂的解读。

## 🧪 [Test-Generator](test-generator/SKILL.md) — 自动生成测试

```bash
# 为指定文件生成测试
test-generator src/services/auth.py
```

**痛点**：写测试太费时间，经常被跳过。
**解法**：自动分析代码逻辑、分支路径、边界条件，生成覆盖正常路径、异常场景、边界条件的 pytest 测试用例。和 wo-yao-yan-pai 天然搭档——先审查再补测试。

## 📋 [Requirements-Analyzer](requirements-analyzer/SKILL.md)

```bash
/requirements-analyzer "做个用户登录系统，支持 SSO"
# → 输出：用户故事 + 技术选型 + API 设计 + 数据模型
```

**痛点**：需求说得不清不楚，「先做着看看」——做着做着就偏了。
**解法**：把模糊需求转化为可落地的结构化文档。

## 🖥️ [Remote-Exec](remote-exec/SKILL.md) — SSH 远程执行

```bash
# 在远程服务器执行命令
remote-exec root@api.example.com "systemctl status app"
```

**痛点**：排查线上问题要切窗口、敲 SSH、复制粘贴，效率低。
**解法**：在当前会话直接 SSH 连接远程服务器执行命令，无需额外窗口。内置安全规则，破坏性操作自动确认。

## 📊 [Log-Analyzer](log-analyzer/SKILL.md) — 日志分析

```bash
# 分析来自 remote-exec 或粘贴的日志
分析这段 Nginx 错误日志：...
```

**痛点**：原始日志堆在一起，肉眼找异常太累。
**解法**：自动识别日志格式（Nginx、JSON、syslog、Java 堆栈等），提取异常模式、频率统计、趋势分析，输出结构化报告。和 remote-exec 天然搭档：远程拉日志，就地分析。

## ⚙️ [CI-Workflow](ci-workflow/SKILL.md) — CI/CD 配置生成器

```bash
# 描述 → CI 配置文件
配个 GitHub Actions，Node.js 项目，npm 构建+测试
```

**痛点**：GitHub Actions 和 GitLab CI 的 YAML 语法没人能一次写对——action 版本、缩进、缓存 key 格式每次都查。更麻烦的是安全：明文 Secrets、pull_request_target 滥用、权限过大，踩坑了才知道。

**解法**：自然语言 → CI 配置文件 + 逐段解释 + 内置安全审查。覆盖构建测试、Docker 推送、部署、Release、Lint、安全扫描等场景。每次输出附带安全审查报告（检测硬编码密钥、权限过大、缺少缓存等问题）。

## ✅ [Deploy-Checklist](deploy-checklist/SKILL.md) — 部署检查清单

```bash
/deploy-checklist  # 生成预发布检查清单
```

**痛点**：线上事故最常见的原因——"忘了改配置"、"忘了备份"、"部署完才发现监控没配"。

**解法**：自动识别项目类型（根据技术栈特征检测），分析 git 最近变更判断风险点（DB 迁移？依赖更新？配置变动？），生成精准的预发布检查清单，覆盖数据库、配置、监控、回滚、上线后验证。

## 📝 [Technical-Article-Writer](technical-article-writer/SKILL.md)

```bash
/technical-article-writer "Go 语言 WebSocket 服务器从零到一"
```

**痛点**：写技术文章太费时间，查资料、组织结构、排版格式。
**解法**：自动搜索资料 → 制定大纲 → 撰写正文 → 多平台适配。

## 🔧 [Shell-Command](shell-command/SKILL.md) — 命令翻译官

```bash
# 自然语言转 shell 命令
帮我找 /var 下超过 100MB 的大文件
```

**痛点**：每天 N 次要敲不熟悉的命令，搜了写、写了改。通用 chat 生成的命令经常漏参数或没有安全提示。

**解法**：自然语言 → shell 命令 + 三级安全标签（🟢 安全/🟡 需确认/🔴 拒绝）。覆盖文件操作、进程管理、网络诊断、Docker、Git 等场景。每次输出都附带命令说明和安全建议。

## 🐛 [Debug-Helper](debug-helper/SKILL.md) — 调试助手

```bash
# 贴报错信息，自动分析
报错了：Traceback... KeyError: 'user_id'
```

**痛点**：Debug 是开发者最高频的 AI 场景，但通用 chat 没有分析框架，反复"再贴点上下文"。

**解法**：固定 5 步调试流水线——定位 → 上下文 → 假设 → 验证 → 修复。支持 Python/Node.js/Go 异常、HTTP 错误、系统错误。输出结构化报告：按概率排序的根因假设、验证方法、具体修复方案。

## 🔤 [Regex-Buddy](regex-buddy/SKILL.md) — 正则助手

```bash
# 描述 → 正则 + 测试用例，一次输出
写个正则匹配中国大陆手机号
```

**痛点**：写正则每次都要 3-4 轮迭代，读别人的正则更痛苦。

**解法**：描述 → 正则 + 逐段解释 + 测试用例，一次性输出。包含正则各段的含义拆解、正反测试用例、边界条件标记。纯翻译工作，不需要创意，就应该一次写对。

## 🎯 [Prompt-Engineering](prompt-engineering/SKILL.md) — Prompt 优化器

```bash
/prompt-engineering "写一个审查 Python 代码安全的 Agent"
```

**痛点**：写 prompt 全靠感觉，同样的任务不同人写出来的效果天差地别。

**解法**：任务描述 → 结构化高质量 prompt。支持 4 种结构模板（分类/生成/COT/代码生成），包含角色设计、输出控制、防御性提示。Dogfooding：这个仓库的技能就是用这个技能写的。

## 📓 [Meeting-Notes](meeting-notes/SKILL.md) — 会议纪要生成器

```bash
/meeting-notes "今天的站会讨论了部署管道的问题..."
```

**痛点**：会议纪要大家都不想写，写了也没人看。但开会没有记录等于没开。

**解法**：会议录音/文字 → 结构化会议纪要。提取讨论要点、决策记录、待办事项（含负责人和截止日期）。支持语音转文字清洗（去除填充词）、技术讨论深度记录（方案对比、架构决策）。

<br>

---

# 📁 项目结构

```
skills/
├── requirements-analyzer/        # 📋 需求分析器
├── task-loom/                    # 🧵 项目编排引擎
├── wo-yao-yan-pai/               # 🃏 我要验牌
├── explain-code/                 # 🧠 代码解析器
├── test-generator/               # 🧪 测试生成器
├── commit/                       # ✍️ Commit 生成器
├── commit-diff-analyzer/         # 🔍 Commit 对比分析
├── pr-description/               # 📝 PR 描述生成器
├── changelog-generator/          # 📜 Changelog 生成器
├── ci-workflow/                  # ⚙️ CI/CD 配置生成器
├── remote-exec/                  # 🖥️ 远程 SSH 执行器
├── log-analyzer/                 # 📊 日志分析器
├── deploy-checklist/             # ✅ 部署检查清单
├── technical-article-writer/     # 📝 技术文章写手
├── shell-command/                # 🔧 Shell 命令翻译官
├── debug-helper/                 # 🐛 调试助手
├── regex-buddy/                  # 🔤 正则助手
├── prompt-engineering/           # 🎯 Prompt 优化器
├── meeting-notes/                # 📓 会议纪要生成器
│
├── api-debug/                    # 🔧 API 调试速查
├── docker-essentials/            # 🐳 Docker 速查
├── linux-ops/                    # 🖧 Linux 运维速查
├── performance-profiling/        # ⚡ 性能分析速查
└── python-testing/               # 🐍 Python 测试速查
```

每个技能目录包含：
- `SKILL.md` — 完整提示词模板，复制即用
- `references/` — 详细参考指南和检查清单

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
