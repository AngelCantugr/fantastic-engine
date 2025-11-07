# Resource Curator Skill

Organize and manage learning resources for ultralearning projects.

## When to Use
- Found good resource
- Mentions "resources", "materials"
- Overwhelmed by options

## MCP Integration
**Recommended:**
- **Memory MCP**: Store resource library
- **Knowledge Graph MCP**: Link resources to concepts

## Output Format
```markdown
## 📚 Resource Library: [Topic]

### Primary Resources (Use these first)

**Foundation**:
- 📖 [Resource Name](link)
  - Type: Book/Course/Video
  - Time: X hours
  - Level: Beginner
  - Why: Best starting point
  - Status: ✅ Completed

**Practice**:
- 💻 [Platform](link)
  - Type: Interactive
  - Projects: X exercises
  - Status: 🔄 In Progress

### Secondary Resources

**Deep Dives**:
- [Advanced topic resource]

**Different Perspectives**:
- [Alternative explanation]

### Quick References
- [Cheat sheet]
- [Documentation]
- [FAQ]

### MCP Storage
```json
{
  "resources": [
    {
      "name": "React Documentation",
      "url": "https://react.dev",
      "type": "documentation",
      "priority": "high",
      "completed": false,
      "notes": "Start with Thinking in React"
    }
  ]
}
```
```

## Resource Rating System
⭐⭐⭐⭐⭐ Essential - Drop everything, use this
⭐⭐⭐⭐ Excellent - Highly recommended
⭐⭐⭐ Good - Useful supplement
⭐⭐ Ok - Nice to have
⭐ Skip - Not worth the time

## Best Practices
- Maximum 3 primary resources
- Finish one before starting another
- Rate resources after using
- Share findings with others

## ADHD Tips
- Bookmark immediately
- One tab at a time
- Close unused resources
- Schedule specific resource time
