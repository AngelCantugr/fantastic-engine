#!/usr/bin/env python3
"""
ADHD Executive Function Dashboard
Main entry point for the terminal dashboard application.

This dashboard helps manage ADHD executive function challenges by providing
a single-view interface for tasks, energy levels, focus patterns, and more.
"""

import argparse
import sys
from pathlib import Path

from dashboard import Dashboard


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ADHD Executive Function Dashboard - Your command center for managing tasks and focus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --theme nord       # Use Nord color theme
  python main.py --refresh 180      # Refresh every 3 minutes
  python main.py --debug            # Enable debug logging

Keyboard shortcuts:
  q - Quit dashboard
  r - Refresh now
  e - Log energy level
  p - Start/pause Pomodoro
  t - Mark task complete
  ? - Show help
        """
    )

    parser.add_argument(
        "--theme",
        type=str,
        default="cyberpunk",
        choices=["cyberpunk", "nord", "monokai", "dracula"],
        help="Color theme for the dashboard (default: cyberpunk)"
    )

    parser.add_argument(
        "--refresh",
        type=int,
        default=300,
        metavar="SECONDS",
        help="Refresh interval in seconds (default: 300 = 5 minutes)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    parser.add_argument(
        "--config",
        type=Path,
        metavar="FILE",
        help="Path to custom configuration file"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="ADHD Executive Function Dashboard v0.1.0"
    )

    return parser.parse_args()


def check_environment():
    """Check that required environment variables and files exist."""
    env_file = Path(".env")

    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Copy .env.example to .env and configure your settings.")
        print()
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)


def main():
    """Main entry point for the dashboard application."""
    args = parse_arguments()

    # Check environment setup
    check_environment()

    # Create and run dashboard
    try:
        dashboard = Dashboard(
            theme=args.theme,
            refresh_interval=args.refresh,
            debug=args.debug,
            config_file=args.config
        )

        dashboard.run()

    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed. Stay focused!")
        sys.exit(0)

    except Exception as e:
        if args.debug:
            raise
        else:
            print(f"\n❌ Error: {e}")
            print("   Run with --debug for more information")
            sys.exit(1)


if __name__ == "__main__":
    main()
