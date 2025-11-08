# Agent 4: Documentation Writer (RAG) ⭐⭐⭐

**Complexity:** Intermediate | **Framework:** `llamaindex` | **Estimated Time:** 3-4 hours

## 🎯 Learning Objectives

- ✅ Understand RAG (Retrieval-Augmented Generation)
- ✅ Use LlamaIndex for document processing
- ✅ Create vector embeddings
- ✅ Implement semantic search
- ✅ Generate documentation from code

## 🧠 Key Concepts

### What is RAG?

**RAG** combines retrieval with generation:
1. Split documents into chunks
2. Create embeddings (vector representations)
3. Store in vector database
4. Retrieve relevant chunks
5. Generate answer using retrieved context

### Why LlamaIndex?

LlamaIndex specializes in connecting LLMs to data sources. Perfect for documentation and knowledge bases.

## 🚀 Usage

```bash
# Generate docs for a codebase
python agent.py --source src/ --output docs/

# Query existing documentation
python agent.py --query "How does authentication work?"
```

**Next:** [Agent 5: Test Generator](../05_test_generator/README.md) →
