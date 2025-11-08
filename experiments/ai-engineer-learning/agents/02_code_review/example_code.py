"""
Sample code files for testing the Code Review Agent
====================================================

These examples demonstrate different types of code issues
that the review agent should catch.
"""

# Example 1: Code with security vulnerability
SQL_INJECTION_EXAMPLE = '''
def get_user_by_name(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return database.execute(query)
'''

# Example 2: Performance issues
PERFORMANCE_ISSUE_EXAMPLE = '''
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j]:
                if items[i] not in duplicates:
                    duplicates.append(items[i])
    return duplicates
'''

# Example 3: Style issues
STYLE_ISSUE_EXAMPLE = '''
def calcTotal(x,y,z):
    t=x+y+z
    return t
'''

# Example 4: Good code (for comparison)
GOOD_CODE_EXAMPLE = '''
from typing import List

def calculate_total(amounts: List[float]) -> float:
    """
    Calculate the sum of all amounts.

    Args:
        amounts: List of numerical amounts to sum

    Returns:
        Total sum of all amounts

    Example:
        >>> calculate_total([1.0, 2.0, 3.0])
        6.0
    """
    if not amounts:
        return 0.0

    return sum(amounts)
'''


if __name__ == "__main__":
    """Test the review agent with these examples."""
    import subprocess
    from pathlib import Path

    examples = [
        ("Security Issue", SQL_INJECTION_EXAMPLE, "security"),
        ("Performance Issue", PERFORMANCE_ISSUE_EXAMPLE, "performance"),
        ("Style Issue", STYLE_ISSUE_EXAMPLE, "style"),
        ("Good Code", GOOD_CODE_EXAMPLE, "general"),
    ]

    for name, code, review_type in examples:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"Review Type: {review_type}")
        print(f"{'='*60}\n")

        # Run review
        subprocess.run(
            ["python", "agent.py", "--code", code, "--review-type", review_type]
        )

        input("\nPress Enter to continue to next example...")
