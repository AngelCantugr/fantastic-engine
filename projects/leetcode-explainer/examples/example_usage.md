# Example Usage - LeetCode Explainer

## Example 1: Explain by Problem ID

```bash
python explainer.py --id 1 --level 3
```

### Output:

```
╔══════════════════════════════════════════════════════════════════╗
║  🧠 LeetCode Solution Explainer                                  ║
║  Problem #1: Two Sum                                             ║
╚══════════════════════════════════════════════════════════════════╝

📊 QUICK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern:      Hash Table Lookup
Difficulty:   Easy
Time:         O(n)
Space:        O(n)
Key Insight:  Use a hash table to store complements for O(n) lookup time.

🎯 EXPLANATION (Level 3: Intermediate)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The problem asks us to find two numbers that add up to a target.

Instead of checking every pair (O(n²)), we use a hash table to:
1. Store each number and its index as we iterate
2. For each number, check if (target - number) exists in our hash table
3. If it exists, we found our pair!

This is the "complement pattern" - instead of looking for pairs,
look for complements.
```

## Example 2: Explain Custom Code

Create a file `my_solution.py`:

```python
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
```

Run:

```bash
python explainer.py --id 1 --code my_solution.py --level 2
```

### Output:

```
🧠 LeetCode Solution Explainer
Problem #1: Two Sum

📊 QUICK SUMMARY
Pattern:      Brute Force
Difficulty:   Easy
Time:         O(n²)
Space:        O(1)
Key Insight:  Check every possible pair until a match is found.

🎯 EXPLANATION (Level 2: Beginner)

This is a straightforward approach: check every pair of numbers.

How it works:
1. Use two nested loops
2. The outer loop picks the first number
3. The inner loop picks the second number (always after the first)
4. If they add up to the target, return their positions

This is called a "brute force" approach because it tries every possibility.

⚠️  Note: This works but is slow for large arrays!
Time: O(n²) - for each number, we check all remaining numbers
Space: O(1) - we only use a few variables

🔄 BETTER APPROACH

Try using a hash table instead! It reduces time from O(n²) to O(n).
```

## Example 3: Focus on Specific Aspect

```bash
python explainer.py --id 1 --focus complexity
```

This provides a deep dive into time/space complexity analysis.

## Example 4: Export to Markdown

```bash
python explainer.py --id 1 --export explanations/two-sum.md
```

Creates a markdown file you can review later.

## Example 5: Interactive Mode

```bash
python explainer.py --interactive
```

```
🧠 LeetCode Solution Explainer - Interactive Mode

What would you like me to explain?
1. Problem ID
2. Problem URL
3. Paste code

Choice: 1

Problem ID: 1

What explanation level? (1-5)
1. ELI5 (Explain Like I'm 5)
2. Beginner
3. Intermediate (recommended)
4. Advanced
5. Expert

Level: 3

Generating explanation...
✓ Done!

[Shows explanation]

What would you like to do next?
1. See different explanation level
2. Focus on specific aspect
3. Export to file
4. Explain another problem
5. Exit

Choice: _
```

## Integration Examples

### With Pattern Trainer

```python
from explainer import LeetCodeExplainer
from pattern_trainer import PatternTrainer

# Explain a problem
explainer = LeetCodeExplainer()
explanation = explainer.explain(problem_id=1)

# Extract the pattern
pattern = explanation.pattern.name  # "Hash Table Lookup"

# Launch pattern trainer for practice
trainer = PatternTrainer()
trainer.practice_pattern(pattern)
```

### With Session Analyzer

```python
from explainer import LeetCodeExplainer
from session_analyzer import SessionAnalyzer

explainer = LeetCodeExplainer()
analyzer = SessionAnalyzer()

# Explain and track
explanation = explainer.explain(problem_id=1)

# Log to session
analyzer.log_event(
    event_type="explanation_viewed",
    problem_id=1,
    pattern=explanation.pattern.name,
    level=3
)
```

### With Gamification Tracker

```python
from explainer import LeetCodeExplainer

# Track explanations toward daily goal
explainer = LeetCodeExplainer()

explanation = explainer.explain(
    problem_id=1,
    track_session=True  # Automatically logs to gamification system
)

# Earns points:
# +5 for viewing explanation
# +10 for completing all sections
# +20 for implementing the solution after
```

## Common Workflows

### Workflow 1: Learning a New Pattern

```bash
# Step 1: Get explanation
python explainer.py --id 1 --level 3

# Step 2: Practice the pattern
python ../leetcode-pattern-trainer/trainer.py --pattern "Hash Table"

# Step 3: Try similar problems
python explainer.py --id 167  # Two Sum II
```

### Workflow 2: Debugging Your Solution

```bash
# Step 1: Explain the correct solution
python explainer.py --id 1 --export correct_solution.md

# Step 2: Compare with your attempt
python ../leetcode-mistake-analyzer/analyzer.py \
  --problem 1 \
  --your-code my_attempt.py \
  --reference correct_solution.md
```

### Workflow 3: Daily Practice

```bash
# Morning routine
python ../leetcode-study-planner/planner.py --today
# → Suggests: "Two Sum (#1) - Hash Table pattern"

python explainer.py --id 1 --level 3
# → Read explanation

# Implement solution
# → Code it yourself

python ../leetcode-session-analyzer/analyzer.py --log-solution 1
# → Track completion

python ../leetcode-gamification/tracker.py --check-streak
# → See progress: "🔥 7 day streak!"
```

## Tips for ADHD Users

1. **Start with Level 2-3**: Don't overwhelm yourself with expert-level details initially

2. **Use Progressive Learning**:
   - Day 1: Read ELI5 explanation
   - Day 2: Read Beginner explanation + implement
   - Day 3: Read Intermediate explanation + optimize

3. **Export for Later**: Can't focus now? Export and read later
   ```bash
   python explainer.py --id 1 --export ~/reading-list/two-sum.md
   ```

4. **Focus Mode**: Struggling with one aspect?
   ```bash
   python explainer.py --id 1 --focus patterns  # Just the pattern
   ```

5. **Visual Learning**: The step-by-step trace is your friend!
   - Watch how variables change
   - See the algorithm in action
   - Better than abstract descriptions

6. **Chunk Your Learning**: Don't try to understand everything at once
   - Read Quick Summary
   - Take a break
   - Read Explanation
   - Take a break
   - Read Trace
   - Done for the day!

## Configuration for Your Style

Edit `.env` to customize:

```bash
# Prefer shorter explanations
DEFAULT_EXPLANATION_LEVEL=2

# Reduce visual clutter
ENABLE_EMOJI=false

# Auto-export everything
AUTO_EXPORT=true
EXPORT_DIR=~/leetcode-notes
```
