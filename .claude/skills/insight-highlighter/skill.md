# Insight Highlighter Skill

Identify and highlight key insights, breakthroughs, and important learnings from notes.

## When to Use
- Reviewing notes
- Mentions "insights", "key learnings"
- Creating knowledge summaries

## MCP Integration
- **Memory MCP**: Store insights
- **Knowledge Graph MCP**: Connect insights to concepts

## Output Format
```markdown
## 💡 Key Insights: [Period/Topic]

### Breakthrough Moments

**1. useEffect Cleanup Aha Moment** ⭐⭐⭐
- **Date**: 2025-01-15
- **Insight**: "Cleanup functions run BEFORE re-render, not after unmount only"
- **Impact**: Prevents memory leaks, explains bugs I had
- **Applied**: Fixed 3 components immediately
- **Source**: Daily note, React docs deep dive

**2. TypeScript Generics Click** ⭐⭐
- **Insight**: "Generics are functions for types"
- **Impact**: Made custom hooks type-safe
- **Source**: Learning session

### Important Learnings

**System Design**:
- Caching dramatically improves performance
- Trade-off: Complexity vs speed
- Real example: Reduced API calls by 80%

**Testing**:
- Test behavior, not implementation
- Mocking is necessary but can hide bugs
- Integration tests catch more issues

### Patterns Discovered

**1. React Hook Dependencies**
- Pattern: Forgetting dependencies → Stale closures
- Solution: ESLint plugin catches most cases
- When: Always use exhaustive-deps rule

**2. Async Error Handling**
- Pattern: try/catch in every async function gets repetitive
- Solution: Error boundary or global error handler
- Tradeoff: Centralized vs localized handling

### Connections Made

```
useState ←→ useEffect
    ↓         ↓
 Renders  Side Effects
    ↓         ↓
Performance Optimization
```

### Quotes Worth Remembering

> "Make it work, make it right, make it fast - in that order"

> "Premature optimization is the root of all evil"

> "If you can't explain it simply, you don't understand it well enough"

### Misconceptions Corrected

**Before**: "useEffect runs after render"
**Actually**: "useEffect runs after paint, useLayoutEffect runs after render"

**Before**: "TypeScript makes code harder to read"
**Actually**: "TypeScript makes intent clearer once you understand it"

### Meta-Insights (About My Learning)

- I learn best by building projects, not watching tutorials
- Morning sessions are 2x more productive
- Breaking down problems into smaller pieces always helps
- Teaching others solidifies my understanding

### Action Items from Insights

- [ ] Write blog post about useEffect cleanup
- [ ] Create TypeScript generics cheat sheet
- [ ] Apply caching pattern to current project
- [ ] Share error boundary pattern with team
```

## Insight Detection
```javascript
function detectInsights(notes) {
  const insightPatterns = {
    breakthrough: /\b(aha|realize|understand now|finally get)\b/i,
    learning: /\b(learned|TIL|discovered|found out)\b/i,
    pattern: /\b(pattern|always|whenever|every time)\b/i,
    misconception: /\b(thought .* but actually|wrong about)\b/i,
    connection: /\b(connect|relate|similar to|like)\b/i
  };

  return notes.filter(note =>
    Object.values(insightPatterns).some(p => p.test(note.content))
  );
}
```

## Insight Rating
⭐⭐⭐ Game-changing - Fundamentally changed understanding
⭐⭐ Significant - Important learning
⭐ Notable - Worth remembering

## MCP Storage
```json
{
  "insight": {
    "id": "insight-123",
    "date": "2025-01-15",
    "content": "useEffect cleanup prevents memory leaks",
    "rating": 3,
    "topic": "React Hooks",
    "impact": "Fixed 3 bugs, improved understanding",
    "connections": ["memory-management", "component-lifecycle"],
    "applied": true,
    "sourceNote": "daily-2025-01-15"
  }
}
```

## Review Process
```markdown
## Weekly Insight Review

1. Read all insights from the week
2. Rate importance (★★★ to ★)
3. Identify connections between insights
4. Create action items from learnings
5. Share most valuable insights
```

## ADHD-Friendly
- Emoji indicators for quick scanning
- Star ratings for prioritization
- Visual connections (diagrams)
- One-sentence summaries
- Immediate application suggestions
