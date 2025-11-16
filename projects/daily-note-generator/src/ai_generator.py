"""
AI-powered content generation using OpenAI
"""
import os
import logging
from pathlib import Path
from typing import Dict, List
import yaml

from openai import OpenAI


logger = logging.getLogger(__name__)


class AIGenerator:
    """Generates AI-powered summaries and suggestions"""

    def __init__(self, prompts_path: Path = None):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', 1000))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.7))

        # Load prompts
        self.prompts = self._load_prompts(prompts_path)

    def _load_prompts(self, prompts_path: Path = None) -> dict:
        """Load AI prompts from config"""
        if prompts_path is None:
            prompts_path = Path(__file__).parent.parent / 'config' / 'prompts.yaml'

        with open(prompts_path) as f:
            return yaml.safe_load(f)

    def generate_summary(self, context: Dict) -> str:
        """
        Generate 'where you left off' summary

        Args:
            context: Context dict from ContextBuilder

        Returns:
            AI-generated summary text
        """
        logger.info("Generating AI summary...")

        # Build prompt
        from context_builder import ContextBuilder
        builder = ContextBuilder()
        context_text = builder.format_for_ai(context)

        # Get today's tasks as text
        tasks_text = '\n'.join([
            f"- {task.get('title', 'Untitled')}"
            for task in context.get('tasks_today', [])
        ])

        # Fill prompt template
        prompt = self.prompts['summary_prompt'].format(
            yesterday_content=context_text,
            today_tasks=tasks_text
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful daily planning assistant for someone with ADHD."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            summary = response.choices[0].message.content.strip()
            logger.info("Summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Return fallback
            return self._fallback_summary(context)

    def suggest_priorities(self, context: Dict, tasks: List[Dict]) -> List[str]:
        """
        Suggest priority tasks for today

        Args:
            context: Context dict
            tasks: List of today's tasks

        Returns:
            List of 1-3 priority task suggestions with explanations
        """
        logger.info("Generating priority suggestions...")

        # Build context
        from context_builder import ContextBuilder
        builder = ContextBuilder()
        context_text = builder.format_for_ai(context)

        # Format tasks
        tasks_text = '\n'.join([
            f"- {task.get('title', 'Untitled')} {' '.join([f'#{t}' for t in task.get('tags', [])])}"
            for task in tasks
        ])

        # Fill prompt
        prompt = self.prompts['priority_prompt'].format(
            context=context_text,
            today_tasks=tasks_text
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful task prioritization assistant for someone with ADHD."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            priorities_text = response.choices[0].message.content.strip()

            # Parse into list
            priorities = self._parse_priorities(priorities_text)
            logger.info(f"Generated {len(priorities)} priority suggestions")
            return priorities

        except Exception as e:
            logger.error(f"Failed to generate priorities: {e}")
            # Return fallback
            return self._fallback_priorities(tasks)

    def _parse_priorities(self, text: str) -> List[str]:
        """Parse AI response into list of priorities"""
        import re

        # Find numbered items (1. 2. 3.)
        pattern = r'\d+\.\s+(.+?)(?=\n\d+\.|\Z)'
        matches = re.findall(pattern, text, re.DOTALL)

        # Clean up and return
        return [match.strip() for match in matches]

    def _fallback_summary(self, context: Dict) -> str:
        """Fallback summary if AI fails"""
        if context.get('has_yesterday'):
            completed = len(context.get('completed_yesterday', []))
            if completed > 0:
                return f"Yesterday you completed {completed} tasks. Let's keep the momentum going today!"
            else:
                return "Starting fresh today! Focus on making progress on your priorities."
        else:
            return "Welcome to a new day! Let's make it productive."

    def _fallback_priorities(self, tasks: List[Dict]) -> List[str]:
        """Fallback priorities if AI fails"""
        max_priorities = int(os.getenv('MAX_PRIORITY_TASKS', 3))

        # Sort by priority field if available
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.get('priority', 0),
            reverse=True
        )

        # Take top N
        priorities = []
        for i, task in enumerate(sorted_tasks[:max_priorities], 1):
            title = task.get('title', 'Untitled')
            priorities.append(f"**{title}** - High priority task")

        return priorities if priorities else ["No tasks for today - enjoy your free time!"]


if __name__ == '__main__':
    # Test AI generator
    ai = AIGenerator()

    context = {
        'has_yesterday': True,
        'completed_yesterday': ['Review PRs', 'Update docs'],
        'unfinished_yesterday': ['Database migration'],
        'notes_yesterday': 'Good progress on auth module',
        'tasks_today': [
            {'title': 'Complete database migration', 'tags': ['dev'], 'priority': 5},
            {'title': 'Write tests', 'tags': ['testing'], 'priority': 3}
        ],
        'target_date': '2025-11-16',
        'day_of_week': 'Saturday'
    }

    summary = ai.generate_summary(context)
    print("Summary:")
    print(summary)

    priorities = ai.suggest_priorities(context, context['tasks_today'])
    print("\nPriorities:")
    for p in priorities:
        print(f"  {p}")
