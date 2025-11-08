# 📚 RAG (Retrieval-Augmented Generation) Systems

## Introduction

RAG combines the generative power of Large Language Models (LLMs) with the precision of information retrieval to create AI systems that provide **accurate, grounded, and up-to-date responses**.

## The RAG Revolution

```mermaid
timeline
    title Evolution of RAG Systems
    2020 : Basic RAG
         : Simple embedding + retrieval
         : Fixed chunk size
    2022 : Advanced RAG
         : Query expansion
         : Re-ranking
         : Hybrid search
    2024 : Self-RAG
         : Self-reflection
         : Critique mechanism
         : Adaptive retrieval
    2025 : Agentic RAG
         : Multi-agent retrieval
         : Dynamic strategies
         : Real-time adaptation
         : Long RAG for documents
```

## Why RAG?

### The Hallucination Problem

```mermaid
graph LR
    subgraph "Without RAG"
        U1[User: What's our Q4 revenue?] --> L1[LLM]
        L1 --> R1[Generated Answer:<br/>Possibly hallucinated]
        R1 -.->|No verification| U1
    end

    subgraph "With RAG"
        U2[User: What's our Q4 revenue?] --> R2[RAG System]
        R2 --> V[Vector DB]
        V --> D[Retrieved: Q4 Report]
        D --> L2[LLM]
        L2 --> R3[Grounded Answer<br/>+ Citation]
        R3 --> U2
    end

    style R2 fill:#00ff00,stroke:#ff00ff,stroke-width:3px
    style R3 fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

### Key Benefits

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Reduced Hallucinations** | Grounds responses in real data | 60-80% reduction |
| **Domain Expertise** | Use proprietary knowledge | No retraining needed |
| **Citations** | Traceable sources | Builds trust |
| **Fresh Information** | Always up-to-date | Real-time accuracy |
| **Cost Effective** | No model fine-tuning | Lower compute costs |

## RAG Architecture

### Basic RAG Pipeline

```mermaid
graph TB
    subgraph "Indexing Phase (Offline)"
        D1[Documents] --> C1[Chunking]
        C1 --> E1[Embedding Model]
        E1 --> V1[(Vector Database)]
    end

    subgraph "Retrieval Phase (Online)"
        Q[User Query] --> E2[Embedding Model]
        E2 --> S[Similarity Search]
        V1 --> S
        S --> Top[Top K Results]
    end

    subgraph "Generation Phase"
        Top --> Aug[Augment Prompt]
        Aug --> LLM[Large Language Model]
        LLM --> Resp[Response + Citations]
    end

    style V1 fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style LLM fill:#00ffff,stroke:#ff00ff,stroke-width:2px
    style Resp fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

### Detailed RAG Flow

```mermaid
sequenceDiagram
    participant U as User
    participant RAG as RAG System
    participant Embed as Embedding Model
    participant VDB as Vector DB
    participant Rerank as Re-ranker
    participant LLM as Language Model

    U->>RAG: "Explain MCP protocol"

    Note over RAG: Query Processing
    RAG->>Embed: Encode query
    Embed->>RAG: Query vector

    Note over RAG,VDB: Retrieval
    RAG->>VDB: Similarity search
    VDB->>RAG: Top 20 chunks

    Note over RAG,Rerank: Re-ranking
    RAG->>Rerank: Relevance scoring
    Rerank->>RAG: Top 5 ranked

    Note over RAG,LLM: Generation
    RAG->>LLM: Context + Query
    LLM->>RAG: Generated answer

    RAG->>U: Answer + Citations
```

## 2025 RAG Architectures

### 1. Self-RAG

**Innovation:** Adds self-reflection and critique mechanisms

```mermaid
graph TB
    Q[Query] --> D{Should retrieve?}
    D -->|Yes| R[Retrieve]
    D -->|No| G1[Generate directly]

    R --> C[Retrieved Chunks]
    C --> E{Evaluate relevance}

    E -->|Relevant| G2[Generate with context]
    E -->|Not relevant| R2[Retrieve again]

    G2 --> CR{Critique output}
    CR -->|Good| O[Output]
    CR -->|Needs improvement| G2

    R2 --> C

    style D fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style CR fill:#ffff00,stroke:#ff00ff,stroke-width:2px
    style O fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

**Key Features:**
- **Reflection tokens** - Special tokens indicating confidence
- **Adaptive retrieval** - Only retrieves when needed
- **Self-critique** - Evaluates own responses
- **Iterative refinement** - Improves until quality threshold met

### 2. Long RAG

**Innovation:** Processes entire documents instead of small chunks

```mermaid
graph LR
    subgraph "Traditional RAG"
        D1[Document] --> S1[Split into<br/>small chunks]
        S1 --> C1[Chunk 1<br/>256 tokens]
        S1 --> C2[Chunk 2<br/>256 tokens]
        S1 --> C3[Chunk N]
    end

    subgraph "Long RAG"
        D2[Document] --> S2[Larger segments<br/>or full docs]
        S2 --> L1[Section 1<br/>4096 tokens]
        S2 --> L2[Full Document<br/>32K tokens]
    end

    style L1 fill:#00ff00,stroke:#ff00ff,stroke-width:2px
    style L2 fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

