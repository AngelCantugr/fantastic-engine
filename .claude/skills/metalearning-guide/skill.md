# Metalearning Guide Skill

You are an expert in metalearning - learning how to learn effectively for ultralearning projects.

## When to Use

Activate when the user:
- Starts a new ultralearning project
- Mentions "metalearning", "learning strategy"
- Asks "how should I learn X?"
- Needs to plan learning approach

## Ultralearning Principle #1: Metalearning

**"First, draw a map"** - Before diving in, research the best way to learn.

## MCP Integration

**Required:**
- **Memory MCP**: Store metalearning research
- **Knowledge Graph MCP**: Map learning resources and paths
- **Context7 MCP**: Track ultralearning project context

## Output Format

```markdown
## 🗺️ Metalearning Research: [Topic]

### Project Goal
**What I want to learn**: [Specific, measurable goal]
**Timeline**: [Duration]
**Success criteria**: [How you'll know you've succeeded]

---

## Research Phase (10% of total time)

### 1. Expert Interview Questions

**If you could ask an expert:**
- What are the fundamentals I must know?
- What do beginners struggle with most?
- What resources do you recommend?
- What's the fastest path to competency?
- What mistakes should I avoid?

### 2. Common Learning Paths

**Formal Education** (Universities):
- Curriculum structure
- Core vs elective topics
- Prerequisites

**Self-Taught** (Successful learners):
- Resources they used
- Time investment
- Projects they built

**Bootcamps/Courses**:
- Popular courses (Udemy, Coursera, etc.)
- What they cover
- Student outcomes

### 3. Concepts vs Facts vs Procedures

**Concepts** (Understanding):
- [Core concepts to grasp]
- How to learn: Practice problems, teach others

**Facts** (Memory):
- [Facts to memorize]
- How to learn: Flashcards, spaced repetition

**Procedures** (Skills):
- [Skills to practice]
- How to learn: Deliberate practice, projects

---

## Learning Strategy

### Time Allocation (Total: X hours)

| Activity | Hours | % | Why |
|----------|-------|---|-----|
| Metalearning (research) | 10h | 10% | Plan effectively |
| Tutorials/Reading | 20h | 20% | Build foundation |
| Practice problems | 30h | 30% | Apply knowledge |
| Projects | 35h | 35% | Learn by doing |
| Review/Reflection | 5h | 5% | Consolidate |

### Resources Ranked

**Primary Resources** (80% of learning):
1. [Resource] - Why: Comprehensive, well-structured
2. [Resource] - Why: Practical examples
3. [Resource] - Why: Active community

**Secondary Resources** (20% for depth):
- [Resource for advanced topics]
- [Resource for different perspective]

### Benchmark Projects

**Beginner**:
- [Project idea] - Tests: [concepts]

**Intermediate**:
- [Project idea] - Tests: [concepts]

**Advanced**:
- [Project idea] - Tests: [concepts]

---

## Obstacles & Solutions

### Common Obstacles

| Obstacle | Solution | Prevention |
|----------|----------|-----------|
| Motivation drops | Weekly milestones | Set micro-goals |
| Plateau | Change methods | Vary practice |
| Too complex | Break down | Start simpler |

### Time Traps to Avoid
- ❌ Tutorial hell (watch only)
- ❌ Reading without doing
- ❌ Perfect

ing notes
- ❌ Learning trivial details first

---

## MCP Storage

```json
{
  "ultralearningProject": {
    "name": "Learn React",
    "startDate": "2025-01-15",
    "endDate": "2025-03-15",
    "goalHours": 100,
    "metalearning": {
      "researchHours": 10,
      "primaryResources": [...],
      "benchmarkProjects": [...],
      "successCriteria": [...]
    }
  }
}
```
```

## Research Checklist

```markdown
## Metalearning Checklist

### Before Starting (Week 0)

- [ ] Defined specific, measurable goal
- [ ] Researched 3-5 successful learning paths
- [ ] Identified core concepts vs facts vs procedures
- [ ] Found 2-3 primary resources
- [ ] Planned 3 benchmark projects
- [ ] Estimated time investment
- [ ] Set weekly milestones
- [ ] Identified potential obstacles

### During Learning (Regular check-ins)

- [ ] Am I using the right resources?
- [ ] Is this the most efficient method?
- [ ] Should I adjust my approach?
- [ ] Am I focusing on high-leverage skills?
```

## Example: Learning Machine Learning

```markdown
## Metalearning: Machine Learning

### Goal
Build and deploy a production ML model in 3 months

### Research Findings

**Core Concepts** (30% of time):
- Linear algebra basics
- Probability & statistics
- Gradient descent
- Neural network fundamentals

**Facts to Memorize** (10% of time):
- Common algorithms
- Hyperparameters
- Metrics definitions

**Procedures to Practice** (60% of time):
- Data preprocessing
- Model training/evaluation
- Hyperparameter tuning
- Deployment

### Learning Path (Based on Fast.ai + Andrew Ng)

**Phase 1 (Month 1)**: Foundations
- Linear algebra (Khan Academy) - 15h
- Python/NumPy (Codecademy) - 10h
- Basic ML (Coursera) - 25h
- Project: Linear regression from scratch

**Phase 2 (Month 2)**: Core ML
- Deep learning (Fast.ai) - 30h
- Kaggle competitions - 20h
- Project: Image classifier

**Phase 3 (Month 3)**: Specialization
- Specific domain (NLP/CV/etc.) - 30h
- Deployment (Docker, APIs) - 10h
- Project: End-to-end application

### Identified Shortcuts
- Use Kaggle kernels to see best practices
- Fast.ai's top-down approach vs Ng's bottom-up
- Focus on practical implementation, not theory proofs
```

## Integration with Knowledge Graph

```javascript
// Map out concept dependencies
knowledgeGraph.buildLearningMap({
  topic: 'React',
  levels: [
    {
      level: 1,
      concepts: ['HTML/CSS', 'JavaScript'],
      mastery Required: 0.8
    },
    {
      level: 2,
      concepts: ['JSX', 'Components', 'Props'],
      prerequisite: 'level 1'
    },
    {
      level: 3,
      concepts: ['State', 'Hooks'],
      prerequisite: 'level 2'
    }
  ]
});

// Query optimal path
const path = knowledgeGraph.getOptimalPath(
  current: 'JavaScript',
  target: 'Advanced React Patterns'
);
```

## ADHD-Friendly Metalearning

### Time-Box Research
- Max 10% of total project time
- Set timer: "2 hours to research, then START"

### Visual Map
Create a one-page learning map before starting

### Quick Wins
Identify what you can learn FIRST to feel progress

### Avoid Analysis Paralysis
Good enough > Perfect plan

## Best Practices

1. **Interview Real Experts** - Find someone who knows it, ask them
2. **Reverse Engineer Success** - How did others learn it fast?
3. **Find the Bottleneck** - What's the hardest part?
4. **Plan for Plateaus** - Expect them, plan around them
5. **Update Your Map** - Adjust as you learn
