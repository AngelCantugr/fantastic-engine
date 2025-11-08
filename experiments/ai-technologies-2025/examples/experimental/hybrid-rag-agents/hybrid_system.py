"""
Experimental: Hybrid RAG + Multi-Agent System
Combines retrieval strategies with multi-agent coordination for adaptive knowledge retrieval.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the system can handle"""
    FACTUAL = "factual"  # "What is MCP?"
    KEYWORD = "keyword"  # "MCP protocol features"
    COMPLEX = "complex"  # "Compare MCP and A2A for enterprise use"
    ANALYTICAL = "analytical"  # "Why is RAG better than fine-tuning?"


class RetrievalStrategy(Enum):
    """Available retrieval strategies"""
    DENSE = "dense"  # Vector similarity
    SPARSE = "sparse"  # BM25 keyword
    HYBRID = "hybrid"  # Combination
    SEMANTIC = "semantic"  # Enhanced embeddings


@dataclass
class RetrievalResult:
    """Result from a retrieval agent"""
    strategy: RetrievalStrategy
    documents: List[Dict[str, Any]]
    confidence: float
    metrics: Dict[str, float]


@dataclass
class CriticEvaluation:
    """Evaluation from critic agent"""
    passed: bool
    score: float
    feedback: str
    suggested_improvement: Optional[str] = None


class RouterAgent:
    """
    Analyzes query and routes to appropriate retrieval strategy.
    This is where the 'intelligence' of adaptive routing lives.
    """

    def __init__(self):
        self.query_history: List[Dict] = []

    def classify_query(self, query: str) -> QueryType:
        """Classify the query type"""

        # Simple heuristic classification (in production, use ML model)
        query_lower = query.lower()

        # Check for question words
        if any(word in query_lower for word in ["what is", "define", "meaning of"]):
            return QueryType.FACTUAL

        # Check for comparative/analytical language
        if any(word in query_lower for word in ["compare", "difference", "versus", "vs"]):
            return QueryType.COMPLEX

        # Check for why/how questions
        if any(word in query_lower for word in ["why", "how does", "explain"]):
            return QueryType.ANALYTICAL

        # Default to keyword search
        return QueryType.KEYWORD

    def select_strategy(
        self,
        query: str,
        query_type: QueryType,
        adaptive: bool = True
    ) -> RetrievalStrategy:
        """Select retrieval strategy based on query characteristics"""

        if not adaptive:
            # Default to hybrid for non-adaptive mode
            return RetrievalStrategy.HYBRID

        # Strategy mapping based on query type
        strategy_map = {
            QueryType.FACTUAL: RetrievalStrategy.DENSE,
            QueryType.KEYWORD: RetrievalStrategy.SPARSE,
            QueryType.COMPLEX: RetrievalStrategy.HYBRID,
            QueryType.ANALYTICAL: RetrievalStrategy.SEMANTIC
        }

        selected = strategy_map.get(query_type, RetrievalStrategy.HYBRID)

        logger.info(f"Router: {query_type.value} → {selected.value}")

        return selected

    def log_query(self, query: str, query_type: QueryType, strategy: RetrievalStrategy):
        """Log query for learning"""
        self.query_history.append({
            "query": query,
            "type": query_type.value,
            "strategy": strategy.value
        })


class DenseRetrievalAgent:
    """Agent specialized in vector similarity search"""

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.name = "Dense Retrieval Agent"

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        """Perform dense retrieval"""
        logger.info(f"{self.name}: Searching via vector similarity...")

        # Perform similarity search
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)

        # Calculate confidence based on scores
        if results:
            avg_score = sum(score for _, score in results) / len(results)
            confidence = min(1.0, avg_score)
        else:
            confidence = 0.0

        documents = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            for doc, score in results
        ]

        return RetrievalResult(
            strategy=RetrievalStrategy.DENSE,
            documents=documents,
            confidence=confidence,
            metrics={
                "num_results": len(documents),
                "avg_score": avg_score if results else 0.0
            }
        )


class SparseRetrievalAgent:
    """Agent specialized in keyword-based search (BM25)"""

    def __init__(self, documents):
        self.documents = documents
        self.name = "Sparse Retrieval Agent"
        # In production, initialize BM25 index here

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        """Perform sparse retrieval"""
        logger.info(f"{self.name}: Searching via BM25...")

        # Simulate BM25 search (in production, use actual BM25)
        # For demonstration, do simple keyword matching
        query_terms = set(query.lower().split())

        scored_docs = []
        for doc in self.documents[:20]:  # Limit for simulation
            content = doc.get("content", "").lower()
            # Simple scoring: count matching terms
            score = sum(1 for term in query_terms if term in content)
            if score > 0:
                scored_docs.append((doc, score))

        # Sort by score
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        documents = [
            {
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "score": float(score)
            }
            for doc, score in scored_docs[:top_k]
        ]

        confidence = min(1.0, len(documents) / top_k)

        return RetrievalResult(
            strategy=RetrievalStrategy.SPARSE,
            documents=documents,
            confidence=confidence,
            metrics={
                "num_results": len(documents),
                "matched_terms": sum(d["score"] for d in documents)
            }
        )


