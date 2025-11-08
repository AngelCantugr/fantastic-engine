"""
Swarm Pattern Example 1: Code Review Team

A decentralized team of code reviewers that handoff to each other
based on issues found. Demonstrates peer-to-peer collaboration.

Usage:
    python examples/swarm/code_review_team.py
"""

import os
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()
console = Console()


# ============================================================================
# State Management
# ============================================================================

class SwarmState(TypedDict):
    """State passed between agents in the swarm."""
    messages: list
    current_agent: str
    handoff_count: int
    findings: dict
    code: str


# ============================================================================
# Handoff Tools (Each agent has specific handoff capabilities)
# ============================================================================

@tool
def handoff_to_security_expert(reason: str) -> str:
    """Handoff to security expert when security vulnerabilities found.

    Args:
        reason: Specific security concern that needs expert review
    """
    return f"HANDOFF:security_expert|REASON:{reason}"


@tool
def handoff_to_performance_expert(reason: str) -> str:
    """Handoff to performance expert when performance issues detected.

    Args:
        reason: Specific performance concern found
    """
    return f"HANDOFF:performance_expert|REASON:{reason}"


@tool
def handoff_to_test_expert(reason: str) -> str:
    """Handoff to test coverage expert for testing concerns.

    Args:
        reason: Testing issue that needs attention
    """
    return f"HANDOFF:test_expert|REASON:{reason}"


@tool
def handoff_to_doc_expert(reason: str) -> str:
    """Handoff to documentation expert for doc review.

    Args:
        reason: Documentation concern
    """
    return f"HANDOFF:doc_expert|REASON:{reason}"


@tool
def mark_review_complete(summary: str) -> str:
    """Mark code review as complete with summary.

    Args:
        summary: Final review summary
    """
    return f"COMPLETE|SUMMARY:{summary}"


# ============================================================================
# Agent Definitions
# ============================================================================

class CodeReviewerAgent:
    """General code reviewer - entry point for the swarm."""

    def __init__(self):
        self.name = "general_reviewer"
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )
        self.tools = [
            handoff_to_security_expert,
            handoff_to_performance_expert,
            handoff_to_test_expert,
            handoff_to_doc_expert,
            mark_review_complete
        ]
        self.system_message = """You are a general code reviewer in a code review swarm.

Your responsibilities:
- Initial code review for basic correctness, logic, and style
- Identify which specialists need to review specific aspects
- Coordinate overall review process

Handoff to specialists when you find:
- Security issues → handoff_to_security_expert()
- Performance problems → handoff_to_performance_expert()
- Testing gaps → handoff_to_test_expert()
- Documentation issues → handoff_to_doc_expert()

If no major issues found, mark_review_complete().

Be specific about WHY you're handing off.
"""

    def invoke(self, state: SwarmState) -> dict:
        """Execute general code review."""
        messages = [SystemMessage(content=self.system_message)] + state["messages"]

        # Add context about what we're reviewing
        context = f"\n\nCode to review:\n```\n{state['code']}\n```"
        messages.append(HumanMessage(content=context))

        response = self.llm.invoke(messages)
        return {
            "content": response.content,
            "next_action": self._parse_action(response.content)
        }

    def _parse_action(self, content: str):
        """Parse handoff or completion from response."""
        if "HANDOFF:" in content:
            parts = content.split("HANDOFF:")[1].split("|")
            agent = parts[0]
            reason = parts[1].replace("REASON:", "") if len(parts) > 1 else ""
            return {"type": "handoff", "agent": agent, "reason": reason}
        elif "COMPLETE" in content:
            return {"type": "complete"}
        return {"type": "continue"}


class SecurityExpertAgent:
    """Security specialist in the swarm."""

    def __init__(self):
        self.name = "security_expert"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.tools = [
            handoff_to_performance_expert,
            handoff_to_doc_expert,
            mark_review_complete
        ]
        self.system_message = """You are a security expert in a code review swarm.

Your expertise: OWASP Top 10, authentication, authorization, injection attacks, XSS, CSRF, etc.

Check for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Authentication/authorization issues
- Sensitive data exposure
- Insecure dependencies

After security review:
- If performance issues noticed → handoff_to_performance_expert()
- If docs need update → handoff_to_doc_expert()
- If all clear → mark_review_complete()

Provide specific, actionable security recommendations.
"""

    def invoke(self, state: SwarmState) -> dict:
        messages = [SystemMessage(content=self.system_message)] + state["messages"]
        response = self.llm.invoke(messages)

        # Record findings
        state["findings"]["security"] = response.content

        return {
            "content": response.content,
            "next_action": self._parse_action(response.content)
        }

    def _parse_action(self, content: str):
        if "HANDOFF:" in content:
            parts = content.split("HANDOFF:")[1].split("|")
            agent = parts[0]
            reason = parts[1].replace("REASON:", "") if len(parts) > 1 else ""
            return {"type": "handoff", "agent": agent, "reason": reason}
        elif "COMPLETE" in content:
            return {"type": "complete"}
        return {"type": "continue"}