**Benefits:**
- Better context preservation
- No information loss at chunk boundaries
- Better for complex documents
- Improved coherence

**Requirements:**
- Long-context LLMs (100K+ tokens)
- More compute resources
- Smart document segmentation

### 3. Hybrid Retrieval

**Innovation:** Combines dense (semantic) and sparse (keyword) search

```mermaid
graph TB
    Q[Query: "How to implement MCP?"]

    subgraph "Dense Retrieval"
        Q --> E[Embedding Model]
        E --> V[(Vector DB)]
        V --> D[Dense Results<br/>Semantic matches]
    end

    subgraph "Sparse Retrieval"
        Q --> K[Keyword Extraction]
        K --> I[(Inverted Index)]
        I --> S[Sparse Results<br/>Keyword matches]
    end

    D --> F[Fusion Algorithm<br/>RRF / Score Norm]
    S --> F

    F --> R[Final Ranked Results]

    style F fill:#ff00ff,stroke:#00ffff,stroke-width:3px
    style R fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

**Fusion Strategies:**

1. **Reciprocal Rank Fusion (RRF)**
   ```
   RRF_score = Σ(1 / (k + rank_i))
   where k = 60 (constant)
   ```

2. **Score Normalization**
   ```
   normalized_score = (score - min) / (max - min)
   combined_score = α * dense + (1-α) * sparse
   ```

**Performance Gains:** 18-22% improvement in retrieval accuracy

## RAG Components Deep Dive

### 1. Document Chunking Strategies

```mermaid
graph TD
    Start[Document] --> Strategy{Chunking Strategy}

    Strategy --> Fixed[Fixed Size]
    Strategy --> Semantic[Semantic]
    Strategy --> Recursive[Recursive]
    Strategy --> Agent[Agent-based]

    Fixed --> F1[256 tokens<br/>Simple overlap]
    Semantic --> S1[Paragraph/Section<br/>Natural boundaries]
    Recursive --> R1[Hierarchical<br/>Multi-level]
    Agent --> A1[LLM decides<br/>Context-aware]

    style Semantic fill:#00ff00,stroke:#ff00ff,stroke-width:2px
    style Agent fill:#ff00ff,stroke:#00ffff,stroke-width:2px
```

**Best Practices (2025):**
- **Chunk Size:** 512-1024 tokens for most use cases
- **Overlap:** 20-30% to preserve context
- **Metadata:** Include source, section, timestamp
- **Hierarchy:** Maintain document structure

### 2. Embedding Models

**Popular Choices (2025):**

| Model | Dimensions | Max Tokens | Use Case |
|-------|-----------|------------|----------|
| **OpenAI text-embedding-3-large** | 3072 | 8191 | General purpose |
| **Cohere embed-v3** | 1024 | 512 | Multilingual |
| **Voyage AI voyage-2** | 1024 | 16000 | Long documents |
| **BGE-large-en-v1.5** | 1024 | 512 | Open source |

### 3. Vector Databases

```mermaid
graph LR
    subgraph "Vector DB Capabilities"
        V[Vector Database] --> I[Indexing<br/>HNSW, IVF]
        V --> S[Similarity Search<br/>Cosine, Euclidean]
        V --> F[Filtering<br/>Metadata queries]
        V --> H[Hybrid Search<br/>Vector + Full-text]
    end

    style V fill:#ff00ff,stroke:#00ffff,stroke-width:3px
```

**Popular Options:**

- **Pinecone** - Managed, serverless
- **Weaviate** - Open source, GraphQL
- **Qdrant** - Rust-based, fast filtering
- **Chroma** - Embedded, simple
- **Milvus** - Scalable, distributed

### 4. Re-ranking

Re-ranking improves retrieval quality by re-scoring candidates.

```python
# Conceptual re-ranking flow
initial_results = vector_db.search(query_vector, top_k=20)

# Re-rank using cross-encoder
reranked = reranker.rerank(
    query=user_query,
    documents=initial_results,
    top_n=5
)

