#!/usr/bin/env python3
"""
LeetCode Session Analyzer

Track and analyze your LeetCode practice sessions for insights and progress monitoring.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import plotext as plt
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

console = Console()
Base = declarative_base()


class ProblemAttempt(Base):
    """Database model for problem attempts"""
    __tablename__ = "problem_attempts"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    problem_id = Column(Integer, nullable=False)
    problem_title = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    pattern = Column(String, nullable=True)
    time_spent = Column(Integer, nullable=False)  # minutes
    success = Column(Boolean, nullable=False)
    attempts = Column(Integer, default=1)
    hints_used = Column(Integer, default=0)
    notes = Column(String, nullable=True)


class SessionAnalyzer:
    """Main analyzer class"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "sessions.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def log_problem(
        self,
        problem_id: int,
        title: str,
        difficulty: str,
        pattern: str,
        time_spent: int,
        success: bool,
        attempts: int = 1,
        hints_used: int = 0,
        notes: str = ""
    ):
        """Log a problem attempt"""
        attempt = ProblemAttempt(
            problem_id=problem_id,
            problem_title=title,
            difficulty=difficulty,
            pattern=pattern,
            time_spent=time_spent,
            success=success,
            attempts=attempts,
            hints_used=hints_used,
            notes=notes
        )
        self.session.add(attempt)
        self.session.commit()

        console.print(f"[green]✓ Logged: {title} ({difficulty})[/green]")

    def show_dashboard(self, days: int = 7):
        """Display analytics dashboard"""
        console.print()
        console.print(Panel.fit(
            f"📈 [bold cyan]LeetCode Session Analyzer[/bold cyan]\n"
            f"Last {days} Days",
            border_style="cyan"
        ))

        # Calculate statistics
        cutoff = datetime.now() - timedelta(days=days)
        recent = self.session.query(ProblemAttempt).filter(
            ProblemAttempt.timestamp >= cutoff
        ).all()

        if not recent:
            console.print("\n[yellow]No sessions found in this period[/yellow]\n")
            return

        total = len(recent)
        success = sum(1 for a in recent if a.success)
        success_rate = (success / total * 100) if total > 0 else 0
        total_time = sum(a.time_spent for a in recent)

        console.print(f"\n📊 [bold]SUMMARY[/bold]")
        console.print(f"  Total Sessions: {total}")
        console.print(f"  Success Rate: {success_rate:.1f}%")
        console.print(f"  Total Time: {total_time}m ({total_time/60:.1f}h)")
        console.print()


@click.command()
@click.option("--init", is_flag=True, help="Initialize database")
@click.option("--log", is_flag=True, help="Log a problem attempt")
@click.option("--dashboard", is_flag=True, help="Show dashboard")
@click.option("--days", default=7, help="Number of days for analysis")
def main(init, log, dashboard, days):
    """LeetCode Session Analyzer"""

    analyzer = SessionAnalyzer()

    if init:
        console.print("[green]✓ Database initialized[/green]")
        return

    if log:
        # Interactive logging
        problem_id = click.prompt("Problem ID", type=int)
        title = click.prompt("Problem title")
        difficulty = click.prompt("Difficulty", type=click.Choice(["Easy", "Medium", "Hard"]))
        pattern = click.prompt("Pattern (optional)", default="")
        time_spent = click.prompt("Time spent (minutes)", type=int)
        success = click.confirm("Success?")

        analyzer.log_problem(problem_id, title, difficulty, pattern, time_spent, success)
        return

    if dashboard:
        analyzer.show_dashboard(days)
        return

    console.print("[yellow]Use --help to see available commands[/yellow]")


if __name__ == "__main__":
    main()
