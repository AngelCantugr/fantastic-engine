"""
Cost tracking for LLM API calls
"""

from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
import hashlib
import json

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class APICall(Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True)
    project = Column(String(100), nullable=False, index=True)
    model = Column(String(50), nullable=False)
    operation = Column(String(50), default="completion")
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    cached = Column(Integer, default=0)  # Boolean as int
    cache_key = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string


class PromptCache(Base):
    __tablename__ = "prompt_cache"

    id = Column(Integer, primary_key=True)
    cache_key = Column(String(64), unique=True, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model = Column(String(50), nullable=False)
    hits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)


# Pricing per 1M tokens (as of Jan 2024)
MODEL_PRICING = {
    "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
}


class CostTracker:
    def __init__(self, project: str, db_url: str = "sqlite:///./llm_costs.db"):
        self.project = project
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage"""
        if model not in MODEL_PRICING:
            # Default pricing for unknown models
            return (prompt_tokens + completion_tokens) / 1_000_000 * 5.0

        pricing = MODEL_PRICING[model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key for prompt"""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def check_cache(self, prompt: str, model: str) -> Optional[str]:
        """Check if prompt response is cached"""
        cache_key = self.get_cache_key(prompt, model)
        cached = self.session.query(PromptCache).filter_by(cache_key=cache_key).first()

        if cached:
            # Update cache hit count
            cached.hits += 1
            cached.last_used = datetime.utcnow()
            self.session.commit()
            return cached.response

        return None

    def cache_response(self, prompt: str, response: str, model: str) -> None:
        """Cache prompt response"""
        cache_key = self.get_cache_key(prompt, model)

        # Check if already exists
        existing = self.session.query(PromptCache).filter_by(cache_key=cache_key).first()
        if existing:
            return

        cached = PromptCache(
            cache_key=cache_key,
            prompt=prompt,
            response=response,
            model=model,
        )
        self.session.add(cached)
        self.session.commit()

    @contextmanager
    def track_call(self, model: str, operation: str = "completion", metadata: Optional[Dict[str, Any]] = None):
        """Context manager to track API calls"""
        start_time = datetime.utcnow()
        call_data = {
            "model": model,
            "operation": operation,
            "metadata": metadata,
        }

        try:
            yield call_data
        finally:
            # Record the call
            if "prompt_tokens" in call_data and "completion_tokens" in call_data:
                self.record_call(
                    model=model,
                    operation=operation,
                    prompt_tokens=call_data["prompt_tokens"],
                    completion_tokens=call_data["completion_tokens"],
                    cached=call_data.get("cached", False),
                    metadata=metadata,
                )

    def record_call(
        self,
        model: str,
        operation: str,
        prompt_tokens: int,
        completion_tokens: int,
        cached: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an API call"""
        total_tokens = prompt_tokens + completion_tokens
        cost = 0.0 if cached else self.calculate_cost(model, prompt_tokens, completion_tokens)

        call = APICall(
            project=self.project,
            model=model,
            operation=operation,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            cached=1 if cached else 0,
            metadata=json.dumps(metadata) if metadata else None,
        )

        self.session.add(call)
        self.session.commit()

    def get_project_stats(self) -> Dict[str, Any]:
        """Get statistics for current project"""
        calls = self.session.query(APICall).filter_by(project=self.project).all()

        total_cost = sum(call.cost for call in calls)
        total_tokens = sum(call.total_tokens for call in calls)
        cached_calls = sum(1 for call in calls if call.cached)

        model_breakdown = {}
        for call in calls:
            if call.model not in model_breakdown:
                model_breakdown[call.model] = {"cost": 0.0, "tokens": 0, "calls": 0}

            model_breakdown[call.model]["cost"] += call.cost
            model_breakdown[call.model]["tokens"] += call.total_tokens
            model_breakdown[call.model]["calls"] += 1

        return {
            "project": self.project,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_calls": len(calls),
            "cached_calls": cached_calls,
            "cache_hit_rate": round(cached_calls / len(calls) * 100, 1) if calls else 0,
            "models": model_breakdown,
        }

    def get_optimization_suggestions(self) -> list[str]:
        """Get suggestions for cost optimization"""
        suggestions = []
        stats = self.get_project_stats()

        # Analyze model usage
        if "models" in stats:
            for model, data in stats["models"].items():
                if model.startswith("gpt-4") and data["cost"] > 10.0:
                    suggestions.append(
                        f"💡 Consider using gpt-3.5-turbo instead of {model} for simple tasks (90% cheaper)"
                    )

                if "claude-3-opus" in model and data["cost"] > 5.0:
                    suggestions.append(
                        f"💡 Consider using claude-3-sonnet for {model} tasks (80% cheaper with similar quality)"
                    )

        # Cache suggestions
        if stats["cache_hit_rate"] < 50:
            suggestions.append(
                f"💡 Your cache hit rate is {stats['cache_hit_rate']:.1f}%. Enable aggressive caching to save costs."
            )

        # Token optimization
        avg_tokens = stats["total_tokens"] / stats["total_calls"] if stats["total_calls"] > 0 else 0
        if avg_tokens > 2000:
            suggestions.append(
                "💡 Average token usage is high. Consider prompt compression or summarization."
            )

        return suggestions
