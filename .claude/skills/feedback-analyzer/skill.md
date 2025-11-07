# Feedback Analyzer Skill

Ultralearning Principle #6: Extract the signal from the noise in feedback.

## When to Use
- Received feedback (code review, critique)
- Mentions "feedback", "criticism"
- Post-project review

## The Feedback Principle
Not all feedback is equal. Learn to extract what matters.

## Output Format
```markdown
## 📊 Feedback Analysis: [Project/Work]

### Raw Feedback Received
[List all feedback]

### Categorized Feedback

**High-Signal** (Act on these):
1. [Feedback] - Why: Specific, actionable, recurring
2. [Feedback] - Why: Addresses core skills

**Medium-Signal**:
- [Feedback] - Consider, but not critical

**Low-Signal/Noise**:
- [Feedback] - Subjective, ignore for now

### Action Plan

**Immediate Actions**:
- [ ] [Fix #1]
- [ ] [Fix #2]

**Practice Needed**:
- [ ] Drill: [Skill to improve]
- [ ] Resources: [Where to learn]

**Long-Term**:
- [ ] [Broader improvement]
```

## Types of Feedback

**Outcome Feedback**: "It works/doesn't work"
- Good for: Knowing if you succeeded
- Bad for: Knowing HOW to improve

**Informational Feedback**: "Here's what's wrong"
- Good for: Understanding mistakes
- Best for learning

**Corrective Feedback**: "Do this instead"
- Good for: Quick fixes
- Can skip learning if over-used

## MCP Storage
```json
{
  "feedbackLog": [
    {
      "date": "2025-01-15",
      "source": "Code Review",
      "feedback": "...",
      "category": "high-signal",
      "actionTaken": "...",
      "improved": true
    }
  ]
}
```

## ADHD-Friendly
- Write it down immediately
- One fix at a time
- Celebrate improvements
