#!/usr/bin/env python3
"""
Training script for Mini Transformer

First transformer model! This will take longer to train but produces better results.
"""

import sys
from pathlib import Path

# Reuse infrastructure from Model 2
model2_path = Path(__file__).parent.parent / "model-02-word-rnn"
sys.path.insert(0, str(model2_path))

from train import Vocabulary, WordDataset, evaluate as base_evaluate
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import time

sys.path.insert(0, str(Path(__file__).parent))
from model import MiniTransformer, count_parameters


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    start_time = time.time()

    for batch_idx, (inputs, targets) in enumerate(dataloader):
        inputs = inputs.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()

        # Forward
        outputs = model(inputs)

        # Loss
        loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

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
            outputs = model(inputs)
            loss = criterion(outputs.view(-1, model.vocab_size), targets.view(-1))
            total_loss += loss.item()

    return total_loss / len(dataloader)


def generate_sample(model, vocab, start_text="", length=50, temperature=0.8, device='cpu'):
    """Generate sample."""
    import re

    if not start_text:
        start_text = "the"

    tokens = re.findall(r'\b\w+\b|[.,!?;:\'\"-]', start_text.lower())
    start_idx = vocab.word_to_idx.get(tokens[-1] if tokens else "the", 1)

    generated = model.generate(start_idx, vocab.idx_to_word, length, temperature, device)
    return ' '.join(generated)


def main():
    # Hyperparameters
    MAX_VOCAB_SIZE = 8000
    MIN_WORD_FREQ = 3
    D_MODEL = 256
    NUM_HEADS = 4
    NUM_LAYERS = 4
    D_FF = 1024
    DROPOUT = 0.1
    SEQ_LENGTH = 64  # Transformers handle longer sequences better
    BATCH_SIZE = 32
    LEARNING_RATE = 0.0001  # Lower LR for transformers
    NUM_EPOCHS = 20

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    print()

    # Load data
    data_path = Path(__file__).parent.parent / "shared" / "data" / "tiny_shakespeare.txt"

    if not data_path.exists():
        print("Error: Data file not found")
        print("Run: python shared/data/download.py")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        text = f.read()

    split_idx = int(0.9 * len(text))
    train_text = text[:split_idx]
    val_text = text[split_idx:]

    # Build vocabulary
    vocab = Vocabulary(max_vocab_size=MAX_VOCAB_SIZE, min_freq=MIN_WORD_FREQ)
    vocab.build_from_text(train_text)

    # Datasets
    train_dataset = WordDataset(train_text, vocab, SEQ_LENGTH)
    val_dataset = WordDataset(val_text, vocab, SEQ_LENGTH)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Create Transformer model
    model = MiniTransformer(
        vocab_size=len(vocab),
        d_model=D_MODEL,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS,
        d_ff=D_FF,
        dropout=DROPOUT
    ).to(device)

    print("🎉 Mini Transformer Model")
    print("=" * 60)
    print("This is THE architecture behind GPT, BERT, and modern LLMs!")
    print(f"\nTotal parameters: {count_parameters(model):,}")
    print()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    checkpoint_dir = Path(__file__).parent / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    best_val_loss = float('inf')
    print("Training Mini Transformer...")
    print("=" * 70)

    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")
        print("-" * 70)

        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        val_loss = evaluate(model, val_loader, criterion, device)

        scheduler.step()

        print(f"\nEpoch {epoch + 1} Summary:")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss: {val_loss:.4f}")
        print(f"  Perplexity: {torch.exp(torch.tensor(val_loss)):.2f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'vocab': {
                    'word_to_idx': vocab.word_to_idx,
                    'idx_to_word': vocab.idx_to_word,
                },
                'hyperparameters': {
                    'd_model': D_MODEL,
                    'num_heads': NUM_HEADS,
                    'num_layers': NUM_LAYERS,
                    'd_ff': D_FF,
                    'dropout': DROPOUT,
                }
            }, checkpoint_dir / "best.pt")
            print(f"  ✓ Saved best model")

        if (epoch + 1) % 5 == 0:
            print("\n  Sample generations:")
            for prompt in ["To be", "The king"]:
                sample = generate_sample(model, vocab, prompt, 30, device=device)
                print(f"  {prompt}: {sample}")

    print("\n" + "=" * 70)
    print(f"Training complete! Best val loss: {best_val_loss:.4f}")
    print("You've trained your first transformer! 🎉")


if __name__ == "__main__":
    main()
