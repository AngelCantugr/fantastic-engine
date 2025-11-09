#!/usr/bin/env python3
"""
Training script for Character-level RNN

This script trains the model on Tiny Shakespeare dataset.
It's designed to be simple and educational, with lots of comments!
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

# Add parent directory to path to import model
sys.path.append(str(Path(__file__).parent))
from model import CharRNN, count_parameters


class CharDataset(Dataset):
    """
    Dataset for character-level language modeling.

    Splits text into sequences of fixed length and creates
    (input, target) pairs where target is input shifted by 1.
    """

    def __init__(self, text, seq_length):
        self.text = text
        self.seq_length = seq_length

        # Create character vocabulary
        self.chars = sorted(list(set(text)))
        self.vocab_size = len(self.chars)

        # Create mappings
        self.char_to_idx = {ch: i for i, ch in enumerate(self.chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(self.chars)}

        # Convert text to indices
        self.data = [self.char_to_idx[ch] for ch in text]

    def __len__(self):
        # Number of complete sequences we can make
        return len(self.data) - self.seq_length

    def __getitem__(self, idx):
        # Input: characters at positions [idx : idx + seq_length]
        # Target: characters at positions [idx + 1 : idx + seq_length + 1]
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

        # Zero gradients
        optimizer.zero_grad()

        # Forward pass
        outputs, _ = model(inputs)

        # Calculate loss
        # outputs: (batch, seq_len, vocab_size)
        # targets: (batch, seq_len)
        # We need to reshape for CrossEntropyLoss
        loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))

        # Backward pass
        loss.backward()

        # Clip gradients to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)

        # Update weights
        optimizer.step()

        total_loss += loss.item()

        # Print progress every 100 batches
        if (batch_idx + 1) % 100 == 0:
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


def generate_sample(model, dataset, length=200, temperature=0.8, device='cpu'):
    """Generate a sample text."""
    # Start with a random character
    start_idx = dataset.char_to_idx['\n']  # Start with newline

    # Generate
    generated_indices = model.generate(start_idx, length, temperature, device)

    # Convert back to text
    generated_text = ''.join([dataset.idx_to_char[idx] for idx in generated_indices])

    return generated_text


def main():
    # Hyperparameters
    HIDDEN_SIZE = 256
    NUM_LAYERS = 2
    DROPOUT = 0.2
    SEQ_LENGTH = 100
    BATCH_SIZE = 64
    LEARNING_RATE = 0.002
    NUM_EPOCHS = 30

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

    # Create datasets
    train_dataset = CharDataset(train_text, SEQ_LENGTH)
    val_dataset = CharDataset(val_text, SEQ_LENGTH)

    print(f"Vocabulary size: {train_dataset.vocab_size}")
    print(f"Characters: {repr(''.join(train_dataset.chars[:20]))}... (showing first 20)")
    print()

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Create model
    model = CharRNN(
        vocab_size=train_dataset.vocab_size,
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
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

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
                'vocab_size': train_dataset.vocab_size,
                'char_to_idx': train_dataset.char_to_idx,
                'idx_to_char': train_dataset.idx_to_char,
                'hyperparameters': {
                    'hidden_size': HIDDEN_SIZE,
                    'num_layers': NUM_LAYERS,
                    'dropout': DROPOUT,
                }
            }, checkpoint_path)
            print(f"  ✓ Saved best model (val_loss: {val_loss:.4f})")

        # Generate sample every 5 epochs
        if (epoch + 1) % 5 == 0:
            print("\n  Sample generation:")
            sample = generate_sample(model, train_dataset, length=200, device=device)
            print("  " + "-" * 66)
            # Print first 200 chars of sample, indented
            for line in sample.split('\n'):
                print(f"  {line}")
            print("  " + "-" * 66)

    print("\n" + "=" * 70)
    print("Training complete!")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Model saved to: {checkpoint_dir / 'best.pt'}")


if __name__ == "__main__":
    main()
