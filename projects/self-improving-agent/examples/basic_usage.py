"""
Basic usage example for Self-Improving Agent.
"""

from self_improving_agent import SelfImprovingAgent, FeedbackRating
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


def main():
    """Run basic usage example."""

    # Initialize agent
    agent = SelfImprovingAgent()

    logger.info("agent_initialized")

    # Example requests
    questions = [
        "How do I deploy a Python application?",
        "What is Docker?",
        "How do I optimize database queries?"
    ]

    for question in questions:
        # Process request
        response = agent.process_request(
            question=question,
            context={"user_level": "intermediate"}
        )

        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        print(f"Response: {response['content'][:200]}...")
        print(f"Prompt Version: {response['prompt_version']}")
        print(f"Strategy: {response['strategy']}")
        print(f"Response Time: {response['response_time']:.2f}s")

        # Simulate user feedback
        rating = 4  # Simulated rating
        agent.record_feedback(
            response_id=response["id"],
            rating=rating,
            comment="Helpful response!"
        )

        print(f"Feedback: {rating}/5")

    # Get metrics
    print(f"\n{'='*60}")
    print("PERFORMANCE METRICS")
    print(f"{'='*60}")

    metrics = agent.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    # Get prompt history
    print(f"\n{'='*60}")
    print("PROMPT HISTORY")
    print(f"{'='*60}")

    history = agent.get_prompt_history()
    for version in history:
        rating_str = f"{version.avg_rating:.2f}" if version.avg_rating else "N/A"
        print(f"Version {version.id}: {rating_str} ({version.sample_size} samples)")


if __name__ == "__main__":
    main()
