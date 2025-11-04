# Project Template

Full README template for structured projects.

## When to Use

Use this template when:
- ✅ Your experiment has proven successful
- ✅ You want to add structure
- ✅ The project might be shared or reused
- ✅ You're building something substantial

## Template

```markdown
# {PROJECT_NAME}

**Status:** 🧪 Experimental | 🚧 In Progress | ✅ Stable | 📦 Graduated

**Tech Stack:** {LANGUAGE/FRAMEWORK}

**Started:** {DATE}

## Overview

Brief description of what this project does and why you created it.

**Problem it solves:**
{What problem does this address?}

**Key features:**
- Feature 1
- Feature 2
- Feature 3

## Architecture

\`\`\`mermaid
graph TD
    A[Component A] --> B[Component B]
    B --> C[Output]

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style B fill:#00ffff,stroke:#ff00ff,stroke-width:2px,color:#000
    style C fill:#00ff00,stroke:#ff00ff,stroke-width:2px,color:#000
\`\`\`

**Components:**
- **Component A** - Does X
- **Component B** - Does Y
- **Output** - Results in Z

## Environment Setup

This project uses the following environment configuration:

- **Language/Runtime:** {e.g., Node.js, Python, Deno, Rust}
- **Version:** {e.g., 20.x, 3.12, 1.40}
- **Environment File:** {e.g., .nvmrc, .python-version, rust-toolchain.toml}

### Quick Start

\`\`\`bash
# Clone/navigate to project
cd projects/{PROJECT_NAME}

# Setup environment
{ENVIRONMENT_SETUP_COMMAND}
# For Node.js: nvm use
# For Python: uv venv && source .venv/bin/activate
# For Deno: (auto-detects from deno.json)
# For Rust: (auto-detects from rust-toolchain.toml)

# Install dependencies
{INSTALL_COMMAND}
# npm install / uv pip install -r requirements.txt / cargo build

# Run
{RUN_COMMAND}
# npm start / python main.py / deno task dev / cargo run
\`\`\`

## Dependencies

See `{DEPENDENCY_FILE}` for full list:

**Core dependencies:**
- {package-name} - {purpose}
- {package-name} - {purpose}

**Dev dependencies:**
- {package-name} - {purpose}

## Features

### Implemented ✅

- [x] Feature 1 - {description}
- [x] Feature 2 - {description}
- [x] Feature 3 - {description}

### In Progress 🚧

- [ ] Feature 4 - {description}
- [ ] Feature 5 - {description}

### Planned 💡

- [ ] Feature 6 - {description}
- [ ] Feature 7 - {description}

## How It Works

### {Core Concept 1}

\`\`\`mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Request
    System-->>User: Response
\`\`\`

{Explanation of how this works}

### {Core Concept 2}

\`\`\`{language}
// Code example demonstrating the concept
{code}
\`\`\`

{Explanation}

## API Reference

### {Function/Method Name}

**Purpose:** {What it does}

**Signature:**
\`\`\`{language}
{function signature}
\`\`\`

**Parameters:**
- `param1` ({type}) - {description}
- `param2` ({type}) - {description}

**Returns:** {return type} - {description}

**Example:**
\`\`\`{language}
{usage example}
\`\`\`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VAR_NAME` | `value` | What it configures |

### Config File

