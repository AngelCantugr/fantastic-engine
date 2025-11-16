"""
ReAct Pattern Template

Use this template to quickly create a new ReAct agent.
Simply fill in your tools and customize the configuration.
"""

from langgraph_patterns import ReActPattern
from langchain_core.tools import tool


# TODO: Define your custom tools
@tool
def my_custom_tool(param: str) -> str:
    """
    Description of what this tool does.

    Args:
        param: Description of the parameter

    Returns:
        Description of the return value
    """
    # TODO: Implement your tool logic
    return f"Processed: {param}"


# TODO: Add more tools as needed
@tool
def another_tool(value: int) -> int:
    """Another tool example."""
    return value * 2


def main():
    """Run your custom ReAct agent."""

    # Configure your agent
    agent = ReActPattern(
        tools=[my_custom_tool, another_tool],  # TODO: List your tools
        model="gpt-4",  # TODO: Choose your model
        max_iterations=10,  # TODO: Set iteration limit
    )

    # TODO: Customize your agent's task
    result = agent.run("Your task description here")

    # Display results
    print("Agent Output:")
    print(result.output)

    if result.success:
        print(f"\nCompleted in {len(result.steps)} steps")
    else:
        print(f"\nFailed: {result.error}")


if __name__ == "__main__":
    main()
