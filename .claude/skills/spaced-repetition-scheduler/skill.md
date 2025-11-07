# Spaced Repetition Scheduler Skill

You are an expert in spaced repetition algorithms and optimal review scheduling for long-term retention.

## When to Use

Activate when the user:
- Wants to schedule reviews
- Mentions "spaced repetition", "SRS", "review schedule"
- Asks when to review material
- Needs help with retention

## MCP Integration

**Required MCP Servers:**
- **Memory MCP**: Store review schedules and performance data
- **Knowledge Graph MCP**: Track concept dependencies
- **Context7 MCP**: Maintain study session context

## Spaced Repetition Science

### The Forgetting Curve
```
Memory Retention
100% |●
     |  ●
     |    ●●
     |       ●●●
     |           ●●●●
     |                ●●●●●●
  0% |________________________
     0  1  3  7  14  30  days
        ↑  ↑  ↑  ↑   ↑   ↑
      Reviews prevent forgetting
```

### Optimal Intervals
- **First Review**: 1 day
- **Second Review**: 3 days
- **Third Review**: 7 days
- **Fourth Review**: 14 days
- **Fifth Review**: 30 days
- **Sixth Review**: 90 days

### Algorithm: SM-2 (SuperMemo 2)

```
interval = previous_interval * easiness_factor

easiness_factor adjusts based on performance:
- Perfect recall: +0.15
- Good recall: +0.10
- Ok recall: +0.00
- Poor recall: -0.20
```

## Output Format

```markdown
## 📅 Spaced Repetition Schedule: [Topic]

### Current Status
- **Items due today**: X
- **Items due this week**: Y
- **Total items**: Z
- **Average retention**: XX%

---

### Today's Reviews

#### Due Now (Urgent)

| Topic | Last Reviewed | Attempts | Next Interval |
|-------|---------------|----------|---------------|
| [Topic 1] | 3 days ago | 2 | 7 days |
| [Topic 2] | 1 week ago | 3 | 14 days |

#### Coming Up

| Topic | Due Date | Priority |
|-------|----------|----------|
| [Topic 3] | Tomorrow | 🔴 High |
| [Topic 4] | In 2 days | 🟡 Medium |

---

### Recommended Study Session

**Duration**: 30 minutes
**Focus**: [Topics due today]

**Order** (by priority):
1. [Most urgent/challenging]
2. [Second priority]
3. [Quick reviews]

---

### Performance Insights

**Strong Areas** (✅ High retention):
- [Topic A] - 95% accuracy
- [Topic B] - 92% accuracy

**Needs Attention** (⚠️ Low retention):
- [Topic C] - 65% accuracy
- [Topic D] - 58% accuracy

**Recommendation**: Focus 70% of time on weak areas

---

### MCP Storage Format

```json
{
  "cards": [
    {
      "id": "uuid",
      "topic": "React useEffect",
      "content": "...",
      "easinessFactor": 2.5,
      "interval": 7,
      "repetitions": 3,
      "lastReviewed": "2025-01-15",
      "nextReview": "2025-01-22",
      "performanceHistory": [5, 4, 5]
    }
  ]
}
```
```

## SM-2 Algorithm Implementation

```javascript
function calculateNextReview(card, performanceRating) {
  // performanceRating: 0-5
  // 5: Perfect recall
  // 4: Correct after hesitation
  // 3: Correct with difficulty
  // 2: Incorrect but remembered
  // 1: Incorrect, familiar
  // 0: Complete blank

  let { easinessFactor, interval, repetitions } = card;

  // Update easiness factor
  easinessFactor = Math.max(1.3,
    easinessFactor + (0.1 - (5 - performanceRating) * (0.08 + (5 - performanceRating) * 0.02))
  );

  // Update interval based on performance
  if (performanceRating < 3) {
    // Failed - reset
    repetitions = 0;
    interval = 1;
  } else {
    repetitions++;

    if (repetitions === 1) {
      interval = 1;
    } else if (repetitions === 2) {
      interval = 6;
    } else {
      interval = Math.round(interval * easinessFactor);
    }
  }

  // Calculate next review date
  const nextReview = new Date();
  nextReview.setDate(nextReview.getDate() + interval);

  return {
    easinessFactor,
    interval,
    repetitions,
    nextReview: nextReview.toISOString().split('T')[0],
    performanceRating
  };
}

// Usage
const updatedCard = calculateNextReview(card, 5); // Perfect recall
```

## MCP Memory Integration

### Store Review Data

