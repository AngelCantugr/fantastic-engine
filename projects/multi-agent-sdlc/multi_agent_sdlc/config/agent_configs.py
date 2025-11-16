"""
Agent configuration management.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import os


class AgentConfig(BaseModel):
    """Configuration for an individual agent."""

    model_name: str = Field(default="gpt-4-turbo-preview")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=128000)
    timeout: int = Field(default=300, ge=1)
    max_retries: int = Field(default=3, ge=0)


class CodeReviewAgentConfig(AgentConfig):
    """Configuration for Code Review Agent."""

    severity_threshold: str = Field(default="warning")
    custom_rules: list[str] = Field(default_factory=list)


class TestGeneratorAgentConfig(AgentConfig):
    """Configuration for Test Generator Agent."""

    coverage_target: float = Field(default=80.0, ge=0.0, le=100.0)
    test_frameworks: list[str] = Field(default_factory=lambda: ["pytest"])


class DeploymentAgentConfig(AgentConfig):
    """Configuration for Deployment Agent."""

    enable_auto_deployment: bool = Field(default=False)
    deployment_mode: str = Field(default="dry_run")


class SDLCConfig(BaseSettings):
    """Main configuration for SDLC orchestration."""

    # API Keys
    openai_api_key: str = Field(default="")
    langchain_api_key: Optional[str] = Field(default=None)

    # General settings
    model_name: str = Field(default="gpt-4-turbo-preview")
    deployment_mode: str = Field(default="dry_run")
    max_cost_per_run: float = Field(default=5.0)

    # Agent configs
    code_review: CodeReviewAgentConfig = Field(default_factory=CodeReviewAgentConfig)
    test_generator: TestGeneratorAgentConfig = Field(default_factory=TestGeneratorAgentConfig)
    deployment: DeploymentAgentConfig = Field(default_factory=DeploymentAgentConfig)

    # Safety settings
    max_actions_per_hour: int = Field(default=100)
    circuit_breaker_failure_threshold: int = Field(default=5)
    circuit_breaker_timeout: int = Field(default=60)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


def load_config(config_file: Optional[str] = None) -> SDLCConfig:
    """
    Load configuration from environment or file.

    Args:
        config_file: Optional path to .env file

    Returns:
        SDLCConfig instance
    """
    if config_file and os.path.exists(config_file):
        return SDLCConfig(_env_file=config_file)
    return SDLCConfig()


# Example configurations
EXAMPLE_CONFIGS = {
    "strict_review": {
        "code_review": {
            "severity_threshold": "info",
            "custom_rules": [
                "Check for SQL injection vulnerabilities",
                "Verify input validation",
                "Check for hardcoded secrets",
                "Validate error handling"
            ]
        }
    },
    "high_coverage": {
        "test_generator": {
            "coverage_target": 95.0,
            "test_frameworks": ["pytest", "unittest"]
        }
    },
    "production_safe": {
        "deployment": {
            "enable_auto_deployment": False,
            "deployment_mode": "staging"
        },
        "max_cost_per_run": 10.0
    }
}
