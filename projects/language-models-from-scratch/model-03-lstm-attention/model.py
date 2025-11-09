"""
LSTM with Attention Language Model

This model introduces the attention mechanism - the foundation of modern LLMs!

Key Concepts:
- LSTM cells (better than RNN/GRU at long-term memory)
- Attention mechanism (selectively focus on relevant parts of input)
- Context vector (weighted summary of all inputs)
- Attention weights (which inputs are important)
- Preparation for transformers!
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class Attention(nn.Module):
    """
    Simple additive attention mechanism (Bahdanau attention).

    Attention answers: "Which past words should I focus on to predict the next word?"

    For example:
        Input: "The cat sat on the mat"
        Predicting: "and" (next word)
        Attention might focus on: "sat", "mat" (verbs and objects)
        Less attention on: "the" (not informative)
    """

    def __init__(self, hidden_size):
        super().__init__()

        # Attention parameters
        # These learn what to pay attention to!
        self.attention = nn.Linear(hidden_size * 2, hidden_size)
        self.v = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, hidden, encoder_outputs):
        """
        Compute attention weights and context vector.

        Args:
            hidden: Current hidden state (num_layers, batch, hidden_size)
            encoder_outputs: All previous outputs (batch, seq_len, hidden_size)

        Returns:
            context: Weighted sum of encoder outputs (batch, hidden_size)
            attention_weights: Weights for visualization (batch, seq_len)
        """
        # Get the last layer's hidden state
        # (num_layers, batch, hidden_size) -> (batch, hidden_size)
        batch_size = encoder_outputs.size(0)
        seq_len = encoder_outputs.size(1)

        # Use last layer's hidden state
        h = hidden[-1]  # (batch, hidden_size)

        # Repeat hidden state for all time steps
        # (batch, hidden_size) -> (batch, seq_len, hidden_size)
        h = h.unsqueeze(1).repeat(1, seq_len, 1)

        # Concatenate hidden with each encoder output
        # (batch, seq_len, hidden_size * 2)
        energy = torch.cat((h, encoder_outputs), dim=2)

        # Calculate attention scores
        # (batch, seq_len, hidden_size * 2) -> (batch, seq_len, hidden_size)
        energy = torch.tanh(self.attention(energy))

        # (batch, seq_len, hidden_size) -> (batch, seq_len, 1) -> (batch, seq_len)
        attention_scores = self.v(energy).squeeze(2)

        # Normalize to get attention weights (probabilities)
        attention_weights = F.softmax(attention_scores, dim=1)

        # Apply attention weights to encoder outputs
        # (batch, seq_len, hidden_size) * (batch, seq_len, 1) -> (batch, hidden_size)
        context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs)
        context = context.squeeze(1)  # (batch, hidden_size)

        return context, attention_weights


class LSTMAttentionLM(nn.Module):
    """
    LSTM Language Model with Attention.

    Architecture:
        Embedding -> LSTM -> Attention -> Combine -> Linear -> Output

    The attention mechanism allows the model to focus on relevant past words
    when predicting the next word.

    Args:
        vocab_size: Number of unique words
        embedding_dim: Size of word embeddings
        hidden_size: Size of LSTM hidden state
        num_layers: Number of LSTM layers
        dropout: Dropout probability
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 256,
        hidden_size: int = 512,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Word embedding
        self.embedding = nn.Embedding(vocab_size, embedding_dim)

        # LSTM instead of GRU
        # LSTM has both hidden state (h) and cell state (c)
        # Better at capturing long-term dependencies!
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        # Attention mechanism
        self.attention = Attention(hidden_size)

        # Combine LSTM output with attention context
        self.combine = nn.Linear(hidden_size * 2, hidden_size)

        # Dropout
        self.dropout = nn.Dropout(dropout)

        # Output layer
        self.fc = nn.Linear(hidden_size, vocab_size)

        self._init_weights()

    def _init_weights(self):
        """Initialize weights."""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, x, hidden=None, return_attention=False):
        """
        Forward pass with attention.

        Args:
            x: Input (batch, seq_len)
            hidden: Previous hidden state (tuple of h and c)
            return_attention: Whether to return attention weights

        Returns:
            output: Logits (batch, seq_len, vocab_size)
            hidden: Final hidden state (tuple)
            attention_weights: If return_attention=True (batch, seq_len, seq_len)
        """
        # Embed
        embedded = self.embedding(x)
        embedded = self.dropout(embedded)

        # LSTM
        lstm_out, hidden = self.lstm(embedded, hidden)
        lstm_out = self.dropout(lstm_out)

        # Apply attention at each position
        batch_size, seq_len, _ = lstm_out.size()

        attended_outputs = []
        all_attention_weights = [] if return_attention else None

        for t in range(seq_len):
            # For position t, attend to all positions 0..t
            if t == 0:
                # No context for first token, just use LSTM output
                attended = lstm_out[:, t, :]
                if return_attention:
                    all_attention_weights.append(torch.zeros(batch_size, 1, device=x.device))
            else:
                # Attend to all previous positions
                encoder_outputs = lstm_out[:, :t+1, :]  # (batch, t+1, hidden)
                h_state = hidden[0]  # hidden is tuple (h, c)

                # Get context from attention
                context, attn_weights = self.attention(h_state, encoder_outputs)

                # Combine LSTM output with attention context
                combined = torch.cat((lstm_out[:, t, :], context), dim=1)
                attended = torch.tanh(self.combine(combined))

                if return_attention:
                    # Pad attention weights to seq_len for visualization
                    padded_attn = torch.zeros(batch_size, seq_len, device=x.device)
                    padded_attn[:, :t+1] = attn_weights
                    all_attention_weights.append(padded_attn)

            attended_outputs.append(attended)

        # Stack all positions
        output = torch.stack(attended_outputs, dim=1)  # (batch, seq_len, hidden)
        output = self.dropout(output)

        # Project to vocabulary
        output = self.fc(output)  # (batch, seq_len, vocab_size)

        if return_attention:
            # Stack attention weights: (batch, seq_len, seq_len)
            attention_weights = torch.stack(all_attention_weights, dim=1)
            return output, hidden, attention_weights

        return output, hidden

    def init_hidden(self, batch_size, device='cpu'):
        """Initialize LSTM hidden state (h and c)."""
        h = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=device)
        c = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=device)
        return (h, c)

    def generate(self, start_word_idx, word_to_idx, idx_to_word, max_length=100,
                 temperature=1.0, device='cpu'):
        """Generate text word by word."""
        self.eval()
        with torch.no_grad():
            input_seq = torch.tensor([[start_word_idx]], device=device)
            hidden = self.init_hidden(1, device)
            generated = [idx_to_word[start_word_idx]]

            eos_idx = word_to_idx.get('<eos>', word_to_idx.get('.', None))

            for _ in range(max_length - 1):
                output, hidden = self.forward(input_seq, hidden)

                logits = output[0, -1] / temperature
                probs = torch.softmax(logits, dim=0)
                next_word_idx = torch.multinomial(probs, 1).item()

                if eos_idx is not None and next_word_idx == eos_idx:
                    generated.append(idx_to_word[next_word_idx])
                    if torch.rand(1).item() < 0.3:
                        break

                generated.append(idx_to_word[next_word_idx])
                input_seq = torch.tensor([[next_word_idx]], device=device)

        return generated


def count_parameters(model):
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test the model
    vocab_size = 5000
    model = LSTMAttentionLM(vocab_size=vocab_size, embedding_dim=256, hidden_size=512, num_layers=2)

    print("LSTM with Attention Language Model")
    print("=" * 60)
    print(f"Vocabulary size: {vocab_size:,}")
    print(f"Embedding dimension: {model.embedding_dim}")
    print(f"Hidden size: {model.hidden_size}")
    print(f"Number of layers: {model.num_layers}")
    print(f"Total parameters: {count_parameters(model):,}")
    print()

    # Test forward pass
    batch_size = 4
    seq_len = 20
    x = torch.randint(0, vocab_size, (batch_size, seq_len))

    output, hidden, attn_weights = model(x, return_attention=True)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Hidden state shape: {hidden[0].shape}")
    print(f"Cell state shape: {hidden[1].shape}")
    print(f"Attention weights shape: {attn_weights.shape}")
    print()

    print("Attention mechanism allows the model to focus on relevant past words!")
    print("This is the foundation of transformers (Models 4 & 5)")
