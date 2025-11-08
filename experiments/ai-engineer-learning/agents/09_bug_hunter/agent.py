#!/usr/bin/env python3
"""
Agent 9: Bug Hunter (ReAct Pattern)
====================================

Learning Objectives:
- Implement ReAct pattern (Reasoning + Acting)
- Use LangGraph for stateful agents
- Create agent loops with tool calling
- Dynamic problem solving

Complexity: ⭐⭐⭐⭐⭐ Very Advanced
Framework: langgraph
"""

import sys
import ast
from pathlib import Path
from typing import TypedDict, Annotated, Sequence
import operator

try:
    from langgraph.graph import Graph, StateGraph, END
    from langgraph.prebuilt import ToolNode
except ImportError:
    print("Error: langgraph not installed. Run: pip install langgraph")
    sys.exit(1)

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, FunctionMessage
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


# Define tools for the bug hunter
@tool
def read_file(file_path: str) -> str:
    """Read a Python file and return its contents."""
    try:
        return Path(file_path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def analyze_ast(file_path: str) -> str:
    """Parse file and analyze AST for potential issues."""
    try:
        code = Path(file_path).read_text()
        tree = ast.parse(code)

        issues = []

        # Check for common issues
        for node in ast.walk(tree):
            # Bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(f"Line {node.lineno}: Bare except clause (catches all exceptions)")

            # Mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(
                            f"Line {node.lineno}: Mutable default argument in function {node.name}"
                        )

        return "\n".join(issues) if issues else "No obvious AST issues found"

    except Exception as e:
        return f"Error analyzing AST: {e}"


@tool
def check_security(code_snippet: str) -> str:
    """Check for common security issues in code."""
    issues = []

    # Simple pattern matching for common issues
    if "eval(" in code_snippet:
        issues.append("CRITICAL: Use of eval() - code injection risk")
    if "exec(" in code_snippet:
        issues.append("CRITICAL: Use of exec() - code injection risk")
    if "pickle.loads" in code_snippet:
        issues.append("HIGH: pickle.loads - deserialization risk")
    if "shell=True" in code_snippet:
        issues.append("HIGH: subprocess with shell=True - command injection risk")
    if "f\"SELECT" in code_snippet or "f'SELECT" in code_snippet:
        issues.append("CRITICAL: Potential SQL injection (f-string in SQL)")

    return "\n".join(issues) if issues else "No obvious security issues found"


# Define agent state
class AgentState(TypedDict):
    """State of the bug hunting agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    file_path: str
    bugs_found: list
    analysis_complete: bool


class BugHunter:
    """
    ReAct agent that hunts for bugs.

    Demonstrates:
    1. ReAct pattern (Reasoning + Acting)
    2. LangGraph stateful agents
    3. Tool usage in loops
    4. Dynamic problem solving
    """

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = ChatOllama(model=model, temperature=0.2)

        # Bind tools to LLM
        self.tools = [read_file, analyze_ast, check_security]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        """Build the ReAct agent graph."""

        workflow = StateGraph(AgentState)

        # Define nodes
        def agent_node(state: AgentState) -> AgentState:
            """Agent reasoning node."""
            messages = state["messages"]

            # Add system message on first call
            if len(messages) == 0 or not isinstance(messages[0], HumanMessage):
                system_msg = HumanMessage(content=f"""You are a bug hunting expert.
Analyze the file: {state['file_path']}

Use these tools:
- read_file: Read the file contents
- analyze_ast: Check for AST-level issues
- check_security: Look for security vulnerabilities

Think step-by-step:
1. Read the file
2. Analyze structure
3. Check for security issues
4. Summarize findings

After using all tools, provide a final summary of bugs found.""")
                messages = [system_msg] + list(messages)

            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def tool_node(state: AgentState) -> AgentState:
            """Execute tools."""
            messages = state["messages"]
            last_message = messages[-1]

            # Execute tool calls
            tool_calls = getattr(last_message, "tool_calls", [])
            if not tool_calls:
                return {"messages": []}

            results = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute tool
                tool_func = next((t for t in self.tools if t.name == tool_name), None)
                if tool_func:
                    result = tool_func.invoke(tool_args)
                    results.append(FunctionMessage(
                        content=str(result),
                        name=tool_name
                    ))

            return {"messages": results}

        def should_continue(state: AgentState) -> str:
            """Decide whether to continue or end."""
            messages = state["messages"]
            last_message = messages[-1]

            # If there are tool calls, continue to tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "continue"
            # Otherwise end
            return "end"

        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)

        # Add edges
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def hunt_bugs(self, file_path: str) -> str:
        """Hunt for bugs in a file."""
        console.print(f"[cyan]Hunting bugs in: {file_path}[/cyan]\n")

        # Initialize state
        initial_state = {
            "messages": [],
            "file_path": file_path,
            "bugs_found": [],
            "analysis_complete": False
        }

        # Run the agent
        final_state = self.graph.invoke(initial_state)

        # Extract final answer
        messages = final_state["messages"]
        if messages:
            final_message = messages[-1]
            return final_message.content if hasattr(final_message, "content") else str(final_message)

        return "No analysis completed"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Bug Hunter (ReAct)")
    parser.add_argument("--file", type=Path, required=True, help="File to analyze")
    parser.add_argument("--model", default="qwen2.5-coder:7b")

    args = parser.parse_args()

    try:
        hunter = BugHunter(model=args.model)

        console.print(Panel.fit(
            "[bold cyan]Bug Hunter (ReAct Pattern)[/bold cyan]\n\n"
            f"File: [yellow]{args.file}[/yellow]\n"
            f"Model: [yellow]{args.model}[/yellow]"
        ))

        # Hunt bugs
        results = hunter.hunt_bugs(str(args.file))

        # Display results
        console.print("\n" + "="*60)
        console.print(Panel(
            Markdown(results),
            title="[bold red]Bug Analysis[/bold red]",
            border_style="red"
        ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
