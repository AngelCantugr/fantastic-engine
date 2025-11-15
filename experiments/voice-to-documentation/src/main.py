#!/usr/bin/env python3
"""
Voice-to-Documentation
Document while coding without context switching
"""

import os
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv()

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(audio_file: Path, model: str = "whisper-1") -> str:
    """Transcribe audio file using Whisper API."""
    console.print(f"[cyan]🎤 Transcribing audio: {audio_file.name}[/cyan]")

    with open(audio_file, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio,
            response_format="text",
        )

    return transcript


def format_as_documentation(
    transcript: str,
    doc_type: str = "general",
    context: Optional[str] = None,
) -> str:
    """Format transcription as proper documentation using GPT-4."""
    console.print("[cyan]✨ Formatting as documentation...[/cyan]")

    system_prompts = {
        "general": "You are a technical documentation expert. Convert voice transcripts into clear, well-structured markdown documentation.",
        "code": "You are a code documentation specialist. Convert voice explanations into clear code comments and README sections.",
        "architecture": "You are a system design expert. Convert voice notes into architecture documentation with diagrams.",
        "api": "You are an API documentation specialist. Convert voice descriptions into OpenAPI-style documentation.",
        "tutorial": "You are a technical tutorial writer. Convert voice explanations into step-by-step tutorial documentation.",
    }

    user_prompt = f"""Convert the following voice transcript into well-structured markdown documentation:

{transcript}

{"Additional context: " + context if context else ""}

Requirements:
- Use proper markdown formatting
- Add relevant sections (## headings)
- Include code blocks where appropriate
- Use bullet points for lists
- Add mermaid diagrams if describing architecture/flows
- Keep the tone professional but accessible
- Fix any transcription errors
"""

    response = client.chat.completions.create(
        model=os.getenv("GPT_MODEL", "gpt-4-turbo-preview"),
        messages=[
            {"role": "system", "content": system_prompts.get(doc_type, system_prompts["general"])},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def save_documentation(content: str, output_file: Path) -> None:
    """Save formatted documentation to file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content)
    console.print(f"[green]✅ Documentation saved: {output_file}[/green]")


@click.group()
def cli() -> None:
    """Voice-to-Documentation: Talk your way to better docs!"""
    pass


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path",
)
@click.option(
    "--type",
    "-t",
    "doc_type",
    type=click.Choice(["general", "code", "architecture", "api", "tutorial"]),
    default="general",
    help="Documentation type",
)
@click.option(
    "--context",
    "-c",
    help="Additional context for formatting",
)
def convert(
    audio_file: Path,
    output: Optional[Path],
    doc_type: str,
    context: Optional[str],
) -> None:
    """Convert audio file to documentation."""
    try:
        # Transcribe
        transcript = transcribe_audio(audio_file)
        console.print(f"\n[yellow]📝 Transcript:[/yellow]\n{transcript}\n")

        # Format
        documentation = format_as_documentation(transcript, doc_type, context)
        console.print(f"\n[yellow]📄 Formatted Documentation:[/yellow]\n{documentation}\n")

        # Save
        if not output:
            output = Path("output") / f"{audio_file.stem}.md"

        save_documentation(documentation, output)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option(
    "--duration",
    "-d",
    type=int,
    default=30,
    help="Recording duration in seconds",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output audio file path",
)
def record(duration: int, output: Optional[Path]) -> None:
    """Record audio for documentation (requires pyaudio)."""
    try:
        import pyaudio
        import wave

        if not output:
            output = Path("recordings") / "recording.wav"

        output.parent.mkdir(parents=True, exist_ok=True)

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()

        console.print(f"[green]🎙️  Recording for {duration} seconds...[/green]")
        console.print("[yellow]Speak now![/yellow]\n")

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Recording...", total=duration)

            for i in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
                if i % (RATE // CHUNK) == 0:
                    progress.update(task, advance=1)

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save recording
        wf = wave.open(str(output), "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        console.print(f"\n[green]✅ Recording saved: {output}[/green]")

    except ImportError:
        console.print(
            "[red]❌ PyAudio not installed. Install with: pip install pyaudio[/red]"
        )
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
def quick(audio_file: Path) -> None:
    """Quick convert: audio → transcript → clipboard."""
    try:
        transcript = transcribe_audio(audio_file)
        console.print(f"\n[green]✅ Transcript:[/green]\n{transcript}")

        try:
            import pyperclip

            pyperclip.copy(transcript)
            console.print("\n[yellow]📋 Copied to clipboard![/yellow]")
        except ImportError:
            console.print("\n[dim]Install pyperclip to copy to clipboard[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
