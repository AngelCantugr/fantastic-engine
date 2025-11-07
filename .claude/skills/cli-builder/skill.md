# CLI Builder Skill

You are an expert at designing and building command-line interface applications.

## When to Use

Activate when the user:
- Wants to create a CLI tool
- Mentions "command line", "terminal app", "CLI"
- Needs to build developer tools
- Wants to automate tasks with a CLI

## CLI Design Principles

### 1. Be Predictable
Follow Unix conventions and user expectations

### 2. Be Helpful
Provide clear help text, examples, and error messages

### 3. Be Respectful
Ask before destructive actions, provide --yes flag for automation

### 4. Be Discoverable
Make features easy to find through help and autocomplete

### 5. Be Fast
Optimize for common use cases, use caching when appropriate

## CLI Structure

```
mycli [global options] <command> [command options] [arguments]

Examples:
  mycli --version
  mycli config --set key=value
  mycli deploy --env production
```

## Output Format

```markdown
## 🖥️  CLI Application: [Name]

### Command Structure

```bash
[app-name] [global-options] <command> [options] [arguments]
```

### Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize new project |
| `start` | Start the application |
| `build` | Build for production |

### Global Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--version` | `-v` | Show version |
| `--help` | `-h` | Show help |
| `--config` | `-c` | Config file path |

---

## Implementation

### File Structure

```
cli-app/
├── bin/
│   └── cli.js          # Entry point
├── src/
│   ├── commands/       # Command implementations
│   │   ├── init.js
│   │   ├── start.js
│   │   └── build.js
│   ├── utils/          # Helper functions
│   │   ├── config.js
│   │   ├── logger.js
│   │   └── spinner.js
│   └── index.js
├── package.json
└── README.md
```

### package.json Setup

```json
{
  "name": "mycli",
  "version": "1.0.0",
  "bin": {
    "mycli": "./bin/cli.js"
  },
  "dependencies": {
    "commander": "^11.0.0",
    "chalk": "^5.0.0",
    "ora": "^6.0.0",
    "inquirer": "^9.0.0"
  }
}
```

### Installation

```bash
npm install
npm link  # Make globally available for testing
```

---

## Testing

```bash
# Run the CLI
mycli --help
mycli start --port 3000
```
```

## Popular CLI Frameworks

### Node.js

#### Commander.js
```javascript
#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';

const program = new Command();

program
  .name('mycli')
  .description('My awesome CLI tool')
  .version('1.0.0');

program
  .command('init')
  .description('Initialize a new project')
  .option('-t, --template <type>', 'template to use')
  .action((options) => {
    console.log(chalk.green('✓ Initializing project...'));
    console.log(`Template: ${options.template || 'default'}`);
  });

program
  .command('build')
  .description('Build the project')
  .option('-e, --env <environment>', 'environment', 'production')
  .option('--watch', 'watch for changes')
  .action((options) => {
    console.log(chalk.blue('Building...'));
    console.log(`Environment: ${options.env}`);
    if (options.watch) {
      console.log(chalk.yellow('👀 Watching for changes...'));
    }
  });

program.parse();
```

#### Yargs
```javascript
#!/usr/bin/env node

import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

yargs(hideBin(process.argv))
  .command('init [name]', 'Initialize project', (yargs) => {
    return yargs.positional('name', {
      describe: 'project name',
      default: 'my-project'
    });
  }, (argv) => {
    console.log(`Initializing ${argv.name}`);
  })
  .command('start', 'Start the server', (yargs) => {
    return yargs
      .option('port', {
        alias: 'p',
        type: 'number',
        description: 'Port number',
        default: 3000
      });
  }, (argv) => {
    console.log(`Starting on port ${argv.port}`);
  })
  .demandCommand(1, 'You need at least one command')
  .help()
  .argv;
```

### Python

#### Click
```python
#!/usr/bin/env python3

import click

@click.group()
@click.version_option()
def cli():
    """My awesome CLI tool"""
    pass

@cli.command()
@click.option('--template', '-t', default='default', help='Template to use')
def init(template):
    """Initialize a new project"""
    click.echo(click.style('✓ Initializing project...', fg='green'))
    click.echo(f'Template: {template}')

