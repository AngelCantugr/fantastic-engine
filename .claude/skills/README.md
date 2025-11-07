# Claude Skills

This directory contains 16 specialized Claude Skills for the fantastic-engine repository.

## 🎯 Skills Overview

### Practical Skills (8)

1. **code-reviewer** - Automated code review with security checks
2. **commit-msg-generator** - Smart git commit messages
3. **bug-hunter** - Systematic debugging assistance
4. **test-writer** - Unit/integration test generation
5. **refactor-guide** - Code refactoring suggestions
6. **api-designer** - REST/GraphQL API design help
7. **security-scanner** - Security audit and vulnerability detection
8. **performance-optimizer** - Performance analysis and optimization

### Experimental/Creative Skills (8)

1. **ascii-art-generator** - ASCII art and diagrams
2. **mermaid-master** - Advanced Mermaid diagram creation
3. **regex-wizard** - Regex pattern generation and testing
4. **data-visualizer** - Chart.js/D3.js visualizations
5. **markdown-beautifier** - Enhanced markdown formatting
6. **cli-builder** - CLI application scaffolding
7. **docker-composer** - Docker setup and compose files
8. **github-actions-builder** - CI/CD workflow creation

## 📖 Documentation

See the full documentation at: [Skills Collection](../../docs/skills-collection.md)

Or visit: https://angelcantugr.github.io/fantastic-engine/skills-collection/

## 🚀 Usage

Skills activate automatically! Just describe your task naturally:

```
"Review my code"              → Activates code-reviewer
"Write tests"                 → Activates test-writer
"Create a Docker setup"       → Activates docker-composer
"Make a Mermaid diagram"      → Activates mermaid-master
```

No need to explicitly call skills - Claude detects and loads them automatically based on your request.

## 📁 Structure

Each skill is a folder containing:
- `skill.md` - Instructions, examples, and best practices

```
skills/
├── code-reviewer/
│   └── skill.md
├── commit-msg-generator/
│   └── skill.md
├── bug-hunter/
│   └── skill.md
└── ... (and 13 more)
```

## ✨ Features

- **Auto-activation**: Skills load automatically when needed
- **Lightweight**: Only 30-50 tokens until loaded
- **Context-aware**: Full content loads only when relevant
- **ADHD-friendly**: Clear, concise, visual guides
- **Comprehensive**: Covers development, debugging, DevOps, and creativity

## 🎨 Highlights

### Most Used Skills
- **commit-msg-generator** - Every commit workflow
- **code-reviewer** - Before every PR
- **test-writer** - TDD and testing
- **bug-hunter** - When things break

### Most Fun Skills
- **ascii-art-generator** - Beautify CLI apps
- **mermaid-master** - Visual diagrams
- **data-visualizer** - Interactive charts

### Most Powerful Skills
- **performance-optimizer** - Speed improvements
- **security-scanner** - Find vulnerabilities
- **api-designer** - Professional APIs

## 🤝 Contributing

Want to customize or add skills?

1. Edit existing `skill.md` files to adapt to your needs
2. Create new folders following the same pattern
3. Follow ADHD-friendly formatting principles

## 📝 Skill Template

```markdown
# [Skill Name] Skill

You are an expert at [description].

## When to Use

Activate when the user:
- [Trigger 1]
- [Trigger 2]

## Output Format

[Define structure]

## Examples

[Provide examples]

## Best Practices

[Tips and guidelines]
```

## 💡 Tips

### For Best Results
1. Be specific about what you need
2. Provide context and examples
3. Let Claude choose the right skill
4. Use skills together for complex tasks

### ADHD-Friendly
- One skill at a time
- Visual feedback with diagrams
- Clear, scannable format
- Quick reference sections

---

**Created:** 2025-11-07

**Skills Count:** 16 (8 practical + 8 experimental)

**Maintained by:** @AngelCantugr
