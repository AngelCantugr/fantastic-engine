"""
Script to create sample documents for RAG learning.
These documents cover common AI/ML topics used in RAG tutorials.
"""

sample_documents = {
    "ai_history.txt": """
The History of Artificial Intelligence

Artificial Intelligence (AI) has a rich history spanning over seven decades. The field was officially founded in 1956 at the Dartmouth Conference, where John McCarthy, Marvin Minsky, Claude Shannon, and others gathered to discuss the possibility of creating machines that could think.

The term "Artificial Intelligence" was coined by John McCarthy at this conference. The early years of AI (1950s-1970s) were marked by great optimism, with researchers believing that human-level AI was just around the corner.

The first AI winter occurred in the 1970s when the limitations of early AI systems became apparent. Expert systems dominated the 1980s, representing knowledge as rules written by human experts. However, these systems were brittle and difficult to maintain.

The second AI winter came in the late 1980s and early 1990s when expert systems failed to live up to their promise. However, the field was revitalized in the 1990s with the rise of machine learning approaches, particularly neural networks and statistical methods.

The modern deep learning revolution began around 2012 with AlexNet's victory in the ImageNet competition. Since then, AI has achieved superhuman performance in many domains including image recognition, game playing (Chess, Go, StarCraft), and natural language processing.

Notable milestones include:
- 1997: IBM's Deep Blue defeats world chess champion Garry Kasparov
- 2011: IBM Watson wins Jeopardy!
- 2016: AlphaGo defeats world Go champion Lee Sedol
- 2018: GPT-1 introduces transformer-based language models
- 2020: GPT-3 demonstrates few-shot learning capabilities
- 2022: ChatGPT brings conversational AI to mainstream

Today, AI is transforming industries from healthcare to transportation, finance to entertainment.
""",

    "machine_learning_basics.txt": """
Machine Learning Fundamentals

Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. Instead of writing rules manually, ML systems discover patterns in data automatically.

There are three main types of machine learning:

1. Supervised Learning
In supervised learning, the algorithm learns from labeled training data. Each training example consists of an input and its corresponding correct output (label). The goal is to learn a mapping from inputs to outputs that generalizes to new, unseen data.

Common supervised learning tasks include:
- Classification: Predicting discrete categories (e.g., spam vs. not spam)
- Regression: Predicting continuous values (e.g., house prices)

Popular algorithms include linear regression, logistic regression, decision trees, random forests, support vector machines (SVM), and neural networks.

2. Unsupervised Learning
Unsupervised learning works with unlabeled data. The algorithm must discover patterns and structure in the data without guidance. This is useful for exploring data and finding hidden patterns.

Common unsupervised learning tasks include:
- Clustering: Grouping similar data points together (e.g., customer segmentation)
- Dimensionality reduction: Reducing the number of features while preserving information
- Anomaly detection: Finding unusual data points

Popular algorithms include K-means clustering, hierarchical clustering, PCA (Principal Component Analysis), and autoencoders.

3. Reinforcement Learning
Reinforcement learning involves an agent learning to make decisions by interacting with an environment. The agent receives rewards or penalties based on its actions and learns to maximize cumulative reward over time.

Applications include game playing, robotics, and autonomous vehicles.

Key Concepts:
- Training vs. Testing: Models are trained on training data and evaluated on separate test data
- Overfitting: When a model performs well on training data but poorly on new data
- Underfitting: When a model is too simple to capture the underlying patterns
- Bias-Variance Tradeoff: Balancing model complexity and generalization
- Cross-validation: Technique for assessing model performance
- Feature engineering: Creating useful input features from raw data

The success of machine learning depends on having sufficient quality data, choosing appropriate algorithms, and careful model evaluation.
""",

    "nlp_basics.txt": """
Natural Language Processing Basics

Natural Language Processing (NLP) is a field at the intersection of computer science, artificial intelligence, and linguistics. It focuses on enabling computers to understand, interpret, and generate human language.

Core NLP Tasks:

1. Text Classification
Assigning categories to text documents. Examples include:
- Sentiment analysis (positive, negative, neutral)
- Topic classification (sports, politics, technology)
- Spam detection

2. Named Entity Recognition (NER)
Identifying and classifying named entities in text:
- Person names: "Albert Einstein"
- Organizations: "Microsoft"
- Locations: "San Francisco"
- Dates, times, monetary values

3. Part-of-Speech (POS) Tagging
Labeling each word with its grammatical role:
- Nouns, verbs, adjectives, adverbs, etc.

4. Machine Translation
Translating text from one language to another automatically. Modern systems use neural machine translation (NMT) based on sequence-to-sequence models.

5. Question Answering
Building systems that can answer questions posed in natural language. This is a key component of virtual assistants and chatbots.

6. Text Generation
Generating human-like text. Applications include:
- Chatbots and conversational agents
- Content creation
- Code generation
- Story writing

Key NLP Concepts:

Tokenization
Breaking text into smaller units (tokens) such as words, subwords, or characters. This is the first step in most NLP pipelines.

Embeddings
Representing words or sentences as dense vectors in a continuous space. Words with similar meanings have similar vector representations. Popular embedding methods include Word2Vec, GloVe, and more recently, contextual embeddings from transformers.

Language Models
Models that predict the probability of sequences of words. They capture the statistical patterns of language. Modern large language models (LLMs) like GPT, BERT, and their variants have achieved remarkable performance across many NLP tasks.

Attention Mechanism
A mechanism that allows models to focus on relevant parts of the input when making predictions. The attention mechanism was a key breakthrough that led to the transformer architecture.

Transformers
The dominant architecture in modern NLP, introduced in the "Attention is All You Need" paper (2017). Transformers use self-attention to process sequences in parallel, making them more efficient than recurrent neural networks (RNNs).

Pre-training and Fine-tuning
Modern NLP follows a two-stage approach:
1. Pre-training: Train a large model on massive amounts of unlabeled text
2. Fine-tuning: Adapt the pre-trained model to specific tasks with labeled data

This approach has led to major improvements in performance across many NLP tasks.

Challenges in NLP:
- Ambiguity: Words and sentences can have multiple meanings
- Context dependency: Meaning changes based on context
- Common sense reasoning: Understanding implicit information
- Multilingual and cross-lingual understanding
- Bias and fairness in language models
- Interpretability: Understanding why models make certain predictions

NLP is rapidly evolving, with new models and techniques emerging regularly. The field has seen tremendous progress in recent years, particularly with the advent of large language models.
""",

    "embeddings_explained.txt": """
Understanding Embeddings in Machine Learning

Embeddings are one of the most important concepts in modern machine learning, particularly in natural language processing and recommendation systems. This document explains what embeddings are, why they're useful, and how they work.

What are Embeddings?

Embeddings are dense vector representations of data in a continuous space. In simpler terms, they convert discrete objects (like words, sentences, images, or users) into arrays of numbers that capture their semantic meaning or characteristics.

For example, the word "cat" might be represented as:
[0.2, -0.5, 0.8, 0.1, -0.3, ...]

The key property of embeddings is that similar items have similar vectors. Words with related meanings will have vectors that are close together in the embedding space.

Why Do We Need Embeddings?

Traditional approaches used one-hot encoding to represent words:
"cat" = [1, 0, 0, 0, ...]
"dog" = [0, 1, 0, 0, ...]
"pizza" = [0, 0, 1, 0, ...]

Problems with one-hot encoding:
1. Sparse vectors: Mostly zeros, inefficient
2. No notion of similarity: "cat" and "dog" are as different as "cat" and "pizza"
3. High dimensionality: Vocabulary size = vector size (can be 50,000+)

Embeddings solve these problems:
1. Dense vectors: All values are meaningful, compact representation
2. Semantic similarity: Related concepts have similar vectors
3. Lower dimensionality: Typically 100-1000 dimensions regardless of vocabulary size

How Are Embeddings Created?

Word Embeddings (Word2Vec, GloVe):
These methods learn embeddings by analyzing word co-occurrence patterns in large text corpora. Words that appear in similar contexts get similar embeddings.

Word2Vec has two training approaches:
- CBOW (Continuous Bag of Words): Predict a word from its context
- Skip-gram: Predict context words from a target word

Contextual Embeddings (BERT, GPT):
Unlike Word2Vec where each word has one fixed embedding, contextual embeddings generate different vectors for the same word depending on context.

Example:
- "I went to the bank to deposit money" (bank = financial institution)
- "I sat on the river bank" (bank = riverside)

BERT would generate different embeddings for "bank" in these two sentences.

Sentence Embeddings:
Methods like Sentence-BERT create embeddings for entire sentences, useful for:
- Semantic search
- Document clustering
- Question answering
- Text similarity

Properties of Good Embeddings:

1. Semantic Similarity
Similar items have high cosine similarity:
similarity(cat, dog) > similarity(cat, pizza)

2. Analogical Reasoning
Vector arithmetic captures relationships:
king - man + woman ≈ queen
Paris - France + Italy ≈ Rome

3. Dimensionality Reduction
Compressed representation while preserving important information

4. Transfer Learning
Embeddings trained on large datasets can be reused for specific tasks

Applications of Embeddings:

1. Search and Information Retrieval
Convert queries and documents to embeddings, find most similar documents using vector similarity. This is the foundation of RAG systems!

2. Recommendation Systems
Embed users and items, recommend items with embeddings similar to user's embedding.

3. Classification
Use embeddings as features for machine learning models.

4. Clustering
Group similar items by clustering their embeddings.

5. Visualization
Reduce embeddings to 2D or 3D using t-SNE or UMAP to visualize relationships.

Distance Metrics for Embeddings:

1. Cosine Similarity
Measures the angle between vectors, range [-1, 1]
Most common for text embeddings

2. Euclidean Distance
Straight-line distance between points
Sensitive to vector magnitude

3. Dot Product
Simple multiplication and summation
Fast to compute, used in many neural networks

Best Practices:

1. Choose appropriate embedding size
- Too small: Loss of information
- Too large: Overfitting, computational cost
- Common sizes: 128, 256, 512, 768

2. Normalize embeddings
Many applications benefit from unit-length vectors

3. Consider domain-specific embeddings
General-purpose embeddings may not capture domain nuances

4. Update embeddings for your data
Fine-tune pre-trained embeddings on your specific dataset

5. Monitor embedding quality
Use intrinsic (similarity tasks) and extrinsic (downstream tasks) evaluation

Embeddings in RAG Systems:

In Retrieval-Augmented Generation:
1. Documents are split into chunks
2. Each chunk is converted to an embedding
3. Embeddings are stored in a vector database
4. User queries are embedded with the same model
5. Similar chunks are retrieved using vector similarity
6. Retrieved chunks provide context to the language model

This is why embeddings are crucial for RAG - they enable efficient semantic search over large document collections!

Advanced Topics:

- Multi-modal embeddings (text + images)
- Cross-lingual embeddings (multiple languages in same space)
- Dynamic embeddings (changing over time)
- Hierarchical embeddings (capturing multiple levels of meaning)

Embeddings have revolutionized how we represent and process information in machine learning systems!
"""
}

def create_sample_files():
    """Create all sample data files."""
    import os

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for filename, content in sample_documents.items():
        filepath = os.path.join(script_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created: {filename}")

    print(f"\nCreated {len(sample_documents)} sample documents in {script_dir}")
    print("\nThese documents cover:")
    print("- History of AI")
    print("- Machine Learning fundamentals")
    print("- Natural Language Processing basics")
    print("- Understanding embeddings")
    print("\nPerfect for testing your RAG system!")

if __name__ == "__main__":
    create_sample_files()