```javascript
// Initialize review card
memory.store({
  namespace: "spaced-repetition",
  key: `card-${topicId}`,
  data: {
    topic: "React Hooks - useEffect cleanup",
    content: "How and why to use cleanup functions in useEffect",
    created: "2025-01-15",
    easinessFactor: 2.5,
    interval: 1,
    repetitions: 0,
    nextReview: "2025-01-16",
    tags: ["react", "hooks", "useEffect"],
    difficultyLevel: "medium"
  }
});

// Update after review
memory.update({
  namespace: "spaced-repetition",
  key: `card-${topicId}`,
  updates: calculateNextReview(card, userRating)
});

// Query due reviews
const dueCards = memory.query({
  namespace: "spaced-repetition",
  filter: {
    nextReview: { $lte: today }
  },
  sort: { nextReview: 1 }
});
```

### Track Performance Over Time

```javascript
// Store performance history
memory.append({
  namespace: "performance-history",
  key: `card-${topicId}`,
  data: {
    date: "2025-01-15",
    rating: 5,
    responseTime: 15, // seconds
    confidence: "high"
  }
});

// Analyze trends
const history = memory.get({
  namespace: "performance-history",
  key: `card-${topicId}`
});

const averageRating = history.reduce((sum, h) => sum + h.rating, 0) / history.length;
const improving = history.slice(-3).every((h, i, arr) =>
  i === 0 || h.rating >= arr[i-1].rating
);
```

## Knowledge Graph Integration

### Track Dependencies

```javascript
// Create concept nodes
knowledgeGraph.addNode({
  id: "react-useEffect",
  type: "concept",
  properties: {
    difficulty: "medium",
    mastery: 0.7
  }
});

// Create prerequisite relationships
knowledgeGraph.addEdge({
  from: "react-basics",
  to: "react-useEffect",
  type: "prerequisite",
  strength: 0.9
});

knowledgeGraph.addEdge({
  from: "react-useEffect",
  to: "react-useEffect-cleanup",
  type: "builds-on",
  strength: 0.8
});

// Smart scheduling based on dependencies
function getReviewOrder(dueCards) {
  // Sort by dependency graph - review prerequisites first
  return knowledgeGraph.topologicalSort(dueCards);
}
```

## Review Session Templates

### Quick Review (15 min)

```markdown
## ⚡ Quick Review Session

**Focus**: High-confidence items

1. React Hooks basics (5 min)
   - 3 questions
   - Expected: 100% accuracy

2. JavaScript closures (5 min)
   - 4 questions
   - Expected: 95% accuracy

3. Git commands (5 min)
   - 5 questions
   - Expected: 90% accuracy

**Goal**: Maintain strong retention
```

### Deep Review (45 min)

```markdown
## 🎯 Deep Review Session

**Focus**: Challenging topics

1. **React useEffect (20 min)**
   - Review cleanup functions
   - Practice with examples
   - Code challenge
   - Target: 80% → 90% mastery

2. **Algorithms (15 min)**
   - Binary search variations
   - Time complexity analysis
   - Target: 70% → 85% mastery

3. **System Design (10 min)**
   - Review trade-offs
   - Quick practice problem
   - Target: 75% → 85% mastery
```

### Catch-Up Session (60 min)

```markdown
## 📚 Catch-Up Session

**Overdue items**: 15

**Strategy**: Triage and prioritize

**High Priority** (30 min):
1. React - Core concepts (10 items)
2. TypeScript - Advanced types (5 items)

**Medium Priority** (20 min):
3. GraphQL basics (8 items)

**Low Priority** (10 min):
4. Quick refreshers (12 items)

**Notes**:
- Don't try to catch up all at once
- Focus on most important items
- Schedule remaining for tomorrow
```

## Scheduling Strategies

### Daily Review Habit

```markdown
## 📅 Daily Schedule

**Morning (10 min)**:
- Quick review of yesterday's learning
- Preview today's new content

**Lunch Break (15 min)**:
- Review cards due today
- High-priority items only

**Evening (20 min)**:
- Deep review of challenging topics
- Update performance data
```

### Weekly Planning

```markdown
## 📊 Weekly Review Plan

**Monday**: Focus on new topics from last week
**Tuesday**: Review algorithms & data structures
**Wednesday**: System design & architecture
**Thursday**: Language-specific concepts
**Friday**: Mixed review + catch-up
**Weekend**: Optional - new learning or rest
```

### Optimized Intervals by Topic Type

```markdown
## ⏱️ Topic-Specific Intervals

**Facts & Definitions** (Fast decay):
- Day 1, 2, 4, 7, 14, 30

**Processes & How-To** (Medium decay):
- Day 1, 3, 7, 14, 30, 60

**Concepts & Why** (Slow decay):
- Day 1, 3, 10, 21, 45, 90

**Skills & Practice** (Very slow decay):
- Day 1, 7, 14, 30, 60, 120
```

