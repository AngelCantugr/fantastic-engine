"""
Parallel Pattern Example 1: Multi-Service Health Checker

Checks health of multiple services concurrently.
Demonstrates parallel execution with result aggregation.

Usage:
    python examples/parallel/health_checker.py
"""

import os
import asyncio
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
import time

load_dotenv()
console = Console()


# Sample service data
SERVICES = {
    "api": {
        "name": "API Gateway",
        "metrics": "CPU: 45%, Memory: 2.1GB/4GB, Requests: 1250/min, Latency: 85ms avg",
        "logs": "2 errors in last hour - timeout on /users endpoint"
    },
    "database": {
        "name": "PostgreSQL Database",
        "metrics": "Connections: 45/100, Query time: 12ms avg, Disk: 65% full",
        "logs": "Slow query detected on orders table"
    },
    "cache": {
        "name": "Redis Cache",
        "metrics": "Memory: 1.8GB/4GB, Hit rate: 92%, Evictions: 15/hour",
        "logs": "No errors in last 24 hours"
    },
    "queue": {
        "name": "Message Queue",
        "metrics": "Queue depth: 1250 messages, Processing: 50 msg/sec, DLQ: 3 messages",
        "logs": "3 messages failed processing - connection timeout"
    },
    "storage": {
        "name": "Object Storage",
        "metrics": "Storage used: 450GB/1TB, Upload rate: 2MB/s, Download rate: 8MB/s",
        "logs": "2 upload failures due to network issues"
    }
}


class ServiceHealthChecker:
    """Checks health of a single service."""

    def __init__(self, service_id: str, service_data: dict):
        self.service_id = service_id
        self.service_data = service_data
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    async def check_health(self) -> dict:
        """Asynchronously check service health."""
        # Simulate some processing time
        await asyncio.sleep(1)

        prompt = f"""Analyze the health of this service:

Service: {self.service_data['name']}
Metrics: {self.service_data['metrics']}
Recent Logs: {self.service_data['logs']}

Provide:
1. Overall status (HEALTHY, DEGRADED, or CRITICAL)
2. Key concerns (if any)
3. Recommended actions
4. Health score (0-100)

Be concise but specific.
"""
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        # Parse status and score
        content = response.content
        status = self._extract_status(content)
        score = self._extract_score(content)

        return {
            "service_id": self.service_id,
            "service_name": self.service_data['name'],
            "status": status,
            "score": score,
            "analysis": content
        }

    def _extract_status(self, content: str) -> str:
        """Extract status from analysis."""
        content_upper = content.upper()
        if "CRITICAL" in content_upper:
            return "CRITICAL"
        elif "DEGRADED" in content_upper:
            return "DEGRADED"
        else:
            return "HEALTHY"

    def _extract_score(self, content: str) -> int:
        """Extract health score."""
        import re
        match = re.search(r'(\d+)/100', content)
        if match:
            return int(match.group(1))

        # Default based on status
        content_upper = content.upper()
        if "CRITICAL" in content_upper:
            return 30
        elif "DEGRADED" in content_upper:
            return 60
        return 85


class ParallelHealthChecker:
    """Coordinates parallel health checks."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    async def check_all_services(self) -> dict:
        """Check all services in parallel."""
        console.print("\n[bold cyan]🏥 Multi-Service Health Check (Parallel)[/bold cyan]\n")

        # Create health checkers for each service
        checkers = [
            ServiceHealthChecker(service_id, service_data)
            for service_id, service_data in SERVICES.items()
        ]

        console.print(f"[yellow]Checking {len(checkers)} services in parallel...[/yellow]\n")

        start_time = time.time()

        # Run all checks concurrently
        with Progress() as progress:
            task = progress.add_task("[cyan]Checking services...", total=len(checkers))

            # Execute all health checks in parallel
            results = await asyncio.gather(*[
                checker.check_health() for checker in checkers
            ])

            progress.update(task, completed=len(checkers))

        elapsed = time.time() - start_time

        # Display individual results
        console.print("\n[bold]Individual Service Results:[/bold]\n")
        for result in results:
            status_color = {
                "HEALTHY": "green",
                "DEGRADED": "yellow",
                "CRITICAL": "red"
            }.get(result["status"], "white")

            panel = Panel(
                result["analysis"],
                title=f"{result['service_name']} - {result['status']} ({result['score']}/100)",
                border_style=status_color
            )
            console.print(panel)

        # Aggregate results
        console.print("\n[yellow]📊 Aggregating results...[/yellow]")
        summary = await self._aggregate_results(results)

        console.print("\n" + "="*60)
        console.print(Panel(
            summary,
            title="Overall System Health",
            border_style="cyan"
        ))

        # Metrics table
        table = Table(title="Health Summary")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Score", style="green")

        for result in sorted(results, key=lambda x: x["score"]):
            status_emoji = {
                "HEALTHY": "✅",
                "DEGRADED": "⚠️",
                "CRITICAL": "🔴"
            }.get(result["status"], "❓")

            table.add_row(
                result["service_name"],
                f"{status_emoji} {result['status']}",
                f"{result['score']}/100"
            )

        console.print(table)

        console.print(f"\n[dim]⚡ Completed in {elapsed:.2f}s (parallel execution)[/dim]")

        return {
            "results": results,
            "summary": summary,
            "elapsed_time": elapsed,
            "avg_score": sum(r["score"] for r in results) / len(results)
        }

    async def _aggregate_results(self, results: list) -> str:
        """Aggregate individual results into overall summary."""
        results_summary = "\n\n".join([
            f"**{r['service_name']}**: {r['status']} ({r['score']}/100)"
            for r in results
        ])

        prompt = f"""Based on these individual service health checks:

{results_summary}

Provide an overall system health summary including:
1. Overall system status
2. Most critical issues to address
3. Priority of actions
4. System-wide patterns or concerns

Be concise and actionable.
"""
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content


async def main():
    checker = ParallelHealthChecker()
    results = await checker.check_all_services()

    console.print("\n[bold green]✅ Health Check Complete![/bold green]")
    console.print(f"[cyan]Average Health Score:[/cyan] {results['avg_score']:.1f}/100")


if __name__ == "__main__":
    asyncio.run(main())
