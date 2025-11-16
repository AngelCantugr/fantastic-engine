"""
Template rendering engine for daily notes
"""
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional

from jinja2 import Template, Environment, FileSystemLoader


logger = logging.getLogger(__name__)


class TemplateEngine:
    """Renders daily note templates with dynamic content"""

    def __init__(self, template_path: Optional[str] = None):
        if template_path:
            self.template_path = Path(template_path)
        else:
            self.template_path = Path(__file__).parent.parent / 'config' / 'template.md'

        self.template = self._load_template()

    def _load_template(self) -> Template:
        """Load Jinja2 template"""
        logger.info(f"Loading template from {self.template_path}")

        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        return Template(template_content)

    def render(self, date: date, ai_summary: str, priority_tasks: List[str],
               all_tasks: List[Dict], context: Dict) -> str:
        """
        Render the daily note template

        Args:
            date: Target date
            ai_summary: AI-generated summary
            priority_tasks: List of priority task strings
            all_tasks: List of all task dicts
            context: Additional context

        Returns:
            Rendered template as string
        """
        logger.info(f"Rendering template for {date}")

        # Format date
        date_str = date.strftime('%Y-%m-%d')
        day_of_week = date.strftime('%A')

        # Format priority tasks
        if priority_tasks:
            priority_text = '\n'.join(priority_tasks)
        else:
            priority_text = "No priority tasks suggested. Great day to tackle whatever feels right!"

        # Format all tasks
        tasks_text = self._format_tasks(all_tasks)

        # Render template
        rendered = self.template.render(
            date=date_str,
            day_of_week=day_of_week,
            ai_summary=ai_summary,
            priority_tasks=priority_text,
            all_tasks=tasks_text,
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            completed_yesterday=len(context.get('completed_yesterday', [])),
            **context  # Include all context for custom templates
        )

        return rendered

    def _format_tasks(self, tasks: List[Dict]) -> str:
        """Format tasks as markdown checkboxes"""
        if not tasks:
            return "*No tasks for today*"

        lines = []

        # Group by tags/list if available
        grouped = self._group_tasks(tasks)

        for group_name, group_tasks in grouped.items():
            if group_name:
                lines.append(f"\n### {group_name}")

            for task in group_tasks:
                title = task.get('title', 'Untitled')
                tags = task.get('tags', [])
                priority = task.get('priority', 0)

                # Build task line
                task_line = f"- [ ] {title}"

                # Add tags
                if tags:
                    tag_str = ' '.join([f'#{tag}' for tag in tags])
                    task_line += f" {tag_str}"

                # Add priority indicator
                if priority > 3:
                    task_line += " ⭐"

                lines.append(task_line)

        return '\n'.join(lines)

    def _group_tasks(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Group tasks by list/project"""
        groups = {}

        for task in tasks:
            # Try to get list/project name
            group = task.get('list', task.get('project', ''))

            if group not in groups:
                groups[group] = []

            groups[group].append(task)

        return groups

    def validate(self):
        """Validate template syntax"""
        try:
            # Try to render with dummy data
            self.render(
                date=datetime.now().date(),
                ai_summary="Test summary",
                priority_tasks=["Test priority"],
                all_tasks=[{'title': 'Test task', 'tags': ['test']}],
                context={}
            )
            logger.info("Template validation successful")
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            raise


if __name__ == '__main__':
    # Test template engine
    engine = TemplateEngine()

    from datetime import datetime

    rendered = engine.render(
        date=datetime.now().date(),
        ai_summary="Yesterday was productive! You completed 3 tasks and made good progress.",
        priority_tasks=[
            "1. **Complete database migration** - Blocked yesterday, check if ready now",
            "2. **Write unit tests** - Follow up on pair programming session"
        ],
        all_tasks=[
            {'title': 'Complete database migration', 'tags': ['dev'], 'priority': 5, 'list': 'Work'},
            {'title': 'Write unit tests', 'tags': ['testing'], 'priority': 3, 'list': 'Work'},
            {'title': 'Buy groceries', 'tags': ['errands'], 'priority': 0, 'list': 'Personal'}
        ],
        context={
            'completed_yesterday': ['Review PRs', 'Update docs']
        }
    )

    print("Rendered template:")
    print(rendered)
