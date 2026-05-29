# Node.js Commander Guide

Commander.js is the most popular framework for building CLI applications in Node.js.

## Installation

```bash
npm install commander
```

## Basic Application

```typescript
#!/usr/bin/env node
import { Command } from 'commander'

const program = new Command()

program
  .name('my-cli')
  .description('A CLI tool for managing projects')
  .version('1.0.0')

program
  .command('greet')
  .description('Say hello')
  .argument('<name>', 'Name to greet')
  .option('-g, --greeting <word>', 'Greeting word', 'Hello')
  .action((name, options) => {
    console.log(`${options.greeting}, ${name}!`)
  })

program.parse()
```

```
$ my-cli greet World
Hello, World!

$ my-cli greet --greeting Hi World
Hi, World!
```

## Arguments

```typescript
// Required argument
program.command('clone <source>')
  .action((source) => console.log(`Cloning ${source}`))

// Optional argument
program.command('install [package]')
  .action((pkg) => console.log(pkg ? `Installing ${pkg}` : 'Installing all'))

// Variadic arguments
program.command('copy <source...>')
  .action((sources) => console.log(`Copying: ${sources.join(', ')}`))

// With type coercion
program.command('add <a> <b>')
  .action((a, b) => console.log(Number(a) + Number(b)))
```

## Options

```typescript
program
  .command('serve')
  .option('-p, --port <number>', 'Port number', '3000')
  .option('-h, --host <host>', 'Host address', 'localhost')
  .option('--no-open', 'Do not open browser')       // Negated boolean
  .option('-v, --verbose', 'Verbose output', false)  // Boolean flag
  .option('-c, --config <path>', 'Config file path')
  .action((options) => {
    const port = parseInt(options.port)
    console.log(`Serving on ${options.host}:${port}`)
    if (options.verbose) console.log('Verbose mode enabled')
  })
```

## Subcommands

```typescript
// Git-style subcommands
const db = program.command('db').description('Database operations')

db.command('migrate')
  .description('Run migrations')
  .option('--dry-run', 'Preview without executing')
  .action((options) => {
    console.log(options.dryRun ? 'Previewing migrations...' : 'Running migrations...')
  })

db.command('seed')
  .description('Seed the database')
  .option('--count <n>', 'Number of records', '100')
  .action((options) => {
    console.log(`Seeding ${options.count} records`)
  })
```

## Custom Help

```typescript
program
  .command('deploy')
  .description('Deploy application')
  .addHelpText('after', `
  
Examples:
  $ my-cli deploy staging
  $ my-cli deploy production --force
  $ my-cli deploy --dry-run
  `)
```

## Async Actions

```typescript
program
  .command('fetch')
  .argument('<url>')
  .action(async (url) => {
    try {
      const response = await fetch(url)
      const data = await response.json()
      console.log(JSON.stringify(data, null, 2))
    } catch (error) {
      console.error('Failed to fetch:', error.message)
      process.exit(1)
    }
  })
```

## Custom Event Handling

```typescript
program.on('command:*', (operands) => {
  console.error(`Unknown command: ${operands[0]}`)
  const available = program.commands.map(c => c.name())
  console.error(`Available commands: ${available.join(', ')}`)
  process.exit(1)
})
```

## Configuration with dotenv

```typescript
import { config } from 'dotenv'
config()

program
  .command('connect')
  .option('--url <url>', 'Database URL', process.env.DATABASE_URL)
  .option('--token <token>', 'Auth token', process.env.AUTH_TOKEN)
  .action((options) => {
    if (!options.url) {
      console.error('Error: --url is required or set DATABASE_URL in .env')
      process.exit(1)
    }
  })
```

## Testing with execa

```typescript
import { execa } from 'execa'
import { describe, it, expect } from 'vitest'

describe('CLI', () => {
  it('shows version', async () => {
    const { stdout } = await execa('node', ['dist/index.js', '--version'])
    expect(stdout).toMatch(/\d+\.\d+\.\d+/)
  })

  it('greets user', async () => {
    const { stdout } = await execa('node', ['dist/index.js', 'greet', 'World'])
    expect(stdout).toBe('Hello, World!')
  })

  it('exits with error on missing arg', async () => {
    await expect(
      execa('node', ['dist/index.js', 'greet'])
    ).rejects.toThrow()
  })
})
```

## Best Practices

1. Always set `.name()` and `.version()` on the root program
2. Use `.argument()` for required inputs, `.option()` for optional config
3. Provide sensible defaults for options
4. Use `addHelpText()` for usage examples
5. Handle errors gracefully with `process.exit(1)`
6. Use `#!/usr/bin/env node` shebang for global installs
7. Validate and coerce types in action handlers
8. Use `program.parseAsync()` for async actions
