#!/usr/bin/env python3
"""
Text Generation Script for Character-level RNN

Load a trained model and generate text!
"""

import sys
from pathlib import Path
import torch
import argparse

sys.path.append(str(Path(__file__).parent))
from model import CharRNN


def load_model(checkpoint_path, device='cpu'):
    """Load a trained model from checkpoint."""
    checkpoint = torch.load(checkpoint_path, map_location=device)

    # Create model with saved hyperparameters
    model = CharRNN(
        vocab_size=checkpoint['vocab_size'],
        hidden_size=checkpoint['hyperparameters']['hidden_size'],
        num_layers=checkpoint['hyperparameters']['num_layers'],
        dropout=checkpoint['hyperparameters']['dropout']
    ).to(device)

    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model, checkpoint['char_to_idx'], checkpoint['idx_to_char']


def generate_text(model, char_to_idx, idx_to_char, prompt="", length=500, temperature=0.8, device='cpu'):
    """
    Generate text from the model.

    Args:
        model: Trained CharRNN model
        char_to_idx: Character to index mapping
        idx_to_char: Index to character mapping
        prompt: Starting text (will use newline if empty)
        length: Number of characters to generate
        temperature: Sampling temperature (higher = more random)
        device: Device to run on

    Returns:
        Generated text string
    """
    # Start with prompt or newline
    if not prompt:
        prompt = "\n"

    # Convert prompt to indices
    prompt_indices = [char_to_idx.get(ch, 0) for ch in prompt]

    # Use last character of prompt as start
    start_idx = prompt_indices[-1]

    # Generate
    generated_indices = model.generate(start_idx, length, temperature, device)

    # Convert back to text
    generated_text = ''.join([idx_to_char[idx] for idx in generated_indices])

    return prompt + generated_text


def interactive_mode(model, char_to_idx, idx_to_char, device='cpu'):
    """Interactive generation mode."""
    print("\n" + "=" * 70)
    print("Interactive Generation Mode")
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
                print("  length=N     Set generation length (default: 500)")
                print("  temp=N       Set temperature (default: 0.8)")
                print("  Example: 'To be or not to be' length=200 temp=1.0")
                print()
                continue

            # Parse options
            parts = prompt.split()
            actual_prompt = []
            length = 500
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
            text = generate_text(model, char_to_idx, idx_to_char, actual_prompt, length, temperature, device)
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
    parser = argparse.ArgumentParser(description='Generate text with trained CharRNN')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.pt',
                        help='Path to model checkpoint')
    parser.add_argument('--prompt', type=str, default='',
                        help='Starting text for generation')
    parser.add_argument('--length', type=int, default=500,
                        help='Number of characters to generate')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Sampling temperature (0.5=conservative, 1.5=creative)')
    parser.add_argument('--interactive', action='store_true',
                        help='Interactive generation mode')

    args = parser.parse_args()

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint_path = Path(__file__).parent / args.checkpoint

    if not checkpoint_path.exists():
        print(f"Error: Checkpoint not found at {checkpoint_path}")
        print("Please train the model first: python train.py")
        return

    print(f"Loading model from {checkpoint_path}...")
    model, char_to_idx, idx_to_char = load_model(checkpoint_path, device)
    print(f"Model loaded! Vocabulary size: {len(char_to_idx)}")
    print()

    if args.interactive:
        interactive_mode(model, char_to_idx, idx_to_char, device)
    else:
        # Single generation
        print(f"Generating {args.length} characters with temperature {args.temperature}...")
        if args.prompt:
            print(f"Prompt: {repr(args.prompt)}")
        print()
        print("=" * 70)

        text = generate_text(model, char_to_idx, idx_to_char, args.prompt, args.length, args.temperature, device)
        print(text)

        print("=" * 70)


if __name__ == "__main__":
    main()
