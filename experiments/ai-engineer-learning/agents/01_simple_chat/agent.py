#!/usr/bin/env python3
"""
Agent 1: Simple Chat Agent
===========================

Learning Objectives:
- Understand basic Ollama API communication
- Learn about streaming vs non-streaming responses
- Practice prompt structuring
- Handle conversation history

Complexity: ⭐ Beginner
Framework: Native ollama library + httpx
"""

import sys
import json
from typing import Iterator, Optional, List, Dict
from pathlib import Path

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

# Initialize rich console for beautiful output
console = Console()


class SimpleChatAgent:
    """
    A simple chat agent that connects to local Ollama.

    This agent demonstrates:
    1. Basic HTTP communication with Ollama API
    2. Streaming responses for better UX
    3. Conversation history management
    4. System message configuration
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ):
        """
        Initialize the chat agent.

        Args:
            model: Ollama model to use (must be pulled first)
            base_url: Ollama server URL
            temperature: Creativity level (0.0 = focused, 1.0 = creative)
            system_message: Initial system prompt
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.conversation_history: List[Dict[str, str]] = []

        # Set default system message
        self.system_message = system_message or (
            "You are a helpful coding assistant for a staff software engineer. "
            "Provide clear, concise, and accurate technical answers. "
            "When showing code, include comments explaining key concepts."
        )

        # Add system message to history
        self.conversation_history.append({
            "role": "system",
            "content": self.system_message
        })

        # HTTP client for API calls
        self.client = httpx.Client(timeout=120.0)

    def chat(self, message: str, stream: bool = True) -> str:
        """
        Send a message and get a response.

        Args:
            message: User's message
            stream: Whether to stream the response

        Returns:
            The assistant's complete response
        """
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Prepare API payload
        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_predict": 2048  # Max tokens to generate
            }
        }

        # Get response (streaming or synchronous)
        if stream:
            response = self._stream_response(payload)
        else:
            response = self._sync_response(payload)

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def _stream_response(self, payload: dict) -> str:
        """
        Handle streaming response from Ollama.

        This is more complex but provides better UX as tokens
        appear in real-time rather than waiting for completion.

        Args:
            payload: API request payload

        Returns:
            Complete response text
        """
        full_response = ""

        try:
            # Make streaming POST request
            with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()

                # Print assistant label
                console.print("\n[bold cyan]Assistant:[/bold cyan] ", end="")

                # Process each chunk as it arrives
                for line in response.iter_lines():
                    if line:
                        # Parse JSON response
                        data = json.loads(line)

                        # Extract message content
                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            full_response += chunk

                            # Print chunk immediately (no newline)
                            console.print(chunk, end="", markup=False)

                        # Check if this is the final message
                        if data.get("done", False):
                            break

                console.print()  # Final newline

        except httpx.HTTPStatusError as e:
            console.print(f"\n[red]HTTP Error: {e}[/red]")
            raise
        except httpx.RequestError as e:
            console.print(f"\n[red]Connection Error: {e}[/red]")
            console.print("[yellow]Is Ollama running? Try: ollama serve[/yellow]")
            raise
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/red]")
            raise

        return full_response

    def _sync_response(self, payload: dict) -> str:
        """
        Handle synchronous (non-streaming) response from Ollama.

        Simpler but less responsive UX.

        Args:
            payload: API request payload

        Returns:
            Complete response text
        """
        payload["stream"] = False

        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            content = data["message"]["content"]

            # Print complete response
            console.print("\n[bold cyan]Assistant:[/bold cyan]")
            console.print(content)

            return content

        except httpx.HTTPStatusError as e:
            console.print(f"[red]HTTP Error: {e}[/red]")
            raise
        except httpx.RequestError as e:
            console.print(f"[red]Connection Error: {e}[/red]")
            console.print("[yellow]Is Ollama running? Try: ollama serve[/yellow]")
            raise

    def check_ollama_health(self) -> bool:
        """
        Check if Ollama server is running and model is available.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check server health
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()

            # Check if model is available
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if self.model not in model_names:
                console.print(f"[yellow]Model '{self.model}' not found.[/yellow]")
                console.print(f"[yellow]Available models: {', '.join(model_names)}[/yellow]")
                console.print(f"\n[cyan]Pull the model with: ollama pull {self.model}[/cyan]")
                return False

            return True

        except Exception as e:
            console.print(f"[red]Cannot connect to Ollama: {e}[/red]")
            console.print("[yellow]Start Ollama with: ollama serve[/yellow]")
            return False

    def reset_conversation(self):
        """Reset conversation history (keep system message)."""
        self.conversation_history = [
            {"role": "system", "content": self.system_message}
        ]


def run_interactive_chat(
    model: str = "qwen2.5-coder:7b",
    stream: bool = True,
    temperature: float = 0.7
):
    """
    Run an interactive chat session.

    Args:
        model: Ollama model to use
        stream: Enable streaming responses
        temperature: Model temperature
    """
    # Create agent
    agent = SimpleChatAgent(model=model, temperature=temperature)

    # Display welcome panel
    console.print(Panel.fit(
        f"[bold cyan]Simple Chat Agent[/bold cyan]\n\n"
        f"Model: [yellow]{model}[/yellow]\n"
        f"Temperature: [yellow]{temperature}[/yellow]\n"
        f"Streaming: [yellow]{stream}[/yellow]\n\n"
        f"[dim]Commands:[/dim]\n"
        f"  • Type your message and press Enter\n"
        f"  • Type 'quit' or 'exit' to end session\n"
        f"  • Type 'reset' to clear conversation history\n"
        f"  • Type 'help' for more options",
        border_style="cyan"
    ))

    # Check Ollama health
    console.print("\n[dim]Checking Ollama connection...[/dim]")
    if not agent.check_ollama_health():
        console.print("[red]Cannot start agent. Please fix the issues above.[/red]")
        sys.exit(1)

    console.print("[green]✓ Connected to Ollama[/green]\n")

    # Main chat loop
    try:
        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold green]You[/bold green]")

            # Handle commands
            if user_input.lower() in ["quit", "exit"]:
                console.print("\n[cyan]Goodbye! Happy coding! 👋[/cyan]")
                break

            elif user_input.lower() == "reset":
                agent.reset_conversation()
                console.print("[yellow]Conversation reset.[/yellow]")
                continue

            elif user_input.lower() == "help":
                console.print(Panel(
                    "[bold]Available Commands:[/bold]\n\n"
                    "• [cyan]quit/exit[/cyan] - End the session\n"
                    "• [cyan]reset[/cyan] - Clear conversation history\n"
                    "• [cyan]help[/cyan] - Show this help message\n\n"
                    "[bold]Tips:[/bold]\n\n"
                    "• Ask about code concepts, debugging, best practices\n"
                    "• Request code examples with explanations\n"
                    "• The agent remembers context from previous messages",
                    border_style="yellow"
                ))
                continue

            elif not user_input.strip():
                continue

            # Get response from agent
            try:
                agent.chat(user_input, stream=stream)
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                console.print("[yellow]Try again or type 'quit' to exit.[/yellow]")

    except KeyboardInterrupt:
        console.print("\n\n[cyan]Session ended. Goodbye! 👋[/cyan]")


def main():
    """Main entry point with CLI argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Simple Chat Agent - Learn basic Ollama integration"
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Ollama model to use (default: qwen2.5-coder:7b)"
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Model temperature 0.0-1.0 (default: 0.7)"
    )

    args = parser.parse_args()

    # Run interactive chat
    run_interactive_chat(
        model=args.model,
        stream=not args.no_stream,
        temperature=args.temperature
    )


if __name__ == "__main__":
    main()
