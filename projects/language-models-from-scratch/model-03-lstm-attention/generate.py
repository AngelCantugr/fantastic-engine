#!/usr/bin/env python3
"""
Text Generation Script for LSTM with Attention
Includes attention visualization!
"""

import sys
from pathlib import Path
import torch
import argparse
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(str(Path(__file__).parent))
from model import LSTMAttentionLM


def load_model(checkpoint_path, device='cpu'):
    """Load trained model."""
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = LSTMAttentionLM(
        vocab_size=len(checkpoint['vocab']['word_to_idx']),
        embedding_dim=checkpoint['hyperparameters']['embedding_dim'],
        hidden_size=checkpoint['hyperparameters']['hidden_size'],
        num_layers=checkpoint['hyperparameters']['num_layers'],
        dropout=checkpoint['hyperparameters']['dropout']
    ).to(device)

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model, checkpoint['vocab']['word_to_idx'], checkpoint['vocab']['idx_to_word']


def visualize_attention(tokens, attention_weights, save_path='attention.png'):
    """
    Visualize attention weights as a heatmap.

    Args:
        tokens: List of words
        attention_weights: Attention matrix (seq_len, seq_len)
        save_path: Where to save the visualization
    """
    plt.figure(figsize=(10, 10))
    plt.imshow(attention_weights, cmap='viridis', aspect='auto')

    # Add labels
    plt.xticks(range(len(tokens)), tokens, rotation=90)
    plt.yticks(range(len(tokens)), tokens)

    plt.xlabel('Attended Words (Source)')
    plt.ylabel('Current Position (Target)')
    plt.title('Attention Weights Visualization')
    plt.colorbar(label='Attention Weight')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ Attention visualization saved to {save_path}")


def generate_with_attention(model, word_to_idx, idx_to_word, prompt, length=30,
                           temperature=0.8, device='cpu', visualize=False):
    """Generate text and optionally visualize attention."""
    import re

    # Tokenize prompt
    tokens = re.findall(r'\b\w+\b|[.,!?;:\'\"-]', prompt.lower())
    if not tokens:
        tokens = ["the"]

    # Convert to indices
    input_indices = [word_to_idx.get(w, word_to_idx['<unk>']) for w in tokens]

    model.eval()
    with torch.no_grad():
        # Encode input
        input_seq = torch.tensor([input_indices], device=device)

        # Get attention weights
        output, hidden, attn_weights = model(input_seq, return_attention=True)

        # Generate more tokens
        generated_indices = input_indices.copy()

        for _ in range(length - len(tokens)):
            logits = output[0, -1] / temperature
            probs = torch.softmax(logits, dim=0)
            next_idx = torch.multinomial(probs, 1).item()

            generated_indices.append(next_idx)

            # Continue generation
            input_seq = torch.tensor([[next_idx]], device=device)
            output, hidden = model(input_seq, hidden)

    # Convert back to words
    generated_words = [idx_to_word[idx] for idx in generated_indices]

    # Visualize if requested
    if visualize and len(tokens) > 1:
        # Use attention from the input sequence
        attn_matrix = attn_weights[0].cpu().numpy()[:len(tokens), :len(tokens)]
        visualize_attention(tokens, attn_matrix)

    return ' '.join(generated_words)


def main():
    parser = argparse.ArgumentParser(description='Generate with LSTM+Attention')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.pt')
    parser.add_argument('--prompt', type=str, default='To be or not to be')
    parser.add_argument('--length', type=int, default=50)
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--visualize', action='store_true',
                        help='Visualize attention weights')

    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint_path = Path(__file__).parent / args.checkpoint

    if not checkpoint_path.exists():
        print(f"Error: Checkpoint not found")
        print("Train the model first: python train.py")
        return

    print("Loading LSTM + Attention model...")
    model, word_to_idx, idx_to_word = load_model(checkpoint_path, device)
    print(f"Vocabulary size: {len(word_to_idx):,}")
    print()

    print("Generating with attention mechanism...")
    print(f"Prompt: '{args.prompt}'")
    print("=" * 70)

    text = generate_with_attention(
        model, word_to_idx, idx_to_word,
        args.prompt, args.length, args.temperature,
        device, args.visualize
    )

    print(text)
    print("=" * 70)

    if args.visualize:
        print("\n Attention weights visualized!")
        print("The heatmap shows which words the model focuses on.")


if __name__ == "__main__":
    main()
