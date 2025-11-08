#!/usr/bin/env python3
"""Generation script for Mini Transformer"""

import sys
from pathlib import Path
import torch
import argparse

sys.path.append(str(Path(__file__).parent))
from model import MiniTransformer


def load_model(checkpoint_path, device='cpu'):
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = MiniTransformer(
        vocab_size=len(checkpoint['vocab']['word_to_idx']),
        d_model=checkpoint['hyperparameters']['d_model'],
        num_heads=checkpoint['hyperparameters']['num_heads'],
        num_layers=checkpoint['hyperparameters']['num_layers'],
        d_ff=checkpoint['hyperparameters']['d_ff'],
        dropout=checkpoint['hyperparameters']['dropout']
    ).to(device)

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model, checkpoint['vocab']['word_to_idx'], checkpoint['vocab']['idx_to_word']


def generate_text(model, word_to_idx, idx_to_word, prompt="", length=100, temperature=0.8, device='cpu'):
    import re

    if not prompt:
        prompt = "the"

    tokens = re.findall(r'\b\w+\b|[.,!?;:\'\"-]', prompt.lower())
    start_idx = word_to_idx.get(tokens[-1] if tokens else "the", 1)

    generated = model.generate(start_idx, idx_to_word, length, temperature, device)
    return ' '.join(generated)


def main():
    parser = argparse.ArgumentParser(description='Generate with Mini Transformer')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.pt')
    parser.add_argument('--prompt', type=str, default='To be or not to be')
    parser.add_argument('--length', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=0.8)

    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint_path = Path(__file__).parent / args.checkpoint

    if not checkpoint_path.exists():
        print("Checkpoint not found. Train first: python train.py")
        return

    print("Loading Mini Transformer...")
    model, word_to_idx, idx_to_word = load_model(checkpoint_path, device)
    print("Generating with transformer architecture...")
    print("=" * 70)

    text = generate_text(model, word_to_idx, idx_to_word, args.prompt, args.length, args.temperature, device)
    print(text)

    print("=" * 70)


if __name__ == "__main__":
    main()
