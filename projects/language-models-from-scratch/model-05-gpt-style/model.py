"""
GPT-style Language Model

The full GPT architecture! This is what powers ChatGPT, GPT-3, GPT-4, etc.

Based on "Language Models are Unsupervised Multitask Learners" (GPT-2 paper)

Key Concepts:
- BPE tokenization (subword level)
- Scaled transformer architecture
- Improved training techniques
- Modern normalization (pre-norm)
- GELU activation
- Dropout and weight decay
- This is production-grade architecture!
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class GELU(nn.Module):
    """
    GELU activation function.
    Used in GPT instead of ReLU for smoother gradients.
    """

    def forward(self, x):
        return 0.5 * x * (1.0 + torch.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * torch.pow(x, 3.0))))


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention (GPT-style)."""

    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()

        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        # Combined QKV projection (more efficient)
        self.qkv = nn.Linear(d_model, 3 * d_model)

        # Output projection
        self.out_proj = nn.Linear(d_model, d_model)

        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        B, T, C = x.size()  # batch, sequence length, embedding dimensionality

        # Calculate Q, K, V
        qkv = self.qkv(x)
        q, k, v = qkv.split(self.d_model, dim=2)

        # Reshape for multi-head attention
        q = q.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)

        # Attention scores
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))

        if mask is not None:
            att = att.masked_fill(mask == 0, float('-inf'))

        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)

        # Apply attention to values
        y = att @ v  # (B, num_heads, T, head_dim)
        y = y.transpose(1, 2).contiguous().view(B, T, C)

        # Output projection
        y = self.resid_dropout(self.out_proj(y))

        return y


class FeedForward(nn.Module):
    """Position-wise feed-forward network (GPT-style)."""

    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()

        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = GELU()  # GPT uses GELU instead of ReLU

    def forward(self, x):
        x = self.fc1(x)
        x = self.activation(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class GPTBlock(nn.Module):
    """
    GPT Transformer Block.

    Key difference from basic transformer: Pre-norm instead of post-norm
    This is more stable for training large models!
    """

    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        self.ln1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, num_heads, dropout)

        self.ln2 = nn.LayerNorm(d_model)
        self.mlp = FeedForward(d_model, d_ff, dropout)

    def forward(self, x, mask=None):
        # Pre-norm: normalize BEFORE attention
        x = x + self.attn(self.ln1(x), mask)

        # Pre-norm: normalize BEFORE feed-forward
        x = x + self.mlp(self.ln2(x))

        return x


class GPT(nn.Module):
    """
    GPT: Generative Pre-trained Transformer

    This is the real deal - the architecture used in GPT-2, GPT-3, etc.
    Scaled down for educational purposes but architecturally identical!

    Args:
        vocab_size: Size of vocabulary (BPE tokens)
        d_model: Model dimension
        num_heads: Number of attention heads
        num_layers: Number of transformer blocks
        max_len: Maximum sequence length
        dropout: Dropout probability
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        max_len: int = 512,
        dropout: float = 0.1
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.d_model = d_model
        self.max_len = max_len

        # Token embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)

        # Positional embeddings (learned, not sinusoidal!)
        # GPT-2 uses learned positional embeddings
        self.position_embedding = nn.Embedding(max_len, d_model)

        self.drop = nn.Dropout(dropout)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            GPTBlock(d_model, num_heads, d_model * 4, dropout)
            for _ in range(num_layers)
        ])

        # Final layer norm
        self.ln_f = nn.LayerNorm(d_model)

        # Output head
        self.head = nn.Linear(d_model, vocab_size, bias=False)

        # Tie weights: token embedding and output projection share weights
        # This is a standard trick in transformers!
        self.token_embedding.weight = self.head.weight

        print(f"Number of parameters: {self.count_parameters():,}")

    def count_parameters(self):
        """Count parameters."""
        return sum(p.numel() for p in self.parameters())

    def _create_causal_mask(self, size, device):
        """Create causal mask."""
        mask = torch.tril(torch.ones(size, size, device=device))
        return mask.view(1, 1, size, size)

    def forward(self, idx):
        """
        Forward pass.

        Args:
            idx: Input indices (batch, seq_len)

        Returns:
            logits: Output logits (batch, seq_len, vocab_size)
        """
        b, t = idx.size()
        assert t <= self.max_len, f"Sequence length {t} exceeds maximum {self.max_len}"

        # Token embeddings
        tok_emb = self.token_embedding(idx)  # (b, t, d_model)

        # Position embeddings
        pos = torch.arange(0, t, dtype=torch.long, device=idx.device).unsqueeze(0)  # (1, t)
        pos_emb = self.position_embedding(pos)  # (1, t, d_model)

        # Combine
        x = self.drop(tok_emb + pos_emb)

        # Create causal mask
        mask = self._create_causal_mask(t, idx.device)

        # Apply transformer blocks
        for block in self.blocks:
            x = block(x, mask)

        # Final layer norm
        x = self.ln_f(x)

        # Project to vocabulary
        logits = self.head(x)

        return logits

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        """
        Generate new tokens.

        Args:
            idx: Starting indices (batch, seq_len)
            max_new_tokens: Number of tokens to generate
            temperature: Sampling temperature
            top_k: If set, only sample from top k tokens

        Returns:
            Generated indices (batch, seq_len + max_new_tokens)
        """
        self.eval()

        for _ in range(max_new_tokens):
            # Crop context if needed
            idx_cond = idx if idx.size(1) <= self.max_len else idx[:, -self.max_len:]

            # Forward pass
            logits = self.forward(idx_cond)

            # Get last token logits
            logits = logits[:, -1, :] / temperature

            # Optionally apply top-k filtering
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float('-inf')

            # Sample
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)

            # Append to sequence
            idx = torch.cat((idx, idx_next), dim=1)

        return idx


if __name__ == "__main__":
    # Test the model
    vocab_size = 50257  # GPT-2 vocabulary size
    model = GPT(vocab_size=vocab_size, d_model=512, num_heads=8, num_layers=6)

    print("\n" + "=" * 60)
    print("GPT Model - Production Architecture!")
    print("=" * 60)
    print(f"Vocabulary size: {vocab_size:,}")
    print(f"Model dimension: {model.d_model}")
    print(f"Number of heads: 8")
    print(f"Number of layers: 6")
    print()
    print("🎉 This is the EXACT architecture used in GPT-2!")
    print("   Only difference: we'll train on less data")
    print("=" * 60)
