# 📊 Datasets

This directory contains the datasets used for training the language models.

## Available Datasets

### 1. Tiny Shakespeare (`tiny_shakespeare.txt`)

**Size:** ~1MB (1,115,394 characters)
**Lines:** ~40,000
**Source:** [Karpathy's char-rnn](https://github.com/karpathy/char-rnn)
**Used in:** Models 1, 2, 3

**Description:**
A collection of Shakespeare's works concatenated together. Perfect for learning character-level and word-level language modeling because:
- Small enough to train quickly on CPU
- Rich vocabulary and varied sentence structures
- Recognizable output makes it easy to evaluate quality
- Classic dataset used in many educational resources

**Example text:**
```
First Citizen:
Before we proceed any further, hear me speak.

All:
Speak, speak.

First Citizen:
You are all resolved rather to die than to famish?
```

### 2. WikiText-2

**Size:** ~4MB
**Source:** [HuggingFace Datasets](https://huggingface.co/datasets/wikitext)
**Used in:** Models 4, 5

**Description:**
A collection of verified Good and Featured articles from Wikipedia. Better for transformer-based models because:
- Longer context and more complex language
- More modern vocabulary
- Larger dataset for better transformer training
- Automatically downloaded by HuggingFace `datasets` library

### 3. TinyStories (Optional)

**Size:** ~500MB
**Source:** [HuggingFace Datasets](https://huggingface.co/datasets/roneneldan/TinyStories)
**Used in:** Model 5 (optional advanced training)

**Description:**
A dataset of synthetically generated short stories designed to be simple yet diverse. Great for:
- Training small language models that can generate coherent stories
- Learning more complex patterns than WikiText-2
- Experimenting with larger-scale training

## Download Instructions

```bash
# Download all datasets
python download.py
```

Or manually:
```bash
# Tiny Shakespeare
wget https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt -O tiny_shakespeare.txt
```

## Dataset Statistics

| Dataset | Size | Tokens (approx) | Vocab Size | Best For |
|---------|------|-----------------|------------|----------|
| Tiny Shakespeare | 1MB | 200K words | ~5K words | Learning basics |
| WikiText-2 | 4MB | 2M words | ~33K words | Transformers |
| TinyStories | 500MB | 100M words | ~50K words | Advanced models |

## Creating Custom Datasets

Want to train on your own text? Here's how:

```python
# 1. Collect your text data
text = """
Your text here.
Can be from books, articles, code, anything!
"""

# 2. Save as .txt file
with open('custom_dataset.txt', 'w', encoding='utf-8') as f:
    f.write(text)

# 3. Update the training script to use your file
# See individual model READMEs for details
```

**Tips for custom datasets:**
- Aim for at least 1MB of text (100K+ words)
- Ensure consistent encoding (UTF-8 recommended)
- Clean the text (remove excessive whitespace, formatting artifacts)
- Keep line breaks meaningful (end of sentences/paragraphs)

## License & Attribution

- **Tiny Shakespeare**: Public domain (Shakespeare's works)
- **WikiText-2**: Creative Commons CC-BY-SA 3.0
- **TinyStories**: MIT License

Always respect dataset licenses and provide proper attribution!
