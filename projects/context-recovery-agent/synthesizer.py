"""AI-powered context synthesis."""

from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.ai_helpers import AIHelper, ModelProvider


class ContextSynthesizer:
    """Synthesizes context using AI."""

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        fallback_to_ollama: bool = True
    ):
        provider_enum = ModelProvider(provider.lower())
        try:
            self.ai = AIHelper(provider=provider_enum, model=model)
        except (ValueError, ImportError) as e:
            if fallback_to_ollama and provider_enum == ModelProvider.OPENAI:
                print(f"⚠️  OpenAI unavailable. Falling back to Ollama...")
                self.ai = AIHelper(provider=ModelProvider.OLLAMA, model=model or "llama3")
            else:
                raise

    def synthesize_context(
        self,
        git_summary: str,
        obsidian_summary: str,
        ticktick_summary: str,
        branch_info: Dict
    ) -> Dict[str, str]:
        """
        Synthesize all context into a coherent summary.

        Returns:
            Dict with keys: 'what_you_were_doing', 'next_steps', 'blockers'
        """
        prompt = self._build_synthesis_prompt(
            git_summary, obsidian_summary, ticktick_summary, branch_info
        )

        response = self.ai.chat(
            messages=[
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more focused output
            max_tokens=1000
        )

        return self._parse_response(response)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI."""
        return """You are a Context Recovery Assistant for developers with ADHD.

Your job is to help them quickly understand where they left off after an interruption.

Analyze their recent digital footprints (git commits, notes, tasks) and provide:
1. What they were working on (concise, 2-3 sentences)
2. Next logical steps (3-5 actionable items)
3. Blockers and relevant context (anything that might slow them down)

Be concise, actionable, and empathetic. Focus on reducing cognitive load.
Use markdown formatting for clarity.
"""

    def _build_synthesis_prompt(
        self,
        git_summary: str,
        obsidian_summary: str,
        ticktick_summary: str,
        branch_info: Dict
    ) -> str:
        """Build the synthesis prompt."""
        prompt_parts = ["Here is the developer's recent activity:\n"]

        # Git context
        prompt_parts.append("### Git Commits (Recent Code Changes)")
        prompt_parts.append(git_summary)
        prompt_parts.append("")

        # Branch info
        prompt_parts.append("### Git Branch Info")
        prompt_parts.append(f"Current branch: {branch_info.get('branch', 'unknown')}")
        if branch_info.get('commits_ahead', 0) > 0:
            prompt_parts.append(f"Commits ahead of remote: {branch_info['commits_ahead']}")
        if branch_info.get('commits_behind', 0) > 0:
            prompt_parts.append(f"Commits behind remote: {branch_info['commits_behind']}")
        prompt_parts.append("")

        # Obsidian context
        prompt_parts.append("### Recent Notes & Thoughts")
        prompt_parts.append(obsidian_summary)
        prompt_parts.append("")

        # TickTick context
        prompt_parts.append("### Active Tasks")
        prompt_parts.append(ticktick_summary)
        prompt_parts.append("")

        prompt_parts.append("---")
        prompt_parts.append("\nBased on this information, provide:")
        prompt_parts.append("1. WHAT_WORKING_ON: A brief summary (2-3 sentences) of what they were working on")
        prompt_parts.append("2. NEXT_STEPS: 3-5 specific, actionable next steps")
        prompt_parts.append("3. BLOCKERS: Any blockers or important context to keep in mind")
        prompt_parts.append("\nFormat your response with these exact section headers.")

        return "\n".join(prompt_parts)

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse the AI response into structured sections."""
        sections = {
            "what_you_were_doing": "",
            "next_steps": "",
            "blockers": ""
        }

        # Split response into sections
        current_section = None
        lines = []

        for line in response.split('\n'):
            line_lower = line.lower().strip()

            if 'what' in line_lower and 'working' in line_lower:
                if lines and current_section:
                    sections[current_section] = '\n'.join(lines).strip()
                current_section = "what_you_were_doing"
                lines = []
            elif 'next' in line_lower and 'step' in line_lower:
                if lines and current_section:
                    sections[current_section] = '\n'.join(lines).strip()
                current_section = "next_steps"
                lines = []
            elif 'blocker' in line_lower or 'context' in line_lower:
                if lines and current_section:
                    sections[current_section] = '\n'.join(lines).strip()
                current_section = "blockers"
                lines = []
            elif current_section and line.strip():
                lines.append(line)

        # Add last section
        if lines and current_section:
            sections[current_section] = '\n'.join(lines).strip()

        # Fallback: if parsing failed, put everything in "what_you_were_doing"
        if not any(sections.values()):
            sections["what_you_were_doing"] = response.strip()

        return sections
