# Daily Note Organizer Skill

You are an expert at parsing and organizing daily markdown notes into structured categories.

## When to Use

Activate when the user:
- Has a daily note to organize
- Mentions "organize my notes", "parse daily notes"
- Provides raw daily notes markdown
- End of day note processing

## MCP Integration

**Required:**
- **Memory MCP**: Store organized notes
- **Knowledge Graph MCP**: Build connections between notes
- **Context7 MCP**: Track note patterns and contexts

## The Daily Note System

### Input Format
User writes in ONE markdown file per day with mixed content:
```markdown
# 2025-01-15

Random thought about React hooks cleanup functions

TODO: Fix the login bug
TODO: Review PR #234

Meeting with team about Q1 roadmap
- Discussed new features
- Timeline: 3 months

Learned: useEffect cleanup prevents memory leaks

Bug in production: users can't login on Safari
Quick fix: added polyfill

IDEA: Build a CLI tool for deployment
```

### Output Format (Organized)
```markdown
## 📝 Organized Notes: 2025-01-15

### 📚 Learning & Insights

**React Hooks**:
- useEffect cleanup prevents memory leaks
- Related: Component lifecycle, memory management
- Tags: #react #hooks #useEffect #best-practices

---

### ✅ Tasks Extracted

**High Priority**:
- [ ] Fix the login bug
  - Context: Production issue on Safari
  - Related Notes: Safari polyfill fix below

**Medium Priority**:
- [ ] Review PR #234
  - Type: Code review

---

### 💡 Ideas

**CLI Tool for Deployment**:
- Category: Tool Development
- Potential Value: High
- Next Step: Research existing solutions
- Tags: #idea #cli #devops

---

### 🐛 Issues & Bugs

**Safari Login Bug** (RESOLVED):
- Problem: Users can't login on Safari
- Solution: Added polyfill
- Status: Fixed
- Tags: #bug #safari #production

---

### 👥 Meetings & Discussions

**Q1 Roadmap Planning**:
- Attendees: Team
- Topics:
  - New features discussed
  - Timeline: 3 months
- Follow-ups: [None specified]
- Tags: #meeting #planning #roadmap

---

### 🔗 Connections Identified

- React cleanup → Memory leaks → Safari bug (related issues)
- Q1 roadmap → Deployment CLI (potential feature)

---

### MCP Storage Recommendation

```json
{
  "date": "2025-01-15",
  "categories": {
    "learning": [
      {
        "topic": "React Hooks",
        "insight": "useEffect cleanup prevents memory leaks",
        "tags": ["react", "hooks", "useEffect"]
      }
    ],
    "tasks": [
      {
        "text": "Fix the login bug",
        "priority": "high",
        "context": "Production issue on Safari"
      }
    ],
    "ideas": [
      {
        "title": "CLI Tool for Deployment",
        "category": "Tool Development"
      }
    ],
    "issues": [
      {
        "title": "Safari Login Bug",
        "status": "resolved",
        "solution": "Added polyfill"
      }
    ],
    "meetings": [
      {
        "title": "Q1 Roadmap Planning",
        "topics": ["New features", "Timeline"]
      }
    ]
  },
  "connections": [...],
  "metadata": {
    "totalItems": 8,
    "processingTime": "2025-01-15T20:00:00Z"
  }
}
```
```

## Automatic Categorization Rules

### Patterns to Detect

**Tasks/TODOs**:
```regex
^TODO:
^- \[ \]
^Fix\s
^Review\s
```

**Ideas**:
```regex
^IDEA:
^What if
^Maybe we could
Possible:
```

**Learning/Insights**:
```regex
^Learned:
^TIL:
^Insight:
^Understanding:
Key takeaway:
```

**Bugs/Issues**:
```regex
^Bug:
^Issue:
^Problem:
not working
broken
error in
```

**Meetings**:
```regex
^Meeting
^Call with
^Discussion
Attendees:
```

**Questions**:
```regex
^\?
^Question:
^Why does
^How to
^What is
```

## Context Classification

```javascript
// Use Context7 MCP or similar to classify context
function classifyContext(note) {
  const contexts = {
    WORK: ['production', 'deploy', 'client', 'deadline'],
    LEARNING: ['learned', 'tutorial', 'course', 'TIL'],
    PERSONAL: ['health', 'exercise', 'family'],
    PROJECT: ['build', 'implement', 'feature'],
    RESEARCH: ['investigate', 'explore', 'research']
  };

  // Score each context
  const scores = {};
  for (const [context, keywords] of Object.entries(contexts)) {
    scores[context] = keywords.filter(k =>
      note.toLowerCase().includes(k)
    ).length;
  }

  return Object.keys(scores).sort((a, b) =>
    scores[b] - scores[a]
  )[0];
}
```

