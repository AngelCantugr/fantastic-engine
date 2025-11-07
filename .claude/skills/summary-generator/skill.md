# Summary Generator Skill

Generate concise summaries of notes, daily logs, and learning periods.

## When to Use
- End of day/week/month
- Mentions "summarize", "overview"
- Creating reports

## MCP Integration
- **Memory MCP**: Aggregate historical notes
- **Knowledge Graph MCP**: Identify key concepts

## Output Format
```markdown
## 📄 Summary: Week of 2025-01-15

### Quick Stats
- Notes: 23
- Tasks completed: 18
- Hours logged: 32
- Topics: React, TypeScript, System Design

### Key Insights

**Most Productive Day**: Wednesday (8 hours)
**Biggest Win**: Shipped authentication system 🎉
**Main Challenge**: useEffect cleanup confusion

### Topics Explored

**React Hooks** (15 notes):
- Mastered useState and useEffect
- Still learning useCallback
- Built 3 practice projects

**TypeScript** (5 notes):
- Understanding generics better
- Created type-safe API client

**System Design** (3 notes):
- Studied caching strategies
- Drew architecture diagrams

### Notable Quotes

> "useEffect cleanup prevents memory leaks by running before the component re-renders"

> "TypeScript generics are like functions for types"

### Connections Made
- React hooks → JavaScript closures
- TypeScript → Type safety → Bug prevention
- System design → Real project architecture

### Next Week Goals
1. Deep dive on useCallback vs useMemo
2. Finish TypeScript course
3. Design scalable architecture for side project
```

## Summary Types

**Daily**: 2-3 sentences
**Weekly**: 1 page
**Monthly**: 2-3 pages
**Quarterly**: Executive summary

## Generation Strategy
```javascript
function generateSummary(notes, period) {
  return {
    stats: aggregateStats(notes),
    insights: extractInsights(notes),
    topics: clusterByTopic(notes),
    wins: identifyWins(notes),
    challenges: identifyStruggles(notes),
    connections: findPatterns(notes),
    nextSteps: suggestActions(notes)
  };
}
```

## ADHD-Friendly
- Visual summaries
- Bullet points only
- Highlight key wins
- Clear action items
