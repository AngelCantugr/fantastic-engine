"""
Database models for ADHD Dev Dashboard
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=1)  # 1-5
    energy_required = Column(Integer, default=5)  # 1-10
    estimated_minutes = Column(Integer, default=25)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    xp_reward = Column(Integer, default=10)

    pomodoros = relationship("PomodoroSession", back_populates="task")


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=25)
    type = Column(String(20), default="work")  # work, short_break, long_break
    completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    task = relationship("Task", back_populates="pomodoros")


class EnergyLog(Base):
    __tablename__ = "energy_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    energy_level = Column(Integer, nullable=False)  # 1-10
    focus_level = Column(Integer, nullable=False)  # 1-10
    mood = Column(String(20), default="neutral")
    notes = Column(Text, nullable=True)


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)  # Support for multi-user in future
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    total_pomodoros = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    icon = Column(String(20), nullable=False)
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
    xp_reward = Column(Integer, default=50)


# Database initialization
def init_db(database_url: str = "sqlite:///./adhd_dashboard.db"):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Initialize default achievements
    db = SessionLocal()
    if db.query(Achievement).count() == 0:
        default_achievements = [
            Achievement(name="First Steps", description="Complete your first task", icon="🎯", xp_reward=10),
            Achievement(name="Week Warrior", description="7 day streak", icon="🔥", xp_reward=100),
            Achievement(name="Focus Master", description="Complete 50 pomodoros", icon="⚡", xp_reward=150),
            Achievement(name="Task Terminator", description="Complete 100 tasks", icon="🏆", xp_reward=200),
            Achievement(name="Early Bird", description="30 morning work sessions", icon="🌟", xp_reward=150),
            Achievement(name="Night Owl", description="30 evening work sessions", icon="🦉", xp_reward=150),
            Achievement(name="Productivity Pro", description="Reach level 10", icon="💪", xp_reward=250),
            Achievement(name="Marathon Runner", description="30 day streak", icon="🚀", xp_reward=500),
        ]
        db.add_all(default_achievements)

        # Initialize default user stats
        user_stats = UserStats()
        db.add(user_stats)

        db.commit()
    db.close()

    return engine, SessionLocal


if __name__ == "__main__":
    init_db()
    print("✅ Database initialized!")
