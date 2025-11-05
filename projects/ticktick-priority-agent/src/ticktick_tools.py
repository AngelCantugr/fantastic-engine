"""
LangChain Tools for TickTick Integration

This module creates LangChain tools that wrap our TickTick API client.
These tools can be used by LangChain agents to interact with TickTick.

Learning Note: Tools are how we give LLMs the ability to take actions!
The LLM reads the tool description and decides when to use each tool.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta

from langchain.tools import Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field
from rich.console import Console
from rich.table import Table

from api_client import TickTickClient

console = Console()


class FetchTasksInput(BaseModel):
    """Input schema for fetch_tasks tool."""
    project_id: Optional[str] = Field(
        None,
        description="Optional project ID to filter tasks. If not provided, fetches all tasks."
    )


class AnalyzeTaskInput(BaseModel):
    """Input schema for analyze_task tool."""
    task_id: str = Field(
        description="ID of the task to analyze"
    )


class TickTickTools:
    """
    Collection of LangChain tools for TickTick operations.

    These tools allow an AI agent to:
    1. Fetch tasks from TickTick
    2. Analyze individual tasks
    3. Get task statistics
    4. Format task information

    Learning Note: Each tool needs:
    - Clear name (agent uses this to decide which tool)
    - Detailed description (agent reads this to understand purpose)
    - Input schema (what parameters does it need?)
    - Function implementation (what does it actually do?)
    """

    def __init__(self, client: TickTickClient):
        """
        Initialize tools with a TickTick client.

        Args:
            client: Authenticated TickTickClient instance
        """
        self.client = client
        self._tasks_cache: List[Dict] = []
        self._cache_time: Optional[datetime] = None

    def _get_cached_tasks(self, max_age_seconds: int = 300) -> List[Dict]:
        """
        Get tasks from cache or fetch fresh if cache is old.

        Args:
            max_age_seconds: Maximum age of cache in seconds (default 5 minutes)

        Returns:
            List of tasks

        Learning Note: Caching reduces API calls and improves performance!
        This is especially important with rate-limited APIs.
        """
        now = datetime.now()

        # Check if cache is fresh
        if self._cache_time and self._tasks_cache:
            age = (now - self._cache_time).total_seconds()
            if age < max_age_seconds:
                console.print(f"📦 Using cached tasks ({age:.0f}s old)")
                return self._tasks_cache

        # Fetch fresh tasks
        self._tasks_cache = self.client.get_tasks()
        self._cache_time = now
        return self._tasks_cache

    def fetch_tasks_tool(self, project_id: Optional[str] = None) -> str:
        """
        Fetch tasks from TickTick.

        This tool retrieves all tasks (or tasks from a specific project)
        and returns them in a formatted, readable way for the agent.

        Args:
            project_id: Optional project ID to filter tasks

        Returns:
            Formatted string with task information

        Learning Note: The return value should be text that the LLM can
        understand and reason about. We format it clearly with structure.
        """
        console.print("🔧 [dim]Tool: fetch_tasks[/dim]")

        try:
            tasks = self._get_cached_tasks()

            if not tasks:
                return "No tasks found in TickTick."

            # Filter by project if specified
            if project_id:
                tasks = [t for t in tasks if t.get("projectId") == project_id]

            # Format tasks for the agent
            task_list = []
            for task in tasks:
                task_info = self._format_task(task)
                task_list.append(task_info)

            result = f"Found {len(tasks)} tasks:\n\n"
            result += "\n\n".join(task_list)

            return result

        except Exception as e:
            return f"Error fetching tasks: {str(e)}"

    def _format_task(self, task: Dict) -> str:
        """
        Format a single task for readability.

        Args:
            task: Task dictionary from TickTick API

        Returns:
            Formatted string representation of the task
        """
        lines = []

        # Basic info
        title = task.get("title", "Untitled")
        task_id = task.get("id", "unknown")
        lines.append(f"**{title}** (ID: {task_id})")

        # Description
        content = task.get("content", "")
        if content:
            lines.append(f"  Description: {content}")

        # Priority (0=None, 1=Low, 3=Medium, 5=High)
        priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
        priority = task.get("priority", 0)
        lines.append(f"  Priority: {priority_map.get(priority, 'Unknown')}")

        # Due date
        due_date = task.get("dueDate")
        if due_date:
            # Parse and format due date
            try:
                due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                now = datetime.now(due_dt.tzinfo)
                delta = due_dt - now

                if delta.days < 0:
                    time_str = f"OVERDUE by {abs(delta.days)} days"
                elif delta.days == 0:
                    time_str = "Due TODAY"
                elif delta.days == 1:
                    time_str = "Due TOMORROW"
                else:
                    time_str = f"Due in {delta.days} days"

                lines.append(f"  Due: {due_dt.strftime('%Y-%m-%d %H:%M')} ({time_str})")
            except:
                lines.append(f"  Due: {due_date}")

        # Tags
        tags = task.get("tags", [])
        if tags:
            lines.append(f"  Tags: {', '.join(tags)}")

        # Status
        status = "Complete" if task.get("status") == 2 else "Incomplete"
        lines.append(f"  Status: {status}")

        return "\n".join(lines)

    def analyze_task_tool(self, task_id: str) -> str:
        """
        Analyze a specific task in detail.

        This provides deeper analysis of a single task, including
        urgency factors, complexity estimates, and recommendations.

        Args:
            task_id: ID of task to analyze

        Returns:
            Detailed analysis of the task
        """
        console.print(f"🔧 [dim]Tool: analyze_task ({task_id})[/dim]")

        try:
            tasks = self._get_cached_tasks()
            task = next((t for t in tasks if t.get("id") == task_id), None)

            if not task:
                return f"Task with ID {task_id} not found."

            # Perform analysis
            analysis = []
            analysis.append(f"## Analysis of: {task.get('title', 'Untitled')}\n")

            # Urgency analysis
            urgency_score, urgency_reason = self._calculate_urgency(task)
            analysis.append(f"**Urgency Score:** {urgency_score}/10")
            analysis.append(f"**Reason:** {urgency_reason}\n")

            # Importance analysis
            importance_score = self._calculate_importance(task)
            analysis.append(f"**Importance Score:** {importance_score}/10\n")

            # Complexity estimate
            complexity = self._estimate_complexity(task)
            analysis.append(f"**Estimated Complexity:** {complexity}\n")

            # Overall priority score
            priority_score = (urgency_score * 0.5) + (importance_score * 0.3) + (3 if complexity == "Low" else 0) * 0.2
            analysis.append(f"**Overall Priority Score:** {priority_score:.1f}/10\n")

            # Recommendations
            recommendations = self._generate_recommendations(task, urgency_score, importance_score, complexity)
            analysis.append("**Recommendations:**")
            for rec in recommendations:
                analysis.append(f"  • {rec}")

            return "\n".join(analysis)

        except Exception as e:
            return f"Error analyzing task: {str(e)}"

    def _calculate_urgency(self, task: Dict) -> tuple[float, str]:
        """
        Calculate urgency score based on due date.

        Returns:
            Tuple of (score, reason)
        """
        due_date = task.get("dueDate")

        if not due_date:
            return 3.0, "No due date set - moderate urgency"

        try:
            due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            now = datetime.now(due_dt.tzinfo)
            delta = due_dt - now
            days = delta.days

            if days < 0:
                return 10.0, f"OVERDUE by {abs(days)} days - URGENT!"
            elif days == 0:
                return 9.0, "Due TODAY - very urgent"
            elif days == 1:
                return 8.0, "Due TOMORROW - urgent"
            elif days <= 3:
                return 7.0, f"Due in {days} days - approaching deadline"
            elif days <= 7:
                return 5.0, f"Due in {days} days - plan soon"
            elif days <= 14:
                return 3.0, f"Due in {days} days - on radar"
            else:
                return 2.0, f"Due in {days} days - low urgency"

        except:
            return 3.0, "Could not parse due date"

    def _calculate_importance(self, task: Dict) -> float:
        """
        Calculate importance score based on priority and tags.

        Returns:
            Importance score (0-10)
        """
        # Base importance from TickTick priority
        priority = task.get("priority", 0)
        importance_map = {0: 5.0, 1: 3.0, 3: 7.0, 5: 10.0}
        score = importance_map.get(priority, 5.0)

        # Boost for certain tags
        tags = task.get("tags", [])
        important_tags = ["urgent", "important", "critical", "asap"]

        for tag in tags:
            if tag.lower() in important_tags:
                score = min(10.0, score + 2.0)

        return score

    def _estimate_complexity(self, task: Dict) -> str:
        """
        Estimate task complexity based on description length and tags.

        Returns:
            Complexity level: "Low", "Medium", or "High"
        """
        content = task.get("content", "")
        title = task.get("title", "")

        # Simple heuristic based on description length
        total_length = len(content) + len(title)

        if total_length < 50:
            return "Low"
        elif total_length < 150:
            return "Medium"
        else:
            return "High"

    def _generate_recommendations(
        self,
        task: Dict,
        urgency: float,
        importance: float,
        complexity: str
    ) -> List[str]:
        """
        Generate actionable recommendations for a task.

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Urgency-based recommendations
        if urgency >= 9:
            recommendations.append("🚨 DO THIS NOW - highest priority")
        elif urgency >= 7:
            recommendations.append("⏰ Schedule for today if possible")
        elif urgency >= 5:
            recommendations.append("📅 Plan for this week")

        # Importance + urgency combination
        if importance >= 7 and urgency >= 7:
            recommendations.append("⭐ Eisenhower Matrix: Urgent + Important - do first")
        elif importance >= 7 and urgency < 5:
            recommendations.append("📋 Eisenhower Matrix: Important, not urgent - schedule time")
        elif importance < 5 and urgency >= 7:
            recommendations.append("🤝 Eisenhower Matrix: Urgent, not important - consider delegating")

        # Complexity-based recommendations
        if complexity == "Low":
            recommendations.append("✨ Quick win - good for low-energy moments")
        elif complexity == "High":
            recommendations.append("🧩 Complex task - break into smaller subtasks")

        return recommendations

    def get_task_statistics_tool(self) -> str:
        """
        Get overall statistics about tasks.

        Returns:
            Formatted statistics string
        """
        console.print("🔧 [dim]Tool: get_task_statistics[/dim]")

        try:
            tasks = self._get_cached_tasks()

            if not tasks:
                return "No tasks found."

            # Calculate statistics
            total = len(tasks)
            complete = sum(1 for t in tasks if t.get("status") == 2)
            incomplete = total - complete

            # Count by priority
            priority_counts = {0: 0, 1: 0, 3: 0, 5: 0}
            for task in tasks:
                priority = task.get("priority", 0)
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

            # Count overdue
            overdue = 0
            due_today = 0
            for task in tasks:
                due_date = task.get("dueDate")
                if due_date and task.get("status") != 2:
                    try:
                        due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                        now = datetime.now(due_dt.tzinfo)
                        if due_dt < now:
                            overdue += 1
                        elif due_dt.date() == now.date():
                            due_today += 1
                    except:
                        pass

            # Format output
            stats = []
            stats.append("## Task Statistics\n")
            stats.append(f"**Total Tasks:** {total}")
            stats.append(f"**Complete:** {complete}")
            stats.append(f"**Incomplete:** {incomplete}\n")

            stats.append("**Priority Breakdown:**")
            stats.append(f"  • None: {priority_counts[0]}")
            stats.append(f"  • Low: {priority_counts[1]}")
            stats.append(f"  • Medium: {priority_counts[3]}")
            stats.append(f"  • High: {priority_counts[5]}\n")

            stats.append("**Urgency:**")
            stats.append(f"  • Overdue: {overdue}")
            stats.append(f"  • Due Today: {due_today}")

            return "\n".join(stats)

        except Exception as e:
            return f"Error getting statistics: {str(e)}"

    def get_langchain_tools(self) -> List[Tool]:
        """
        Convert methods to LangChain tools.

        Returns:
            List of LangChain Tool objects that can be used by agents

        Learning Note: This is where we connect our Python functions
        to LangChain. The descriptions here are CRITICAL - they tell
        the agent when and how to use each tool!
        """
        tools = [
            Tool(
                name="fetch_tasks",
                func=lambda x: self.fetch_tasks_tool(),
                description=(
                    "Fetch all tasks from TickTick. "
                    "Use this to see what tasks the user has. "
                    "Returns a formatted list of tasks with their details. "
                    "Input: empty string or project_id"
                )
            ),
            Tool(
                name="analyze_task",
                func=self.analyze_task_tool,
                description=(
                    "Analyze a specific task in detail. "
                    "Provides urgency score, importance, complexity, and recommendations. "
                    "Use this when you need detailed analysis of a particular task. "
                    "Input: task_id (string)"
                )
            ),
            Tool(
                name="get_statistics",
                func=lambda x: self.get_task_statistics_tool(),
                description=(
                    "Get overall statistics about tasks. "
                    "Shows total tasks, completion status, priority breakdown, etc. "
                    "Use this for a high-level overview. "
                    "Input: empty string"
                )
            ),
        ]

        return tools


def create_tools_from_env() -> TickTickTools:
    """
    Create TickTick tools using environment variables.

    Returns:
        Configured TickTickTools instance
    """
    from api_client import create_client_from_env

    client = create_client_from_env()
    return TickTickTools(client)


# Example usage
if __name__ == "__main__":
    # Test the tools
    try:
        tools = create_tools_from_env()

        # Test fetch tasks
        console.print("\n[bold]Testing fetch_tasks tool:[/bold]")
        result = tools.fetch_tasks_tool()
        console.print(result)

        # Test statistics
        console.print("\n[bold]Testing statistics tool:[/bold]")
        result = tools.get_task_statistics_tool()
        console.print(result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
