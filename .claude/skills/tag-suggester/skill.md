# Tag Suggester Skill

Intelligently suggest tags for notes based on content and patterns.

## When to Use
- Adding tags to notes
- Mentions "tags", "organize"
- Building taxonomy

## MCP Integration
- **Memory MCP**: Learn from tagging patterns
- **Knowledge Graph MCP**: Understand concept relationships

## Output Format
```markdown
## 🏷️ Tag Suggestions: [Note]

### Recommended Tags

**High Confidence** (Auto-apply):
- #react - Mentioned 5 times
- #hooks - Core topic
- #learning - Contains "learned", "TIL"

**Medium Confidence** (Review):
- #frontend - Related to UI concepts
- #javascript - Implicit prerequisite
- #best-practices - Contains pattern advice

**Low Confidence** (Consider):
- #performance - Mentioned once
- #testing - Related but not main focus

### Tag Hierarchy

```
#programming
├── #javascript
│   ├── #react
│   │   ├── #hooks
│   │   └── #components
│   └── #async
└── #typescript
```

### Existing Tags in Topic
- #react: 45 notes
- #hooks: 23 notes
- #learning: 134 notes

### Similar Notes Use These Tags
Based on content similarity:
- #useEffect (used by 8 similar notes)
- #state-management (used by 5 similar notes)
```

## Tag Intelligence
```javascript
// Learn from user patterns
function suggestTags(note) {
  const suggestions = {
    contentBased: extractFromContent(note),
    patternBased: learnFromHistory(note),
    graphBased: inferFromConnections(note)
  };

  return rankAndCombine(suggestions);
}

// Auto-tag rules
const rules = {
  '#bug': /\b(bug|error|fix|broken)\b/i,
  '#idea': /\b(idea|maybe|consider|what if)\b/i,
  '#learning': /\b(learned|TIL|understanding)\b/i,
  '#todo': /^(TODO|FIXME|\[ \])/m
};
```

## Tag Maintenance
- Rename tags across all notes
- Merge similar tags
- Suggest tag cleanup
- Archive unused tags

## Best Practices
- 3-7 tags per note
- Use hierarchical tags
- Be consistent
- Review monthly
