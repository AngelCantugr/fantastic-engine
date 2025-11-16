#!/usr/bin/env python3
"""
LeetCode Pattern Recognition Trainer

Master the 15 core algorithmic patterns through spaced repetition
and deliberate practice.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.markdown import Markdown
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Initialize
console = Console()
Base = declarative_base()


class MasteryLevel(Enum):
    """Pattern mastery levels"""
    NOT_STARTED = (0, "⚪", "Not Started")
    STRUGGLING = (1, "🔴", "Struggling")
    NOVICE = (2, "📚", "Novice")
    LEARNING = (3, "🎯", "Learning")
    PROFICIENT = (4, "💪", "Proficient")
    MASTERED = (5, "⭐", "Mastered")

    def __init__(self, level, emoji, name):
        self.level = level
        self.emoji = emoji
        self.display_name = name

    @staticmethod
    def from_percentage(percentage: float):
        """Convert percentage to mastery level"""
        if percentage >= 95:
            return MasteryLevel.MASTERED
        elif percentage >= 80:
            return MasteryLevel.PROFICIENT
        elif percentage >= 60:
            return MasteryLevel.LEARNING
        elif percentage >= 40:
            return MasteryLevel.NOVICE
        elif percentage >= 20:
            return MasteryLevel.STRUGGLING
        else:
            return MasteryLevel.NOT_STARTED


# Database Models
class PatternProgress(Base):
    """Track progress for each pattern"""
    __tablename__ = "pattern_progress"

    id = Column(Integer, primary_key=True)
    pattern_name = Column(String, unique=True, nullable=False)
    mastery_percentage = Column(Float, default=0.0)
    total_drills = Column(Integer, default=0)
    correct_drills = Column(Integer, default=0)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5)  # SM-2 algorithm
    interval = Column(Integer, default=1)  # days
    consecutive_correct = Column(Integer, default=0)
    is_mastered = Column(Boolean, default=False)


class DrillHistory(Base):
    """Track individual drill attempts"""
    __tablename__ = "drill_history"

    id = Column(Integer, primary_key=True)
    pattern_name = Column(String, nullable=False)
    problem_description = Column(String, nullable=False)
    user_answer = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=True)  # seconds
    timestamp = Column(DateTime, default=datetime.now)


@dataclass
class Pattern:
    """Pattern definition"""
    id: int
    name: str
    category: str
    difficulty: str
    explanation: str
    visual_example: str
    code_template: str
    time_complexity: str
    space_complexity: str
    when_to_use: List[str]
    when_not_to_use: List[str]
    variations: List[str]
    common_mistakes: List[str]
    related_patterns: List[str]
    example_problems: List[Dict[str, any]]  # {id, title, difficulty}


# Define all 15 core patterns
PATTERNS = [
    Pattern(
        id=1,
        name="Two Pointers",
        category="Array/String",
        difficulty="Easy",
        explanation="""
Two pointers technique uses two pointers moving through data from different
positions or speeds to find relationships between elements. Common variations:
- Opposite ends moving toward each other
- Same direction at different speeds
- Fast and slow pointers
""",
        visual_example="""
Problem: Find pair summing to target in sorted array

[1, 2, 3, 4, 6, 8, 9]  target=10
 ↑                 ↑
left             right

1 + 9 = 10  ✓ Found!
""",
        code_template="""
def two_pointers(arr, target):
    left, right = 0, len(arr) - 1

    while left < right:
        current_sum = arr[left] + arr[right]

        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return None
""",
        time_complexity="O(n)",
        space_complexity="O(1)",
        when_to_use=[
            "Array/string is sorted or can be sorted",
            "Need to find pairs/triplets",
            "Problem mentions 'two elements'",
            "Can reduce O(n²) to O(n)"
        ],
        when_not_to_use=[
            "Data is unsorted and can't be sorted",
            "Need to maintain original order",
            "Problem requires visiting all pairs"
        ],
        variations=[
            "Opposite direction (left/right)",
            "Same direction (fast/slow)",
            "Multiple pointers (3-way, 4-way)"
        ],
        common_mistakes=[
            "Not handling edge cases (empty, single element)",
            "Off-by-one errors with indices",
            "Infinite loops when pointers don't converge"
        ],
        related_patterns=["Sliding Window", "Fast & Slow Pointers"],
        example_problems=[
            {"id": 1, "title": "Two Sum II", "difficulty": "Easy"},
            {"id": 15, "title": "3Sum", "difficulty": "Medium"},
            {"id": 11, "title": "Container With Most Water", "difficulty": "Medium"}
        ]
    ),

    Pattern(
        id=2,
        name="Sliding Window",
        category="Array/String",
        difficulty="Medium",
        explanation="""
