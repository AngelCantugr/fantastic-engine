#!/usr/bin/env python3
"""
Training script for Word-level RNN

Introduces vocabulary building, word tokenization, and handling unknown words.
"""

import os
import sys
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import time
import json
from collections import Counter
import re

sys.path.append(str(Path(__file__).parent))
from model import WordRNN, count_parameters


class Vocabulary:
    """
    Vocabulary builder and manager.

    Handles:
    - Building vocabulary from text
    - Word to index mapping
    - Special tokens (unknown, padding)
    - Frequency-based filtering
    """

    def __init__(self, max_vocab_size=10000, min_freq=2):
        self.max_vocab_size = max_vocab_size
        self.min_freq = min_freq

        # Special tokens
        self.pad_token = '<pad>'
        self.unk_token = '<unk>'
        self.eos_token = '<eos>'

        self.word_to_idx = {}
        self.idx_to_word = {}
        self.word_freq = Counter()

    def build_from_text(self, text):
        """Build vocabulary from text."""
        # Tokenize
        words = self.tokenize(text)

        # Count frequencies
        self.word_freq = Counter(words)

        # Get most common words
        most_common = self.word_freq.most_common(self.max_vocab_size - 3)  # -3 for special tokens

        # Filter by minimum frequency
        vocab_words = [word for word, freq in most_common if freq >= self.min_freq]

        # Build mappings
        # Special tokens go first
        self.word_to_idx = {
            self.pad_token: 0,
            self.unk_token: 1,
            self.eos_token: 2,
        }

        for idx, word in enumerate(vocab_words, start=3):
            self.word_to_idx[word] = idx

        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}

        print(f"Built vocabulary:")
        print(f"  Total unique words in text: {len(self.word_freq):,}")
        print(f"  Vocabulary size: {len(self.word_to_idx):,}")
        print(f"  Coverage: {self.calculate_coverage(words):.2%}")

    def tokenize(self, text):
        """
        Simple word tokenization.

        Converts: "Hello, world!" -> ["hello", ",", "world", "!"]
        """
        # Convert to lowercase
        text = text.lower()

        # Split on whitespace and punctuation (but keep punctuation)
        # This regex keeps punctuation as separate tokens
        words = re.findall(r'\b\w+\b|[.,!?;:\'\"-]', text)

        return words

    def encode(self, text):
        """Convert text to indices."""
        words = self.tokenize(text)
        indices = [self.word_to_idx.get(word, self.word_to_idx[self.unk_token]) for word in words]
        return indices

    def decode(self, indices):
        """Convert indices back to text."""
        words = [self.idx_to_word.get(idx, self.unk_token) for idx in indices]
        return ' '.join(words)

    def calculate_coverage(self, words):
        """Calculate what percentage of words are in vocabulary."""
        known_words = sum(1 for word in words if word in self.word_to_idx)
        return known_words / len(words) if words else 0

    def __len__(self):
        return len(self.word_to_idx)


class WordDataset(Dataset):
    """Dataset for word-level language modeling."""

    def __init__(self, text, vocab, seq_length=50):
        self.vocab = vocab
        self.seq_length = seq_length

        # Encode text
        self.data = vocab.encode(text)

        print(f"Dataset created:")
        print(f"  Total tokens: {len(self.data):,}")
        print(f"  Sequence length: {seq_length}")
        print(f"  Number of sequences: {len(self):,}")

    def __len__(self):
        return max(0, len(self.data) - self.seq_length)

    def __getitem__(self, idx):
        # Input and target (shifted by 1)
        input_seq = torch.tensor(self.data[idx:idx + self.seq_length], dtype=torch.long)
        target_seq = torch.tensor(self.data[idx + 1:idx + self.seq_length + 1], dtype=torch.long)
        return input_seq, target_seq


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    start_time = time.time()

    for batch_idx, (inputs, targets) in enumerate(dataloader):
        inputs = inputs.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()

        # Forward pass
        outputs, _ = model(inputs)

        # Calculate loss
        loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))

        # Backward pass
        loss.backward()

        # Clip gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)

        optimizer.step()

        total_loss += loss.item()

        if (batch_idx + 1) % 50 == 0:
            elapsed = time.time() - start_time
            print(f"  Batch {batch_idx + 1}/{len(dataloader)} | "
                  f"Loss: {loss.item():.4f} | "
                  f"Time: {elapsed:.1f}s")

    return total_loss / len(dataloader)


