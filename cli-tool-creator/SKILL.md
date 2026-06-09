---
name: cli-tool-creator
description: |
  【CLI工具开发】设计和开发命令行工具，包含参数解析、子命令、交互式提示、输出格式化、自动补全。

  触发时机：
  - 用户要求"开发CLI工具"、"命令行工具"
  - 需要将脚本封装为可分发的 CLI
  - 需要添加交互式命令行界面

  支持 Python(Click/Typer) 和 Node.js(Commander/Ink)。
category: development
---

# CLI Tool Creator — CLI 工具开发技能

设计和开发专业的命令行工具，提供良好的用户体验。


## Goal

设计和开发命令行工具，包含参数解析、子命令、交互式提示、输出格式化、自动补全

## Trigger

- 用户要求"开发CLI工具"、"命令行工具"
  - 需要将脚本封装为可分发的 CLI
  - 需要添加交互式命令行界面

## 工作流程

```
技术选型 → 项目生成 → 命令实现 → 测试与分发
```

### Step 1: 技术选型
- 选择语言和框架（Python Typer/Click 或 Node.js Commander/Ink）
- 确定功能需求（子命令、交互式提示、输出格式）

### Step 2: 项目生成
- 创建项目目录结构
- 生成配置文件（pyproject.toml / package.json）
- 生成入口文件和命令注册

### Step 3: 命令实现
- 实现参数解析和验证
- 实现子命令逻辑
- 添加彩色输出和进度条
- 添加自动补全脚本

### Step 4: 测试与分发
- 编写单元测试
- 打包分发（pip publish / npm publish）

## 语言选择决策流程

```
用户需求分析
  │
  ├─ 团队熟悉 Python？──是──→ 需要 TUI？
  │                              ├─ 是 → InquirerPy + Rich
  │                              └─ 否 → Typer（推荐，自动生成帮助）
  │
  ├─ 团队熟悉 Node.js？──是──→ 需要复杂终端 UI？
  │                                ├─ 是 → Ink（React 风格）
  │                                └─ 否 → Commander（推荐，轻量）
  │
  ├─ 团队熟悉 Go？──是──→ Cobra（高性能，静态二进制）
  │
  ├─ 需要分发为单文件？──是──→ Go + Cobra
  │
  └─ 不确定？→ Typer（开发效率最高）
```

## 技术选型

| 语言 | 框架 | 特点 |
|------|------|------|
| Python | Typer | 类型提示、自动生成帮助 |
| Python | Click | 功能丰富、灵活 |
| Node.js | Commander | 流行、轻量 |
| Node.js | Ink | React 风格的终端 UI |
| Go | Cobra | 功能强大、kubectl 使用 |

## Python + Typer 实现

### 项目结构

```
my-cli/
├── src/
│   └── my_cli/
│       ├── __init__.py
│       ├── main.py          # 入口
│       ├── commands/         # 子命令
│       │   ├── __init__.py
│       │   ├── init.py
│       │   ├── build.py
│       │   └── deploy.py
│       ├── utils/            # 工具函数
│       │   ├── config.py
│       │   └── output.py
│       └── types.py          # 类型定义
├── tests/
├── pyproject.toml
└── README.md
```

### 主入口

```python
# src/my_cli/main.py
import typer
from typing import Optional
from enum import Enum

app = typer.Typer(
    name="my-cli",
    help="一个示例 CLI 工具",
    no_args_is_help=True,
)

class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"

@app.command()
def init(
    name: str = typer.Argument(..., help="项目名称"),
    template: str = typer.Option("default", "-t", "--template", help="项目模板"),
    force: bool = typer.Option(False, "-f", "--force", help="强制覆盖已存在的目录"),
):
    """初始化新项目"""
    typer.echo(f"正在创建项目: {name}")
    # 初始化逻辑
    typer.echo(typer.style("✓ 项目创建成功!", fg=typer.colors.GREEN))

@app.command()
def build(
    target: str = typer.Option("production", "-t", "--target", help="构建目标"),
    watch: bool = typer.Option(False, "-w", "--watch", help="监听文件变化"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="详细输出"),
):
    """构建项目"""
    typer.echo(f"构建目标: {target}")
    if watch:
        typer.echo("监听模式已启用...")

@app.command()
def deploy(
    environment: str = typer.Argument(..., help="部署环境"),
    dry_run: bool = typer.Option(False, "--dry-run", help="模拟部署"),
):
    """部署项目"""
    typer.echo(f"部署到: {environment}")
    if dry_run:
        typer.echo("模拟部署模式，不会实际部署")

@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-V", help="显示版本"),
    log_level: LogLevel = typer.Option(LogLevel.info, "--log-level", help="日志级别"),
):
    """My CLI - 一个示例命令行工具"""
    if version:
        typer.echo("my-cli v1.0.0")
        raise typer.Exit()

if __name__ == "__main__":
    app()
```

### 交互式提示

```python
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.console import Console

console = Console()

def interactive_init():
    """交互式初始化"""
    name = Prompt.ask("项目名称", default="my-project")
    
    template = Prompt.ask(
        "选择模板",
        choices=["default", "react", "vue", "python"],
        default="default"
    )
    
    use_typescript = Confirm.ask("使用 TypeScript?", default=True)
    
    port = IntPrompt.ask("开发端口", default=3000)
    
    console.print(f"\n配置确认:")
    console.print(f"  名称: {name}")
    console.print(f"  模板: {template}")
    console.print(f"  TypeScript: {use_typescript}")
    console.print(f"  端口: {port}")
    
    if Confirm.ask("确认创建?"):
        # 执行创建逻辑
        pass
```