class PerformanceExpertAgent:
    """Performance specialist in the swarm."""

    def __init__(self):
        self.name = "performance_expert"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.system_message = """You are a performance expert in a code review swarm.

Your expertise: Algorithm complexity, database queries, caching, memory usage.

Check for:
- O(n²) or worse algorithms that could be optimized
- N+1 query problems
- Missing indexes
- Inefficient loops
- Memory leaks
- Unnecessary computations

After performance review:
- If testing concerns → handoff_to_test_expert()
- If docs need update → handoff_to_doc_expert()
- If all clear → mark_review_complete()

Provide specific optimization suggestions with complexity analysis.
"""

    def invoke(self, state: SwarmState) -> dict:
        messages = [SystemMessage(content=self.system_message)] + state["messages"]
        response = self.llm.invoke(messages)

        state["findings"]["performance"] = response.content

        return {
            "content": response.content,
            "next_action": self._parse_action(response.content)
        }

    def _parse_action(self, content: str):
        if "HANDOFF:" in content:
            parts = content.split("HANDOFF:")[1].split("|")
            agent = parts[0]
            reason = parts[1].replace("REASON:", "") if len(parts) > 1 else ""
            return {"type": "handoff", "agent": agent, "reason": reason}
        elif "COMPLETE" in content:
            return {"type": "complete"}
        return {"type": "continue"}


# ============================================================================
# Swarm Orchestrator
# ============================================================================

class CodeReviewSwarm:
    """Orchestrates the code review swarm."""

    def __init__(self):
        self.agents = {
            "general_reviewer": CodeReviewerAgent(),
            "security_expert": SecurityExpertAgent(),
            "performance_expert": PerformanceExpertAgent(),
            # Add more specialists as needed
        }
        self.max_handoffs = 8

    def review(self, code: str) -> dict:
        """Run code review swarm."""
        state: SwarmState = {
            "messages": [HumanMessage(content="Please review this code.")],
            "current_agent": "general_reviewer",
            "handoff_count": 0,
            "findings": {},
            "code": code
        }

        console.print("\n[bold cyan]🔍 Starting Code Review Swarm[/bold cyan]\n")

        while state["handoff_count"] < self.max_handoffs:
            current_agent_name = state["current_agent"]
            current_agent = self.agents.get(current_agent_name)

            if not current_agent:
                console.print(f"[red]Error: Agent {current_agent_name} not found[/red]")
                break

            # Display current agent
            console.print(f"\n[yellow]👤 {current_agent.name}[/yellow]")

            # Execute agent
            try:
                result = current_agent.invoke(state)

                # Display result
                panel = Panel(
                    Markdown(result["content"]),
                    title=f"{current_agent.name}",
                    border_style="cyan"
                )
                console.print(panel)

                # Process next action
                action = result["next_action"]

                if action["type"] == "complete":
                    console.print("\n[bold green]✅ Code review complete![/bold green]")
                    return {
                        "status": "complete",
                        "findings": state["findings"],
                        "handoff_count": state["handoff_count"]
                    }

                elif action["type"] == "handoff":
                    next_agent = action["agent"]
                    reason = action.get("reason", "")

                    console.print(f"\n[magenta]🔄 Handoff to {next_agent}[/magenta]")
                    console.print(f"[dim]Reason: {reason}[/dim]")

                    # Update state for handoff
                    state["current_agent"] = next_agent
                    state["handoff_count"] += 1
                    state["messages"].append(AIMessage(
                        content=result["content"],
                        name=current_agent_name
                    ))

                    # Check for loops
                    if self._detect_loop(state):
                        console.print("[yellow]⚠️  Handoff loop detected, terminating[/yellow]")
                        return {
                            "status": "loop_detected",
                            "findings": state["findings"],
                            "handoff_count": state["handoff_count"]
                        }

            except Exception as e:
                console.print(f"[red]Error in {current_agent_name}: {e}[/red]")
                break

        console.print("\n[yellow]⚠️  Max handoffs reached[/yellow]")
        return {
            "status": "max_handoffs",
            "findings": state["findings"],
            "handoff_count": state["handoff_count"]
        }

    def _detect_loop(self, state: SwarmState) -> bool:
        """Detect if we're in a handoff loop."""
        # Simple loop detection: check if we've visited same agent 3+ times
        recent_messages = state["messages"][-6:]  # Last 6 messages
        agent_sequence = [msg.name for msg in recent_messages if hasattr(msg, 'name')]

        if len(agent_sequence) >= 4:
            # Check if pattern repeats
            if agent_sequence[-2:] == agent_sequence[-4:-2]:
                return True

        return False


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Sample code to review
    sample_code = '''
def get_user_data(user_id):
    """Fetch user data from database."""
    # Query database
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)

    # Get user posts
    posts = []
    for post_id in result.post_ids:
        post = db.execute(f"SELECT * FROM posts WHERE id = {post_id}")
        posts.append(post)

    return {
        "user": result,
        "posts": posts
    }
'''

    # Run code review
    swarm = CodeReviewSwarm()
    result = swarm.review(sample_code)

    # Display final summary
    console.print("\n" + "="*60)
    console.print("[bold]📊 Review Summary[/bold]")
    console.print(f"Status: {result['status']}")
    console.print(f"Handoffs: {result['handoff_count']}")
    console.print("\n[bold]Findings by Specialist:[/bold]")
    for agent, finding in result['findings'].items():
        console.print(f"\n[cyan]{agent}:[/cyan]")
        console.print(Markdown(finding))