Sliding window maintains a subset of elements (window) that slides through the
array/string. Used for contiguous subarray/substring problems.
- Fixed size window
- Variable size window
- Shrinking/expanding window
""",
        visual_example="""
Problem: Max sum of k consecutive elements

[2, 1, 5, 1, 3, 2]  k=3
[2, 1, 5] = 8
   [1, 5, 1] = 7
      [5, 1, 3] = 9  ← max!
""",
        code_template="""
def sliding_window(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum

    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i-k] + arr[i]
        max_sum = max(max_sum, window_sum)

    return max_sum
""",
        time_complexity="O(n)",
        space_complexity="O(1)",
        when_to_use=[
            "Contiguous subarray/substring problem",
            "Need max/min length/sum",
            "Problem mentions 'window'",
            "Looking for patterns in sequences"
        ],
        when_not_to_use=[
            "Elements don't need to be contiguous",
            "Need to maintain all subarrays",
            "Problem requires sorting"
        ],
        variations=[
            "Fixed size window",
            "Variable size window",
            "Multiple windows"
        ],
        common_mistakes=[
            "Not handling window boundaries correctly",
            "Forgetting to update window when shrinking",
            "Incorrect initialization of window"
        ],
        related_patterns=["Two Pointers", "Prefix Sum"],
        example_problems=[
            {"id": 3, "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium"},
            {"id": 209, "title": "Minimum Size Subarray Sum", "difficulty": "Medium"},
            {"id": 438, "title": "Find All Anagrams in a String", "difficulty": "Medium"}
        ]
    ),

    Pattern(
        id=3,
        name="Fast & Slow Pointers",
        category="Linked List",
        difficulty="Medium",
        explanation="""
Two pointers moving at different speeds through a linked list or array.
Slow pointer moves one step, fast pointer moves two steps.
Commonly used to detect cycles and find middle elements.
""",
        visual_example="""
Detect cycle:

1 → 2 → 3 → 4
    ↑       ↓
    6 ← 5 ←┘

slow: 1→2→3→4→5→6→2 (meets here)
fast: 1→3→5→2→4→6→3→2
""",
        code_template="""
def has_cycle(head):
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow == fast:
            return True

    return False
""",
        time_complexity="O(n)",
        space_complexity="O(1)",
        when_to_use=[
            "Detect cycle in linked list",
            "Find middle of linked list",
            "Find nth from end",
            "Need to traverse at different rates"
        ],
        when_not_to_use=[
            "Need random access to elements",
            "Array-based problems (use two pointers instead)",
            "Need to track multiple previous positions"
        ],
        variations=[
            "Cycle detection",
            "Finding middle",
            "k-way fast pointer"
        ],
        common_mistakes=[
            "Not checking for null pointers",
            "Wrong speed ratio (not 1:2)",
            "Incorrect cycle detection logic"
        ],
        related_patterns=["Two Pointers", "Linked List Reversal"],
        example_problems=[
            {"id": 141, "title": "Linked List Cycle", "difficulty": "Easy"},
            {"id": 142, "title": "Linked List Cycle II", "difficulty": "Medium"},
            {"id": 876, "title": "Middle of the Linked List", "difficulty": "Easy"}
        ]
    ),

    Pattern(
        id=4,
        name="Hash Map/Set",
        category="Hash Table",
        difficulty="Easy",
        explanation="""
Use hash tables (dictionaries/maps/sets) for O(1) lookups.
Trade space for time complexity. Common uses:
- Finding complements/pairs
- Counting frequency
- Detecting duplicates
- Caching results
""",
        visual_example="""
Two Sum with hash map:

nums=[2,7,11,15], target=9

seen = {}
num=2: target-2=7 not in seen → seen={2:0}
num=7: target-7=2 IS in seen → return [0,1] ✓
""",
        code_template="""
def two_sum(nums, target):
    seen = {}

    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    return None
