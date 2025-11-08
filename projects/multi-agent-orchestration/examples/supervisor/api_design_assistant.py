"""
Supervisor Pattern Example 1: API Design Assistant

A supervisor coordinates specialist agents to design a complete REST API.
Demonstrates centralized orchestration with clear hierarchy.

Usage:
    python examples/supervisor/api_design_assistant.py
"""

import os
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

load_dotenv()
console = Console()


# ============================================================================
# State Management
# ============================================================================

class APIDesignState(TypedDict):
    """State managed by supervisor."""
    messages: list
    requirement: str
    agent_results: dict
    completed_agents: list
    iteration: int


class AgentChoice(BaseModel):
    """Structured output for supervisor routing decision."""
    next_agent: Literal["requirements", "validator", "schema_designer", "security", "documenter", "FINISH"]
    reasoning: str = Field(description="Why this agent should act next")


# ============================================================================
# Specialized Sub-Agents
# ============================================================================

class RequirementsAgent:
    """Clarifies and documents API requirements."""

    def __init__(self):
        self.name = "requirements"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.system_message = """You are a requirements analyst for API design.

Your job:
1. Clarify functional requirements
2. Identify resources and operations needed
3. Determine authentication/authorization needs
4. List non-functional requirements (performance, scalability)

Provide clear, structured requirements that other specialists can use.
"""

    def invoke(self, state: APIDesignState) -> str:
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=f"Analyze requirements for: {state['requirement']}")
        ]
        response = self.llm.invoke(messages)
        return response.content


class RESTValidatorAgent:
    """Validates API design against REST principles."""

    def __init__(self):
        self.name = "validator"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.system_message = """You are a REST API validator.

Validate against REST principles:
- Resource-based URLs (nouns, not verbs)
- Proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Correct status codes
- Stateless communication
- HATEOAS where appropriate
- Proper use of headers

Review the requirements and provide validation feedback.
"""

    def invoke(self, state: APIDesignState) -> str:
        context = f"""
Requirement: {state['requirement']}

Requirements Analysis:
{state['agent_results'].get('requirements', 'Not yet analyzed')}

Validate this against REST principles.
"""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=context)
        ]
        response = self.llm.invoke(messages)
        return response.content


class SchemaDesignerAgent:
    """Designs detailed API schema and endpoints."""

    def __init__(self):
        self.name = "schema_designer"
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)  # Better model for complex design
        self.system_message = """You are an API schema designer.

Create detailed API design:
- Endpoint paths with HTTP methods
- Request/response schemas (JSON)
- Query parameters, path parameters, request bodies
- Response formats for success and errors
- Pagination strategy if needed
- Filtering and sorting options

Provide concrete, implementable schemas.
"""

    def invoke(self, state: APIDesignState) -> str:
        context = f"""
Requirement: {state['requirement']}

Requirements: {state['agent_results'].get('requirements', '')}
REST Validation: {state['agent_results'].get('validator', '')}

Design the complete API schema with all endpoints and data models.
"""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=context)
        ]
        response = self.llm.invoke(messages)
        return response.content


class SecurityReviewerAgent:
    """Reviews API design for security concerns."""

    def __init__(self):
        self.name = "security"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.system_message = """You are an API security reviewer.

Review for security:
- Authentication mechanism (JWT, OAuth, API keys)
- Authorization and access control
- Input validation requirements
- Rate limiting needs
- CORS configuration
- Sensitive data handling
- Security headers

Provide specific security recommendations.
"""

    def invoke(self, state: APIDesignState) -> str:
        context = f"""
Requirement: {state['requirement']}

API Schema:
{state['agent_results'].get('schema_designer', '')}

Review security aspects and provide recommendations.
"""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=context)
        ]
        response = self.llm.invoke(messages)
        return response.content


class DocumenterAgent:
    """Generates OpenAPI specification."""

    def __init__(self):
        self.name = "documenter"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.system_message = """You are an OpenAPI documentation specialist.

Generate OpenAPI 3.0 specification including:
- info section (title, version, description)
- servers
- paths with operations
- components (schemas, securitySchemes)
- security requirements
- tags

Create complete, valid OpenAPI YAML.
"""

    def invoke(self, state: APIDesignState) -> str:
        context = f"""
Based on all the work from the team, generate OpenAPI spec:

Requirements: {state['agent_results'].get('requirements', '')}
Schema Design: {state['agent_results'].get('schema_designer', '')}
Security Review: {state['agent_results'].get('security', '')}

Generate complete OpenAPI 3.0 YAML specification.
"""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=context)
        ]
        response = self.llm.invoke(messages)
        return response.content


# ============================================================================
# Supervisor Agent
# ============================================================================

