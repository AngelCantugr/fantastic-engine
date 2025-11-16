"""
Message passing protocol for inter-agent communication.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """
    Message structure for agent communication.
    """
    sender: str
    receiver: str
    action: str
    data: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "action": self.action,
            "data": self.data,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "reply_to": self.reply_to
        }


class MessageBus:
    """
    Message bus for agent communication.

    Provides publish-subscribe pattern for agent messaging.
    """

    def __init__(self):
        """Initialize the message bus."""
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List[callable]] = {}

    def publish(self, message: Message):
        """
        Publish a message to the bus.

        Args:
            message: Message to publish
        """
        self.messages.append(message)

        # Notify subscribers
        if message.receiver in self.subscribers:
            for callback in self.subscribers[message.receiver]:
                callback(message)

    def subscribe(self, agent_name: str, callback: callable):
        """
        Subscribe to messages for an agent.

        Args:
            agent_name: Name of the agent
            callback: Callback function to invoke on message
        """
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)

    def get_messages_for(
        self,
        agent_name: str,
        action: Optional[str] = None
    ) -> List[Message]:
        """
        Get messages for a specific agent.

        Args:
            agent_name: Name of the agent
            action: Optional action filter

        Returns:
            List of messages
        """
        messages = [m for m in self.messages if m.receiver == agent_name]

        if action:
            messages = [m for m in messages if m.action == action]

        return messages

    def get_conversation(self, correlation_id: str) -> List[Message]:
        """
        Get all messages in a conversation.

        Args:
            correlation_id: Correlation ID

        Returns:
            List of messages in conversation
        """
        return [m for m in self.messages if m.correlation_id == correlation_id]

    def clear(self):
        """Clear all messages from the bus."""
        self.messages.clear()