\`\`\`{format}
{example configuration}
\`\`\`

## Testing

### Running Tests

\`\`\`bash
{TEST_COMMAND}
# npm test / pytest / deno test / cargo test
\`\`\`

### Test Coverage

- Unit tests: {percentage}
- Integration tests: {percentage}
- E2E tests: {percentage}

### Adding Tests

\`\`\`{language}
// Example test
{test code}
\`\`\`

## Troubleshooting

### Common Issues

**Problem:** {Common issue}

**Solution:** {How to fix}

**Details:**
\`\`\`
{Additional context or commands}
\`\`\`

---

**Problem:** {Another issue}

**Solution:** {Fix}

## Performance

{If applicable}

- **Startup time:** {metric}
- **Response time:** {metric}
- **Memory usage:** {metric}
- **Throughput:** {metric}

**Tested with:** {scale/load information}

## Learning Log

### What I Learned

- **{Concept/Technology}** - {What you learned and why it matters}
- **{Pattern/Technique}** - {How it helped solve problems}
- **{Tool/Library}** - {When and why to use it}

### Challenges

**Challenge:** {What was difficult}

**Root cause:** {Why it was hard}

**Solution:** {How you solved it}

**Lesson learned:** {What you'd do differently}

---

**Challenge:** {Another challenge}

...

### Key Insights

💡 {Important realization or breakthrough}

💡 {Pattern or principle discovered}

💡 {Tradeoff or design decision}

## Next Steps

### Short Term

- [ ] {Task} - ⏱️ {time estimate}
- [ ] {Task} - ⏱️ {time estimate}

### Long Term

- [ ] {Feature or improvement}
- [ ] {Feature or improvement}

## Graduation Criteria

Before moving to its own repository:

### Code Quality
- [ ] Core functionality complete
- [ ] Tests written and passing
- [ ] Error handling comprehensive
- [ ] Code reviewed and refactored

### Documentation
- [ ] README comprehensive
- [ ] API fully documented
- [ ] Examples provided
- [ ] Setup instructions clear

### Production Readiness
- [ ] No critical TODOs
- [ ] Dependencies up to date
- [ ] Security reviewed
- [ ] Performance acceptable
- [ ] License chosen
- [ ] CI/CD configured (if needed)

## Resources

- [{Tutorial/Doc used}]({URL}) - {Why helpful}
- [{Library docs}]({URL}) - {What to look for}
- [{Related article}]({URL}) - {Key insights}

## License

{License choice - MIT, Apache, GPL, etc.}

---

**Created:** {DATE}

**Last Updated:** {DATE}
\`\`\`

## Customization Guide

### 1. Project Name & Status

Replace `{PROJECT_NAME}` with your actual project name.

Choose initial status:
- 🧪 **Experimental** - Just created
- 🚧 **In Progress** - Actively developing
- ✅ **Stable** - Production-ready
- 📦 **Graduated** - Moved to own repo

### 2. Tech Stack

Be specific:
- ❌ "JavaScript"
- ✅ "Node.js 20 + TypeScript + Express"

### 3. Architecture Diagram

Create a Mermaid diagram showing:
- Main components
- Data flow
- External dependencies
- Key interactions

Types to consider:
- **Flowchart** - Process/logic flow
- **Sequence** - API interactions
- **Class** - Data structures
- **Graph** - Component relationships

### 4. Environment Setup

Provide exact commands:

```bash
# Good
nvm install 20.11.0
nvm use
npm install

# Bad
Install Node and dependencies
```

### 5. Features Section

Use checkboxes and status emojis:
- ✅ Completed
- 🚧 In progress
- 💡 Planned
- ❌ Removed

### 6. Learning Log

This is CRUCIAL! Document:
- What you learned (concepts, not just tools)
- Why you made certain decisions
- What surprised you
- What you'd do differently

### 7. Graduation Criteria

Be honest about what "ready" means:
- Don't set the bar too high (you'll never graduate)
- Don't set it too low (you'll graduate too early)
- Focus on real usability, not perfection

## Using the Template

### Copy It

```bash
cp -r templates/project-template projects/my-project
cd projects/my-project
```

### Search and Replace

```bash
# Replace all placeholders
sed -i 's/{PROJECT_NAME}/My Awesome Project/g' README.md
sed -i 's/{LANGUAGE\/FRAMEWORK}/Python 3.12 + FastAPI/g' README.md
sed -i 's/{DATE}/2024-01-15/g' README.md
# etc.
```

### Or Use Claude

```
@doc-writer help me fill out the project template for {my project}
```

## Template Sections Explained

### Overview
**Purpose:** Quick understanding of what this is

**Length:** 2-3 sentences + feature list

**Answer:** What does it do? Why did you build it?

### Architecture
**Purpose:** Visual understanding of structure

**Length:** 1 diagram + component descriptions

**Show:** How pieces fit together

### Environment Setup
**Purpose:** Get someone running ASAP

**Length:** Exact commands that work

**Include:** Version requirements, installation steps

### Features
**Purpose:** What works, what doesn't

**Length:** Checklist with status

**Keep current:** Update as you build

### How It Works
**Purpose:** Explain key concepts

**Length:** As much as needed for understanding

**Include:** Diagrams, code examples, explanations

### Learning Log
**Purpose:** Capture knowledge and context

**Length:** Be thorough - this is for future you

**Include:** Concepts, challenges, decisions, insights

### Graduation Criteria
**Purpose:** Clear definition of "done"

**Length:** Comprehensive checklist

**Be realistic:** This determines when to graduate

## Examples

See these projects for inspiration:

- [Experiments Index](../experiments/index.md) - Simple projects
- [Projects Index](../projects/index.md) - Mature projects

---

**Ready to use the template? Copy it and start building! 🚀**
