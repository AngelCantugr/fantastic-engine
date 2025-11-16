"""
Synthetic error generation for testing.
"""

from typing import Dict, Any
import random
import time
import structlog

logger = structlog.get_logger()


class SyntheticErrorGenerator:
    """
    Generates synthetic errors for testing the guardian agent.
    """

    def __init__(self):
        """Initialize the synthetic error generator."""
        self.is_running = False

    def inject_error_logs(self, error_rate: float = 0.1, duration: int = 300):
        """
        Inject synthetic error logs.

        Args:
            error_rate: Error rate (0.0 to 1.0)
            duration: Duration in seconds
        """
        logger.info(
            "injecting_error_logs",
            error_rate=error_rate,
            duration=duration
        )

        self.is_running = True
        start_time = time.time()

        while time.time() - start_time < duration and self.is_running:
            if random.random() < error_rate:
                # Generate error log
                error_types = [
                    "ERROR: Database connection failed",
                    "ERROR: Null pointer exception",
                    "ERROR: Timeout waiting for response",
                    "CRITICAL: Out of memory",
                    "ERROR: Failed to process request"
                ]
                error = random.choice(error_types)
                logger.error("synthetic_error", error=error)

            time.sleep(1)

        logger.info("error_injection_complete")

    def inject_high_cpu(self, cpu_percent: int = 85, duration: int = 180):
        """
        Simulate high CPU usage.

        Args:
            cpu_percent: Target CPU percentage
            duration: Duration in seconds
        """
        logger.info(
            "injecting_high_cpu",
            cpu_percent=cpu_percent,
            duration=duration
        )

        # In a real implementation, this would actually consume CPU
        # For now, just log the simulation
        logger.warning(
            "synthetic_high_cpu",
            cpu_percent=cpu_percent,
            duration=duration
        )

    def inject_high_memory(self, memory_percent: int = 92, duration: int = 180):
        """
        Simulate high memory usage.

        Args:
            memory_percent: Target memory percentage
            duration: Duration in seconds
        """
        logger.info(
            "injecting_high_memory",
            memory_percent=memory_percent,
            duration=duration
        )

        # In a real implementation, this would actually consume memory
        # For now, just log the simulation
        logger.warning(
            "synthetic_high_memory",
            memory_percent=memory_percent,
            duration=duration
        )

    def stop(self):
        """Stop error injection."""
        logger.info("stopping_error_injection")
        self.is_running = False