class SupervisorAgent:
    """Coordinates the API design process."""

    def __init__(self):
        self.name = "supervisor"
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.system_message = """You are a supervisor coordinating API design specialists.

Your team:
- requirements: Analyzes and documents requirements
- validator: Validates against REST principles
- schema_designer: Creates detailed API schema
- security: Reviews security aspects
- documenter: Generates OpenAPI documentation

Workflow:
1. Start with requirements analyst
2. Then validator to check REST compliance
3. Schema designer creates detailed design
4. Security reviewer checks security
5. Documenter generates final OpenAPI spec
6. FINISH when all done

Choose the next agent or FINISH if complete.
"""

    def route(self, state: APIDesignState) -> AgentChoice:
        """Decide which agent should act next."""

        # Build context about what's been done
        completed = state["completed_agents"]
        context = f"""
Current state of API design:

Requirement: {state['requirement']}

Completed agents: {', '.join(completed) if completed else 'None yet'}

Agent results so far:
{self._format_results(state['agent_results'])}

Which agent should act next, or should we FINISH?
"""

        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=context)
        ]

        # Get structured output
        response = self.llm.with_structured_output(AgentChoice).invoke(messages)
        return response

    def _format_results(self, results: dict) -> str:
        """Format agent results for display."""
        if not results:
            return "No results yet"

        formatted = []
        for agent, result in results.items():
            formatted.append(f"\n{agent}:\n{result[:200]}...")  # First 200 chars

        return "\n".join(formatted)

    def synthesize(self, state: APIDesignState) -> str:
        """Create final synthesis of all agent work."""

        synthesis_prompt = f"""
You are synthesizing the complete API design from your team.

Create a comprehensive final summary including:
1. Overview of the API
2. Key design decisions
3. Endpoints summary
4. Security approach
5. Link to OpenAPI spec

Team Results:
{self._format_results(state['agent_results'])}

Create a clear, executive-friendly summary.
"""

        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=synthesis_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content


# ============================================================================
# Supervisor Orchestrator
# ============================================================================

class APIDesignSupervisor:
    """Orchestrates the API design workflow."""

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.agents = {
            "requirements": RequirementsAgent(),
            "validator": RESTValidatorAgent(),
            "schema_designer": SchemaDesignerAgent(),
            "security": SecurityReviewerAgent(),
            "documenter": DocumenterAgent()
        }
        self.max_iterations = 10

    def design_api(self, requirement: str) -> dict:
        """Run supervised API design process."""

        state: APIDesignState = {
            "messages": [],
            "requirement": requirement,
            "agent_results": {},
            "completed_agents": [],
            "iteration": 0
        }

        console.print("\n[bold cyan]🎯 Starting Supervised API Design[/bold cyan]\n")
        console.print(f"[yellow]Requirement:[/yellow] {requirement}\n")

        while state["iteration"] < self.max_iterations:
            # Supervisor decides next agent
            console.print(f"\n[dim]Iteration {state['iteration'] + 1}[/dim]")
            console.print("[magenta]👔 Supervisor thinking...[/magenta]")

            decision = self.supervisor.route(state)

            console.print(f"[cyan]Decision:[/cyan] {decision.next_agent}")
            console.print(f"[dim]Reasoning: {decision.reasoning}[/dim]\n")

            if decision.next_agent == "FINISH":
                console.print("[bold green]✅ Design complete! Synthesizing results...[/bold green]\n")
                final_summary = self.supervisor.synthesize(state)

                panel = Panel(
                    Markdown(final_summary),
                    title="Final API Design Summary",
                    border_style="green"
                )
                console.print(panel)

                return {
                    "status": "complete",
                    "summary": final_summary,
                    "agent_results": state["agent_results"],
                    "iterations": state["iteration"]
                }

            # Execute chosen agent
            agent_name = decision.next_agent
            agent = self.agents.get(agent_name)

            if not agent:
                console.print(f"[red]Error: Unknown agent {agent_name}[/red]")
                break

            console.print(f"[yellow]🤖 {agent.name} working...[/yellow]")

            try:
                result = agent.invoke(state)

                # Store result
                state["agent_results"][agent_name] = result
                state["completed_agents"].append(agent_name)

                # Display result
                panel = Panel(
                    Markdown(result),
                    title=f"{agent.name} - Complete",
                    border_style="cyan"
                )
                console.print(panel)

                state["iteration"] += 1

            except Exception as e:
                console.print(f"[red]Error in {agent_name}: {e}[/red]")
                break

        console.print("\n[yellow]⚠️  Max iterations reached[/yellow]")
        return {
            "status": "max_iterations",
            "agent_results": state["agent_results"],
            "iterations": state["iteration"]
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # API requirement
    requirement = """
    Design a REST API for a task management system. Users should be able to:
    - Create, read, update, and delete tasks
    - Assign tasks to users
    - Mark tasks as complete
    - Filter tasks by status, assignee, and due date
    - Tasks have: title, description, status, priority, due date, assignee
    """

    # Run supervised design
    supervisor = APIDesignSupervisor()
    result = supervisor.design_api(requirement)

    # Display metrics
    console.print("\n" + "="*60)
    table = Table(title="📊 Design Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Status", result["status"])
    table.add_row("Iterations", str(result["iterations"]))
    table.add_row("Agents Used", str(len(result["agent_results"])))

    console.print(table)
