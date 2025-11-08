"""
Reflection Pattern Example 1: Architecture Decision Review

Iteratively improve an Architecture Decision Record (ADR) through
critic feedback. Demonstrates quality improvement through reflection.

Usage:
    python examples/reflection/architecture_review.py
"""

import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

load_dotenv()
console = Console()


# ============================================================================
# Agents
# ============================================================================

class ADRWriterAgent:
    """Generates and improves Architecture Decision Records."""

    def __init__(self):
        self.name = "adr_writer"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.system_message = """You are an expert software architect writing Architecture Decision Records (ADRs).

An ADR should include:
1. Title: Short noun phrase
2. Context: What forces are at play (technical, political, social, project)
3. Decision: What we're doing (active voice: "We will...")
4. Consequences: Both positive and negative consequences
5. Alternatives Considered: What other options were evaluated

Write thorough, well-reasoned ADRs that document important architectural choices.
"""

    def write_initial(self, topic: str) -> str:
        """Write initial ADR draft."""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=f"Write an ADR for: {topic}")
        ]
        response = self.llm.invoke(messages)
        return response.content

    def improve(self, previous_adr: str, feedback: str) -> str:
        """Improve ADR based on feedback."""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=f"""
Your previous ADR:
{previous_adr}

Feedback from reviewer:
{feedback}

Please improve the ADR by addressing all feedback points.
For each criticism, explain what you changed and why.
""")
        ]
        response = self.llm.invoke(messages)
        return response.content


class ADRCriticAgent:
    """Reviews and critiques Architecture Decision Records."""

    def __init__(self):
        self.name = "adr_critic"
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.system_message = """You are a senior architect reviewing Architecture Decision Records.

Evaluate the ADR for:

1. **Completeness**:
   - Are all sections present and well-developed?
   - Is the context sufficiently detailed?
   - Are consequences (both positive and negative) listed?
   - Were alternatives properly considered?

2. **Clarity**:
   - Is the decision stated clearly and unambiguously?
   - Are technical terms explained?
   - Is the reasoning easy to follow?

3. **Reasoning**:
   - Are the trade-offs well-analyzed?
   - Is the decision justified by the context?
   - Are risks adequately addressed?

4. **Actionability**:
   - Is it clear what action should be taken?
   - Can engineers implement this decision?

Provide:
- What's done well (be specific)
- What needs improvement (be specific and actionable)
- Overall quality score (1-10)
- Whether this is ready to publish (yes/no)
"""

    def review(self, adr: str, iteration: int) -> dict:
        """Review an ADR and provide feedback."""
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=f"""
Review this ADR (iteration {iteration}):

{adr}

Provide structured feedback.
""")
        ]
        response = self.llm.invoke(messages)

        # Parse quality score and approval
        content = response.content
        quality_score = self._extract_score(content)
        ready = self._is_ready(content)

        return {
            "feedback": content,
            "quality_score": quality_score,
            "ready": ready
        }

    def _extract_score(self, content: str) -> float:
        """Extract quality score from feedback."""
        # Simple extraction - look for "score: X/10" or similar
        import re
        match = re.search(r'score[:\s]+(\d+(?:\.\d+)?)/10', content, re.IGNORECASE)
        if match:
            return float(match.group(1))

        match = re.search(r'(\d+(?:\.\d+)?)/10', content)
        if match:
            return float(match.group(1))

        return 7.0  # Default

    def _is_ready(self, content: str) -> bool:
        """Determine if ADR is ready to publish."""
        content_lower = content.lower()
        if "ready to publish: yes" in content_lower or "ready: yes" in content_lower:
            return True
        if "ready to publish: no" in content_lower or "ready: no" in content_lower:
            return False

        # Default: if score is mentioned as 8+, consider ready
        return "8/10" in content or "9/10" in content or "10/10" in content


# ============================================================================
# Reflection Loop
# ============================================================================

