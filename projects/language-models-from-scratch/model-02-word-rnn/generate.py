#!/usr/bin/env python3
"""
Text Generation Script for Word-level RNN
"""

import sys
from pathlib import Path
import torch
import argparse

sys.path.append(str(Path(__file__).parent))
from model import WordRNN


def load_model(checkpoint_path, device='cpu'):
    """Load a trained model from checkpoint."""
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = WordRNN(
        vocab_size=len(checkpoint['vocab']['word_to_idx']),
        embedding_dim=checkpoint['hyperparameters']['embedding_dim'],
        hidden_size=checkpoint['hyperparameters']['hidden_size'],
        num_layers=checkpoint['hyperparameters']['num_layers'],
        dropout=checkpoint['hyperparameters']['dropout']
    ).to(device)

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model, checkpoint['vocab']['word_to_idx'], checkpoint['vocab']['idx_to_word']


def generate_text(model, word_to_idx, idx_to_word, prompt="", max_length=100, temperature=0.8, device='cpu'):
    """Generate text from the model."""
    import re

    if not prompt:
        prompt = "the"

    # Simple tokenization
    tokens = re.findall(r'\b\w+\b|[.,!?;:\'\"-]', prompt.lower())
    if not tokens:
        tokens = ["the"]

    # Get starting word
    start_word = tokens[-1]
    start_idx = word_to_idx.get(start_word, word_to_idx.get('<unk>', 1))

    # Generate
    generated_words = model.generate(
        start_idx,
        word_to_idx,
        idx_to_word,
        max_length=max_length,
        temperature=temperature,
        device=device
    )

    return ' '.join(generated_words)


def interactive_mode(model, word_to_idx, idx_to_word, device='cpu'):
    """Interactive generation mode."""
    print("\n" + "=" * 70)
    print("Interactive Generation Mode - Word-level RNN")
    print("=" * 70)
    print("\nCommands:")
    print("  - Type a prompt and press Enter to generate")
    print("  - Type 'quit' or 'exit' to quit")
    print("  - Type 'help' for more options")
    print()

    while True:
        try:
            prompt = input("Prompt (or command): ").strip()

            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if prompt.lower() == 'help':
                print("\nOptions:")
                print("  length=N     Set generation length in words (default: 100)")
                print("  temp=N       Set temperature (default: 0.8)")
                print("  Example: 'To be or not to be' length=50 temp=1.0")
                print()
                continue

            # Parse options
            parts = prompt.split()
            actual_prompt = []
            length = 100
            temperature = 0.8

            for part in parts:
                if part.startswith('length='):
                    length = int(part.split('=')[1])
                elif part.startswith('temp='):
                    temperature = float(part.split('=')[1])
                else:
                    actual_prompt.append(part)

            actual_prompt = ' '.join(actual_prompt)

            # Generate
            print("\nGenerating...\n")
            print("-" * 70)
            text = generate_text(model, word_to_idx, idx_to_word, actual_prompt, length, temperature, device)
            print(text)
            print("-" * 70)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


def main():
    parser = argparse.ArgumentParser(description='Generate text with trained WordRNN')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.pt',
                        help='Path to model checkpoint')
    parser.add_argument('--prompt', type=str, default='',
                        help='Starting text for generation')
    parser.add_argument('--length', type=int, default=100,
                        help='Number of words to generate')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Sampling temperature (0.5=conservative, 1.5=creative)')
    parser.add_argument('--interactive', action='store_true',
                        help='Interactive generation mode')

    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint_path = Path(__file__).parent / args.checkpoint

    if not checkpoint_path.exists():
        print(f"Error: Checkpoint not found at {checkpoint_path}")
        print("Please train the model first: python train.py")
        return

    print(f"Loading model from {checkpoint_path}...")
    model, word_to_idx, idx_to_word = load_model(checkpoint_path, device)
    print(f"Model loaded! Vocabulary size: {len(word_to_idx):,}")
    print()

    if args.interactive:
        interactive_mode(model, word_to_idx, idx_to_word, device)
    else:
        print(f"Generating {args.length} words with temperature {args.temperature}...")
        if args.prompt:
            print(f"Prompt: {repr(args.prompt)}")
        print()
        print("=" * 70)

        text = generate_text(model, word_to_idx, idx_to_word, args.prompt, args.length, args.temperature, device)
        print(text)

        print("=" * 70)


if __name__ == "__main__":
    main()
