# Context Classifier Skill

Automatically classify notes into contexts (Work, Learning, Personal, etc.) using MCP servers.

## When to Use
- Processing notes
- Mentions "context", "categorize"
- Building knowledge organization

## MCP Integration
**Required:**
- **Context7 MCP**: Maintain context across sessions
- **Memory MCP**: Store classification patterns

## Output Format
```markdown
## 🏷️ Context Classification

**Note**: [Title/Preview]

**Primary Context**: WORK (85% confidence)
**Secondary Contexts**:
- Learning (40%)
- Project (30%)

**Indicators**:
- Keywords: "production", "deploy", "client"
- Time: During work hours (9-5)
- Related notes: 5 work notes this week

**Suggested Tags**: #work #production #deployment

**Recommended Folder**: /work/2025-Q1/
```

## Context Types
- **WORK**: Job-related tasks, meetings, projects
- **LEARNING**: Tutorials, courses, study notes
- **PERSONAL**: Health, family, hobbies
- **PROJECT**: Side projects, experiments
- **RESEARCH**: Deep dives, investigations
- **MEETING**: Discussions, calls
- **IDEA**: Brainstorming, future plans

## Classification Algorithm
```javascript
// Multi-signal classification
function classifyContext(note) {
  const signals = {
    keywords: analyzeKeywords(note.content),
    time: analyzeTimeOfDay(note.timestamp),
    location: analyzeLocation(note.metadata),
    linkedNotes: analyzeConnections(note.links),
    userPatterns: analyzeHistory(note.author)
  };

  return weightedScore(signals);
}
```

## ADHD Tips
- Auto-classify in background
- Review only edge cases
- Learn from corrections