class HybridRetrievalAgent:
    """Agent that combines dense and sparse strategies"""

    def __init__(self, dense_agent: DenseRetrievalAgent, sparse_agent: SparseRetrievalAgent):
        self.dense_agent = dense_agent
        self.sparse_agent = sparse_agent
        self.name = "Hybrid Retrieval Agent"

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        """Perform hybrid retrieval with fusion"""
        logger.info(f"{self.name}: Combining dense + sparse retrieval...")

        # Get results from both strategies
        dense_results = self.dense_agent.retrieve(query, top_k * 2)
        sparse_results = self.sparse_agent.retrieve(query, top_k * 2)

        # Reciprocal Rank Fusion (RRF)
        k = 60
        doc_scores = {}

        # Add dense scores
        for rank, doc in enumerate(dense_results.documents, 1):
            doc_id = doc["content"][:100]  # Use snippet as ID
            rrf_score = 1 / (k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (0.7 * rrf_score)

        # Add sparse scores
        for rank, doc in enumerate(sparse_results.documents, 1):
            doc_id = doc["content"][:100]
            rrf_score = 1 / (k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + (0.3 * rrf_score)

        # Sort and take top k
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Reconstruct documents
        documents = []
        for doc_snippet, score in sorted_docs:
            # Find original doc
            for doc in dense_results.documents + sparse_results.documents:
                if doc["content"][:100] == doc_snippet:
                    doc["score"] = float(score)
                    documents.append(doc)
                    break

        confidence = (dense_results.confidence + sparse_results.confidence) / 2

        return RetrievalResult(
            strategy=RetrievalStrategy.HYBRID,
            documents=documents,
            confidence=confidence,
            metrics={
                "num_results": len(documents),
                "dense_contribution": 0.7,
                "sparse_contribution": 0.3
            }
        )


class CriticAgent:
    """
    Evaluates retrieval quality and decides if results are good enough.
    Inspired by Self-RAG's reflection mechanism.
    """

    def __init__(self, quality_threshold: float = 0.7):
        self.quality_threshold = quality_threshold
        self.name = "Critic Agent"

    def evaluate(self, query: str, retrieval_result: RetrievalResult) -> CriticEvaluation:
        """Evaluate retrieval quality"""
        logger.info(f"{self.name}: Evaluating retrieval quality...")

        # Criteria for evaluation
        criteria_scores = []

        # 1. Confidence score
        criteria_scores.append(retrieval_result.confidence)

        # 2. Number of results (should have at least 3 good results)
        result_count_score = min(1.0, len(retrieval_result.documents) / 3)
        criteria_scores.append(result_count_score)

        # 3. Relevance check (simple keyword overlap)
        query_terms = set(query.lower().split())
        relevance_scores = []
        for doc in retrieval_result.documents[:3]:  # Check top 3
            content_terms = set(doc["content"].lower().split())
            overlap = len(query_terms & content_terms)
            relevance = overlap / max(len(query_terms), 1)
            relevance_scores.append(relevance)

        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        criteria_scores.append(avg_relevance)

        # Overall score
        overall_score = sum(criteria_scores) / len(criteria_scores)

        passed = overall_score >= self.quality_threshold

        feedback = f"Quality score: {overall_score:.2f} (threshold: {self.quality_threshold})"

        if not passed:
            suggestion = self._suggest_improvement(retrieval_result)
        else:
            suggestion = None

        logger.info(f"{self.name}: {'✓ PASS' if passed else '✗ FAIL'} - {feedback}")

        return CriticEvaluation(
            passed=passed,
            score=overall_score,
            feedback=feedback,
            suggested_improvement=suggestion
        )

    def _suggest_improvement(self, result: RetrievalResult) -> str:
        """Suggest how to improve retrieval"""
        if result.strategy == RetrievalStrategy.DENSE:
            return "Try sparse retrieval for better keyword matching"
        elif result.strategy == RetrievalStrategy.SPARSE:
            return "Try dense retrieval for better semantic matching"
        else:
            return "Try adjusting retrieval parameters or expanding query"


class HybridRAGAgentSystem:
    """
    Main system coordinating all agents.
    Implements adaptive, multi-pass retrieval with quality control.
    """

    def __init__(self, vectorstore=None, documents=None):
        # Agents
        self.router = RouterAgent()

        # Retrieval agents (initialized when documents are indexed)
        self.dense_agent = None
        self.sparse_agent = None
        self.hybrid_agent = None

        # Critic
        self.critic = CriticAgent(quality_threshold=0.7)

        # Storage
        self.vectorstore = vectorstore
        self.documents = documents or []

    def index_documents(self, documents: List[str]):
        """Index documents (simplified)"""
        self.documents = [
            {"content": doc, "metadata": {"index": i}}
            for i, doc in enumerate(documents)
        ]

        # In production, create actual vectorstore
        logger.info(f"Indexed {len(self.documents)} documents")

    def query(
        self,
        query: str,
        adaptive: bool = True,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Query the system with adaptive multi-agent retrieval.

        Args:
            query: User query
            adaptive: Use adaptive strategy selection
            max_retries: Maximum retry attempts if quality check fails

        Returns:
            Final response with metadata
        """

        logger.info(f"\n{'='*60}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*60}")

        # 1. Route query
        query_type = self.router.classify_query(query)
        strategy = self.router.select_strategy(query, query_type, adaptive)
        self.router.log_query(query, query_type, strategy)

        # 2. Attempt retrieval with quality checks
        for attempt in range(max_retries + 1):
            logger.info(f"\nAttempt {attempt + 1}/{max_retries + 1}")

            # Retrieve based on strategy
            retrieval_result = self._execute_retrieval(query, strategy)

            # 3. Critic evaluates
            evaluation = self.critic.evaluate(query, retrieval_result)

            if evaluation.passed:
                # 4. Generate response (simplified)
                logger.info("✓ Quality check passed, generating response...")
                response = self._generate_response(query, retrieval_result)

                return {
                    "answer": response,
                    "strategy_used": strategy.value,
                    "quality_score": evaluation.score,
                    "attempts": attempt + 1,
                    "documents_used": len(retrieval_result.documents)
                }
            else:
                # Try different strategy
                logger.info(f"✗ Quality check failed: {evaluation.feedback}")
                if evaluation.suggested_improvement and attempt < max_retries:
                    logger.info(f"Suggestion: {evaluation.suggested_improvement}")
                    strategy = self._adjust_strategy(strategy)

        # If all retries failed, return best attempt
        logger.warning("⚠ All retrieval attempts below quality threshold")
        response = self._generate_response(query, retrieval_result)

        return {
            "answer": response,
            "strategy_used": strategy.value,
            "quality_score": evaluation.score,
            "attempts": max_retries + 1,
            "documents_used": len(retrieval_result.documents),
            "warning": "Quality below threshold"
        }

    def _execute_retrieval(self, query: str, strategy: RetrievalStrategy) -> RetrievalResult:
        """Execute retrieval with selected strategy"""

        # Simulated retrieval (in production, use actual agents)
        documents = [
            {"content": doc["content"], "metadata": doc["metadata"], "score": 0.8}
            for doc in self.documents[:5]
        ]

        return RetrievalResult(
            strategy=strategy,
            documents=documents,
            confidence=0.75,
            metrics={"num_results": len(documents)}
        )

    def _generate_response(self, query: str, retrieval: RetrievalResult) -> str:
        """Generate response from retrieved documents"""

        context = "\n\n".join([
            f"[{i+1}] {doc['content'][:200]}..."
            for i, doc in enumerate(retrieval.documents[:3])
        ])

        # Simulated response
        return f"""Based on the retrieved information using {retrieval.strategy.value} strategy:

{context}

[This would be the LLM-generated response in production]
"""

    def _adjust_strategy(self, current: RetrievalStrategy) -> RetrievalStrategy:
        """Adjust strategy for retry"""
        if current == RetrievalStrategy.DENSE:
            return RetrievalStrategy.HYBRID
        elif current == RetrievalStrategy.SPARSE:
            return RetrievalStrategy.DENSE
        else:
            return RetrievalStrategy.SPARSE


def main():
    """Demo the experimental system"""

    # Sample documents
    documents = [
        "MCP is a protocol by Anthropic for connecting AI to data sources",
        "RAG combines retrieval with generation for grounded responses",
        "LangGraph enables stateful multi-agent workflows",
        "CrewAI orchestrates role-based agent teams"
    ]

    # Initialize system
    system = HybridRAGAgentSystem()
    system.index_documents(documents)

    # Test queries
    queries = [
        "What is MCP?",  # Factual
        "agent protocol features",  # Keyword
        "How do RAG and multi-agent systems work together?"  # Complex
    ]

    for query in queries:
        result = system.query(query, adaptive=True)
        print(f"\n{'='*60}")
        print(f"Result: {result}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
