"""Session tracking and storage for Pomodoro sessions."""
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
from pydantic import BaseModel, Field
from config import get_config


class PomodoroSession(BaseModel):
    """A single Pomodoro session record."""

    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(description="Planned duration in minutes")
    actual_duration_seconds: Optional[int] = Field(default=None, description="Actual duration in seconds")
    topic: str = Field(description="What you're working on")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    value_rating: Optional[int] = Field(default=None, ge=1, le=5, description="Value rating 1-5")
    completed: bool = Field(default=False, description="Whether session was completed")
    notes: Optional[str] = Field(default=None, description="Additional notes")

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @property
    def duration_display(self) -> str:
        """Get human-readable duration."""
        if self.actual_duration_seconds:
            mins = self.actual_duration_seconds // 60
            secs = self.actual_duration_seconds % 60
            return f"{mins}m {secs}s"
        return f"{self.duration_minutes}m (planned)"

    @property
    def is_productive(self) -> bool:
        """Determine if session was productive based on value rating."""
        return self.value_rating is not None and self.value_rating >= 3

    def complete(self, actual_duration_seconds: int, value_rating: int, notes: Optional[str] = None) -> None:
        """Mark session as completed."""
        self.end_time = datetime.now()
        self.actual_duration_seconds = actual_duration_seconds
        self.value_rating = value_rating
        self.completed = True
        if notes:
            self.notes = notes


class SessionStore:
    """Manages storage and retrieval of Pomodoro sessions."""

    def __init__(self, sessions_path: Optional[Path] = None):
        """Initialize session store."""
        config = get_config()
        self.sessions_path = sessions_path or config.sessions_path
        self.sessions_path.parent.mkdir(parents=True, exist_ok=True)

    def load_sessions(self) -> List[PomodoroSession]:
        """Load all sessions from storage."""
        if not self.sessions_path.exists():
            return []

        try:
            with open(self.sessions_path, 'r') as f:
                data = json.load(f)
                sessions = [PomodoroSession(**session) for session in data]
                return sessions
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not load sessions: {e}")
            return []

    def save_sessions(self, sessions: List[PomodoroSession]) -> None:
        """Save all sessions to storage."""
        try:
            with open(self.sessions_path, 'w') as f:
                data = [session.dict() for session in sessions]
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving sessions: {e}")
            raise

    def add_session(self, session: PomodoroSession) -> None:
        """Add a new session to storage."""
        sessions = self.load_sessions()
        sessions.append(session)
        self.save_sessions(sessions)

    def update_session(self, session: PomodoroSession) -> None:
        """Update an existing session."""
        sessions = self.load_sessions()
        for i, s in enumerate(sessions):
            if s.id == session.id:
                sessions[i] = session
                break
        self.save_sessions(sessions)

    def get_session_by_id(self, session_id: str) -> Optional[PomodoroSession]:
        """Get a specific session by ID."""
        sessions = self.load_sessions()
        for session in sessions:
            if session.id == session_id:
                return session
        return None

    def get_sessions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[PomodoroSession]:
        """Get sessions within a date range."""
        sessions = self.load_sessions()
        return [
            s for s in sessions
            if start_date <= s.start_time <= end_date
        ]

    def get_sessions_by_tag(self, tag: str) -> List[PomodoroSession]:
        """Get all sessions with a specific tag."""
        sessions = self.load_sessions()
        return [s for s in sessions if tag in s.tags]

    def get_recent_sessions(self, limit: int = 10) -> List[PomodoroSession]:
        """Get the most recent sessions."""
        sessions = self.load_sessions()
        return sorted(sessions, key=lambda s: s.start_time, reverse=True)[:limit]

    def get_all_tags(self) -> List[str]:
        """Get all unique tags across all sessions."""
        sessions = self.load_sessions()
        tags = set()
        for session in sessions:
            tags.update(session.tags)
        return sorted(list(tags))

    def get_completed_sessions(self) -> List[PomodoroSession]:
        """Get all completed sessions."""
        sessions = self.load_sessions()
        return [s for s in sessions if s.completed]

    def get_session_count(self) -> int:
        """Get total number of sessions."""
        return len(self.load_sessions())


def create_session(
    topic: str,
    duration_minutes: int = 30,
    tags: Optional[List[str]] = None
) -> PomodoroSession:
    """Create a new Pomodoro session."""
    return PomodoroSession(
        topic=topic,
        duration_minutes=duration_minutes,
        tags=tags or []
    )
