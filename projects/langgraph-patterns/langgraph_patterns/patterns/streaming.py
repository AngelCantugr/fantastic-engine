"""Streaming pattern implementation (skeleton)."""

from langgraph_patterns.base import BasePattern, PatternResult

class StreamingPattern(BasePattern):
    """Streaming pattern - implementation coming soon."""
    
    def build_graph(self):
        raise NotImplementedError()
    
    def run(self, input_text: str, **kwargs) -> PatternResult:
        raise NotImplementedError()

