"""
Prompt version control and storage.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger()


@dataclass
class PromptVersion:
    """Prompt version data structure."""
    id: str
    template: str
    version_number: float
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    avg_rating: Optional[float] = None
    sample_size: int = 0
    is_active: bool = False


class PromptStore:
    """
    Stores and manages prompt versions.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the prompt store.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.versions: List[PromptVersion] = []
        self.current_version_id: Optional[str] = None
        self.ab_tests: List[Dict[str, Any]] = []

        # Initialize with a baseline prompt
        self._create_baseline_prompt()

    def _create_baseline_prompt(self):
        """Create initial baseline prompt."""
        baseline = PromptVersion(
            id="v1.0",
            template="""You are a helpful assistant.

User question: {question}

Please provide a clear and accurate answer.""",
            version_number=1.0,
            is_active=True
        )

        self.versions.append(baseline)
        self.current_version_id = baseline.id

        logger.info("baseline_prompt_created", version=baseline.id)

    def get_current_version(self) -> PromptVersion:
        """
        Get current active prompt version.

        Returns:
            Current PromptVersion
        """
        for version in self.versions:
            if version.id == self.current_version_id:
                return version

        # Fallback to first version
        return self.versions[0]

    def get_prompt_template(self, version_id: str) -> str:
        """
        Get prompt template by version ID.

        Args:
            version_id: Version ID

        Returns:
            Prompt template string
        """
        for version in self.versions:
            if version.id == version_id:
                return version.template

        raise ValueError(f"Prompt version {version_id} not found")

    def create_version(
        self,
        template: str,
        version_number: float = None
    ) -> PromptVersion:
        """
        Create a new prompt version.

        Args:
            template: Prompt template
            version_number: Optional version number

        Returns:
            New PromptVersion
        """
        if version_number is None:
            # Auto-increment version
            max_version = max((v.version_number for v in self.versions), default=0.0)
            version_number = max_version + 0.1

        version = PromptVersion(
            id=f"v{version_number}",
            template=template,
            version_number=version_number,
            is_active=False
        )

        self.versions.append(version)

        logger.info("prompt_version_created", version=version.id)

        return version

    def activate_version(self, version_id: str):
        """
        Activate a prompt version.

        Args:
            version_id: Version ID to activate
        """
        # Deactivate current
        for version in self.versions:
            version.is_active = False

        # Activate new
        for version in self.versions:
            if version.id == version_id:
                version.is_active = True
                self.current_version_id = version_id
                logger.info("prompt_version_activated", version=version_id)
                return

        raise ValueError(f"Prompt version {version_id} not found")

    def update_version_metrics(
        self,
        version_id: str,
        avg_rating: float,
        sample_size: int
    ):
        """
        Update metrics for a prompt version.

        Args:
            version_id: Version ID
            avg_rating: Average rating
            sample_size: Number of samples
        """
        for version in self.versions:
            if version.id == version_id:
                version.avg_rating = avg_rating
                version.sample_size = sample_size
                logger.info(
                    "prompt_metrics_updated",
                    version=version_id,
                    avg_rating=avg_rating
                )
                return

    def get_version_history(self) -> List[PromptVersion]:
        """
        Get version history.

        Returns:
            List of prompt versions
        """
        return sorted(self.versions, key=lambda v: v.version_number, reverse=True)

    def create_ab_test(self, variant_a: str, variant_b: str):
        """
        Create an A/B test between two variants.

        Args:
            variant_a: Version ID for variant A
            variant_b: Version ID for variant B
        """
        test = {
            "id": f"test_{len(self.ab_tests) + 1}",
            "variant_a": variant_a,
            "variant_b": variant_b,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }

        self.ab_tests.append(test)

        logger.info("ab_test_created", test_id=test["id"])
