# Introduction to Model Fine-Tuning

## The Big Picture

Imagine you have a really smart assistant who knows a lot about everything, but doesn't know the specifics of YOUR job. Fine-tuning is like giving that assistant specialized training so they become an expert in your domain.

```mermaid
graph LR
    A[General Knowledge<br/>GPT-2, BERT, etc.] -->|Fine-Tuning| B[Specialized Expert<br/>Your Task]

    C[Your Data<br/>1000s examples] --> B

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style B fill:#00ff00,stroke:#ff00ff,stroke-width:2px
    style C fill:#ffff00,stroke:#ff00ff,stroke-width:2px
```

## How Models Learn

### Pre-training (What You Start With)

Pre-trained models have already learned from massive amounts of text:
- **GPT models:** Learned from billions of web pages
- **BERT models:** Learned language understanding from Wikipedia + Books
- **LLaMA models:** Trained on trillions of tokens

This gives them:
- Grammar and language structure
- General world knowledge
- Common sense reasoning
- Basic task capabilities

### Fine-Tuning (What You Add)

You teach the model YOUR specific:
- Domain vocabulary
- Task patterns
- Output format
- Style and tone
- Edge cases

```mermaid
graph TD
    A[Pre-trained Model] --> B{What to Update?}

    B -->|All Parameters| C[Full Fine-Tuning]
    B -->|Subset of Parameters| D[Efficient Fine-Tuning]

    C --> C1[Best Quality]
    C --> C2[High Cost]

    D --> D1[Good Quality]
    D --> D2[Low Cost]
    D --> D3[LoRA, QLoRA, etc.]

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style C fill:#ff6b6b,stroke:#00ffff,stroke-width:2px
    style D fill:#4ecdc4,stroke:#ff00ff,stroke-width:2px
```

## The Training Loop Explained

Every fine-tuning method follows this basic pattern:

```mermaid
graph TD
    A[Start] --> B[Load Batch of Data]
    B --> C[Forward Pass]
    C --> D[Calculate Loss]
    D --> E[Backward Pass]
    E --> F[Update Weights]
    F --> G{More Batches?}
    G -->|Yes| B
    G -->|No| H[Epoch Complete]
    H --> I{More Epochs?}
    I -->|Yes| B
    I -->|No| J[Training Complete]

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style J fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

### Step by Step

1. **Load Batch:** Get examples from your training data
2. **Forward Pass:** Run input through model, get predictions
3. **Calculate Loss:** Compare predictions to actual answers
4. **Backward Pass:** Calculate gradients (which direction to adjust weights)
5. **Update Weights:** Adjust model parameters to reduce loss
6. **Repeat:** Continue until model performs well

## Key Concepts

### 1. Parameters (Weights)

The numbers in the model that determine its behavior.

- **Small model (GPT-2):** ~125M parameters
- **Medium model (LLaMA 7B):** ~7B parameters
- **Large model (LLaMA 70B):** ~70B parameters

Each parameter needs:
- **Memory to store:** 2-4 bytes
- **Memory for gradients:** Same size during training
- **Memory for optimizer:** 2-3x size for Adam optimizer

**Example:** Training GPT-2 (125M params) with Adam:
- Model: 500 MB
- Gradients: 500 MB
- Optimizer: 1000 MB
- **Total: ~2 GB minimum**

### 2. Gradients

Gradients tell us which direction to adjust each parameter.

```mermaid
graph LR
    A[Current<br/>Parameter] -->|Gradient| B[Updated<br/>Parameter]

    C[Loss] --> |Backpropagation| D[Gradients]
    D --> B

    style A fill:#ff00ff,stroke:#00ffff
    style B fill:#00ff00,stroke:#ff00ff
    style C fill:#ff6b6b,stroke:#00ffff
