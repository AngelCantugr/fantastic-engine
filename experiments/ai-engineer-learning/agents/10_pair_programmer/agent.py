#!/usr/bin/env python3
"""
Agent 10: AI Pair Programmer
=============================

Learning Objectives:
- Build a complete agentic workflow
- Implement planning and execution loops
- Orchestrate multiple tools
- Manage complex state
- Create an interactive coding assistant

Complexity: ⭐⭐⭐⭐⭐⭐ Expert
Framework: langgraph + all previous concepts
"""

import sys
import subprocess
from pathlib import Path
from typing import TypedDict, Annotated, Sequence
import operator

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
except ImportError:
    print("Error: langgraph not installed. Run: pip install langgraph")
    sys.exit(1)

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

console = Console()


# Define tools for the pair programmer
@tool
def read_code_file(file_path: str) -> str:
    """Read a code file and return its contents."""
    try:
        return Path(file_path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_code_file(file_path: str, content: str) -> str:
    """Write content to a code file."""
    try:
        Path(file_path).write_text(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def run_tests(test_command: str) -> str:
    """Run tests and return results."""
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return f"Exit code: {result.returncode}\n\nOutput:\n{output}"
    except subprocess.TimeoutExpired:
        return "Tests timed out after 30 seconds"
    except Exception as e:
        return f"Error running tests: {e}"


@tool
def search_codebase(pattern: str, directory: str = ".") -> str:
    """Search for a pattern in the codebase."""
    try:
        result = subprocess.run(
            ["grep", "-r", pattern, directory],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.stdout else "No matches found"
    except Exception as e:
        return f"Error searching: {e}"


@tool
def lint_code(file_path: str) -> str:
    """Run linter on code file."""
    try:
        result = subprocess.run(
            ["ruff", "check", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.stdout else "No linting issues"
    except FileNotFoundError:
        return "Ruff not installed (optional)"
    except Exception as e:
        return f"Error linting: {e}"


# Define agent state
class PairProgrammerState(TypedDict):
    """State of the pair programming session."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: str
    plan: list
    current_step: int
    code_changes: dict
    test_results: str
    iteration: int
    max_iterations: int
    completed: bool


class AIPairProgrammer:
    """
    Full-featured AI pair programmer.

    Demonstrates:
    1. Complete agentic workflow
    2. Planning and execution
    3. Tool orchestration
    4. Iterative refinement
    5. State management
    """

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = ChatOllama(model=model, temperature=0.2)

        # Bind tools
        self.tools = [
            read_code_file,
            write_code_file,
            run_tests,
            search_codebase,
            lint_code
        ]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the pair programming workflow graph."""

        workflow = StateGraph(PairProgrammerState)

        def plan_node(state: PairProgrammerState) -> PairProgrammerState:
            """Create a plan for the task."""
            if state.get("plan"):  # Already have a plan
                return {}

            console.print("\n[cyan]📋 Planning...[/cyan]")

            prompt = f"""You are an AI pair programmer.

Task: {state['task']}

Create a step-by-step plan to complete this task. Consider:
1. Understanding existing code (if any)
2. Writing/modifying code
3. Testing
4. Code quality checks

Provide a numbered plan (3-5 steps):"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            plan_text = response.content

            # Parse plan into steps
            plan = []
            for line in plan_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    plan.append(line.lstrip('0123456789.-) '))

            console.print(f"[green]Created plan with {len(plan)} steps[/green]")
            for i, step in enumerate(plan, 1):
                console.print(f"  {i}. {step}")

            return {"plan": plan, "current_step": 0}

        def execute_step_node(state: PairProgrammerState) -> PairProgrammerState:
            """Execute the current step of the plan."""
            current_step = state["current_step"]
            plan = state["plan"]

            if current_step >= len(plan):
                return {"completed": True}

            step = plan[current_step]
            console.print(f"\n[cyan]⚙️  Executing step {current_step + 1}: {step}[/cyan]")

            # Build context
            context = f"""Task: {state['task']}

Plan step {current_step + 1}/{len(plan)}: {step}

Previous results:
{state.get('test_results', 'None yet')}

Execute this step. Use tools as needed."""

            # Execute with tools
            messages = [HumanMessage(content=context)]
            response = self.llm_with_tools.invoke(messages)

            # If tool calls, execute them
            if hasattr(response, "tool_calls") and response.tool_calls:
                console.print(f"[yellow]Using {len(response.tool_calls)} tools[/yellow]")

            return {
                "messages": [response],
                "current_step": current_step + 1,
                "iteration": state.get("iteration", 0) + 1
            }

        def should_continue(state: PairProgrammerState) -> str:
            """Decide next action."""
            if state.get("completed"):
                return "end"

            if state.get("iteration", 0) >= state.get("max_iterations", 10):
                console.print("[yellow]⚠️  Max iterations reached[/yellow]")
                return "end"

            if state.get("current_step", 0) >= len(state.get("plan", [])):
                return "end"

            return "continue"

        # Add nodes
        workflow.add_node("plan", plan_node)
        workflow.add_node("execute", execute_step_node)

        # Add edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")
        workflow.add_conditional_edges(
            "execute",
            should_continue,
            {
                "continue": "execute",
                "end": END
            }
        )

        return workflow.compile()

    def pair_program(self, task: str, max_iterations: int = 10) -> dict:
        """Start a pair programming session."""
        console.print(Panel.fit(
            f"[bold cyan]AI Pair Programmer[/bold cyan]\n\n"
            f"Task: [yellow]{task}[/yellow]",
            border_style="cyan"
        ))

        # Initialize state
        initial_state = {
            "messages": [],
            "task": task,
            "plan": [],
            "current_step": 0,
            "code_changes": {},
            "test_results": "",
            "iteration": 0,
            "max_iterations": max_iterations,
            "completed": False
        }

        # Run workflow
        final_state = self.graph.invoke(initial_state)

        return final_state


def interactive_mode():
    """Run in interactive mode."""
    console.print(Panel.fit(
        "[bold cyan]🤖 AI Pair Programmer - Interactive Mode[/bold cyan]\n\n"
        "I'll help you code, test, and refactor.\n"
        "Type 'quit' to exit.",
        border_style="cyan"
    ))

    programmer = AIPairProgrammer()

    while True:
        task = Prompt.ask("\n[bold green]What would you like to work on?[/bold green]")

        if task.lower() in ["quit", "exit"]:
            console.print("[cyan]Happy coding! 👋[/cyan]")
            break

        try:
            result = programmer.pair_program(task)

            console.print("\n[green]✅ Task completed![/green]")

            if Confirm.ask("Would you like to work on something else?"):
                continue
            else:
                break

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            if not Confirm.ask("Continue?"):
                break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI Pair Programmer")
    parser.add_argument("--task", help="Task to complete")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--max-iterations", type=int, default=10)

    args = parser.parse_args()

    try:
        if args.task:
            # Single task mode
            programmer = AIPairProgrammer(model=args.model)
            programmer.pair_program(args.task, args.max_iterations)
        else:
            # Interactive mode
            interactive_mode()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
