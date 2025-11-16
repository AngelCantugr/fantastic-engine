"""
Metrics monitoring module.
"""

from typing import Dict, Any, AsyncGenerator
import asyncio
import httpx
import psutil
import structlog

logger = structlog.get_logger()


class MetricsMonitor:
    """
    Monitors system and application metrics.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the metrics monitor.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.check_interval = self.config.get("check_interval", 30)

    async def stream_metrics(self, endpoint: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream metrics.

        Args:
            endpoint: Optional metrics endpoint URL

        Yields:
            Metrics batches
        """
        logger.info("streaming_metrics", endpoint=endpoint)

        while True:
            metrics = await self.collect_metrics(endpoint)
            yield metrics
            await asyncio.sleep(self.check_interval)

    async def collect_metrics(self, endpoint: str = None) -> Dict[str, Any]:
        """
        Collect current metrics.

        Args:
            endpoint: Optional metrics endpoint URL

        Returns:
            Metrics dictionary
        """
        metrics = {}

        # Collect system metrics
        metrics["system"] = self._collect_system_metrics()

        # Collect application metrics if endpoint provided
        if endpoint:
            metrics["application"] = await self._collect_application_metrics(endpoint)

        return metrics

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect system metrics using psutil.

        Returns:
            System metrics
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": asyncio.get_event_loop().time()
        }

    async def _collect_application_metrics(self, endpoint: str) -> Dict[str, Any]:
        """
        Collect application metrics from endpoint.

        Args:
            endpoint: Metrics endpoint URL

        Returns:
            Application metrics
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("metrics_collection_failed", endpoint=endpoint, error=str(e))
            return {}
