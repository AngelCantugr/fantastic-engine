# Retrieval Practice Skill

Ultralearning Principle #5: Test to learn, don't learn then test.

## When to Use
- Wants to test knowledge
- Mentions "retrieval", "testing effect"
- Consolidation phase

## The Retrieval Principle
Testing yourself IS learning, not just assessment.

## Output Format
```markdown
## 🧠 Retrieval Practice: [Topic]

### Retrieval Strategy
**Frequency**: Every study session
**Method**: [Chosen method]
**Duration**: 20% of study time

### Retrieval Exercises

**Free Recall** (Hardest, most effective):
- Close all materials
- Write everything you remember
- Check and note gaps

**Cued Recall**:
- Q: [Prompt]
- A: [Try to recall]

**Recognition** (Easiest, least effective):
- Multiple choice
- True/false

### Weekly Retrieval Sessions
- **Monday**: Free recall - Last week's topics
- **Wednesday**: Practice problems - No looking
- **Friday**: Teach someone (retrieval + elaboration)
```

## Research-Backed Benefits
- 50%+ better retention than re-reading
- Identifies gaps immediately
- Strengthens memory pathways

## MCP Integration
```javascript
// Schedule regular retrieval practice
spaced_repetition_scheduler.scheduleRetrieval({
  topic: "React Hooks",
  method: "free-recall",
  frequency: "every-3-days"
});
```

## ADHD Tips
- Mini retrieval: 5 minutes
- Immediate feedback
- Make it a game
