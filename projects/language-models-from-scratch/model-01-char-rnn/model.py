"""
Character-level RNN Language Model

This is the simplest language model. It learns to predict the next character
in a sequence by processing one character at a time.

Key Concepts:
- One-hot encoding for characters
- Vanilla RNN cell
- Hidden state carries information through the sequence
- Character-level tokenization
"""

import torch
import torch.nn as nn


class CharRNN(nn.Module):
    """
    A simple character-level RNN language model.

    Architecture:
        Input (one-hot) -> RNN -> Linear -> Output (character probabilities)

    Args:
        vocab_size: Number of unique characters
        hidden_size: Size of the RNN hidden state
        num_layers: Number of stacked RNN layers
        dropout: Dropout probability (0 = no dropout)
    """

    def __init__(
        self,
        vocab_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Embedding layer: converts character indices to dense vectors
        # This is more efficient than one-hot encoding
        self.embedding = nn.Embedding(vocab_size, hidden_size)

        # RNN layer: processes sequences of embedded characters
        # input: (batch, seq_len, hidden_size)
        # output: (batch, seq_len, hidden_size)
        self.rnn = nn.RNN(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)

        # Output layer: converts RNN outputs to character probabilities
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x, hidden=None):
        """
        Forward pass through the model.

        Args:
            x: Input tensor of shape (batch, seq_len) containing character indices
            hidden: Previous hidden state, or None to start fresh

        Returns:
            output: Logits of shape (batch, seq_len, vocab_size)
            hidden: Final hidden state for use in next step
        """
        # Embed the input characters
        # x: (batch, seq_len) -> (batch, seq_len, hidden_size)
        embedded = self.embedding(x)

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
        """
        Initialize hidden state with zeros.

        Args:
            batch_size: Number of sequences in the batch
            device: Device to create tensor on

        Returns:
            Hidden state tensor of shape (num_layers, batch_size, hidden_size)
        """
        return torch.zeros(self.num_layers, batch_size, self.hidden_size, device=device)

    def generate(self, start_char_idx, length, temperature=1.0, device='cpu'):
        """
        Generate text character by character.

        Args:
            start_char_idx: Index of the starting character
            length: Number of characters to generate
            temperature: Sampling temperature (higher = more random)
            device: Device to run on

        Returns:
            List of generated character indices
        """
        self.eval()
        with torch.no_grad():
            # Start with the given character
            input_seq = torch.tensor([[start_char_idx]], device=device)
            hidden = self.init_hidden(1, device)
            generated = [start_char_idx]

            for _ in range(length - 1):
                # Get predictions for next character
                output, hidden = self.forward(input_seq, hidden)

                # Apply temperature
                logits = output[0, -1] / temperature

                # Sample from the distribution
                probs = torch.softmax(logits, dim=0)
                next_char = torch.multinomial(probs, 1).item()

                generated.append(next_char)

                # Use the predicted character as input for next step
                input_seq = torch.tensor([[next_char]], device=device)

        return generated


def count_parameters(model):
    """Count the number of trainable parameters in the model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test the model
    vocab_size = 65  # Example: lowercase + uppercase + digits + punctuation
    model = CharRNN(vocab_size=vocab_size, hidden_size=128, num_layers=2)

    print("Character-level RNN Model")
    print("=" * 50)
    print(f"Vocabulary size: {vocab_size}")
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

    # Test generation
    generated = model.generate(start_char_idx=0, length=50)
    print(f"Generated {len(generated)} character indices")