```

- **Positive gradient:** Decrease parameter
- **Negative gradient:** Increase parameter
- **Large gradient:** Big adjustment needed
- **Small gradient:** Almost optimal

### 3. Learning Rate

How big of a step to take when updating parameters.

```mermaid
graph TD
    A[Learning Rate] --> B{Size}

    B -->|Too High| C[Unstable Training]
    C --> C1[Loss explodes]
    C --> C2[Can't converge]

    B -->|Just Right| D[Good Training]
    D --> D1[Steady progress]
    D --> D2[Reaches optimum]

    B -->|Too Low| E[Slow Training]
    E --> E1[Takes forever]
    E --> E2[May get stuck]

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style D fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

**Typical values:**
- Full fine-tuning: `1e-5` to `5e-5`
- LoRA: `1e-4` to `3e-4`
- Prompt tuning: `1e-3` to `1e-2`

### 4. Batch Size

How many examples to process before updating weights.

- **Small batch (8-16):** Less memory, noisier updates, more iterations
- **Medium batch (32-64):** Good balance
- **Large batch (128+):** More memory, smoother updates, faster epochs

**Memory-constrained?** Use gradient accumulation:
- Process small batches
- Accumulate gradients
- Update after N batches (effective larger batch)

### 5. Epochs

One complete pass through your training dataset.

```mermaid
graph LR
    A[Epoch 1] --> B[Epoch 2]
    B --> C[Epoch 3]
    C --> D[...]
    D --> E[Epoch N]

    F[Dataset] -.-> A
    F -.-> B
    F -.-> C

    style A fill:#ff00ff,stroke:#00ffff
    style E fill:#00ff00,stroke:#ff00ff
    style F fill:#ffff00,stroke:#ff00ff
```

**How many epochs?**
- Too few: Underfitting (hasn't learned enough)
- Just right: Good performance
- Too many: Overfitting (memorizes training data)

**Typical:** 3-10 epochs for most tasks

### 6. Overfitting vs Underfitting

```mermaid
graph TD
    A[Model Fit] --> B{Quality}

    B -->|Underfitting| C[Poor Training<br/>Poor Validation]
    C --> C1[Train more epochs]
    C --> C2[Increase model size]

    B -->|Good Fit| D[Good Training<br/>Good Validation]
    D --> D1[Just right!]

    B -->|Overfitting| E[Great Training<br/>Poor Validation]
    E --> E1[Reduce epochs]
    E --> E2[Add regularization]
    E --> E3[Get more data]

    style B fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style D fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

**Signs of overfitting:**
- Training loss keeps decreasing
- Validation loss starts increasing
- Perfect on training data, poor on new data

**Prevention:**
- Use validation set
- Early stopping
- Dropout
- Weight decay

## Memory Requirements

Understanding memory is crucial for choosing a technique.

### Formula

```
Total Memory = Model Size + Gradients + Optimizer States + Activations + Batch Data
```

### Example: Fine-tuning LLaMA 7B

**Full Fine-Tuning (Float32):**
- Model: 28 GB
- Gradients: 28 GB
- Adam optimizer: 56 GB
- Activations: ~20 GB
- **Total: ~132 GB** 🔴 Requires A100 80GB (or multiple GPUs)

**LoRA (Float32):**
- Base model: 28 GB (frozen, can use float16)
- LoRA parameters: 40 MB
- Gradients: 40 MB
- Optimizer: 80 MB
- Activations: ~10 GB
- **Total: ~40 GB** 🟡 Fits on A100 40GB

**QLoRA (4-bit):**
- Base model: 7 GB (4-bit quantized)
- LoRA parameters: 40 MB
- Gradients: 40 MB
- Optimizer: 80 MB
- Activations: ~10 GB
- **Total: ~18 GB** 🟢 Fits on RTX 3090/4090!

## Common Use Cases

### Text Classification

Categorize text into predefined classes.

**Examples:**
- Sentiment analysis (positive/negative/neutral)
- Spam detection
- Topic classification
- Intent recognition

**Best technique:** LoRA or Full fine-tuning
**Data needed:** 500-5000 labeled examples

### Text Generation

Generate coherent text for specific purposes.

**Examples:**
- Creative writing in specific style
- Code generation
- Report generation
- Dialogue generation

**Best technique:** Full fine-tuning or LoRA
**Data needed:** 1000-10000 examples

### Question Answering

Answer questions based on context.

**Examples:**
- Customer support bots
- Document QA
- Technical support
- Educational tutoring

**Best technique:** LoRA or Prompt tuning
**Data needed:** 1000-5000 Q&A pairs

### Named Entity Recognition

Extract specific entities from text.

**Examples:**
- Extract names, dates, locations
- Medical entity extraction
- Legal document parsing
- Product information extraction

**Best technique:** Full fine-tuning
**Data needed:** 1000-5000 annotated examples

### Instruction Following

Make model follow specific instruction formats.

**Examples:**
- Task-specific assistants
- API calling agents
- Multi-step reasoning
- Tool use

**Best technique:** Full fine-tuning or LoRA
**Data needed:** 5000-50000 instruction-response pairs

## Quick Decision Tree

```mermaid
graph TD
    A[Start Fine-Tuning] --> B{GPU Memory?}

    B -->|80GB+| C[Full Fine-Tuning]
    B -->|40GB| D[LoRA]
    B -->|24GB| E[QLoRA]
    B -->|<16GB| F[QLoRA + Small Model]

    C --> G{Dataset Size?}
    D --> G
    E --> G
    F --> G

    G -->|<1000| H[Risk of Overfitting]
    H --> H1[Use small model]
    H --> H2[Strong regularization]

    G -->|1000-10000| I[Sweet Spot]
    I --> I1[Most techniques work]

    G -->|>10000| J[Large Dataset]
    J --> J1[Full fine-tuning shines]

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style C fill:#00ff00,stroke:#ff00ff
    style D fill:#00ff00,stroke:#ff00ff
    style E fill:#00ff00,stroke:#ff00ff
    style I fill:#00ff00,stroke:#ff00ff,stroke-width:2px
```

## Next Steps

Now that you understand the basics:

1. **Start simple:** Begin with [Full Fine-Tuning - Beginner](../examples/beginner/full-fine-tuning/)
2. **Learn efficient methods:** Try [LoRA - Beginner](../examples/beginner/lora/)
3. **Explore techniques:** Read technique-specific guides:
   - [Full Fine-Tuning Guide](02-full-fine-tuning.md)
   - [LoRA Guide](03-lora.md)
   - [QLoRA Guide](04-qlora.md)
   - [Prompt Tuning Guide](05-prompt-tuning.md)

## Key Takeaways

- **Fine-tuning adapts pre-trained models to your specific task**
- **Different techniques trade off quality, speed, and memory**
- **Start with LoRA for most use cases**
- **Use QLoRA when memory is extremely limited**
- **Full fine-tuning for maximum quality with sufficient resources**
- **More data generally means better results**
- **Monitor for overfitting using validation set**

**Remember:** The best way to learn is by doing! Move on to the practical examples and get your hands dirty with code.