@cli.command()
@click.option('--env', '-e', default='production', help='Environment')
@click.option('--watch', is_flag=True, help='Watch for changes')
def build(env, watch):
    """Build the project"""
    click.echo(click.style('Building...', fg='blue'))
    click.echo(f'Environment: {env}')
    if watch:
        click.echo(click.style('👀 Watching for changes...', fg='yellow'))

if __name__ == '__main__':
    cli()
```

#### Typer
```python
#!/usr/bin/env python3

import typer
from typing import Optional

app = typer.Typer()

@app.command()
def init(
    name: str = typer.Argument("my-project"),
    template: str = typer.Option("default", "--template", "-t")
):
    """Initialize a new project"""
    typer.echo(f"Initializing {name} with {template} template")

@app.command()
def start(
    port: int = typer.Option(3000, "--port", "-p"),
    watch: bool = typer.Option(False, "--watch")
):
    """Start the server"""
    typer.echo(f"Starting on port {port}")
    if watch:
        typer.echo("Watching for changes...")

if __name__ == "__main__":
    app()
```

### Go

#### Cobra
```go
package main

import (
    "fmt"
    "github.com/spf13/cobra"
    "os"
)

var rootCmd = &cobra.Command{
    Use:   "mycli",
    Short: "My awesome CLI tool",
    Long:  `A CLI tool for managing projects`,
}

var initCmd = &cobra.Command{
    Use:   "init [name]",
    Short: "Initialize a new project",
    Args:  cobra.MaximumNArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        name := "my-project"
        if len(args) > 0 {
            name = args[0]
        }
        fmt.Printf("Initializing %s\n", name)
    },
}

var buildCmd = &cobra.Command{
    Use:   "build",
    Short: "Build the project",
    Run: func(cmd *cobra.Command, args []string) {
        env, _ := cmd.Flags().GetString("env")
        watch, _ := cmd.Flags().GetBool("watch")

        fmt.Printf("Building for %s\n", env)
        if watch {
            fmt.Println("Watching for changes...")
        }
    },
}