class ADRReflectionLoop:
    """Manages the iterative improvement of ADRs."""

    def __init__(self, max_iterations: int = 4, min_quality: float = 8.0):
        self.writer = ADRWriterAgent()
        self.critic = ADRCriticAgent()
        self.max_iterations = max_iterations
        self.min_quality = min_quality

    def reflect(self, topic: str) -> dict:
        """Run reflection loop to create high-quality ADR."""

        console.print("\n[bold cyan]🔄 Starting ADR Reflection Loop[/bold cyan]\n")
        console.print(f"[yellow]Topic:[/yellow] {topic}\n")

        iterations = []
        adr = None

        with Progress() as progress:
            task = progress.add_task("[cyan]Reflecting...", total=self.max_iterations)

            for i in range(self.max_iterations):
                iteration_num = i + 1

                console.print(f"\n[bold magenta]{'='*60}[/bold magenta]")
                console.print(f"[bold magenta]Iteration {iteration_num}[/bold magenta]")
                console.print(f"[bold magenta]{'='*60}[/bold magenta]\n")

                # Write or improve
                if i == 0:
                    console.print("[yellow]✍️  Writer: Creating initial ADR...[/yellow]")
                    adr = self.writer.write_initial(topic)
                else:
                    console.print(f"[yellow]✍️  Writer: Improving based on feedback...[/yellow]")
                    previous_feedback = iterations[-1]["review"]["feedback"]
                    adr = self.writer.improve(adr, previous_feedback)

                # Display current ADR
                panel = Panel(
                    Markdown(adr),
                    title=f"ADR Draft (v{iteration_num})",
                    border_style="cyan"
                )
                console.print(panel)

                # Critic reviews
                console.print("\n[yellow]🔍 Critic: Reviewing...[/yellow]")
                review = self.critic.review(adr, iteration_num)

                # Display review
                review_panel = Panel(
                    Markdown(review["feedback"]),
                    title=f"Critic Feedback (Quality: {review['quality_score']}/10)",
                    border_style="magenta"
                )
                console.print(review_panel)

                # Store iteration
                iterations.append({
                    "iteration": iteration_num,
                    "adr": adr,
                    "review": review
                })

                progress.update(task, advance=1)

                # Check termination conditions
                if review["ready"] and review["quality_score"] >= self.min_quality:
                    console.print("\n[bold green]✅ ADR meets quality standards![/bold green]")
                    break

                if iteration_num < self.max_iterations:
                    # Check for convergence
                    if self._has_converged(iterations):
                        console.print("\n[yellow]⚠️  ADR has converged (no significant changes)[/yellow]")
                        break
                else:
                    console.print("\n[yellow]⚠️  Max iterations reached[/yellow]")

        return {
            "final_adr": adr,
            "iterations": iterations,
            "quality_scores": [it["review"]["quality_score"] for it in iterations],
            "total_iterations": len(iterations)
        }

    def _has_converged(self, iterations: list) -> bool:
        """Check if quality has stopped improving."""
        if len(iterations) < 2:
            return False

        recent_scores = [it["review"]["quality_score"] for it in iterations[-2:]]

        # If improvement is less than 0.5 points, consider converged
        improvement = recent_scores[-1] - recent_scores[-2]
        return improvement < 0.5


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # ADR topic
    topic = """
    We need to decide on a state management solution for our React application.
    The app is growing complex with lots of shared state between components.
    Options include: Redux, Zustand, Recoil, MobX, or React Context + hooks.
    """

    # Run reflection loop
    reflection_loop = ADRReflectionLoop(max_iterations=4, min_quality=8.0)
    result = reflection_loop.reflect(topic)

    # Display final results
    console.print("\n" + "="*60)
    console.print("[bold]📊 Reflection Summary[/bold]\n")

    console.print(f"[cyan]Total Iterations:[/cyan] {result['total_iterations']}")
    console.print(f"[cyan]Quality Progression:[/cyan] {' → '.join(map(str, result['quality_scores']))}")

    final_score = result['quality_scores'][-1]
    improvement = final_score - result['quality_scores'][0]
    console.print(f"[cyan]Quality Improvement:[/cyan] +{improvement:.1f} points")

    console.print("\n[bold green]✅ Final ADR:[/bold green]")
    final_panel = Panel(
        Markdown(result["final_adr"]),
        title=f"Final ADR (Quality: {final_score}/10)",
        border_style="green",
        padding=(1, 2)
    )
    console.print(final_panel)

    # Quality improvement chart
    console.print("\n[bold]📈 Quality Progression:[/bold]")
    for i, score in enumerate(result['quality_scores'], 1):
        bar = "█" * int(score)
        console.print(f"Iteration {i}: [cyan]{bar}[/cyan] {score}/10")
