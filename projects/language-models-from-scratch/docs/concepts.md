# 🧠 Core Concepts Explained

A comprehensive guide to all concepts covered in the 5 models.

## Table of Contents
1. [Tokenization](#tokenization)
2. [Embeddings](#embeddings)
3. [Recurrent Neural Networks](#recurrent-neural-networks)
4. [Attention Mechanism](#attention-mechanism)
5. [Transformers](#transformers)
6. [Training & Optimization](#training--optimization)

---

## Tokenization

### What is Tokenization?

**Breaking text into units** that models can process.

### Three Levels

#### 1. Character-Level (Model 1)
```
"Hello world!" → ['H', 'e', 'l', 'l', 'o', ' ', 'w', 'o', 'r', 'l', 'd', '!']
```

**Pros:**
- Small vocabulary (~100 characters)
- Never encounters unknown tokens
- Can spell any word

**Cons:**
- Long sequences (slow)
- Must learn spelling
- Less semantic meaning per token

#### 2. Word-Level (Models 2-3)
```
"Hello world!" → ['hello', 'world', '!']
```

**Pros:**
- Shorter sequences (faster)
- Semantic meaning per token
- Natural language units

**Cons:**
- Large vocabulary (10K-100K words)
- Unknown words → `<unk>`
- Can't handle typos or new words

#### 3. Subword-Level (BPE) (Model 5)
```
"Hello world!" → ['Hello', ' world', '!']
"unbelievable" → ['un', 'believ', 'able']
```

**Pros:**
- Best of both worlds!
- Reasonable vocabulary (~50K)
- Handles unknown words
- Captures morphology

**Cons:**
- More complex algorithm
- Requires trained tokenizer

### Byte-Pair Encoding (BPE)

**Algorithm:**
1. Start with characters
2. Find most frequent pair
3. Merge into new token
4. Repeat until vocabulary size reached

**Example:**
```
Iteration 0: ['l', 'o', 'w', 'e', 'r']
Iteration 1: ['lo', 'w', 'e', 'r']  # 'l'+'o' frequent
Iteration 2: ['lo', 'w', 'er']      # 'e'+'r' frequent
Iteration 3: ['low', 'er']          # 'lo'+'w' frequent
```

---

## Embeddings

### What are Embeddings?

**Dense vector representations** of tokens that capture meaning.

### One-Hot Encoding (The Old Way)

```python
# Vocabulary: ["cat", "dog", "bird"]
"cat"  → [1, 0, 0]
"dog"  → [0, 1, 0]
"bird" → [0, 0, 1]
```

**Problems:**
- ❌ Sparse (mostly zeros)
- ❌ High dimensional (vocab_size)
- ❌ No similarity (all equidistant)

### Dense Embeddings (The Modern Way)

```python
# Dimension: 256 (much smaller!)
"cat"  → [0.2, -0.5, 0.8, 0.1, ..., 0.3]
"dog"  → [0.3, -0.4, 0.7, 0.2, ..., 0.4]
"bird" → [0.1, -0.2, 0.9, -0.1, ..., 0.2]
```

**Benefits:**
- ✅ Dense (meaningful values)
- ✅ Low dimensional (256-512)
- ✅ Similar words = similar vectors
- ✅ Learned during training!

### Properties of Good Embeddings

```
similarity("cat", "dog") > similarity("cat", "car")
similarity("king", "queen") > similarity("king", "apple")

# Famous example:
king - man + woman ≈ queen
```

### Word2Vec Intuition

"You shall know a word by the company it keeps"

Words appearing in similar contexts get similar embeddings.

---

## Recurrent Neural Networks

### The Sequential Processing Pattern

**Problem:** Text is sequential. "I love" vs. "love I" are different!

**Solution:** Process one token at a time, maintaining a hidden state.

### Vanilla RNN

```
Input:  x₁    x₂    x₃    x₄
        ↓     ↓     ↓     ↓
Hidden: h₀ → h₁ → h₂ → h₃ → h₄
        ↓     ↓     ↓     ↓
Output: y₁    y₂    y₃    y₄
```

**Forward pass:**
```python
h_t = tanh(W_hh @ h_{t-1} + W_xh @ x_t)
y_t = W_hy @ h_t
```

**Problem:** Vanishing gradients!
- Can't remember long-term dependencies
- Information "fades" over time

### GRU (Gated Recurrent Unit)

**Adds gates to control information flow:**

1. **Reset Gate:** What to forget from previous state
2. **Update Gate:** What to keep vs. what to update

```python
z_t = sigmoid(W_z @ [h_{t-1}, x_t])  # Update gate
r_t = sigmoid(W_r @ [h_{t-1}, x_t])  # Reset gate
h̃_t = tanh(W @ [r_t * h_{t-1}, x_t]) # Candidate
h_t = (1 - z_t) * h_{t-1} + z_t * h̃_t  # New state
```

**Better at long-term dependencies!**

### LSTM (Long Short-Term Memory)

**Even more sophisticated gates:**

1. **Forget Gate:** What to forget from cell state
2. **Input Gate:** What to add to cell state
3. **Output Gate:** What to output from cell state

**Two states:**
- **Hidden state (h):** Short-term memory
- **Cell state (c):** Long-term memory

```python
f_t = sigmoid(W_f @ [h_{t-1}, x_t])  # Forget
i_t = sigmoid(W_i @ [h_{t-1}, x_t])  # Input
c̃_t = tanh(W_c @ [h_{t-1}, x_t])    # Candidate
c_t = f_t * c_{t-1} + i_t * c̃_t     # Cell state
o_t = sigmoid(W_o @ [h_{t-1}, x_t])  # Output
h_t = o_t * tanh(c_t)                # Hidden state
```

**Best at long-term dependencies among RNNs!**

---

## Attention Mechanism

### The Problem with RNNs

**Information bottleneck:**
```
"The cat that chased the mouse was very tired"
                                      ↑
                            Must remember "cat"!
```

All information compressed into one vector h_final

### Attention Solution

**Don't compress! Keep all hidden states and selectively focus!**

```python
# Encoder outputs: [h_1, h_2, ..., h_n]
# Decoder state: s_t

# 1. Calculate attention scores
scores = [score(s_t, h_i) for h_i in encoder_outputs]

# 2. Normalize to probabilities
weights = softmax(scores)

# 3. Weighted sum
context = sum(weights[i] * h_i for all i)

# 4. Use context for prediction
output = predict(s_t, context)
```

### Attention Variants

#### Additive (Bahdanau) Attention
```python
score(s, h) = v^T @ tanh(W_1 @ s + W_2 @ h)
```

#### Dot-Product Attention
```python
score(s, h) = s^T @ h
```

#### Scaled Dot-Product (Transformer)
```python
score(q, k) = (q^T @ k) / sqrt(d_k)
```

### Self-Attention

**Attention applied to the sequence itself!**

```
Input: "The cat sat on the mat"

For "sat":
- Attends to "cat" (subject)
- Attends to "mat" (object)
- Attends to "on" (preposition)
```

**Key innovation:** Direct connections between all positions!

---

## Transformers

### The Revolutionary Architecture

**Core idea:** Replace recurrence with attention!

### Multi-Head Attention

**Instead of one attention pattern, learn multiple:**

```python
# Single head:
Attention(Q, K, V) = softmax(QK^T/√d_k)V

# Multi-head:
head_i = Attention(Q@W_i^Q, K@W_i^K, V@W_i^V)
MultiHead = Concat(head_1, ..., head_h) @ W^O
```

**Why multiple heads?**
- Head 1: Syntax
- Head 2: Semantics
- Head 3: Long-range dependencies
- Head 4: Local context

Each head learns different patterns!

### Positional Encoding

**Problem:** Attention has no sense of position!

**Solutions:**

#### Sinusoidal (Model 4)
```python
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```

**Pros:** Fixed, works for any length
**Cons:** Not learned from data

#### Learned (Model 5 / GPT)
```python
position_embedding = nn.Embedding(max_len, d_model)
```

**Pros:** Optimized for task
**Cons:** Fixed maximum length

### Layer Normalization

**Normalizes across features (not batch):**

```python
# Batch norm: normalize across batch
# Layer norm: normalize across features

mean = x.mean(dim=-1, keepdim=True)
std = x.std(dim=-1, keepdim=True)
x_norm = (x - mean) / (std + eps)
output = gamma * x_norm + beta  # Learnable
```

**Why:** Stabilizes training, enables deeper networks

### Residual Connections

**Skip connections that preserve information:**

```python
# Without residual:
x = layer(x)  # Information can be lost

# With residual:
x = x + layer(x)  # Always preserves original
```

**Why:** Enables training 100+ layer networks!

### Feed-Forward Networks

**Position-wise fully connected network:**

```python
FFN(x) = max(0, x @ W_1 + b_1) @ W_2 + b_2

# Or with GELU (GPT):
FFN(x) = GELU(x @ W_1 + b_1) @ W_2 + b_2
```

**Applied to each position independently.**

---

## Training & Optimization

### Loss Functions

#### Cross-Entropy Loss
```python
# For language modeling:
loss = -log P(next_token | context)

# Multi-class:
loss = -sum(y_i * log(ŷ_i))
```

**Lower loss = better predictions**

### Perplexity

```python
perplexity = exp(loss)
```

**Intuition:** "How perplexed is the model?"

- Perplexity of 100: Model as confused as choosing from 100 equally likely options
- Lower = better
- Good models: 20-50
- Bad models: 200+

### Optimizers

#### SGD (Stochastic Gradient Descent)
```python
params = params - lr * gradients
```

**Simple but works!**

#### Adam
```python
# Adaptive learning rates
m_t = β_1 * m_{t-1} + (1 - β_1) * g_t        # Momentum
v_t = β_2 * v_{t-1} + (1 - β_2) * g_t^2      # RMSprop
params = params - lr * m_t / (√v_t + eps)
```

**Better for most tasks!**

#### AdamW
```python
# Adam + decoupled weight decay
# Used in GPT and modern transformers
```

### Learning Rate Schedules

#### Cosine Annealing
```python
lr_t = lr_min + 0.5 * (lr_max - lr_min) * (1 + cos(π * t / T))
```

**Gradually decreases learning rate**

#### Warmup
```python
if step < warmup_steps:
    lr = lr_max * (step / warmup_steps)
else:
    lr = cosine_schedule(step)
```

**Start slow, then increase, then decrease**

### Regularization

#### Dropout
```python
# Randomly zero out activations during training
output = x * mask / (1 - p)  # mask: random 0/1
```

**Prevents overfitting!**

#### Weight Decay
```python
loss = loss + λ * ||weights||^2
```

**Encourages smaller weights**

#### Gradient Clipping
```python
if ||gradients|| > threshold:
    gradients = gradients * threshold / ||gradients||
```

**Prevents exploding gradients!**

---

## Summary Table

| Concept | Model | Why Important |
|---------|-------|---------------|
| Char tokenization | 1 | Fundamentals of sequence processing |
| Word tokenization | 2 | Semantic units |
| Embeddings | 2 | Learned representations |
| GRU | 2 | Better than vanilla RNN |
| LSTM | 3 | Best RNN for long sequences |
| Attention | 3 | Foundation of transformers |
| Self-attention | 4 | Process sequences in parallel |
| Multi-head | 4 | Multiple attention patterns |
| Positional encoding | 4 | Order information |
| Transformers | 4 | Modern architecture |
| BPE tokenization | 5 | Production tokenization |
| Pre-norm | 5 | Stable deep networks |
| GPT architecture | 5 | Production-grade LLMs |

---

**You now understand all core concepts of modern LLMs!** 🎉
