#!/usr/bin/env python3
"""Generation script for GPT"""

import sys
from pathlib import Path
import torch
import tiktoken
import argparse

sys.path.append(str(Path(__file__).parent))
from model import GPT


def load_model(checkpoint_path, device):
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = GPT(
        vocab_size=50257,
        d_model=checkpoint['config']['d_model'],
        num_heads=checkpoint['config']['num_heads'],
        num_layers=checkpoint['config']['num_layers']
    ).to(device)

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type=str, default='To be or not to be')
    parser.add_argument('--length', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--top_k', type=int, default=40)

    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint_path = Path(__file__).parent / "checkpoints" / "best.pt"

    if not checkpoint_path.exists():
        print("Checkpoint not found. Train first: python train.py")
        return

    print("Loading GPT model...")
    model = load_model(checkpoint_path, device)

    enc = tiktoken.get_encoding("gpt2")

    # Encode prompt
    tokens = enc.encode(args.prompt)
    x = torch.tensor([tokens], dtype=torch.long, device=device)

    # Generate
    print(f"\nPrompt: {args.prompt}")
    print("=" * 70)

    with torch.no_grad():
        y = model.generate(x, args.length, args.temperature, args.top_k)

    generated = enc.decode(y[0].tolist())
    print(generated)
    print("=" * 70)


if __name__ == "__main__":
    main()
