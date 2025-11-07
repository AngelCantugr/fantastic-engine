# Drill Identifier Skill

Ultralearning Principle #4: Attack your weakest point through isolated drills.

## When to Use
- Identifies a specific weakness
- Stuck on one aspect
- Mentions "practice", "drill"

## The Drill Principle
Isolate the hardest part and practice THAT specifically.

## Output Format
```markdown
## 🎯 Drill Plan: [Weak Point]

### Bottleneck Analysis
**Skill**: [Overall skill]
**Weak Component**: [Specific weakness]
**Impact**: [How it holds you back]

### Drill Design

**Drill 1**: [Isolated exercise]
- Focus: [Specific sub-skill]
- Duration: 15 minutes
- Reps: X times
- Success metric: [How to measure]

### Practice Schedule
- **Day 1-3**: Drill only (isolated)
- **Day 4-7**: Integration (use in projects)
- **Week 2**: Retest original skill

### Progress Tracking
```
Week 1: [███░░░░░░░] 30%
Week 2: [██████░░░░] 60%
Week 3: [█████████░] 90%
```
```

## Example Drills

**Typing Speed**:
- Drill: Practice only the keys you miss
- Not: Random typing tests

**Coding Interviews**:
- Drill: Only array manipulation problems
- Not: Random LeetCode questions

**Public Speaking**:
- Drill: Record and review your filler words
- Not: Full presentations

## Integration
```javascript
// Identify bottlenecks from quiz results
const weaknesses = quiz_master.analyzeWeaknesses();
drill_identifier.createDrills(weaknesses);
```
