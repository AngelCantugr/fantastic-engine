"""
Example: Using the ReAct Pattern

This example demonstrates how to use the ReAct pattern to build
an agent that can search the web and perform calculations.
"""

from langgraph_patterns import ReActPattern
from langchain.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool


# Define custom tools
@tool
def calculator(expression: str) -> float:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression like "2 + 2" or "10 * 5"

    Returns:
        The result of the calculation
    """
    try:
        # Note: eval() is used here for demo purposes only
        # In production, use a safe math parser
        result = eval(expression)
        return float(result)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time in a specific timezone.

    Args:
        timezone: The timezone (e.g., "UTC", "America/New_York")

    Returns:
        Current time as a string
    """
    from datetime import datetime
    import pytz

    tz = pytz.timezone(timezone)
    current_time = datetime.now(tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")


def main():
    """Run the ReAct pattern example."""

    # Initialize tools
    search = DuckDuckGoSearchResults()

    # Create agent with ReAct pattern
    agent = ReActPattern(
        tools=[search, calculator, get_current_time],
        model="gpt-4",
        max_iterations=5,
    )

    # Example 1: Simple calculation
    print("Example 1: Simple Calculation")
    print("-" * 50)
    result = agent.run("What is 156 * 42?")
    print(f"Result: {result.output}")
    print(f"Steps taken: {len(result.steps)}")
    print()

    # Example 2: Web search + calculation
    print("Example 2: Research + Calculation")
    print("-" * 50)
    result = agent.run(
        "What is the population of Tokyo? Then multiply it by 0.05"
    )
    print(f"Result: {result.output}")
    print(f"Steps taken: {len(result.steps)}")
    print()

    # Example 3: Multiple tool usage
    print("Example 3: Multiple Tools")
    print("-" * 50)
    result = agent.run(
        "What time is it in Tokyo right now? How does that compare to New York?"
    )
    print(f"Result: {result.output}")
    print(f"Steps taken: {len(result.steps)}")
    print()

    # View the execution steps
    if result.steps:
        print("Execution Steps:")
        print("-" * 50)
        for i, step in enumerate(result.steps, 1):
            print(f"\nStep {i}:")
            print(f"  Action: {step.get('action', 'N/A')}")
            print(f"  Observation: {step.get('observation', 'N/A')}")


if __name__ == "__main__":
    main()