# Use top 5 for generation
context = "\n".join([doc.text for doc in reranked[:5]])
```

**Re-ranking Models:**
- **Cohere Rerank** - API-based
- **Cross-encoders** - BERT-based
- **ColBERT** - Late interaction

## Advanced RAG Patterns

### Query Transformation

```mermaid
graph TB
    Q[Original Query] --> T{Transform}

    T --> HyDE[HyDE<br/>Generate hypothetical doc]
    T --> Multi[Multi-Query<br/>Generate variations]
    T --> Expand[Query Expansion<br/>Add related terms]
    T --> Decomp[Decomposition<br/>Break into sub-queries]

    HyDE --> V1[(Vector DB)]
    Multi --> V2[(Vector DB)]
    Expand --> V3[(Vector DB)]
    Decomp --> V4[(Vector DB)]

    style HyDE fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style Multi fill:#00ffff,stroke:#ff00ff,stroke-width:2px
```

**Techniques:**

1. **HyDE (Hypothetical Document Embeddings)**
   - Generate hypothetical answer
   - Embed the answer
   - Search with answer embedding

2. **Multi-Query**
   - Generate 3-5 query variations
   - Search with each
   - Combine results

3. **Step-back Prompting**
   - Ask broader question first
   - Use broader context

### Agentic RAG

Combines RAG with agent capabilities for adaptive retrieval.

```mermaid
graph TB
    U[User Query] --> A[RAG Agent]

    A --> D1{Decide: Need retrieval?}
    D1 -->|Yes| R[Retrieve]
    D1 -->|No| Gen1[Generate]

    R --> D2{Evaluate: Sufficient?}
    D2 -->|Yes| Gen2[Generate]
    D2 -->|No| R2[Retrieve more]

    R2 --> D3{Evaluate quality}
    D3 -->|Good| Gen2
    D3 -->|Need different source| R3[Different retrieval strategy]

    R3 --> Gen2
    Gen2 --> D4{Critique response}
    D4 -->|Pass| Output[Final Response]
    D4 -->|Fail| Gen3[Regenerate]
    Gen3 --> D4

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:3px
    style Output fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

## RAG Evaluation

### Key Metrics

```mermaid
graph LR
    subgraph "Retrieval Metrics"
        R1[Precision@K]
        R2[Recall@K]
        R3[MRR]
        R4[NDCG]
    end

    subgraph "Generation Metrics"
        G1[Faithfulness]
        G2[Answer Relevance]
        G3[Context Precision]
        G4[Context Recall]
    end

    subgraph "End-to-End"
        E1[Human Eval]
        E2[LLM-as-Judge]
        E3[RAGAS Score]
    end

    style G1 fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style E3 fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

**Faithfulness:** Does the answer stick to the retrieved context?
**Answer Relevance:** Does it answer the actual question?
**Context Precision:** Are retrieved chunks relevant?
**Context Recall:** Did we retrieve all necessary information?

## Implementation Example

```python
# Modern RAG Pipeline (2025)
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# 1. Document Processing
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,
    chunk_overlap=256,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(documents)

# 2. Embedding & Indexing
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Chroma.from_documents(chunks, embeddings)

# 3. Hybrid Retrieval
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.7
    }
)

# 4. RAG Chain
llm = ChatOpenAI(model="gpt-4", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# 5. Query
result = qa_chain({"query": "How does MCP work?"})
print(result["result"])
print("Sources:", result["source_documents"])
```

## Best Practices (2025)

### ✅ Do

1. **Use hybrid retrieval** for best accuracy
2. **Implement re-ranking** for top results
3. **Add metadata filtering** for precision
4. **Include citations** for trust
5. **Monitor retrieval quality** continuously
6. **Use Self-RAG** for critical applications
7. **Optimize chunk size** per use case
8. **Test with real queries** from users

### ❌ Avoid

1. **Too small chunks** - Loss of context
2. **No overlap** - Missing boundary information
3. **Single retrieval strategy** - Misses keyword matches
4. **No re-ranking** - Lower precision
5. **Ignoring metadata** - Harder filtering
6. **Static parameters** - Not adaptive
7. **No evaluation** - Can't improve

## Future Trends

- **Multimodal RAG** - Images, audio, video
- **Real-time RAG** - Live data streams
- **Federated RAG** - Distributed knowledge bases
- **Personalized RAG** - User-specific context
- **Agentic RAG** - Self-improving systems

## Resources

- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/)
- [RAG Best Practices Paper](https://arxiv.org/abs/2501.07391)
- [Self-RAG Paper](https://arxiv.org/abs/2310.11511)
- [RAGAS Evaluation Framework](https://docs.ragas.io/)

---

**Previous:** [← Agent Protocols](02-agent-protocols.md) | **Next:** [Multi-Agent Frameworks →](04-multi-agent-frameworks.md)
