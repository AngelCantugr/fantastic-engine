# TODO Extractor Skill

Extract and organize action items from notes automatically.

## When to Use
- Processing notes with tasks
- Mentions "TODO", "extract tasks"
- Creating task lists

## MCP Integration
- **Memory MCP**: Store tasks
- **Knowledge Graph MCP**: Link tasks to projects

## Output Format
```markdown
## ✅ Extracted Tasks: 2025-01-15

### Urgent (Do Today)
- [ ] Fix login bug (Safari) #bug #urgent
  - Source: Daily note line 15
  - Context: Production issue
  - Estimated: 2 hours

### High Priority (This Week)
- [ ] Review PR #234 #code-review
  - Source: Team meeting notes
  - Due: Friday
  - Estimated: 1 hour

- [ ] Complete React hooks module #learning
  - Source: Learning log
  - Progress: 75%
  - Remaining: 3 hours

### Medium Priority (Next Week)
- [ ] Research deployment CLI options #research
  - Source: Idea log
  - Type: Exploration

### Low Priority (Someday)
- [ ] Refactor old components #tech-debt
  - Source: Code review notes

### Recurring
- [ ] Weekly team sync (Mondays 10am) #meeting

### Projects

**Authentication System**:
- [ ] Implement OAuth
- [ ] Add 2FA
- [ ] Write tests

**Learning React**:
- [ ] Finish hooks section
- [ ] Build practice project
- [ ] Take quiz

### Export Options
- [ ] Export to markdown checklist
- [ ] Export to GitHub Issues
- [ ] Export to task manager API
```

## Detection Patterns
```javascript
const todoPatterns = [
  /^TODO:/,
  /^- \[ \]/,
  /^FIXME:/,
  /^Action item:/,
  /^Need to/,
  /^Should/,
  /^Must/,
  /^\[ \]/
];

function extractTodos(text) {
  return text
    .split('\n')
    .filter(line => todoPatterns.some(p => p.test(line)))
    .map(parseTodo);
}
```

## Priority Detection
- **Urgent**: "asap", "urgent", "critical", "!!!"
- **High**: "important", "soon", "this week"
- **Medium**: "should", "would be good"
- **Low**: "maybe", "someday", "consider"

## Context Extraction
- Source note
- Surrounding text
- Related tasks
- Project association
- Time estimates
- Dependencies

## Integration
- Export to TickTick
- Export to GitHub Issues
- Export to Notion
- Export to plain markdown
