"""
Database initialization script.
"""

from sqlalchemy import create_engine
from self_improving_agent.database.models import Base
import os


def init_database(database_url: str = None):
    """
    Initialize the database.

    Args:
        database_url: Database URL (defaults to SQLite)
    """
    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///./self_improving_agent.db"
        )

    # Create engine
    engine = create_engine(database_url)

    # Create all tables
    Base.metadata.create_all(engine)

    print(f"Database initialized at: {database_url}")


if __name__ == "__main__":
    init_database()
