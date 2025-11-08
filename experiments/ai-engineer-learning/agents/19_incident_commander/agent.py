#!/usr/bin/env python3
"""Agent 19: Incident Commander - Guide incident response and generate postmortems."""

import sys
from datetime import datetime
from typing import List, Dict
from langchain_ollama import OllamaLLM
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

class IncidentCommander:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def guide_incident(self, description: str) -> List[str]:
        """Generate incident response steps."""
        prompt = f"""Incident: {description}

As an SRE incident commander, provide:
1. Immediate actions to mitigate
2. Investigation steps
3. Communication plan
4. Recovery procedures

Format as numbered action items.
"""
        response = self.llm.invoke(prompt)
        return [line.strip() for line in response.split('\n') if line.strip() and line[0].isdigit()]

    def generate_postmortem(self, incident_data: Dict) -> str:
        """Generate postmortem document."""
        prompt = f"""Generate a blameless postmortem for this incident:

Incident: {incident_data.get('title')}
Duration: {incident_data.get('duration')}
Impact: {incident_data.get('impact')}
Timeline: {incident_data.get('timeline')}

Include:
1. Summary
2. Impact assessment
3. Root cause analysis
4. Timeline of events
5. Action items to prevent recurrence
6. What went well / What could be improved
"""
        return self.llm.invoke(prompt)

def interactive_mode():
    """Interactive incident response mode."""
    console.print(Panel.fit("[bold red]🚨 Incident Commander[/bold red]\n\nGuiding you through incident response"))

    description = Prompt.ask("\n[bold]Describe the incident[/bold]")

    commander = IncidentCommander()
    console.print("\n[cyan]Generating response plan...[/cyan]\n")

    steps = commander.guide_incident(description)

    for i, step in enumerate(steps, 1):
        console.print(f"[bold yellow]{i}.[/bold yellow] {step}")
        if Confirm.ask(f"\nCompleted step {i}?"):
            continue

    if Confirm.ask("\n[bold]Generate postmortem?[/bold]"):
        incident_data = {
            'title': description,
            'duration': Prompt.ask("Incident duration"),
            'impact': Prompt.ask("Impact description"),
            'timeline': "Interactive session - manual timeline"
        }
        postmortem = commander.generate_postmortem(incident_data)
        console.print(Panel(postmortem, title="Postmortem", border_style="green"))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Incident Commander")
    parser.add_argument("--incident", help="Incident description")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--postmortem", type=str, help="Generate postmortem (provide JSON)")
    args = parser.parse_args()

    if args.interactive or not (args.incident or args.postmortem):
        interactive_mode()
    elif args.incident:
        commander = IncidentCommander()
        steps = commander.guide_incident(args.incident)
        for i, step in enumerate(steps, 1):
            console.print(f"{i}. {step}")

if __name__ == "__main__":
    main()
