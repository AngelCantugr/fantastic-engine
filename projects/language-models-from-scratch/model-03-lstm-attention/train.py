#!/usr/bin/env python3
"""
Training script for LSTM with Attention

Similar to Model 2, but uses LSTM and attention mechanism.
"""

import sys
from pathlib import Path

# Reuse Model 2's training infrastructure
model2_path = Path(__file__).parent.parent / "model-02-word-rnn"
sys.path.insert(0, str(model2_path))

from train import Vocabulary, WordDataset, evaluate, main as base_main
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import time

sys.path.insert(0, str(Path(__file__).parent))
from model import LSTMAttentionLM, count_parameters


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    start_time = time.time()

    for batch_idx, (inputs, targets) in enumerate(dataloader):
        inputs = inputs.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()

        # Forward (don't need attention weights during training)
        outputs, _ = model(inputs)

        loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()

        total_loss += loss.item()

        if (batch_idx + 1) % 50 == 0:
            elapsed = time.time() - start_time
            print(f"  Batch {batch_idx + 1}/{len(dataloader)} | "
                  f"Loss: {loss.item():.4f} | "
                  f"Time: {elapsed:.1f}s")

    return total_loss / len(dataloader)


def generate_sample(model, vocab, start_text="", length=50, temperature=0.8, device='cpu'):
    """Generate sample text."""
    import re

    if not start_text:
        start_text = "the"

    tokens = re.findall(r'\b\w+\b|[.,!?;:\'\"-]', start_text.lower())
    if not tokens:
        tokens = ["the"]

    start_word = tokens[-1]
    start_idx = vocab.word_to_idx.get(start_word, vocab.word_to_idx[vocab.unk_token])

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
    # Hyperparameters (similar to Model 2 but slightly different)
    MAX_VOCAB_SIZE = 8000
    MIN_WORD_FREQ = 3
    EMBEDDING_DIM = 256
    HIDDEN_SIZE = 512
    NUM_LAYERS = 2
    DROPOUT = 0.3
    SEQ_LENGTH = 50
    BATCH_SIZE = 32  # Smaller because attention is more memory-intensive
    LEARNING_RATE = 0.001
    NUM_EPOCHS = 20

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

    split_idx = int(0.9 * len(text))
    train_text = text[:split_idx]
    val_text = text[split_idx:]

    # Build vocabulary
    print("Building vocabulary...")
    vocab = Vocabulary(max_vocab_size=MAX_VOCAB_SIZE, min_freq=MIN_WORD_FREQ)
    vocab.build_from_text(train_text)
    print()

    # Create datasets
    train_dataset = WordDataset(train_text, vocab, SEQ_LENGTH)
    val_dataset = WordDataset(val_text, vocab, SEQ_LENGTH)
    print()

    # Dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Create model with ATTENTION!
    model = LSTMAttentionLM(
        vocab_size=len(vocab),
        embedding_dim=EMBEDDING_DIM,
        hidden_size=HIDDEN_SIZE,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT
    ).to(device)

    print("Model Architecture: LSTM + Attention")
    print("=" * 60)
    print(model)
    print(f"\nTotal parameters: {count_parameters(model):,}")
    print("Note: More parameters than Model 2 due to attention mechanism!")
    print()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

    checkpoint_dir = Path(__file__).parent / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    best_val_loss = float('inf')
    print("Starting training with ATTENTION mechanism...")
    print("=" * 70)

    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")
        print("-" * 70)

        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        val_loss = evaluate(model, val_loader, criterion, device)

        scheduler.step(val_loss)

        print(f"\nEpoch {epoch + 1} Summary:")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss: {val_loss:.4f}")
        print(f"  Perplexity: {torch.exp(torch.tensor(val_loss)):.2f}")

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
                },
                'hyperparameters': {
                    'embedding_dim': EMBEDDING_DIM,
                    'hidden_size': HIDDEN_SIZE,
                    'num_layers': NUM_LAYERS,
                    'dropout': DROPOUT,
                }
            }, checkpoint_path)
            print(f"  ✓ Saved best model")

        if (epoch + 1) % 5 == 0:
            print("\n  Sample generations:")
            print("  " + "-" * 66)
            for prompt in ["To be", "The king", "What is"]:
                sample = generate_sample(model, vocab, start_text=prompt, length=30, device=device)
                print(f"  {prompt}: {sample}")
            print("  " + "-" * 66)

    print("\n" + "=" * 70)
    print("Training complete!")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print("The model now uses attention to focus on relevant past words!")


if __name__ == "__main__":
    main()