### 进度条和表格

```python
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.live import Live
import time

def show_progress():
    """显示进度条"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("处理中...", total=100)
        for i in range(100):
            time.sleep(0.05)
            progress.update(task, advance=1)

def show_table():
    """显示表格"""
    table = Table(title="项目列表")
    table.add_column("名称", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("版本", style="yellow")
    
    table.add_row("project-a", "✓ 正常", "1.2.0")
    table.add_row("project-b", "⚠ 警告", "0.9.0")
    table.add_row("project-c", "✗ 错误", "0.1.0")
    
    console.print(table)
```

## Node.js + Commander 实现

```javascript
#!/usr/bin/env node

const { program } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');
const ora = require('ora');

program
  .name('my-cli')
  .description('一个示例 CLI 工具')
  .version('1.0.0');

program
  .command('init <name>')
  .description('初始化新项目')
  .option('-t, --template <template>', '项目模板', 'default')
  .option('-f, --force', '强制覆盖', false)
  .action(async (name, options) => {
    const spinner = ora(`创建项目 ${name}...`).start();
    
    try {
      // 创建逻辑
      await createProject(name, options.template);
      spinner.succeed(chalk.green(`项目 ${name} 创建成功!`));
    } catch (error) {
      spinner.fail(chalk.red(`创建失败: ${error.message}`));
    }
  });

program
  .command('build')
  .description('构建项目')
  .option('-t, --target <target>', '构建目标', 'production')
  .option('-w, --watch', '监听模式', false)
  .action((options) => {
    console.log(`构建目标: ${options.target}`);
  });

// 交互式命令
program
  .command('interactive')
  .description('交互式配置')
  .action(async () => {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: '项目名称:',
        default: 'my-project'
      },
      {
        type: 'list',
        name: 'template',
        message: '选择模板:',
        choices: ['default', 'react', 'vue', 'python']
      },
      {
        type: 'confirm',
        name: 'typescript',
        message: '使用 TypeScript?',
        default: true
      }
    ]);
    
    console.log(chalk.green('\n配置:'));
    console.log(JSON.stringify(answers, null, 2));
  });

program.parse();
```

## 输出格式化

### JSON 输出

```python
import json

def output_json(data, pretty=True):
    """JSON 格式输出"""
    if pretty:
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        typer.echo(json.dumps(data, ensure_ascii=False))
```

### 表格输出

```python
from rich.table import Table

def output_table(headers: list, rows: list):
    """表格格式输出"""
    table = Table()
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)
```

## 自动补全

```python
# Typer 自动生成补全
# 安装: my-cli --install-completion

# 手动添加补全
@app.command()
def deploy(
    environment: str = typer.Argument(
        ...,
        help="部署环境",
        autocompletion=lambda: ["dev", "staging", "production"]
    )
):
    pass
```

## 打包发布

### Python (pyproject.toml)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-cli"
version = "1.0.0"
description = "A sample CLI tool"
requires-python = ">=3.11"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.scripts]
my-cli = "my_cli.main:app"
```

### Node.js (package.json)

```json
{
  "name": "my-cli",
  "version": "1.0.0",
  "bin": {
    "my-cli": "./bin/cli.js"
  },
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  }
}
```

## 快速使用

```
# 开发 Python CLI
用 Typer 开发一个文件管理 CLI 工具

# 开发 Node.js CLI
用 Commander 开发一个项目脚手架工具

# 添加交互式功能
为 CLI 添加交互式配置向导

# 发布 CLI 工具
将 CLI 工具发布到 PyPI/npm
```

## 输出模板

Claude 开发 CLI 工具时，按以下格式输出：

```
## CLI 脚手架报告

### 技术选型
- 语言：{Python / Node.js / Go}
- 框架：{Typer / Commander / Cobra}
- 理由：{选择原因}

### 生成文件清单
| 文件路径 | 说明 | 状态 |
|---------|------|------|
| src/my_cli/main.py | 主入口 | 新建 |
| src/my_cli/commands/init.py | init 子命令 | 新建 |
| src/my_cli/utils/output.py | 输出格式化 | 新建 |
| pyproject.toml / package.json | 项目配置 | 新建 |
| ... | ... | ... |

### 命令结构
my-cli
├── init      初始化新项目
├── build     构建项目
└── deploy    部署项目

### 关键代码
（展示主入口和 1-2 个子命令的完整代码）

### 后续步骤
1. pip install -e . / npm link
2. 运行 my-cli --help 验证命令注册
3. 添加子命令实现逻辑
```

**端到端示例：**

用户输入：`用 Typer 开发一个文件管理 CLI 工具`

Claude 输出以上模板，文件清单中包含 Python 项目结构、Typer 入口、子命令文件、pyproject.toml 等，并附上 main.py 的完整代码。

## Edge Cases

- 已有 Python 脚本需要封装为 CLI：使用 Typer 装饰器包装现有函数
- 需要交互式 UI（多选、确认）：Python 用 InquirerPy，Node.js 用 Ink
- 需要自动更新：添加版本检查和更新提示逻辑
- Windows 兼容性：避免使用 Unix-only 的 shell 特性
- 大型 CLI（>20 子命令）：按功能分组，使用命令命名空间

## 不适用

- Web API 服务 → 使用 [python-service-creator](../python-service-creator/SKILL.md) 或 [typescript-service-creator](../typescript-service-creator/SKILL.md)
- GUI 应用 → 使用对应平台的 GUI 框架

## 参考资料

- Typer 文档: [references/typer.md](references/typer.md)
- Commander 文档: [references/commander.md](references/commander.md)
