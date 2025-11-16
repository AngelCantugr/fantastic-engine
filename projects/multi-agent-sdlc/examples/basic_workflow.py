"""
Basic workflow example for multi-agent SDLC orchestration.
"""

from multi_agent_sdlc import SDLCOrchestrator
from multi_agent_sdlc.config import load_config
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
    """Run a basic SDLC workflow."""

    # Load configuration
    config = load_config()

    # Initialize orchestrator
    orchestrator = SDLCOrchestrator(config.dict())

    # Example code changes (in practice, this would be a git diff)
    code_changes = """
diff --git a/app/utils.py b/app/utils.py
index 1234567..abcdefg 100644
--- a/app/utils.py
+++ b/app/utils.py
@@ -1,5 +1,10 @@
 def calculate_total(items):
-    return sum(item.price for item in items)
+    if not items:
+        return 0.0
+
+    total = sum(item.price for item in items)
+    return round(total, 2)
"""

    logger.info("starting_workflow", code_changes=code_changes[:100])

    try:
        # Process code changes through the workflow
        result = orchestrator.process_changes(
            code_changes=code_changes,
            target_branch="main",
            deployment_target="staging",
            dry_run=True  # Safe mode for testing
        )

        # Check results
        logger.info("workflow_complete", workflow_id=result["workflow_id"])

        if result.get("review_result"):
            print(f"\n{'='*60}")
            print("CODE REVIEW RESULTS")
            print(f"{'='*60}")
            print(f"Approved: {result['review_result']['approved']}")
            print(f"Severity: {result['review_result']['severity']}")
            print(f"Issues: {len(result['review_result']['issues'])}")
            for issue in result['review_result']['issues'][:3]:
                print(f"  - {issue.get('message', 'N/A')}")

        if result.get("test_result"):
            print(f"\n{'='*60}")
            print("TEST GENERATION RESULTS")
            print(f"{'='*60}")
            print(f"Tests Generated: {len(result['test_result']['tests_generated'])}")
            print(f"Coverage: {result['test_result']['coverage_estimate']}%")
            print(f"Framework: {result['test_result']['framework']}")

        if result.get("deployment_result"):
            print(f"\n{'='*60}")
            print("DEPLOYMENT RESULTS")
            print(f"{'='*60}")
            print(f"Status: {result['deployment_result']['status']}")
            print(f"Target: {result['deployment_result']['target_environment']}")
            print(f"Health Check: {'Passed' if result['deployment_result']['health_check_passed'] else 'Failed'}")

        if result.get("errors"):
            print(f"\n{'='*60}")
            print("ERRORS")
            print(f"{'='*60}")
            for error in result["errors"]:
                print(f"  - {error}")

        print(f"\n{'='*60}")
        print(f"Total Cost: ${result['total_cost']:.2f}")
        print(f"{'='*60}\n")

    except Exception as e:
        logger.error("workflow_failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