""",
        time_complexity="O(n)",
        space_complexity="O(n)",
        when_to_use=[
            "Need O(1) lookup time",
            "Finding pairs/complements",
            "Counting frequencies",
            "Detecting duplicates"
        ],
        when_not_to_use=[
            "Memory is severely constrained",
            "Need sorted output",
            "Problem requires specific ordering"
        ],
        variations=[
            "Hash map (key-value)",
            "Hash set (existence check)",
            "Frequency counter"
        ],
        common_mistakes=[
            "Using same element twice",
            "Not handling duplicates",
            "Choosing wrong data structure (map vs set)"
        ],
        related_patterns=["Two Pointers", "Frequency Counter"],
        example_problems=[
            {"id": 1, "title": "Two Sum", "difficulty": "Easy"},
            {"id": 49, "title": "Group Anagrams", "difficulty": "Medium"},
            {"id": 217, "title": "Contains Duplicate", "difficulty": "Easy"}
        ]
    ),

    Pattern(
        id=5,
        name="Binary Search",
        category="Search",
        difficulty="Medium",
        explanation="""
Divide and conquer algorithm for searching sorted arrays.
Repeatedly divides search space in half.
Time complexity: O(log n)

Key insight: Eliminate half the possibilities each iteration.
""",
        visual_example="""
Find 7 in sorted array:

[1, 3, 5, 7, 9, 11, 13]
          ↑
       mid=7 ✓ Found!