## Performance Metrics

### Dashboard View

```markdown
## 📈 Spaced Repetition Dashboard

### Today's Stats
- ✅ Cards reviewed: 12 / 15
- 📊 Average rating: 4.2 / 5
- ⏱️ Time spent: 25 minutes
- 🎯 Accuracy: 87%

### This Week
- Cards reviewed: 67
- Streak: 5 days 🔥
- Topics covered: 8
- Mastery improvement: +12%

### Overall Progress
- Total cards: 234
- Mature cards: 145 (62%)
- Average interval: 18 days
- Retention rate: 85%

### Upcoming
- Tomorrow: 14 cards
- This week: 42 cards
- Overdue: 3 cards ⚠️
```

### Retention Analysis

```markdown
## 🧠 Retention Analysis

**Strong Retention** (>90%):
- JavaScript fundamentals
- Git workflows
- HTTP/REST concepts

**Moderate Retention** (70-90%):
- React hooks
- TypeScript advanced types
- Database indexing

**Weak Retention** (<70%):
- System design patterns
- Algorithm optimization
- Docker networking

**Action Items**:
1. Increase review frequency for weak areas
2. Create more example problems
3. Add visual aids to cards
```

## Adaptive Scheduling

```javascript
// Adjust intervals based on global performance
function adaptiveInterval(baseInterval, globalStats) {
  const { overallAccuracy, averageConfidence } = globalStats;

  let multiplier = 1.0;

  // If struggling globally, reduce intervals
  if (overallAccuracy < 0.75) {
    multiplier = 0.7;
  } else if (overallAccuracy > 0.90) {
    multiplier = 1.3; // Can extend intervals
  }

  // Adjust for confidence
  if (averageConfidence < 0.6) {
    multiplier *= 0.8;
  }

  return Math.round(baseInterval * multiplier);
}

// Per-topic adjustment
function topicSpecificInterval(topic, baseInterval) {
  const difficulty = {
    'algorithms': 0.8,        // Review more often
    'syntax': 1.2,            // Can space out more
    'system-design': 0.9,
    'frameworks': 1.0
  };

  return Math.round(baseInterval * (difficulty[topic] || 1.0));
}
```

## Integration with Active Recall

```markdown
## 🔄 Combined Workflow

**Step 1**: Learn new material
**Step 2**: Create active recall questions (active-recall-generator skill)
**Step 3**: Initial review (immediately)
**Step 4**: Schedule with spaced repetition (this skill)
**Step 5**: Review at calculated intervals
**Step 6**: Track performance and adjust

**Example Timeline**:
```
Day 0: Learn React useEffect
       ↓
       Create 5 questions
       ↓
       Answer immediately (baseline)
       ↓
Day 1: First review (scheduled)
       Performance: 4/5 ✅
       ↓
Day 3: Second review
       Performance: 5/5 ✅
       ↓
Day 10: Third review
       Performance: 5/5 ✅
       ↓
Day 24: Fourth review
```
```

## Best Practices

### 1. Be Consistent
Review every day, even if just 10 minutes

### 2. Don't Cram
Trust the algorithm - no need to review early

### 3. Be Honest with Ratings
Accurate ratings = better scheduling

### 4. Review Prerequisites First
Follow the knowledge graph

### 5. Track Trends
Look for patterns in what you forget

### 6. Adjust for Life
Busy week? Reduce new cards, focus on reviews

## ADHD-Friendly Features

### Gamification
```
🏆 Achievements
✅ 7-day streak
✅ 100 cards reviewed
✅ 90% retention rate
🔒 30-day streak (locked)
```

### Visual Progress
```
This Month's Progress
Week 1: ████████░░ 80%
Week 2: ██████████ 100%
Week 3: ████░░░░░░ 40%
Week 4: ░░░░░░░░░░  0%

Let's finish strong! 💪
```

### Reminders & Nudges
```
🔔 Hey! You have 12 cards due today
⏰ Best time to review: After lunch
🎯 Goal: Maintain your 7-day streak!
```

## Export & Backup

```javascript
// Export to Anki format
function exportToAnki(cards) {
  return cards.map(card => ({
    front: card.question,
    back: card.answer,
    tags: card.tags.join(' '),
    interval: card.interval,
    easeFactor: card.easinessFactor * 1000 // Anki uses different scale
  }));
}

// Import from other SRS systems
function importFromSuperMemo(smData) {
  return smData.items.map(item => ({
    topic: item.title,
    content: item.question,
    easinessFactor: item.eFactor,
    interval: item.interval,
    nextReview: item.nextRepetition
  }));
}
```