func init() {
    buildCmd.Flags().StringP("env", "e", "production", "Environment")
    buildCmd.Flags().Bool("watch", false, "Watch for changes")

    rootCmd.AddCommand(initCmd)
    rootCmd.AddCommand(buildCmd)
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

## Essential CLI Features

### 1. Color Output

```javascript
import chalk from 'chalk';

console.log(chalk.green('✓ Success!'));
console.log(chalk.red('✗ Error'));
console.log(chalk.yellow('⚠ Warning'));
console.log(chalk.blue('ℹ Info'));
console.log(chalk.gray('Debug info'));
```

### 2. Progress Indicators

```javascript
import ora from 'ora';

const spinner = ora('Loading...').start();

setTimeout(() => {
  spinner.succeed('Done!');
  // or spinner.fail('Failed!');
}, 2000);
```

### 3. Interactive Prompts

```javascript
import inquirer from 'inquirer';

const answers = await inquirer.prompt([
  {
    type: 'input',
    name: 'projectName',
    message: 'What is your project name?',
    default: 'my-project'
  },
  {
    type: 'list',
    name: 'template',
    message: 'Choose a template:',
    choices: ['React', 'Vue', 'Vanilla']
  },
  {
    type: 'confirm',
    name: 'typescript',
    message: 'Use TypeScript?',
    default: true
  }
]);

console.log(answers);
```

### 4. Progress Bars

```javascript
import cliProgress from 'cli-progress';

const bar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);

bar.start(100, 0);

let progress = 0;
const interval = setInterval(() => {
  progress += 10;
  bar.update(progress);

  if (progress >= 100) {
    bar.stop();
    clearInterval(interval);
  }
}, 200);
```

### 5. Tables

```javascript
import Table from 'cli-table3';

const table = new Table({
  head: ['Name', 'Status', 'Port'],
  colWidths: [20, 15, 10]
});

table.push(
  ['API Server', 'Running', '3000'],
  ['Database', 'Running', '5432'],
  ['Redis', 'Stopped', '-']
);

console.log(table.toString());
```

### 6. Configuration Management

```javascript
import Configstore from 'configstore';
import { readPackageUp } from 'read-pkg-up';

const { packageJson } = await readPackageUp();
const config = new Configstore(packageJson.name);

// Set
config.set('apiKey', 'abc123');

// Get
const apiKey = config.get('apiKey');

// Delete
config.delete('apiKey');

// Get all
const all = config.all;
```

### 7. Argument Parsing

```javascript
// Using minimist
import minimist from 'minimist';

const args = minimist(process.argv.slice(2));
console.log(args);

// node cli.js --port 3000 --watch
// { _: [], port: 3000, watch: true }
```

### 8. File Operations

```javascript
import fs from 'fs/promises';
import path from 'path';

// Check if file exists
const exists = async (filePath) => {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
};

// Create directory recursively
await fs.mkdir(dirPath, { recursive: true });

// Copy file
await fs.copyFile(source, destination);

// Read JSON
const data = JSON.parse(await fs.readFile('config.json', 'utf8'));
```

## CLI Best Practices

### 1. Exit Codes

```javascript
process.exit(0);  // Success
process.exit(1);  // General error
process.exit(2);  // Misuse of command
```

### 2. Handle Signals

```javascript
process.on('SIGINT', () => {
  console.log('\nGracefully shutting down...');
  // Cleanup
  process.exit(0);
});
```

### 3. Error Handling

```javascript
try {
  await riskyOperation();
} catch (error) {
  console.error(chalk.red('✗ Error:'), error.message);
  if (process.env.DEBUG) {
    console.error(error.stack);
  }
  process.exit(1);
}
```

### 4. Verbose Mode

```javascript
const verbose = program.opts().verbose;

function log(message) {
  if (verbose) {
    console.log(chalk.gray(`[DEBUG] ${message}`));
  }
}
```

### 5. Version Information

```javascript
import { readFileSync } from 'fs';

const packageJson = JSON.parse(
  readFileSync('./package.json', 'utf8')
);

program.version(packageJson.version);
```

### 6. Help Text

```javascript
program
  .command('deploy')
  .description('Deploy to production')
  .option('-e, --env <environment>', 'deployment environment')
  .addHelpText('after', `

Examples:
  $ mycli deploy --env production
  $ mycli deploy --env staging

More info:
  Documentation: https://docs.example.com
  `);
```

## Testing CLIs

### Integration Tests

```javascript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

describe('CLI', () => {
  test('shows version', async () => {
    const { stdout } = await execAsync('node bin/cli.js --version');
    expect(stdout.trim()).toBe('1.0.0');
  });

  test('initializes project', async () => {
    const { stdout } = await execAsync('node bin/cli.js init test-project');
    expect(stdout).toContain('Initializing test-project');
  });
});
```

## Distribution

### npm Package

```bash
# Publish to npm
npm publish

# Install globally
npm install -g mycli

# Use
mycli --help
```

### Standalone Binary (pkg)

```bash
npm install -g pkg

# Create binaries
pkg package.json

# Outputs:
# - mycli-linux
# - mycli-macos
# - mycli-win.exe
```

## Example: Full CLI App

```javascript
#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import fs from 'fs/promises';

const program = new Command();

program
  .name('project-cli')
  .description('Project management CLI')
  .version('1.0.0');

program
  .command('init')
  .description('Initialize a new project')
  .action(async () => {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: 'Project name:',
        default: 'my-project'
      },
      {
        type: 'list',
        name: 'template',
        message: 'Template:',
        choices: ['basic', 'advanced', 'enterprise']
      }
    ]);

    const spinner = ora('Creating project...').start();

    await fs.mkdir(answers.name, { recursive: true });
    await fs.writeFile(
      `${answers.name}/package.json`,
      JSON.stringify({ name: answers.name, version: '1.0.0' }, null, 2)
    );

    spinner.succeed(chalk.green(`✓ Project ${answers.name} created!`));

    console.log('\nNext steps:');
    console.log(chalk.cyan(`  cd ${answers.name}`));
    console.log(chalk.cyan('  npm install'));
  });

program.parse();
```

## ADHD-Friendly CLI Development

### Start with One Command
Don't build everything at once. Get one command working first.

### Use Templates
Copy structure from successful CLIs like:
- `create-react-app`
- `vue-cli`
- `angular-cli`

### Test Immediately
Run your CLI after every change:
```bash
node bin/cli.js --help
```

### Use Link for Development
```bash
npm link
# Now you can run: mycli anywhere
```
