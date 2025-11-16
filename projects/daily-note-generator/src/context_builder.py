"""
Build context for AI generation
"""
import logging
from datetime import date
from typing import Optional, Dict, List


logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds context for AI from various sources"""

    def build(self, yesterday_note: Optional[str], today_tasks: List[Dict], target_date: date) -> Dict:
        """
        Build comprehensive context for AI generation

        Args:
            yesterday_note: Content of yesterday's daily note
            today_tasks: List of tasks for today
            target_date: The date being generated for

        Returns:
            Dict with structured context
        """
        context = {
            'target_date': target_date,
            'day_of_week': target_date.strftime('%A'),
            'has_yesterday': yesterday_note is not None,
            'yesterday_summary': None,
            'completed_yesterday': [],
            'unfinished_yesterday': [],
            'notes_yesterday': None,
            'tasks_today': today_tasks,
            'task_count': len(today_tasks)
        }

        # Parse yesterday's note if available
        if yesterday_note:
            context.update(self._parse_yesterday_note(yesterday_note))

        return context

    def _parse_yesterday_note(self, note_content: str) -> Dict:
        """Extract structured information from yesterday's note"""
        import re

        result = {
            'yesterday_summary': self._extract_summary(note_content),
            'completed_yesterday': self._extract_completed_tasks(note_content),
            'unfinished_yesterday': self._extract_unfinished_tasks(note_content),
            'notes_yesterday': self._extract_notes(note_content),
            'wins_yesterday': self._extract_wins(note_content)
        }

        return result

    def _extract_summary(self, content: str) -> Optional[str]:
        """Extract the 'Where You Left Off' section if it exists"""
        import re
        pattern = r'## 🌅 Where You Left Off\s+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_completed_tasks(self, content: str) -> List[str]:
        """Extract completed tasks"""
        import re
        pattern = r'- \[x\] (.+)'
        return re.findall(pattern, content)

    def _extract_unfinished_tasks(self, content: str) -> List[str]:
        """Extract unfinished tasks"""
        import re
        pattern = r'- \[ \] (.+)'
        return re.findall(pattern, content)

    def _extract_notes(self, content: str) -> Optional[str]:
        """Extract notes section"""
        import re
        pattern = r'## 📝 Notes\s+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            notes = match.group(1).strip()
            return notes if notes else None
        return None

    def _extract_wins(self, content: str) -> List[str]:
        """Extract wins/accomplishments"""
        import re
        pattern = r'## 🏆 Wins\s+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            wins_section = match.group(1).strip()
            # Extract bullet points
            wins = re.findall(r'- (.+)', wins_section)
            return wins
        return []

    def format_for_ai(self, context: Dict) -> str:
        """Format context as text for AI prompt"""
        parts = []

        # Yesterday's summary
        if context.get('has_yesterday'):
            parts.append("Yesterday's Activity:")

            if context.get('completed_yesterday'):
                parts.append(f"\nCompleted tasks ({len(context['completed_yesterday'])}):")
                for task in context['completed_yesterday'][:5]:  # Limit to top 5
                    parts.append(f"  ✓ {task}")

            if context.get('unfinished_yesterday'):
                parts.append(f"\nUnfinished tasks:")
                for task in context['unfinished_yesterday'][:3]:
                    parts.append(f"  ○ {task}")

            if context.get('notes_yesterday'):
                parts.append(f"\nNotes from yesterday:\n{context['notes_yesterday']}")

            if context.get('wins_yesterday'):
                parts.append(f"\nWins:")
                for win in context['wins_yesterday']:
                    parts.append(f"  🏆 {win}")
        else:
            parts.append("No information from yesterday (fresh start!).")

        # Today's tasks
        parts.append(f"\n\nTasks for {context['target_date']} ({context['task_count']} total):")
        for task in context['tasks_today'][:10]:  # Limit to top 10
            title = task.get('title', 'Untitled')
            tags = ' '.join([f'#{tag}' for tag in task.get('tags', [])])
            parts.append(f"  - {title} {tags}")

        return '\n'.join(parts)


if __name__ == '__main__':
    # Test context builder
    builder = ContextBuilder()

    yesterday_note = """
# 2025-11-15

## Tasks
- [x] Review pull requests
- [x] Update documentation
- [ ] Database migration (blocked)

## Notes
- Good progress on auth module
- Performance issue in user queries needs investigation
"""

    today_tasks = [
        {'title': 'Complete database migration', 'tags': ['dev']},
        {'title': 'Fix user query performance', 'tags': ['bug']},
        {'title': 'Write tests', 'tags': ['testing']}
    ]

    from datetime import datetime
    context = builder.build(yesterday_note, today_tasks, datetime.now().date())

    print("Context:")
    print(builder.format_for_ai(context))
