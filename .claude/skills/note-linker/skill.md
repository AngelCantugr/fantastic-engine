# Note Linker Skill

Create bidirectional links between related notes automatically.

## When to Use
- Building connections
- Mentions "link", "connect", "relate"
- Knowledge graph building

## MCP Integration
**Required:**
- **Knowledge Graph MCP**: Store note relationships
- **Memory MCP**: Query related notes

## Output Format
```markdown
## 🔗 Note Links: [Note Title]

### Suggested Links

**Strong Connections** (>80% similarity):
- [[React Hooks Basics]] - Shared: useState, hooks, React
- [[Component Lifecycle]] - Shared: useEffect, lifecycle
- [[Memory Management]] - Shared: cleanup, memory leaks

**Moderate Connections** (50-80%):
- [[JavaScript Async]] - Shared: async patterns
- [[Testing React]] - Shared: React, testing

**Weak Connections** (<50%):
- [[TypeScript Guide]] - Shared: typing

### Link Types

**Explains**: This note explains concepts in [[Other Note]]
**Builds On**: This note builds on [[Foundation Note]]
**Contradicts**: This note disagrees with [[That Note]]
**Related**: General connection to [[Related Note]]

### Backlinks

**Notes linking to this**:
- [[Advanced React]] mentions this note
- [[Learning Log 2025-01]] references this note
```

## Link Detection
```javascript
// Find related notes
function findRelatedNotes(currentNote, allNotes) {
  return allNotes
    .map(note => ({
      note,
      similarity: calculateSimilarity(currentNote, note),
      sharedConcepts: findSharedConcepts(currentNote, note)
    }))
    .filter(({similarity}) => similarity > 0.5)
    .sort((a, b) => b.similarity - a.similarity);
}
```

## Auto-Linking
- Detect mentions of other note titles
- Find concept overlaps
- Identify temporal relationships
- Track citation patterns
