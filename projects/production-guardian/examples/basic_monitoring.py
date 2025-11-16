"""
Basic monitoring example for Production Guardian Agent.
"""

import asyncio
from production_guardian import GuardianAgent
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


async def main():
    """Run basic monitoring."""

    # Initialize agent in dry-run mode for safety
    agent = GuardianAgent(
        config={
            "log_file_path": "/var/log/application/app.log",
            "metrics_endpoint": "http://localhost:9090",
            "check_interval": 30,
            "max_actions_per_hour": 5,
            "require_approval_threshold": "medium"
        },
        dry_run=True  # IMPORTANT: Start in dry-run mode
    )

    logger.info("starting_production_guardian", dry_run=True)

    try:
        # Start monitoring
        await agent.start_monitoring()

    except KeyboardInterrupt:
        logger.info("shutting_down_gracefully")
        agent.stop_monitoring()

    except Exception as e:
        logger.error("monitoring_error", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
