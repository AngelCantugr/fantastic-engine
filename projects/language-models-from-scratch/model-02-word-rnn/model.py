"""
Word-level RNN Language Model

This model processes text at the word level instead of characters.
Introduces vocabulary management and word embeddings.

Key Concepts:
- Word tokenization (splitting text into words)
- Vocabulary building and management
- Word embeddings (learned representations)
- Handling unknown words
- More efficient than char-level for coherent text
"""

import torch
import torch.nn as nn


class WordRNN(nn.Module):
    """
    A word-level RNN language model.

    Compared to char-level:
    - Processes words instead of characters
    - Larger vocabulary but shorter sequences
    - Learns word meanings through embeddings
    - More coherent output, but can't spell new words

    Args:
        vocab_size: Number of unique words in vocabulary
        embedding_dim: Size of word embedding vectors
        hidden_size: Size of RNN hidden state
        num_layers: Number of stacked RNN layers
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

        # Word embedding layer
        # This will learn semantic representations of words
        # Similar words will have similar embeddings
        self.embedding = nn.Embedding(vocab_size, embedding_dim)

        # RNN layer - using GRU instead of vanilla RNN
        # GRU is more stable and trains better (we'll learn why in Model 3!)
        self.rnn = nn.GRU(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)

        # Output layer: project to vocabulary
        self.fc = nn.Linear(hidden_size, vocab_size)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights with better defaults."""
        # Initialize embeddings from uniform distribution
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, x, hidden=None):
        """
        Forward pass through the model.

        Args:
            x: Input tensor of shape (batch, seq_len) containing word indices
            hidden: Previous hidden state, or None to start fresh

        Returns:
            output: Logits of shape (batch, seq_len, vocab_size)
            hidden: Final hidden state for use in next step
        """
        # Embed the input words
        # (batch, seq_len) -> (batch, seq_len, embedding_dim)
        embedded = self.embedding(x)
        embedded = self.dropout(embedded)

        # Process through RNN
        # output: (batch, seq_len, hidden_size)
        # hidden: (num_layers, batch, hidden_size)
        output, hidden = self.rnn(embedded, hidden)

        # Apply dropout
        output = self.dropout(output)

        # Project to vocabulary size
        # (batch, seq_len, hidden_size) -> (batch, seq_len, vocab_size)
        output = self.fc(output)

        return output, hidden

    def init_hidden(self, batch_size, device='cpu'):
        """Initialize hidden state with zeros."""
        return torch.zeros(self.num_layers, batch_size, self.hidden_size, device=device)

    def generate(self, start_word_idx, word_to_idx, idx_to_word, max_length=100,
                 temperature=1.0, device='cpu'):
        """
        Generate text word by word.

        Args:
            start_word_idx: Index of the starting word
            word_to_idx: Word to index mapping (for <unk> handling)
            idx_to_word: Index to word mapping
            max_length: Maximum number of words to generate
            temperature: Sampling temperature
            device: Device to run on

        Returns:
            List of generated words
        """
        self.eval()
        with torch.no_grad():
            # Start with the given word
            input_seq = torch.tensor([[start_word_idx]], device=device)
            hidden = self.init_hidden(1, device)
            generated = [idx_to_word[start_word_idx]]

            # Special tokens
            eos_idx = word_to_idx.get('<eos>', word_to_idx.get('.', None))

            for _ in range(max_length - 1):
                # Get predictions for next word
                output, hidden = self.forward(input_seq, hidden)

                # Apply temperature
                logits = output[0, -1] / temperature

                # Sample from the distribution
                probs = torch.softmax(logits, dim=0)
                next_word_idx = torch.multinomial(probs, 1).item()

                # Stop if we hit end of sentence (optional)
                if eos_idx is not None and next_word_idx == eos_idx:
                    generated.append(idx_to_word[next_word_idx])
                    # 30% chance to actually stop (makes generation more natural)
                    if torch.rand(1).item() < 0.3:
                        break

                generated.append(idx_to_word[next_word_idx])

                # Use the predicted word as input for next step
                input_seq = torch.tensor([[next_word_idx]], device=device)

        return generated


def count_parameters(model):
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test the model
    vocab_size = 5000  # Typical small vocabulary
    model = WordRNN(vocab_size=vocab_size, embedding_dim=256, hidden_size=512, num_layers=2)

    print("Word-level RNN Model")
    print("=" * 50)
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

    output, hidden = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Hidden shape: {hidden.shape}")
    print()

    # Compare with char-level RNN
    char_vocab = 65
    char_model_params = (char_vocab * 256) + (256 * 512 * 2) + (512 * 65)
    print("Comparison with char-level RNN:")
    print(f"  Char-level parameters: ~{char_model_params:,}")
    print(f"  Word-level parameters: {count_parameters(model):,}")
    print(f"  Word-level is {count_parameters(model) / char_model_params:.1f}x larger")
    print(f"  But processes {vocab_size / char_vocab:.1f}x more tokens per step!")
