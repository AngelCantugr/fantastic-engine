"""
Self-Improving Agent

An AI agent that learns from user feedback and continuously improves.
"""

from self_improving_agent.agent import SelfImprovingAgent
from self_improving_agent.feedback.collector import FeedbackRating

__version__ = "0.1.0"
__all__ = ["SelfImprovingAgent", "FeedbackRating"]
