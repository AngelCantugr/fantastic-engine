"""
Database models using SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ResponseModel(Base):
    """Response model for storing agent responses."""

    __tablename__ = "responses"

    id = Column(String, primary_key=True)
    content = Column(Text)
    prompt_version = Column(String)
    strategy = Column(String)
    response_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to feedback
    feedback = relationship("FeedbackModel", back_populates="response", uselist=False)


class FeedbackModel(Base):
    """Feedback model for storing user ratings."""

    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    response_id = Column(String, ForeignKey("responses.id"))
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to response
    response = relationship("ResponseModel", back_populates="feedback")


class PromptVersionModel(Base):
    """Prompt version model for storing prompt evolution."""

    __tablename__ = "prompt_versions"

    id = Column(String, primary_key=True)
    template = Column(Text)
    version_number = Column(Float)
    avg_rating = Column(Float, nullable=True)
    sample_size = Column(Integer, default=0)
    is_active = Column(Integer, default=0)  # SQLite uses 0/1 for boolean
    created_at = Column(DateTime, default=datetime.utcnow)
