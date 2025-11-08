#!/usr/bin/env python3
"""
Training script for GPT-style model

Uses tiktoken for BPE tokenization (same as GPT-2/3/4)
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import tiktoken
import time

sys.path.append(str(Path(__file__).parent))
from model import GPT


class GPTDataset(Dataset):
    """Dataset with BPE tokenization."""

    def __init__(self, text, seq_length=256):
        # Use GPT-2 tokenizer
        self.enc = tiktoken.get_encoding("gpt2")
        self.seq_length = seq_length

        # Encode text
        self.tokens = self.enc.encode(text)

        print(f"Dataset: {len(self.tokens):,} tokens, {len(self)} sequences")

    def __len__(self):
        return max(0, len(self.tokens) - self.seq_length)

    def __getitem__(self, idx):
        chunk = self.tokens[idx:idx + self.seq_length + 1]
        x = torch.tensor(chunk[:-1], dtype=torch.long)
        y = torch.tensor(chunk[1:], dtype=torch.long)
        return x, y


def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss = 0

    for i, (x, y) in enumerate(loader):
        x, y = x.to(device), y.to(device)

        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        total_loss += loss.item()

        if (i + 1) % 50 == 0:
            print(f"  Batch {i+1}/{len(loader)}, Loss: {loss.item():.4f}")

    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    total_loss = 0

    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))
        total_loss += loss.item()

    return total_loss / len(loader)


def main():
    # Hyperparameters
    D_MODEL = 384
    NUM_HEADS = 6
    NUM_LAYERS = 6
    SEQ_LENGTH = 256
    BATCH_SIZE = 16
    LEARNING_RATE = 3e-4
    NUM_EPOCHS = 10

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}\n")

    # Load data
    data_path = Path(__file__).parent.parent / "shared" / "data" / "tiny_shakespeare.txt"
    if not data_path.exists():
        print("Data not found. Run: python shared/data/download.py")
        return

    with open(data_path, 'r') as f:
        text = f.read()

    split = int(0.9 * len(text))
    train_text, val_text = text[:split], text[split:]

    # Create datasets with BPE tokenization
    train_data = GPTDataset(train_text, SEQ_LENGTH)
    val_data = GPTDataset(val_text, SEQ_LENGTH)

    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE)

    # Create GPT model
    model = GPT(
        vocab_size=50257,  # GPT-2 vocab size
        d_model=D_MODEL,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS,
        max_len=SEQ_LENGTH
    ).to(device)

    print("\n🎉 GPT Model - Production Architecture!")
    print("=" * 60)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    checkpoint_dir = Path(__file__).parent / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    best_val_loss = float('inf')

    print("\nTraining GPT...")
    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS}")
        print("-" * 60)

        train_loss = train_epoch(model, train_loader, optimizer, device)
        val_loss = evaluate(model, val_loader, device)

        print(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'model_state_dict': model.state_dict(),
                'config': {
                    'd_model': D_MODEL,
                    'num_heads': NUM_HEADS,
                    'num_layers': NUM_LAYERS,
                }
            }, checkpoint_dir / "best.pt")
            print("✓ Saved")

    print(f"\n🎉 Training complete! Best val loss: {best_val_loss:.4f}")


if __name__ == "__main__":
    import torch.nn.functional as F
    main()
