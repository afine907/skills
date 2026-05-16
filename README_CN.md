<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-%F0%9F%94%8D-blue?logo=claude&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Cursor-%E2%9C%A8-purple?logo=cursor&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/Windsurf-%F0%9F%8C%8A-teal?logo=windsurf&labelColor=1a1a2e" />
  <img src="https://img.shields.io/badge/OpenClaw-%F0%9F%A6%9E-orange?labelColor=1a1a2e" />
  <img src="https://img.shields.io/github/stars/afine907/skills?style=flat&labelColor=1a1a2e" />
</p>

<h1 align="center">🎰 AI Skills — 让你的AI编码助理赌一把</h1>

<p align="center">
  <b>一套专业级 AI Agent 提示词模板，覆盖从验牌到上线的完整开发链。</b><br>
  代码审查、需求拆解、Commit 生成、技术写作 —— 一句话搞定。
</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a>
</p>

<br>

---

<h2 align="center">🃏 主打技能 · 我要验牌</h2>

<p align="center">
  <a href="wo-yao-yan-pai/SKILL.md">
    <img src="https://img.shields.io/badge/🔥_我要验牌-WO_YAO_YAN_PAI-red?style=for-the-badge&labelColor=1a1a2e" />
  </a>
</p>

<p align="center">
  <b>你是「赌侠」还是「小瘪三」？验一验就知道了。</b><br>
  <i>迭代式代码审查 → 报告 → 修复，自动把关 AI 生成代码的质量门槛</i>
</p>

```bash
# 写完代码后，直接说：
我要验牌

# Agent 自动执行：
# 🔍 多维审查 → 📊 生成报告 → 🎯 判定评分 → 🔧 自动修复 → 🔄 迭代闭环

# 👇 判定结果
#   「小瘪三」→ 需要擦皮鞋 🧹
#   「赌侠」  → 质量达标，全场最佳 🎉
```

<table align="center">
<tr>
  <td align="center"><b>🎯 多维审查</b></td>
  <td align="center"><b>🧹 擦皮鞋</b></td>
  <td align="center"><b>🔄 迭代优化</b></td>
  <td align="center"><b>🏆 赌侠认证</b></td>
</tr>
<tr>
  <td>代码质量 · 潜在Bug<br>性能 · 安全 · 最佳实践</td>
  <td>自动修复<br>Medium 及以上问题</td>
  <td>最多 5 轮<br>持续改进</td>
  <td>质量守门人<br>杜绝低质量代码</td>
</tr>
</table>

<details>
<summary><b>⚡ 30 秒安装</b></summary>

```bash
# 一键安装全部
npx skills add https://github.com/afine907/skills

# 只安装我要验牌
npx skills add https://github.com/afine907/skills --skill wo-yao-yan-pai
```
</details>

<br>

---

<h2 align="center">🗂️ 技能牌组</h2>

| 技能 | 一句话 |
|------|--------|
| 🎰 **我要验牌** | 代码审查 → 报告 → 修复。主角技，必须第一个上。 |
| 🧵 **task-loom** | 万字 PRD 秒变可执行代码计划 |
| ✍️ **commit** | 再也不用想 commit message |
| 🔍 **commit-diff-analyzer** | 两个 commit 之间改了啥，一眼看穿 |
| 🧠 **explain-code** | 代码结构 + 设计质量一键分析 |
| 📋 **requirements-analyzer** | 模糊需求 → 结构化文档 |
| 📝 **technical-article-writer** | 自动搜索 + 写技术文章 |

<br>

---

<h2 align="center">🎯 其他技能速览</h2>

### 🧵 [Task-Loom](task-loom/SKILL.md) — 项目编排引擎

```
/task-loom init my-project docs/prd.md
/task-loom audit    → 风险扫描，P0 问题提前暴露
/task-loom plan     → DAG 任务图，依赖一目了然
/task-loom execute  → 按依赖顺序生成代码
```

**适合**：新项目启动、大需求拆解、多人协作对齐

### ✍️ [Commit](commit/SKILL.md) — Commit 生成器

```bash
git add .
/commit    → feat(auth): add JWT token refresh
```

自动分析 diff，生成 Conventional Commits 规范消息。

### 🔍 [Commit-Diff-Analyzer](commit-diff-analyzer/SKILL.md)

对比两个 commit 的变更内容，快速定位改动影响范围。

### 🧠 [Explain-Code](explain-code/SKILL.md)

分析代码结构、设计质量、复杂度，一键生成代码解读。

### 📋 [Requirements-Analyzer](requirements-analyzer/SKILL.md)

把模糊的需求描述转化为结构化的需求文档、功能列表和技术方案。

### 📝 [Technical-Article-Writer](technical-article-writer/SKILL.md)

自动搜索相关资料，撰写结构清晰的技术文章，支持多平台格式输出。

<br>

---

<h2 align="center">📁 项目结构</h2>

```
skills/
├── wo-yao-yan-pai/          # 🃏 主角技 — 迭代式代码审查
├── task-loom/               # 项目编排引擎
├── commit/                  # Commit 生成器
├── commit-diff-analyzer/    # Commit 对比分析
├── explain-code/            # 代码解析
├── requirements-analyzer/   # 需求分析
└── technical-article-writer/# 技术文章写作
```

每个目录包含一个 `SKILL.md`，复制即用。

<br>

---

<h2 align="center">🤝 贡献</h2>

<p align="center">
  欢迎 PR！新建目录 + 写好 <code>SKILL.md</code> = 一个新的技能。<br>
  觉得有用的话，点个 ⭐ 让更多人看到！
</p>

<br>

---

<p align="center">
  <a href="https://github.com/afine907/skills/issues">🐛 报 Bug</a>
  ·
  <a href="https://github.com/afine907/skills/pulls">🔧 提 PR</a>
  ·
  <a href="LICENSE">📄 MIT License</a>
</p>

<p align="center">
  <sub>Made with 🎰 by <a href="https://github.com/afine907">afine907</a></sub>
</p>