""",
        code_template="""
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
""",
        time_complexity="O(log n)",
        space_complexity="O(1)",
        when_to_use=[
            "Array is sorted",
            "Need O(log n) search",
            "Search space can be halved",
            "Finding insertion point"
        ],
        when_not_to_use=[
            "Array is unsorted and can't be sorted",
            "Need to find all occurrences",
            "Small dataset (linear search is simpler)"
        ],
        variations=[
            "Standard binary search",
            "Find first/last occurrence",
            "Search in rotated array"
        ],
        common_mistakes=[
            "Integer overflow with (left+right)/2",
            "Wrong boundary conditions (< vs <=)",
            "Not handling edge cases"
        ],
        related_patterns=["Two Pointers", "Divide and Conquer"],
        example_problems=[
            {"id": 704, "title": "Binary Search", "difficulty": "Easy"},
            {"id": 35, "title": "Search Insert Position", "difficulty": "Easy"},
            {"id": 33, "title": "Search in Rotated Sorted Array", "difficulty": "Medium"}
        ]
    ),

    # Additional patterns (6-15) defined similarly...
    # For brevity, showing structure for remaining patterns

    Pattern(
        id=6,
        name="BFS (Breadth-First Search)",
        category="Tree/Graph",
        difficulty="Medium",
        explanation="Level-order traversal using queue. Finds shortest path.",
        visual_example="Tree level-order: 1 → [2,3] → [4,5,6,7]",
        code_template="# Use queue for BFS",
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        when_to_use=["Shortest path", "Level-order traversal"],
        when_not_to_use=["Need all paths", "DFS is more natural"],
        variations=["Tree BFS", "Graph BFS", "Multi-source BFS"],
        common_mistakes=["Not marking visited", "Wrong termination"],
        related_patterns=["DFS", "Two Pointers"],
        example_problems=[
            {"id": 102, "title": "Binary Tree Level Order Traversal", "difficulty": "Medium"}
        ]
    ),

    Pattern(
        id=7,
        name="DFS (Depth-First Search)",
        category="Tree/Graph",
        difficulty="Medium",
        explanation="Explore as far as possible before backtracking. Uses stack/recursion.",
        visual_example="Tree DFS: 1→2→4→5→3→6→7",
        code_template="# Recursive or stack-based DFS",
        time_complexity="O(V + E)",
        space_complexity="O(h) for recursion",
        when_to_use=["Explore all paths", "Tree traversal", "Backtracking"],
        when_not_to_use=["Shortest path needed", "Memory constrained"],
        variations=["Preorder", "Inorder", "Postorder"],
        common_mistakes=["Stack overflow", "Not handling cycles"],
        related_patterns=["BFS", "Backtracking"],
        example_problems=[
            {"id": 200, "title": "Number of Islands", "difficulty": "Medium"}
        ]
    ),

    # Patterns 8-15 similarly defined...
]


class PatternTrainer:
    """Main trainer class"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "progress.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.patterns = {p.name: p for p in PATTERNS}

    def get_pattern(self, name: str) -> Optional[Pattern]:
        """Get pattern by name"""
        return self.patterns.get(name)

    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns"""
        return list(self.patterns.values())

    def get_or_create_progress(self, pattern_name: str) -> PatternProgress:
        """Get or create progress record for a pattern"""
        progress = self.session.query(PatternProgress).filter_by(
            pattern_name=pattern_name
        ).first()

        if not progress:
            progress = PatternProgress(pattern_name=pattern_name)
            self.session.add(progress)
            self.session.commit()

        return progress

    def show_pattern_tutorial(self, pattern_name: str):
        """Display comprehensive pattern tutorial"""
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            console.print(f"[red]Pattern '{pattern_name}' not found[/red]")
            return

        console.print()
        console.print(Panel.fit(
            f"🎯 [bold cyan]Pattern #{pattern.id}: {pattern.name}[/bold cyan]\n"
            f"Category: {pattern.category} | Difficulty: {pattern.difficulty}",
            border_style="cyan"
        ))

        # Explanation
        console.print("\n📖 [bold]WHAT IS IT?[/bold]")
        console.rule(style="dim")
        console.print(pattern.explanation.strip())

        # Visual Example
        console.print("\n🎬 [bold]VISUAL EXAMPLE[/bold]")
        console.rule(style="dim")
        console.print(f"[dim]{pattern.visual_example.strip()}[/dim]")

        # Code Template
        console.print("\n💻 [bold]CODE TEMPLATE[/bold]")
        console.rule(style="dim")
        console.print(f"[dim]{pattern.code_template.strip()}[/dim]")

        # Complexity
        console.print("\n⏱️  [bold]COMPLEXITY[/bold]")
        console.rule(style="dim")
        console.print(f"Time:  {pattern.time_complexity}")
        console.print(f"Space: {pattern.space_complexity}")

        # When to use
        console.print("\n🎯 [bold]WHEN TO USE[/bold]")
        console.rule(style="dim")
        for use_case in pattern.when_to_use:
            console.print(f"  ✓ {use_case}")

        # Example problems
        console.print("\n📝 [bold]PRACTICE PROBLEMS[/bold]")
        console.rule(style="dim")
        for prob in pattern.example_problems[:5]:
            console.print(f"  • #{prob['id']}: {prob['title']} ({prob['difficulty']})")

        console.print()

    def show_dashboard(self):
        """Display progress dashboard"""
        console.print()
        console.print(Panel.fit(
            "📊 [bold cyan]Pattern Mastery Dashboard[/bold cyan]",
            border_style="cyan"
        ))

        # Calculate overall progress
        all_progress = self.session.query(PatternProgress).all()
        if not all_progress:
            console.print("\n[yellow]No progress yet. Start learning patterns![/yellow]\n")
            return

        total_mastery = sum(p.mastery_percentage for p in all_progress)
        avg_mastery = total_mastery / len(PATTERNS) if PATTERNS else 0

        console.print(f"\nOverall Progress: [bold]{avg_mastery:.1f}%[/bold] "
                     f"({sum(1 for p in all_progress if p.is_mastered)}/{len(PATTERNS)} patterns mastered)\n")

        # Pattern table
        console.print("[bold]Pattern Mastery:[/bold]")
        console.rule(style="dim")

        for pattern in PATTERNS[:10]:  # Show first 10
            progress = self.get_or_create_progress(pattern.name)
            mastery = MasteryLevel.from_percentage(progress.mastery_percentage)

            # Progress bar
            filled = int(progress.mastery_percentage / 5)
            bar = "█" * filled + "░" * (20 - filled)

            console.print(
                f"{pattern.name:.<25} {bar} {progress.mastery_percentage:>3.0f}% "
                f"{mastery.emoji} {mastery.display_name}"
            )

        console.print()


@click.command()
@click.option("--learn", help="Learn a specific pattern")
@click.option("--drill", is_flag=True, help="Start pattern recognition drill")
@click.option("--dashboard", is_flag=True, help="Show progress dashboard")
@click.option("--init", is_flag=True, help="Initialize database")
def main(learn, drill, dashboard, init):
    """LeetCode Pattern Recognition Trainer"""

    trainer = PatternTrainer()

    if init:
        console.print("[green]✓ Database initialized[/green]")
        return

    if learn:
        trainer.show_pattern_tutorial(learn)
        return

    if dashboard:
        trainer.show_dashboard()
        return

    if drill:
        console.print("[yellow]Drill mode coming soon![/yellow]")
        return

    # Default: show available patterns
    console.print("\n[bold magenta]🎯 LeetCode Pattern Trainer[/bold magenta]\n")
    console.print("Available patterns:")
    for pattern in PATTERNS[:10]:
        console.print(f"  {pattern.id}. {pattern.name} ({pattern.category})")
    console.print("\nUse --learn <pattern> to start learning!")


if __name__ == "__main__":
    main()
