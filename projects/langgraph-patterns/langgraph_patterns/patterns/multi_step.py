"""Multi_step pattern implementation (skeleton)."""

from langgraph_patterns.base import BasePattern, PatternResult

class Multi_stepPattern(BasePattern):
    """Multi_step pattern - implementation coming soon."""
    
    def build_graph(self):
        raise NotImplementedError()
    
    def run(self, input_text: str, **kwargs) -> PatternResult:
        raise NotImplementedError()

