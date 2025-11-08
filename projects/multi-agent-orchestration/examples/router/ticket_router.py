"""
Router Pattern Example 1: Support Ticket Router

Routes support tickets to appropriate specialist teams.
Demonstrates simple classification and delegation.

Usage:
    python examples/router/ticket_router.py
"""

import os
from typing import Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()


class RouteDecision(BaseModel):
    """Structured routing decision."""
    team: Literal["billing", "technical", "account", "sales"]
    priority: Literal["low", "medium", "high", "critical"]
    reasoning: str = Field(description="Why this team and priority")


class RouterAgent:
    """Routes tickets to appropriate teams."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    def route(self, ticket: str) -> RouteDecision:
        prompt = f"""Route this support ticket to the appropriate team:

Ticket: {ticket}

Teams:
- billing: Payment issues, invoices, subscriptions
- technical: Bugs, errors, performance issues
- account: Login, password, account settings
- sales: Pricing, upgrades, features

Also assess priority: low, medium, high, or critical
"""
        response = self.llm.with_structured_output(RouteDecision).invoke([
            HumanMessage(content=prompt)
        ])
        return response


class BillingTeamAgent:
    """Handles billing inquiries."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    def handle(self, ticket: str) -> str:
        prompt = f"""You are the billing support team. Handle this ticket:

{ticket}

Provide:
- What you'll investigate
- What information you need from customer
- Expected resolution time
"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


class TechnicalTeamAgent:
    """Handles technical issues."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    def handle(self, ticket: str) -> str:
        prompt = f"""You are the technical support team. Handle this ticket:

{ticket}

Provide:
- Initial diagnosis
- Debugging steps
- Possible workarounds
- Escalation if needed
"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


class SupportTicketRouter:
    """Routes and handles support tickets."""

    def __init__(self):
        self.router = RouterAgent()
        self.teams = {
            "billing": BillingTeamAgent(),
            "technical": TechnicalTeamAgent(),
            # Add other teams as needed
        }

    def process_ticket(self, ticket: str) -> dict:
        console.print("\n[bold cyan]🎫 Ticket Routing System[/bold cyan]\n")

        console.print(Panel(ticket, title="Incoming Ticket", border_style="yellow"))

        # Route ticket
        console.print("\n[yellow]🔀 Routing ticket...[/yellow]")
        route = self.router.route(ticket)

        # Display routing decision
        table = Table(title="Routing Decision")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_row("Team", route.team.upper())
        table.add_row("Priority", route.priority.upper())
        table.add_row("Reasoning", route.reasoning)
        console.print(table)

        # Handle by appropriate team
        team = self.teams.get(route.team)
        if team:
            console.print(f"\n[yellow]👥 {route.team.title()} Team handling...[/yellow]")
            response = team.handle(ticket)

            console.print(Panel(
                response,
                title=f"{route.team.title()} Team Response",
                border_style="green"
            ))

            return {
                "routing": {
                    "team": route.team,
                    "priority": route.priority,
                    "reasoning": route.reasoning
                },
                "response": response
            }
        else:
            console.print(f"[red]Team {route.team} not available[/red]")
            return {"error": f"Team {route.team} not found"}


if __name__ == "__main__":
    tickets = [
        "My payment failed last night and now I can't access my account. I need this fixed ASAP!",
        "The dashboard is loading extremely slowly and sometimes times out. This started after yesterday's update.",
        "I forgot my password and the reset email isn't arriving. Can you help?"
    ]

    router = SupportTicketRouter()

    for i, ticket in enumerate(tickets, 1):
        console.print(f"\n{'='*60}")
        console.print(f"[bold]Ticket {i}[/bold]")
        console.print(f"{'='*60}")
        router.process_ticket(ticket)
