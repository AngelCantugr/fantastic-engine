"""
Main Self-Improving Agent implementation.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import structlog

from self_improving_agent.feedback.collector import FeedbackCollector
from self_improving_agent.feedback.analyzer import FeedbackAnalyzer
from self_improving_agent.prompts.store import PromptStore
from self_improving_agent.prompts.optimizer import PromptOptimizer
from self_improving_agent.strategies.registry import StrategyRegistry
from self_improving_agent.metrics.tracker import MetricsTracker
from self_improving_agent.metrics.evaluator import PerformanceEvaluator

logger = structlog.get_logger()


class SelfImprovingAgent:
    """
    An AI agent that learns from feedback and improves over time.

    The agent:
    1. Generates responses using current best strategy
    2. Collects user feedback on responses
    3. Analyzes feedback to identify improvement opportunities
    4. Tests new prompt variations via A/B testing
    5. Adopts better strategies when proven effective
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the self-improving agent.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.get("model_name", "gpt-4-turbo-preview"),
            temperature=self.config.get("temperature", 0.7)
        )

        # Initialize components
        self.feedback_collector = FeedbackCollector(config)
        self.feedback_analyzer = FeedbackAnalyzer(config)
        self.prompt_store = PromptStore(config)
        self.prompt_optimizer = PromptOptimizer(config)
        self.strategy_registry = StrategyRegistry(config)
        self.metrics_tracker = MetricsTracker(config)
        self.evaluator = PerformanceEvaluator(config)

        # State
        self.request_count = 0
        self.is_learning_enabled = True

        logger.info("self_improving_agent_initialized")

    def process_request(
        self,
        question: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a user request.

        Args:
            question: User's question
            context: Optional context information

        Returns:
            Response dictionary with id, content, prompt_version, etc.
        """
        self.request_count += 1
        request_id = f"req_{self.request_count}_{datetime.utcnow().timestamp()}"

        logger.info("processing_request", request_id=request_id)

        try:
            # Get current best prompt strategy
            prompt_version = self.prompt_store.get_current_version()
            strategy = self.strategy_registry.get_active_strategy()

            # Create prompt
            prompt = self.prompt_store.get_prompt_template(prompt_version.id)
            formatted_prompt = prompt.format(
                question=question,
                context=context or {},
                **strategy.get_params()
            )

            # Generate response
            start_time = datetime.utcnow()
            llm_response = self.llm.invoke(formatted_prompt)
            response_time = (datetime.utcnow() - start_time).total_seconds()

            response = {
                "id": request_id,
                "content": llm_response.content,
                "prompt_version": prompt_version.id,
                "strategy": strategy.name,
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Track metrics
            self.metrics_tracker.record_request(
                request_id=request_id,
                prompt_version=prompt_version.id,
                strategy=strategy.name,
                response_time=response_time
            )

            logger.info("request_processed", request_id=request_id)

            # Trigger learning if threshold reached
            if self.is_learning_enabled and self.request_count % 100 == 0:
                self._trigger_learning_cycle()

            return response

        except Exception as e:
            logger.error("request_processing_failed", request_id=request_id, error=str(e))
            raise

    def record_feedback(
        self,
        response_id: str,
        rating: int,
        comment: str = None
    ):
        """
        Record user feedback on a response.

        Args:
            response_id: ID of the response
            rating: Rating (1-5)
            comment: Optional feedback comment
        """
        logger.info("recording_feedback", response_id=response_id, rating=rating)

        try:
            # Collect feedback
            feedback = self.feedback_collector.collect(
                response_id=response_id,
                rating=rating,
                comment=comment
            )

            # Track metrics
            self.metrics_tracker.record_feedback(
                response_id=response_id,
                rating=rating
            )

            # Analyze feedback
            if rating <= 2:  # Negative feedback
                analysis = self.feedback_analyzer.analyze_failure(feedback)
                logger.warning("negative_feedback_analyzed", analysis=analysis)

            # Check if we should trigger learning
            if self.feedback_collector.get_feedback_count() % 20 == 0:
                self._trigger_learning_cycle()

        except Exception as e:
            logger.error("feedback_recording_failed", response_id=response_id, error=str(e))
            raise

    def _trigger_learning_cycle(self):
        """Trigger a learning cycle to improve the agent."""
        logger.info("triggering_learning_cycle")

        try:
            # Evaluate current performance
            metrics = self.evaluator.evaluate()

            # Check if improvement is needed
            if metrics["average_rating"] < 4.0:
                logger.info("performance_below_target", avg_rating=metrics["average_rating"])

                # Analyze feedback patterns
                patterns = self.feedback_analyzer.identify_patterns()

                # Optimize prompts
                new_prompt = self.prompt_optimizer.optimize(
                    current_prompt=self.prompt_store.get_current_version(),
                    feedback_patterns=patterns,
                    metrics=metrics
                )

                # Create A/B test if improvement detected
                if new_prompt:
                    self.prompt_store.create_ab_test(
                        variant_a=self.prompt_store.get_current_version().id,
                        variant_b=new_prompt.id
                    )

            logger.info("learning_cycle_complete")

        except Exception as e:
            logger.error("learning_cycle_failed", error=str(e))

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.

        Returns:
            Metrics dictionary
        """
        return self.metrics_tracker.get_summary_metrics()

    def get_prompt_history(self) -> list:
        """
        Get prompt evolution history.

        Returns:
            List of prompt versions with performance
        """
        return self.prompt_store.get_version_history()

    def get_responses_by_rating(
        self,
        min_rating: int = None,
        max_rating: int = None
    ) -> list:
        """
        Get responses filtered by rating.

        Args:
            min_rating: Minimum rating filter
            max_rating: Maximum rating filter

        Returns:
            List of responses
        """
        return self.feedback_collector.get_responses_by_rating(
            min_rating=min_rating,
            max_rating=max_rating
        )

    def analyze_failure_patterns(self, responses: list) -> list:
        """
        Analyze failure patterns in responses.

        Args:
            responses: List of responses to analyze

        Returns:
            List of identified patterns
        """
        return self.feedback_analyzer.identify_patterns(responses)

    def apply_strategy(self, strategy_name: str):
        """
        Apply a specific strategy.

        Args:
            strategy_name: Name of strategy to apply
        """
        logger.info("applying_strategy", strategy=strategy_name)
        self.strategy_registry.set_active_strategy(strategy_name)
