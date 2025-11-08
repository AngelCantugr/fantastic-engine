#!/usr/bin/env python3
"""
Agent 8: Architecture Advisor
==============================

Learning Objectives:
- Build multi-agent systems with CrewAI
- Implement role-based collaboration
- Coordinate multiple specialists
- Generate comprehensive architecture docs

Complexity: ⭐⭐⭐⭐⭐ Advanced
Framework: crewai
"""

import sys

try:
    from crewai import Agent, Task, Crew, Process
    from langchain_ollama import ChatOllama
except ImportError:
    print("Error: crewai not installed. Run: pip install crewai crewai-tools")
    sys.exit(1)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class ArchitectureAdvisor:
    """
    Multi-agent architecture advisor using CrewAI.

    Demonstrates:
    1. Multi-agent coordination
    2. Role specialization
    3. Collaborative problem solving
    4. Task delegation
    """

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = ChatOllama(model=model, base_url="http://localhost:11434")

        # Define specialized agents
        self.architect = Agent(
            role="Software Architect",
            goal="Design scalable, maintainable system architectures",
            backstory="You are a senior software architect with 15+ years experience "
                     "designing distributed systems. You excel at high-level design and "
                     "making technology decisions.",
            llm=self.llm,
            verbose=True
        )

        self.security_expert = Agent(
            role="Security Engineer",
            goal="Ensure system security and identify vulnerabilities",
            backstory="You are a security expert specializing in application security, "
                     "authentication, and data protection. You think like an attacker.",
            llm=self.llm,
            verbose=True
        )

        self.performance_engineer = Agent(
            role="Performance Engineer",
            goal="Optimize system performance and scalability",
            backstory="You specialize in high-performance systems, caching strategies, "
                     "and database optimization. You always consider scalability.",
            llm=self.llm,
            verbose=True
        )

        self.devops_engineer = Agent(
            role="DevOps Engineer",
            goal="Design deployment and infrastructure strategy",
            backstory="You are a DevOps expert focused on CI/CD, containerization, "
                     "and cloud infrastructure. You ensure systems are deployable.",
            llm=self.llm,
            verbose=True
        )

    def advise(self, project_description: str, constraints: dict = None) -> str:
        """
        Get architecture advice from the team of agents.

        Args:
            project_description: Description of the project
            constraints: Optional constraints (users, budget, timeline)

        Returns:
            Comprehensive architecture recommendation
        """
        constraints_str = ""
        if constraints:
            constraints_str = f"\n\nConstraints:\n{self._format_constraints(constraints)}"

        # Define tasks for each agent
        architecture_task = Task(
            description=f"""Design a high-level architecture for this project:

{project_description}{constraints_str}

Provide:
1. System components and their responsibilities
2. Technology stack recommendations
3. Data flow and communication patterns
4. Scalability approach
""",
            agent=self.architect,
            expected_output="Detailed architecture design with component diagram"
        )

        security_task = Task(
            description=f"""Review the architecture for security:

{project_description}{constraints_str}

Provide:
1. Security risks and concerns
2. Authentication/authorization strategy
3. Data protection recommendations
4. Security best practices to follow
""",
            agent=self.security_expert,
            expected_output="Security analysis and recommendations"
        )

        performance_task = Task(
            description=f"""Analyze performance and scalability:

{project_description}{constraints_str}

Provide:
1. Performance bottleneck predictions
2. Caching strategy
3. Database optimization approaches
4. Scalability plan
""",
            agent=self.performance_engineer,
            expected_output="Performance analysis and optimization plan"
        )

        devops_task = Task(
            description=f"""Design deployment and infrastructure:

{project_description}{constraints_str}

Provide:
1. Deployment strategy
2. CI/CD pipeline design
3. Infrastructure recommendations
4. Monitoring and logging approach
""",
            agent=self.devops_engineer,
            expected_output="DevOps and infrastructure plan"
        )

        # Create crew
        crew = Crew(
            agents=[self.architect, self.security_expert,
                   self.performance_engineer, self.devops_engineer],
            tasks=[architecture_task, security_task,
                  performance_task, devops_task],
            process=Process.sequential,
            verbose=True
        )

        # Execute
        console.print("\n[cyan]Consulting the architecture team...[/cyan]\n")
        result = crew.kickoff()

        return str(result)

    def _format_constraints(self, constraints: dict) -> str:
        """Format constraints for prompt."""
        lines = []
        for key, value in constraints.items():
            lines.append(f"- {key.title()}: {value}")
        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Architecture Advisor")
    parser.add_argument("--project", required=True, help="Project description")
    parser.add_argument("--users", type=int, help="Expected number of users")
    parser.add_argument("--budget", choices=["low", "medium", "high"], help="Budget constraint")
    parser.add_argument("--timeline", help="Timeline constraint")
    parser.add_argument("--model", default="qwen2.5-coder:7b")

    args = parser.parse_args()

    try:
        advisor = ArchitectureAdvisor(model=args.model)

        console.print(Panel.fit(
            "[bold cyan]Architecture Advisor[/bold cyan]\n\n"
            f"Project: [yellow]{args.project}[/yellow]"
        ))

        # Build constraints
        constraints = {}
        if args.users:
            constraints["expected users"] = f"{args.users:,}"
        if args.budget:
            constraints["budget"] = args.budget
        if args.timeline:
            constraints["timeline"] = args.timeline

        # Get advice
        advice = advisor.advise(args.project, constraints if constraints else None)

        # Display
        console.print("\n" + "="*60)
        console.print(Panel(
            Markdown(advice),
            title="[bold green]Architecture Recommendations[/bold green]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