## Priority Detection

```javascript
function detectPriority(task) {
  const highPriorityIndicators = [
    'urgent', 'asap', 'critical', 'production',
    'bug', 'broken', 'blocking', '!!!'
  ];

  const lowPriorityIndicators = [
    'someday', 'maybe', 'nice to have', 'consider'
  ];

  const text = task.toLowerCase();

  if (highPriorityIndicators.some(ind => text.includes(ind))) {
    return 'high';
  }
  if (lowPriorityIndicators.some(ind => text.includes(ind))) {
    return 'low';
  }
  return 'medium';
}
```

## Linking Strategy

```javascript
// Build connections between notes
function findConnections(notes) {
  const connections = [];

  // Find shared topics/tags
  for (let i = 0; i < notes.length; i++) {
    for (let j = i + 1; j < notes.length; j++) {
      const sharedTags = intersection(notes[i].tags, notes[j].tags);
      if (sharedTags.length > 0) {
        connections.push({
          from: notes[i].id,
          to: notes[j].id,
          via: sharedTags,
          strength: sharedTags.length / notes[i].tags.length
        });
      }
    }
  }

  // Find mentioned concepts
  // Find temporal relationships (same day/week)

  return connections;
}
```

## Batch Processing Mode

```markdown
## 🗂️ Batch Organization: Week of 2025-01-15

**Files Processed**: 7 daily notes
**Total Items**: 143
**Time Saved**: ~2 hours

### Summary by Category

**Tasks** (45):
- High Priority: 12
- Medium: 28
- Low: 5

**Learnings** (32):
- React: 15 insights
- TypeScript: 10 insights
- System Design: 7 insights

**Ideas** (18):
- Tool ideas: 8
- Feature ideas: 10

**Bugs Fixed** (11)
**Meetings** (8)

### Trends This Week
- 📈 Increased focus on React hooks
- 🐛 Safari compatibility issues recurring
- 💡 CLI automation is a theme

### Recommended Actions
1. Create dedicated React hooks learning path
2. Research Safari compatibility best practices
3. Start CLI tools project
```

## ADHD-Friendly Features

### One-Click Organization
```bash
# Process today's notes
daily-note-organizer --date today

# Process this week
daily-note-organizer --week

# Interactive mode
daily-note-organizer --interactive
```

### Visual Output
```
Processing: daily-2025-01-15.md

Found:
  ✅ 5 tasks
  📚 3 learnings
  💡 2 ideas
  🐛 1 bug
  👥 1 meeting

Organizing... [████████████] Done!

Summary saved to: organized/2025-01-15.md
```

### Quick Review
Show before/after stats:
```
Before: 1 messy file, 234 lines
After: 5 organized sections, 12 items categorized
Connections: 8 links created
Time to review: 5 minutes (vs 30 minutes searching)
```

## Best Practices

1. **Write Freely During the Day**: Don't organize while capturing
2. **Process EOD**: Spend 10 minutes organizing before bed
3. **Consistent Format**: Use same daily note structure
4. **Tag Liberally**: Over-tag rather than under-tag
5. **Review Weekly**: Look for patterns and connections

## Integration with Other Skills

```javascript
// After organizing, trigger other skills

// 1. Extract tasks → Your task manager
todoExtractor.process(organized.tasks);

// 2. Identify key insights
insightHighlighter.analyze(organized.learning);

// 3. Build knowledge graph
knowledgeGraphBuilder.update(organized);

// 4. Suggest tags
tagSuggester.recommend(organized);

// 5. Create summaries
summaryGenerator.create(organized, 'weekly');
```

## MCP Memory Integration

```javascript
// Store daily notes in Memory MCP
memory.store({
  namespace: 'daily-notes',
  key: '2025-01-15',
  data: {
    raw: rawMarkdown,
    organized: organizedData,
    categories: categories,
    connections: connections,
    tags: extractedTags
  }
});

// Query notes by context
const workNotes = memory.query({
  namespace: 'daily-notes',
  filter: {
    'categories.context': 'WORK',
    date: { $gte: '2025-01-01' }
  }
});

// Find related notes
const relatedNotes = knowledgeGraph.getRelated({
  nodeId: 'note-2025-01-15',
  depth: 2,
  minStrength: 0.5
});
```
