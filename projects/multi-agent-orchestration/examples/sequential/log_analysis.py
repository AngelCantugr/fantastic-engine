"""
Sequential Pattern Example 1: Log Analysis Pipeline

A linear pipeline of agents that process logs step by step.
Demonstrates simple sequential processing.

Usage:
    python examples/sequential/log_analysis.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()
console = Console()


# Sample log data
SAMPLE_LOGS = """
2024-11-08 10:15:23 INFO [UserService] User 12345 logged in
2024-11-08 10:15:45 ERROR [PaymentService] Payment processing failed for order #5678 - timeout
2024-11-08 10:16:12 WARN [DatabasePool] Connection pool at 85% capacity
2024-11-08 10:16:23 ERROR [PaymentService] Payment processing failed for order #5679 - network error
2024-11-08 10:17:01 INFO [OrderService] Order #5680 created successfully
2024-11-08 10:18:30 ERROR [AuthService] Invalid token for user 98765
2024-11-08 10:19:15 ERROR [PaymentService] Payment processing failed for order #5681 - timeout
2024-11-08 10:20:00 CRITICAL [DatabasePool] Connection pool exhausted - cannot accept new connections
2024-11-08 10:20:30 ERROR [OrderService] Failed to create order #5682 - database unavailable
"""


class LogParserAgent:
    """Parses raw logs into structured format."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    def parse(self, logs: str) -> str:
        prompt = f"""Parse these logs into structured format:

{logs}

Extract for each log entry:
- Timestamp
- Level (INFO, WARN, ERROR, CRITICAL)
- Service
- Message

Return as markdown table.
"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


class ErrorExtractorAgent:
    """Extracts and categorizes errors."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    def extract(self, parsed_logs: str) -> str:
        prompt = f"""From these parsed logs, extract all ERROR and CRITICAL entries:

{parsed_logs}

Group by:
- Service
- Error type
- Count

Identify the most critical issues.
"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


class PatternAnalyzerAgent:
    """Analyzes patterns in errors."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    def analyze(self, errors: str) -> str:
        prompt = f"""Analyze these errors for patterns:

{errors}

Look for:
- Repeated failures
- Cascading failures
- Time-based patterns
- Service dependencies

Identify root causes and relationships between errors.
"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


class AlertGeneratorAgent:
    """Generates alerts and recommendations."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

    def generate_alerts(self, analysis: str) -> str:
        prompt = f"""Based on this error analysis:

{analysis}

Generate:
1. Priority alerts (CRITICAL, HIGH, MEDIUM)
2. Recommended actions for each
3. Services that need immediate attention
4. Suggested monitoring improvements

Format as actionable alert report.
"""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


class LogAnalysisPipeline:
    """Sequential pipeline for log analysis."""

    def __init__(self):
        self.parser = LogParserAgent()
        self.extractor = ErrorExtractorAgent()
        self.analyzer = PatternAnalyzerAgent()
        self.alerter = AlertGeneratorAgent()

    def analyze(self, raw_logs: str) -> dict:
        console.print("\n[bold cyan]📊 Log Analysis Pipeline (Sequential)[/bold cyan]\n")

        results = {}

        # Step 1: Parse
        console.print("[yellow]Step 1/4:[/yellow] Parsing logs...")
        parsed = self.parser.parse(raw_logs)
        results["parsed"] = parsed
        console.print(Panel(Markdown(parsed), title="Parsed Logs", border_style="cyan"))

        # Step 2: Extract errors
        console.print("\n[yellow]Step 2/4:[/yellow] Extracting errors...")
        errors = self.extractor.extract(parsed)
        results["errors"] = errors
        console.print(Panel(Markdown(errors), title="Extracted Errors", border_style="yellow"))

        # Step 3: Analyze patterns
        console.print("\n[yellow]Step 3/4:[/yellow] Analyzing patterns...")
        analysis = self.analyzer.analyze(errors)
        results["analysis"] = analysis
        console.print(Panel(Markdown(analysis), title="Pattern Analysis", border_style="magenta"))

        # Step 4: Generate alerts
        console.print("\n[yellow]Step 4/4:[/yellow] Generating alerts...")
        alerts = self.alerter.generate_alerts(analysis)
        results["alerts"] = alerts
        console.print(Panel(Markdown(alerts), title="Alerts & Recommendations", border_style="red"))

        return results


if __name__ == "__main__":
    pipeline = LogAnalysisPipeline()
    results = pipeline.analyze(SAMPLE_LOGS)

    console.print("\n[bold green]✅ Pipeline Complete![/bold green]")
