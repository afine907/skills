# Task-Loom - 项目编排引擎

专业级项目编排系统，专为大规模 PRD（10,000+ 行）多文档项目设计。

## 核心特性

- 🔍 **审计优先** - 写代码前识别 PRD 中的逻辑缺陷和安全风险
- ⚙️ **状态机驱动** - INIT → AUDIT → PLAN → EXECUTE → VERIFY 结构化工作流
- ✅ **验证驱动** - 测试通过才算任务完成
- 📝 **上下文连续** - Ledger 系统实现跨任务知识传递

## 命令

| 命令 | 说明 |
|------|------|
| `/task-loom init <project> <prd_paths...>` | 初始化项目工作区 |
| `/task-loom audit` | 扫描 PRD 风险，生成审计报告 |
| `/task-loom plan` | 构建 DAG，分解任务 |
| `/task-loom execute [--task T_XXX]` | 按依赖顺序执行任务 |
| `/task-loom status` | 查看项目状态 |
| `/task-loom resume` | 从检查点恢复 |

## 工作流程

### Phase 1: INIT（初始化）

```bash
/task-loom init my-project docs/prd/*.md
```

执行步骤：
1. 验证项目名称和 PRD 文件存在性
2. 创建目录结构 `.claude/orchestra/my-project/`
3. 解析 PRD 文档，计算 SHA-256 哈希
4. 提取全局约束写入 `constitution.md`
5. 初始化 `manifest.json`

### Phase 2: AUDIT（审计）

```bash
/task-loom audit
```

执行步骤：
1. 滑动窗口扫描（500行，10%重叠）
2. 识别风险并分类：

   **P0（严重）- 必须确认**：
   - 安全漏洞：SQL注入、XSS、CSRF、认证绕过
   - 资金安全：支付逻辑缺陷、金额计算错误
   - 数据安全：敏感数据泄露、权限绕过
   - 并发问题：死锁、竞态条件
   - 可用性：单点故障

   **P1（高）- 建议确认**：
   - 边界条件、缺失的状态转换
   - 性能瓶颈（N+1查询、全表扫描）
   - 未覆盖的异常场景

   **P2（普通）- 自动记录**：
   - 命名不一致、文档歧义

3. 生成 `vulnerability_report.md`
4. P0 风险逐条等待用户确认

### Phase 3: PLAN（规划）

```bash
/task-loom plan
```

执行步骤：
1. 识别功能模块
2. 分解为任务（类型：MODULE_IMPL、TEST、INTEGRATE、REFACTOR）
3. 构建 DAG 依赖图
4. 为每个任务生成 `specs/*.md`

### Phase 4: EXECUTE（执行）

```bash
/task-loom execute
/task-loom execute --task T_001
```

执行步骤：
1. 选择依赖已满足的任务
2. 加载上下文（constitution.md、spec、依赖 ledger）
3. 生成代码文件
4. 生成执行 ledger
5. 更新任务状态

### Phase 5: VERIFY（验证）

```bash
/task-loom verify
```

执行步骤：
1. 检测测试框架（Jest/Vitest/Pytest/go test）
2. 生成/更新测试用例
3. 执行测试
4. 失败自动修复（最多3次）
5. 3次失败触发熔断，回滚 Git

## 工作区结构

```
.claude/orchestra/
└── {{project_name}}/
    ├── manifest.json         # 状态中枢
    ├── constitution.md       # 全局约束
    ├── vulnerability_report.md # 风险审计报告
    ├── specs/                # 技术规格文档
    │   └── T_001.md
    └── ledgers/              # 执行记录
        └── T_001.md
```

## 使用示例

```bash
# 1. 初始化项目
/task-loom init ecommerce docs/prd/*.md

# 2. 审计风险
/task-loom audit

# 3. 规划任务
/task-loom plan

# 4. 执行开发
/task-loom execute

# 5. 验证完成
/task-loom verify

# 查看状态
/task-loom status

# 中断后恢复
/task-loom resume
```

## 关键机制

### 全局约束注入

每次执行任务前，自动注入：
```
【全局约束 - 必须遵守】
以下规则来自 constitution.md：
1. 所有数据库事务必须使用行级锁
2. 所有 API 响应必须包含 requestId
...
```

### 熔断机制

| 触发条件 | 行为 |
|---------|------|
| 单任务失败3次 | SYSTEM_HALT，回滚 Git |
| P0 风险未确认 | AUDIT_HALT |
| 依赖任务失败 | 任务状态 → BLOCKED |
| 测试覆盖率 < 80% | VERIFY_HALT |

### Ledger 上下文传递

执行任务 N+1 时自动加载：
```
【前置任务上下文】
来自 T_001：
- 隐式决策：JWT 有效期 24h
- 导出接口：authMiddleware()、User 类型
```

## 相关脚本

| 脚本 | 说明 |
|------|------|
| `scripts/init_workspace.py` | 初始化工作区 |
| `scripts/dag_manager.py` | DAG 状态管理 |
| `scripts/risk_scanner.py` | PRD 风险扫描 |
| `scripts/spec_generator.py` | 生成任务规格 |
| `scripts/ledger_generator.py` | 生成执行记录 |
