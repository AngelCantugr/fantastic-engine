# Reflection Journal Skill

Structured reflection for ultralearning projects to consolidate learning and insights.

## When to Use
- End of week/project
- Stuck or plateaued
- Mentions "reflection", "review"

## Ultralearning Principle #9: Experimentation + Reflection
Learn from your experience through systematic reflection.

## MCP Integration
**Required:**
- **Memory MCP**: Store reflections for pattern analysis
- **Knowledge Graph MCP**: Connect insights to concepts

## Output Format
```markdown
## 📝 Reflection Journal: Week X

### Date: [YYYY-MM-DD]

---

## What I Learned

**New Concepts**:
- [Concept 1]: [Key insight]
- [Concept 2]: [Aha moment]

**Skills Improved**:
- [Skill]: From [X%] to [Y%]

**Projects Completed**:
- [Project]: [What it taught me]

---

## What Worked Well ✅

**Study Methods**:
- [Method] was effective because [reason]

**Resources**:
- [Resource] helped me understand [topic]

**Strategies**:
- [Strategy] accelerated learning by [impact]

---

## What Didn't Work ❌

**Challenges**:
- [Challenge]: [Why it was difficult]

**Time Wasters**:
- [Activity]: Spent X hours, low ROI

**Confusing Topics**:
- [Topic]: Still unclear on [aspect]

---

## Insights & Patterns

**About My Learning**:
- I learn best when [condition]
- I struggle with [type of content]
- Peak focus time: [time of day]

**About the Topic**:
- Key realization: [insight]
- Connection to: [other concepts]
- Surprised by: [unexpected finding]

---

## Adjustments for Next Week

**Continue**:
- [What's working]

**Stop**:
- [What's not working]

**Start**:
- [New strategy to try]

**Experiment**:
- Try [new approach] to see if [hypothesis]

---

## Questions to Investigate

- [ ] Why does [concept] work this way?
- [ ] How is [A] different from [B]?
- [ ] What's the best practice for [scenario]?

---

## Weekly Stats

**Hours**: X (Target: Y)
**Projects**: X completed
**Concepts**: X mastered
**Mood**: 😊 Confident | 😐 Ok | 😓 Struggling

---

## MCP Storage

```json
{
  "reflection": {
    "week": 5,
    "date": "2025-01-15",
    "hoursLogged": 15,
    "effectiveness": 8,
    "insights": [...],
    "adjustments": [...],
    "mood": "confident"
  }
}
```
```

## Reflection Prompts

### Daily (5 min)
- What's one thing I learned today?
- What confused me?
- What will I do differently tomorrow?

### Weekly (20 min)
- What patterns do I notice in my learning?
- What was my biggest win?
- What needs more practice?

### Monthly (60 min)
- Am I on track to meet my goal?
- What's changed in my approach?
- What surprised me this month?

## Pattern Analysis

```javascript
// Analyze reflection patterns
const patterns = memory.analyze({
  namespace: 'reflections',
  analyze: {
    effectiveMethods: reflections.filter(r => r.effectiveness > 7),
    commonChallenges: reflections.map(r => r.challenges).flat(),
    peakPerformanceTimes: reflections.map(r => r.peakFocusTime)
  }
});

// Output insights
console.log("You learn best using:", patterns.effectiveMethods);
console.log("Common struggles:", patterns.commonChallenges);
console.log("Best time to study:", patterns.peakPerformanceTimes);
```

## Reflection Questions by Learning Stage

### Beginning
- What do I already know about this?
- What are my assumptions?
- What's my learning goal?

### Middle
- Is my strategy working?
- What's harder than expected?
- Do I need to adjust my approach?

### End
- Did I achieve my goal?
- What would I do differently?
- What's the most important thing I learned?

## ADHD-Friendly Reflection

### Keep It Short
- Daily: 5 min max
- Weekly: 15-20 min
- Monthly: 30 min

### Use Templates
Copy-paste, fill in blanks

### Voice Recording
Talk it out, transcribe later

### Visual Reflection
Draw your learning journey

### Bullet Points
Not essays!

## Integration with Other Skills

```javascript
// After reflection, update other systems

// 1. Update knowledge graph with insights
knowledgeGraph.addInsights(reflection.insights);

// 2. Adjust learning path
learningPathDesigner.adjust({
  based: reflection.adjustments
});

// 3. Create drills for struggles
drillIdentifier.createDrills(reflection.challenges);

// 4. Schedule reviews
spacedRepetitionScheduler.adjust({
  based: reflection.masteryLevels
});
```

## Monthly Review Template

```markdown
## 🗓️ Month X Review

### Goal Progress
- **Target**: [Original goal]
- **Achieved**: [What's done]
- **Gap**: [What's left]
- **On Track?**: Yes/No

### Statistics
- Total hours: X
- Projects completed: X
- Concepts mastered: X
- Skills acquired: X

### Biggest Wins 🏆
1. [Achievement]
2. [Breakthrough]
3. [Milestone]

### Biggest Struggles 😓
1. [Challenge] - [How addressed]
2. [Difficulty] - [Plan to overcome]

### Key Insights 💡
1. [Learning about self]
2. [Learning about topic]
3. [Learning about process]

### Next Month Plan
- Focus on: [Priority areas]
- Experiment with: [New approaches]
- Complete: [Specific goals]
```

## Best Practices

1. **Be Honest**: No sugarcoating
2. **Be Specific**: "useEffect confusing" not "React hard"
3. **Note Emotions**: Frustration reveals hard parts
4. **Track Experiments**: Did it work?
5. **Review Past Reflections**: See growth
