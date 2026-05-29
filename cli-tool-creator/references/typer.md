# Python Typer Guide

Typer is a library for building CLI applications in Python, built on top of Click with type-hint-based argument parsing.

## Installation

```bash
pip install typer[all]  # Includes rich for pretty output
```

## Basic Application

```python
import typer

app = typer.Typer(help="A simple CLI tool.")

@app.command()
def hello(name: str, greeting: str = "Hello"):
    """Say hello to someone."""
    typer.echo(f"{greeting}, {name}!")

if __name__ == "__main__":
    app()
```

```
$ python main.py hello World
Hello, World!

$ python main.py hello --greeting Hi World
Hi, World!
```

## Arguments and Options

```python
@app.command()
def process(
    filename: str,                              # Required argument
    output: str = typer.Option("out.txt", help="Output file"),  # Optional option
    verbose: bool = typer.Option(False, "--verbose", "-v"),     # Boolean flag
    count: int = typer.Option(1, min=1, max=100),               # Constrained int
    format: str = typer.Option("json", click_type=typer.Choice(["json", "csv", "xml"])),
):
    """Process a file with given options."""
    if verbose:
        typer.echo(f"Processing {filename} -> {output} (format: {format})")
```

## Multiple Commands (Subcommands)

```python
app = typer.Typer()

@app.command()
def init(name: str):
    """Initialize a new project."""
    typer.echo(f"Creating project: {name}")

@app.command()
def build(target: str = "production"):
    """Build the project."""
    typer.echo(f"Building for {target}")

@app.command()
def deploy(env: str = "staging"):
    """Deploy the project."""
    typer.echo(f"Deploying to {env}")

# Subcommand groups
db_app = typer.Typer()
app.add_typer(db_app, name="db", help="Database commands")

@db_app.command("migrate")
def db_migrate():
    """Run database migrations."""
    typer.echo("Running migrations...")

@db_app.command("seed")
def db_seed():
    """Seed the database."""
    typer.echo("Seeding database...")
```

```
$ python main.py init my-project
$ python main.py db migrate
$ python main.py db seed
```

## Rich Output

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
import time

console = Console()

@app.command()
def list_users():
    """Display users in a table."""
    table = Table(title="Users")
    table.add_column("Name", style="cyan")
    table.add_column("Email", style="green")
    table.add_column("Role", style="yellow")

    table.add_row("Alice", "alice@example.com", "Admin")
    table.add_row("Bob", "bob@example.com", "User")

    console.print(table)

@app.command()
def process_files(files: list[str]):
    """Process multiple files with progress bar."""
    for file in track(files, description="Processing..."):
        time.sleep(0.5)
        console.print(f"  Processed [green]{file}[/green]")
```

## Prompts and Confirmation

```python
@app.command()
def delete(name: str, force: bool = typer.Option(False, "--force", "-f")):
    """Delete a resource."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete {name}?")
        if not confirm:
            raise typer.Abort()

    typer.echo(f"Deleted {name}")

@app.command()
def create():
    """Create with interactive prompts."""
    name = typer.prompt("Project name")
    template = typer.prompt("Template", default="default")
    typer.echo(f"Creating {name} from {template}")
```

## Error Handling

```python
@app.command()
def risky():
    """Command that might fail."""
    try:
        result = do_something()
    except FileNotFoundError:
        typer.echo("Error: File not found", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
```

## Callbacks (Before/After)

```python
@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-V", is_eager=True),
):
    """My CLI Tool - manage your projects."""
    if version:
        typer.echo("my-cli v1.0.0")
        raise typer.Exit()
```

## Testing

```python
from typer.testing import CliRunner

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_hello_with_greeting():
    result = runner.invoke(app, ["hello", "--greeting", "Hi", "World"])
    assert result.exit_code == 0
    assert "Hi, World!" in result.output
```

## Best Practices

1. Use type hints for automatic argument parsing and validation
2. Add `help` strings to all options and commands
3. Use `typer.secho()` for colored output
4. Group related commands with `typer.Typer()` subgroups
5. Use `typer.testing.CliRunner` for automated testing
6. Keep business logic separate from CLI handlers for testability
