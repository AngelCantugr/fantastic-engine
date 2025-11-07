# Project Tracker Skill

Track progress, milestones, and time investment for ultralearning projects.

## When to Use
- Starting ultralearning project
- Weekly progress check
- Mentions "tracking", "progress"

## MCP Integration
**Required:**
- **Memory MCP**: Store project data
- **Knowledge Graph MCP**: Map concept mastery
- **Context7 MCP**: Maintain project context

## Output Format
```markdown
## 📊 Project Tracker: [Project Name]

### Overview
- **Start Date**: 2025-01-15
- **Target Date**: 2025-03-15
- **Progress**: [████████░░] 80%
- **Hours Logged**: 75 / 100

### This Week
**Completed**:
- ✅ Built authentication system
- ✅ Completed React hooks tutorial
- ✅ Shipped project to production

**In Progress**:
- 🔄 Learning GraphQL
- 🔄 Building API endpoints

**Planned**:
- ⏳ Add testing
- ⏳ Performance optimization

### Milestones

| Milestone | Target | Status | Actual |
|-----------|--------|--------|--------|
| Phase 1: Basics | Week 2 | ✅ | Week 2 |
| Phase 2: Intermediate | Week 4 | ✅ | Week 5 |
| Phase 3: Advanced | Week 6 | 🔄 | - |
| Final Project | Week 8 | ⏳ | - |

### Time Breakdown
```
Study: 30h ████████░░ 
Practice: 35h ███████████
Projects: 10h ███░░░░░░░
```

### MCP Storage
```json
{
  "project": "Learn React",
  "startDate": "2025-01-15",
  "hoursLogged": 75,
  "milestones": [...],
  "weeklyLogs": [...]
}
```
```

## Weekly Review Template
```markdown
## Week X Review

**Hours This Week**: X
**Topics Covered**: [List]
**Projects Completed**: [List]

**Wins** 🎉:
- [Achievement 1]
- [Achievement 2]

**Challenges** 😓:
- [Difficulty 1]
- [How I overcame it]

**Next Week Goals**:
- [ ] [Goal 1]
- [ ] [Goal 2]
- [ ] [Goal 3]

**Adjustments Needed**:
- [What to change]
```

## ADHD-Friendly
- Daily 5-minute check-in
- Visual progress bars
- Celebrate small wins
- Flexible milestones
