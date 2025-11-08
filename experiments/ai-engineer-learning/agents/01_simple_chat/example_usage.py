#!/usr/bin/env python3
"""
Example usage of Simple Chat Agent
===================================

This file shows how to use the SimpleChatAgent programmatically
in your own scripts, rather than just the interactive CLI.
"""

from agent import SimpleChatAgent
from rich.console import Console

console = Console()


def example_1_basic_chat():
    """Example 1: Basic single-turn conversation."""
    console.print("\n[bold cyan]Example 1: Basic Chat[/bold cyan]\n")

    # Create agent
    agent = SimpleChatAgent(model="qwen2.5-coder:7b")

    # Send a message (streaming enabled by default)
    response = agent.chat("What is a Python decorator in one sentence?")

    # Response is automatically printed, but also returned
    console.print(f"\n[dim]Response length: {len(response)} characters[/dim]")


def example_2_non_streaming():
    """Example 2: Non-streaming response (wait for complete answer)."""
    console.print("\n[bold cyan]Example 2: Non-Streaming[/bold cyan]\n")

    agent = SimpleChatAgent(model="qwen2.5-coder:7b")

    # Disable streaming - wait for complete response
    response = agent.chat(
        "Explain list comprehension in Python with an example.",
        stream=False
    )


def example_3_multi_turn():
    """Example 3: Multi-turn conversation with context."""
    console.print("\n[bold cyan]Example 3: Multi-Turn Conversation[/bold cyan]\n")

    agent = SimpleChatAgent(model="qwen2.5-coder:7b")

    # First question
    agent.chat("What is the difference between a list and a tuple?")

    # Follow-up question (agent remembers context)
    console.print("\n[yellow]--- Follow-up question ---[/yellow]")
    agent.chat("Which one should I use for function arguments?")

    # Another follow-up
    console.print("\n[yellow]--- Another follow-up ---[/yellow]")
    agent.chat("Show me an example of both.")


def example_4_custom_system_message():
    """Example 4: Customize the system message for specific behavior."""
    console.print("\n[bold cyan]Example 4: Custom System Message[/bold cyan]\n")

    # Create agent with custom personality
    agent = SimpleChatAgent(
        model="qwen2.5-coder:7b",
        system_message=(
            "You are a senior Python developer who loves teaching junior engineers. "
            "Always include practical examples and explain the 'why' behind concepts. "
            "Use analogies when helpful. Keep responses concise but complete."
        )
    )

    agent.chat("What are Python generators and when should I use them?")


def example_5_temperature_comparison():
    """Example 5: Compare different temperature settings."""
    console.print("\n[bold cyan]Example 5: Temperature Comparison[/bold cyan]\n")

    question = "Write a creative variable name for a shopping cart total."

    # Low temperature (focused, deterministic)
    console.print("\n[yellow]Temperature 0.1 (Focused):[/yellow]")
    agent_focused = SimpleChatAgent(temperature=0.1)
    agent_focused.chat(question, stream=False)

    # High temperature (creative, varied)
    console.print("\n[yellow]Temperature 0.9 (Creative):[/yellow]")
    agent_creative = SimpleChatAgent(temperature=0.9)
    agent_creative.chat(question, stream=False)


def example_6_error_handling():
    """Example 6: Handle errors gracefully."""
    console.print("\n[bold cyan]Example 6: Error Handling[/bold cyan]\n")

    try:
        # Try with a model that doesn't exist
        agent = SimpleChatAgent(model="nonexistent-model:latest")

        if not agent.check_ollama_health():
            console.print("[yellow]Model not available. Using fallback.[/yellow]")
            # Fallback to default model
            agent = SimpleChatAgent(model="qwen2.5-coder:7b")

        agent.chat("Hello!")

    except Exception as e:
        console.print(f"[red]Error occurred: {e}[/red]")


def example_7_conversation_reset():
    """Example 7: Reset conversation to start fresh."""
    console.print("\n[bold cyan]Example 7: Conversation Reset[/bold cyan]\n")

    agent = SimpleChatAgent()

    # First conversation
    agent.chat("My favorite language is Python.")
    agent.chat("What is my favorite language?")

    # Reset conversation
    console.print("\n[yellow]--- Resetting conversation ---[/yellow]")
    agent.reset_conversation()

    # Agent won't remember the previous context
    agent.chat("What is my favorite language?")


def example_8_code_generation():
    """Example 8: Use agent for code generation."""
    console.print("\n[bold cyan]Example 8: Code Generation[/bold cyan]\n")

    agent = SimpleChatAgent(
        temperature=0.3,  # Lower temperature for more consistent code
        system_message=(
            "You are a code generation assistant. "
            "Always include type hints, docstrings, and comments. "
            "Follow PEP 8 style guidelines."
        )
    )

    agent.chat(
        "Write a Python function that takes a list of numbers and "
        "returns only the even numbers using list comprehension."
    )


if __name__ == "__main__":
    """Run all examples."""
    import argparse

    parser = argparse.ArgumentParser(description="Run SimpleChatAgent examples")
    parser.add_argument(
        "--example",
        type=int,
        choices=range(1, 9),
        help="Run specific example (1-8)"
    )

    args = parser.parse_args()

    examples = {
        1: example_1_basic_chat,
        2: example_2_non_streaming,
        3: example_3_multi_turn,
        4: example_4_custom_system_message,
        5: example_5_temperature_comparison,
        6: example_6_error_handling,
        7: example_7_conversation_reset,
        8: example_8_code_generation,
    }

    if args.example:
        examples[args.example]()
    else:
        # Run all examples
        console.print(Panel.fit(
            "[bold]SimpleChatAgent Examples[/bold]\n\n"
            "Running all examples...\n"
            "Press Ctrl+C to skip to next example",
            border_style="cyan"
        ))

        for i, func in examples.items():
            try:
                func()
                console.print("\n" + "─" * 60)
            except KeyboardInterrupt:
                console.print("\n[yellow]Skipped.[/yellow]")
                continue

        console.print("\n[green]All examples completed![/green]")