def evaluate(model, dataloader, criterion, device):
    """Evaluate the model."""
    model.eval()
    total_loss = 0

    with torch.no_grad():
        for inputs, targets in dataloader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            outputs, _ = model(inputs)
            loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))
            total_loss += loss.item()

    return total_loss / len(dataloader)


def generate_sample(model, vocab, start_text="", length=50, temperature=0.8, device='cpu'):
    """Generate a sample text."""
    if not start_text:
        start_text = "the"

    # Tokenize start text
    tokens = vocab.tokenize(start_text.lower())
    if not tokens:
        tokens = ["the"]

    # Get the last word
    start_word = tokens[-1]
    start_idx = vocab.word_to_idx.get(start_word, vocab.word_to_idx[vocab.unk_token])

    # Generate
    generated_words = model.generate(
        start_idx,
        vocab.word_to_idx,
        vocab.idx_to_word,
        max_length=length,
        temperature=temperature,
        device=device
    )

    return ' '.join(generated_words)


def main():
    # Hyperparameters
    MAX_VOCAB_SIZE = 8000
    MIN_WORD_FREQ = 3
    EMBEDDING_DIM = 256
    HIDDEN_SIZE = 512
    NUM_LAYERS = 2
    DROPOUT = 0.3
    SEQ_LENGTH = 50
    BATCH_SIZE = 64
    LEARNING_RATE = 0.001
    NUM_EPOCHS = 25

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    print()

    # Load data
    data_path = Path(__file__).parent.parent / "shared" / "data" / "tiny_shakespeare.txt"

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        print("Please run: python shared/data/download.py")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Loaded {len(text):,} characters")

    # Split data
    split_idx = int(0.9 * len(text))
    train_text = text[:split_idx]
    val_text = text[split_idx:]

    print(f"Training set: {len(train_text):,} characters")
    print(f"Validation set: {len(val_text):,} characters")
    print()

    # Build vocabulary
    print("Building vocabulary...")
    vocab = Vocabulary(max_vocab_size=MAX_VOCAB_SIZE, min_freq=MIN_WORD_FREQ)
    vocab.build_from_text(train_text)
    print()

    # Create datasets
    train_dataset = WordDataset(train_text, vocab, SEQ_LENGTH)
    print()
    val_dataset = WordDataset(val_text, vocab, SEQ_LENGTH)
    print()

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Create model
    model = WordRNN(
        vocab_size=len(vocab),
        embedding_dim=EMBEDDING_DIM,
        hidden_size=HIDDEN_SIZE,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)

    print("Model Architecture:")
    print(model)
    print(f"\nTotal parameters: {count_parameters(model):,}")
    print()

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

    # Create checkpoint directory
    checkpoint_dir = Path(__file__).parent / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    # Training loop
    best_val_loss = float('inf')
    print("Starting training...")
    print("=" * 70)

    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")
        print("-" * 70)

        # Train
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)

        # Validate
        val_loss = evaluate(model, val_loader, criterion, device)

        # Update learning rate
        scheduler.step(val_loss)

        print(f"\nEpoch {epoch + 1} Summary:")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss: {val_loss:.4f}")
        print(f"  Perplexity: {torch.exp(torch.tensor(val_loss)):.2f}")
        print(f"  Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint_path = checkpoint_dir / "best.pt"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'vocab': {
                    'word_to_idx': vocab.word_to_idx,
                    'idx_to_word': vocab.idx_to_word,
                    'word_freq': dict(vocab.word_freq.most_common(1000)),  # Save top 1000 for reference
                },
                'hyperparameters': {
                    'embedding_dim': EMBEDDING_DIM,
                    'hidden_size': HIDDEN_SIZE,
                    'num_layers': NUM_LAYERS,
                    'dropout': DROPOUT,
                }
            }, checkpoint_path)
            print(f"  ✓ Saved best model (val_loss: {val_loss:.4f})")

        # Generate sample every 5 epochs
        if (epoch + 1) % 5 == 0:
            print("\n  Sample generations:")
            print("  " + "-" * 66)

            prompts = ["To be or not to be", "What is", "The king"]
            for prompt in prompts:
                sample = generate_sample(model, vocab, start_text=prompt, length=30, device=device)
                print(f"  Prompt: '{prompt}'")
                print(f"  → {sample}")
                print()

            print("  " + "-" * 66)

    print("\n" + "=" * 70)
    print("Training complete!")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Best perplexity: {torch.exp(torch.tensor(best_val_loss)):.2f}")
    print(f"Model saved to: {checkpoint_dir / 'best.pt'}")


if __name__ == "__main__":
    main()
