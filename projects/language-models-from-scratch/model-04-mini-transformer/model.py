"""
Mini Transformer Language Model

This is THE architecture that revolutionized NLP!
Based on "Attention Is All You Need" (Vaswani et al., 2017)

Key Concepts:
- Self-attention (attention to itself!)
- Multi-head attention (multiple attention patterns)
- Positional encoding (how to represent position)
- Feed-forward networks
- Layer normalization
- Residual connections
- No RNNs needed!
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class PositionalEncoding(nn.Module):
    """
    Add position information to embeddings.

    Problem: Transformers have no inherent sense of order!
    Solution: Add position-dependent patterns to each word.

    Uses sine and cosine functions of different frequencies.
    """

    def __init__(self, d_model, max_len=5000):
        super().__init__()

        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                           (-math.log(10000.0) / d_model))

        # Apply sine to even indices
        pe[:, 0::2] = torch.sin(position * div_term)
        # Apply cosine to odd indices
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0)  # Add batch dimension
        self.register_buffer('pe', pe)

    def forward(self, x):
        """Add positional encoding to embeddings."""
        # x: (batch, seq_len, d_model)
        return x + self.pe[:, :x.size(1)]


class MultiHeadAttention(nn.Module):
    """
    Multi-head self-attention mechanism.

    Instead of one attention pattern, learn MULTIPLE patterns!
    - Head 1 might focus on grammar
    - Head 2 might focus on semantics
    - Head 3 might focus on long-range dependencies
    """

    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()

        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        # Linear projections for Q, K, V
        self.q_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)

        # Output projection
        self.out_linear = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        """
        Self-attention forward pass.

        Args:
            x: Input (batch, seq_len, d_model)
            mask: Attention mask (optional)

        Returns:
            output: (batch, seq_len, d_model)
            attention: Attention weights for visualization
        """
        batch_size, seq_len, d_model = x.size()

        # Linear projections and split into heads
        # (batch, seq_len, d_model) -> (batch, num_heads, seq_len, head_dim)
        Q = self.q_linear(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_linear(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_linear(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled dot-product attention
        # (batch, num_heads, seq_len, head_dim) @ (batch, num_heads, head_dim, seq_len)
        # = (batch, num_heads, seq_len, seq_len)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # Apply mask (for causal attention)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        # Softmax to get attention weights
        attention = F.softmax(scores, dim=-1)
        attention = self.dropout(attention)

        # Apply attention to values
        # (batch, num_heads, seq_len, seq_len) @ (batch, num_heads, seq_len, head_dim)
        # = (batch, num_heads, seq_len, head_dim)
        output = torch.matmul(attention, V)

        # Concatenate heads
        # (batch, num_heads, seq_len, head_dim) -> (batch, seq_len, d_model)
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, d_model)

        # Final linear projection
        output = self.out_linear(output)

        return output, attention


class FeedForward(nn.Module):
    """
    Position-wise feed-forward network.

    Simple: Linear -> ReLU -> Linear
    Applied to each position independently.
    """

    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()

        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # (batch, seq_len, d_model) -> (batch, seq_len, d_ff) -> (batch, seq_len, d_model)
        return self.linear2(self.dropout(F.relu(self.linear1(x))))


class TransformerBlock(nn.Module):
    """
    One transformer block = Multi-head attention + Feed-forward

    Key features:
    - Residual connections (x + layer(x))
    - Layer normalization
    """

    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        """
        Forward pass with residual connections.

        Pattern: x = x + layer(norm(x))
        """
        # Self-attention
        attn_out, attention = self.attention(self.norm1(x), mask)
        x = x + self.dropout1(attn_out)

        # Feed-forward
        ff_out = self.feed_forward(self.norm2(x))
        x = x + self.dropout2(ff_out)

        return x, attention


class MiniTransformer(nn.Module):
    """
    A mini transformer language model (decoder-only).

    This is similar to GPT but simplified for learning!

    Args:
        vocab_size: Number of unique tokens
        d_model: Model dimension (embedding size)
        num_heads: Number of attention heads
        num_layers: Number of transformer blocks
        d_ff: Feed-forward dimension
        max_len: Maximum sequence length
        dropout: Dropout probability
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 256,
        num_heads: int = 4,
        num_layers: int = 4,
        d_ff: int = 1024,
        max_len: int = 512,
        dropout: float = 0.1
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.d_model = d_model

        # Token embedding
        self.embedding = nn.Embedding(vocab_size, d_model)

        # Positional encoding
        self.pos_encoding = PositionalEncoding(d_model, max_len)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        # Output layer
        self.norm = nn.LayerNorm(d_model)
        self.fc = nn.Linear(d_model, vocab_size)

        self.dropout = nn.Dropout(dropout)

        self._init_weights()

    def _init_weights(self):
        """Initialize weights."""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def _create_mask(self, size, device):
        """
        Create causal mask to prevent attending to future tokens.

        Returns lower triangular matrix:
        [[1, 0, 0, 0],
         [1, 1, 0, 0],
         [1, 1, 1, 0],
         [1, 1, 1, 1]]
        """
        mask = torch.tril(torch.ones(size, size, device=device))
        return mask.unsqueeze(0).unsqueeze(0)  # Add batch and head dimensions

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: Input indices (batch, seq_len)

        Returns:
            output: Logits (batch, seq_len, vocab_size)
        """
        batch_size, seq_len = x.size()

        # Create causal mask
        mask = self._create_mask(seq_len, x.device)

        # Embed and add positional encoding
        x = self.embedding(x) * math.sqrt(self.d_model)  # Scale embeddings
        x = self.pos_encoding(x)
        x = self.dropout(x)

        # Pass through transformer blocks
        attentions = []
        for block in self.blocks:
            x, attention = block(x, mask)
            attentions.append(attention)

        # Final norm and projection
        x = self.norm(x)
        output = self.fc(x)

        return output

    def generate(self, start_idx, idx_to_word, max_length=100, temperature=1.0, device='cpu'):
        """Generate text autoregressively."""
        self.eval()
        with torch.no_grad():
            generated = [start_idx]

            for _ in range(max_length - 1):
                # Get current sequence
                x = torch.tensor([generated], device=device)

                # Forward pass
                output = self.forward(x)

                # Get last token logits
                logits = output[0, -1] / temperature

                # Sample
                probs = F.softmax(logits, dim=0)
                next_idx = torch.multinomial(probs, 1).item()

                generated.append(next_idx)

        return [idx_to_word[idx] for idx in generated]


def count_parameters(model):
    """Count parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    vocab_size = 5000
    model = MiniTransformer(vocab_size=vocab_size, d_model=256, num_heads=4, num_layers=4)

    print("Mini Transformer Model")
    print("=" * 60)
    print(f"Vocabulary size: {vocab_size:,}")
    print(f"Model dimension: {model.d_model}")
    print(f"Number of heads: 4")
    print(f"Number of layers: 4")
    print(f"Total parameters: {count_parameters(model):,}")
    print()
    print("🎉 This is the architecture that powers GPT, BERT, and all modern LLMs!")
