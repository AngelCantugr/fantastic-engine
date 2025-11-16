"""
Template rendering for meeting notes
"""
import logging
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Template


logger = logging.getLogger(__name__)


class TemplateEngine:
    """Renders meeting note templates"""

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

    def render(self, context: Dict) -> str:
        """
        Render the meeting note template

        Args:
            context: Dictionary with all template variables

        Returns:
            Rendered template as string
        """
        logger.info("Rendering template...")

        # Format timestamps if present
        if context.get('timestamps'):
            context['timestamps'] = self._format_timestamps(context['timestamps'])

        # Format transcript if present
        if context.get('full_transcript'):
            context['full_transcript'] = self._format_transcript(
                context['full_transcript'],
                context.get('segments', [])
            )

        # Render
        rendered = self.template.render(**context)

        return rendered

    def _format_timestamps(self, segments: list) -> str:
        """Format timestamp links"""
        if not segments:
            return ""

        lines = []
        for segment in segments:
            start_time = self._format_time(segment['start'])
            text = segment.get('text', 'Section')
            lines.append(f"- [{start_time}] - {text[:50]}...")

        return '\n'.join(lines)

    def _format_transcript(self, transcript: str, segments: list = None) -> str:
        """Format transcript with speaker labels and timestamps"""
        if not segments:
            # No segments, return plain transcript
            return transcript

        lines = []
        for segment in segments:
            start_time = self._format_time(segment['start'])
            text = segment.get('text', '').strip()

            if text:
                lines.append(f"**[{start_time}]** {text}")

        return '\n\n'.join(lines)

    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS or MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


if __name__ == '__main__':
    # Test template engine
    engine = TemplateEngine()

    context = {
        'meeting_title': 'Sprint Planning',
        'meeting_date': '2025-11-16',
        'meeting_type': 'Sprint Planning',
        'duration': '45 minutes',
        'attendees': 'Alice, Bob, Carol',
        'ai_summary': 'Productive sprint planning session.',
        'key_outcomes': '- Committed to 23 story points\n- Decided on GraphQL',
        'action_items': '- [ ] **Bob** - Set up GraphQL by 11/18',
        'decisions': '1. **Use GraphQL**\n   - Decision: GraphQL over REST',
        'key_topics': '### Analytics Integration\nDiscussed technical approach.',
        'include_transcript': False,
        'timestamps': [
            {'start': 300, 'text': 'Analytics discussion'},
            {'start': 1125, 'text': 'Design review'}
        ],
        'generation_date': '2025-11-16',
        'generation_time': '14:30:00',
        'processing_stats': True,
        'processing_time': '3m 42s',
        'processing_cost': '1.23'
    }

    rendered = engine.render(context)
    print(rendered)
