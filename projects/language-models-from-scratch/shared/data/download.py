#!/usr/bin/env python3
"""
Dataset Download Script for Language Models from Scratch
Downloads all datasets needed for the 5 models.
"""

import os
import urllib.request
from pathlib import Path
from typing import Optional

def download_file(url: str, destination: Path, chunk_size: int = 8192) -> None:
    """Download a file with progress indication."""
    print(f"Downloading {url}...")

    destination.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(url) as response:
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded = 0

        with open(destination, 'wb') as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)

    print(f"\n✓ Saved to {destination}")


def download_tiny_shakespeare(data_dir: Path) -> None:
    """Download Tiny Shakespeare dataset."""
    url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
    destination = data_dir / "tiny_shakespeare.txt"

    if destination.exists():
        print(f"✓ Tiny Shakespeare already exists at {destination}")
        return

    download_file(url, destination)

    # Print stats
    with open(destination, 'r', encoding='utf-8') as f:
        text = f.read()
        print(f"  - Size: {len(text):,} characters")
        print(f"  - Unique chars: {len(set(text))}")


def download_wikitext2(data_dir: Path) -> None:
    """Download WikiText-2 dataset (we'll use HuggingFace datasets library)."""
    print("\nWikiText-2 will be downloaded automatically by HuggingFace datasets")
    print("when you run the training scripts for Models 4-5.")
    print("No action needed here.")


def main():
    """Download all datasets."""
    # Get the data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir

    print("=" * 60)
    print("Language Models from Scratch - Dataset Downloader")
    print("=" * 60)
    print()

    # Download datasets
    print("📥 Downloading datasets...")
    print()

    # 1. Tiny Shakespeare (for Models 1-3)
    print("1. Tiny Shakespeare (for Models 1-3)")
    download_tiny_shakespeare(data_dir)
    print()

    # 2. WikiText-2 info
    print("2. WikiText-2 (for Models 4-5)")
    download_wikitext2(data_dir)
    print()

    print("=" * 60)
    print("✅ Dataset download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. cd model-01-char-rnn")
    print("  2. python train.py")
    print()


if __name__ == "__main__":
    main()
