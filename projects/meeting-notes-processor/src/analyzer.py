"""
Meeting content analysis using GPT-4
"""
import os
import logging
from pathlib import Path
from typing import Dict
import yaml

from openai import OpenAI


logger = logging.getLogger(__name__)


class MeetingAnalyzer:
    """Analyzes meeting transcripts using GPT-4"""

    def __init__(self, prompts_path: Path = None, settings_path: Path = None):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('GPT_MODEL', 'gpt-4-turbo-preview')
        self.max_tokens = int(os.getenv('GPT_MAX_TOKENS', 2000))
        self.temperature = float(os.getenv('GPT_TEMPERATURE', 0.7))

        # Load prompts and settings
        self.prompts = self._load_prompts(prompts_path)
        self.settings = self._load_settings(settings_path)

    def _load_prompts(self, prompts_path: Path = None) -> dict:
        """Load AI prompts"""
        if prompts_path is None:
            prompts_path = Path(__file__).parent.parent / 'config' / 'prompts.yaml'

        with open(prompts_path) as f:
            return yaml.safe_load(f)

    def _load_settings(self, settings_path: Path = None) -> dict:
        """Load settings"""
        if settings_path is None:
            settings_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'

        with open(settings_path) as f:
            return yaml.safe_load(f)

    def analyze(self, transcript: str, transcript_data: Dict = None) -> Dict:
        """
        Analyze meeting transcript

        Returns:
            Dict with summary, action_items, decisions, key_topics, etc.
        """
        logger.info("Analyzing meeting transcript...")

        # Chunk if transcript is too long
        if len(transcript) > self.settings['analysis']['max_transcript_length']:
            transcript = self._chunk_transcript(transcript)

        results = {}

        # Extract each component
        if self.settings['analysis']['extract_summary']:
            results['summary'] = self._extract_summary(transcript)

        if self.settings['analysis']['extract_key_outcomes']:
            results['key_outcomes'] = self._extract_key_outcomes(transcript)

        if self.settings['analysis']['extract_action_items']:
            results['action_items'] = self._extract_action_items(transcript)

        if self.settings['analysis']['extract_decisions']:
            results['decisions'] = self._extract_decisions(transcript)

        if self.settings['analysis']['extract_key_topics']:
            results['key_topics'] = self._extract_key_topics(transcript, transcript_data)

        if self.settings['analysis']['extract_attendees']:
            results['attendees'] = self._extract_attendees(transcript)

        if self.settings['analysis']['detect_meeting_type']:
            results['meeting_type'] = self._detect_meeting_type(transcript)

        return results

    def _extract_summary(self, transcript: str) -> str:
        """Generate meeting summary"""
        logger.info("Extracting summary...")

        prompt = self.prompts['summary_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content.strip()

    def _extract_key_outcomes(self, transcript: str) -> str:
        """Extract key outcomes"""
        logger.info("Extracting key outcomes...")

        prompt = self.prompts['key_outcomes_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content.strip()

    def _extract_action_items(self, transcript: str) -> str:
        """Extract action items"""
        logger.info("Extracting action items...")

        prompt = self.prompts['action_items_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content.strip()

    def _extract_decisions(self, transcript: str) -> str:
        """Extract decisions"""
        logger.info("Extracting decisions...")

        prompt = self.prompts['decisions_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content.strip()

    def _extract_key_topics(self, transcript: str, transcript_data: Dict = None) -> str:
        """Extract key topics with timestamps"""
        logger.info("Extracting key topics...")

        prompt = self.prompts['key_topics_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content.strip()

    def _extract_attendees(self, transcript: str) -> str:
        """Extract attendees"""
        logger.info("Extracting attendees...")

        prompt = self.prompts['attendees_extraction_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    def _detect_meeting_type(self, transcript: str) -> str:
        """Detect meeting type"""
        logger.info("Detecting meeting type...")

        prompt = self.prompts['meeting_type_prompt'].format(transcript=transcript)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    def _chunk_transcript(self, transcript: str) -> str:
        """Chunk long transcript (simple implementation)"""
        max_length = self.settings['analysis']['max_transcript_length']

        if len(transcript) <= max_length:
            return transcript

        # Take first N characters with sentence boundary
        truncated = transcript[:max_length]
        last_period = truncated.rfind('.')

        if last_period > 0:
            return truncated[:last_period + 1] + "\n\n[Transcript truncated for analysis]"
        else:
            return truncated + "..."


if __name__ == '__main__':
    # Test analyzer
    analyzer = MeetingAnalyzer()

    sample_transcript = """
    Alice: Good morning everyone. Let's start our sprint planning.
    Bob: Sounds good. I reviewed the backlog yesterday.
    Alice: Great. What did you find?
    Bob: We have 23 story points ready. I think we should prioritize the analytics feature.
    Alice: Agreed. Carol, can you handle the design mockups by Friday?
    Carol: Yes, I'll have them done by end of week.
    Bob: I'll set up the GraphQL endpoint. Should be done by Thursday.
    """

    result = analyzer.analyze(sample_transcript)

    print("Summary:", result['summary'])
    print("\nAction Items:", result['action_items'])
    print("\nDecisions:", result.get('decisions', 'None'))
