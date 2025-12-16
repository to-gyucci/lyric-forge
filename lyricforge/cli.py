import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .analyzer import DEFAULT_MODEL, AnalyzerError, analyze_lyrics
from .lyrics import LyricsError, fetch_lyrics

app = typer.Typer(
    name="lyricforge",
    help="Analyze English song lyrics and generate flashcards for language learning",
)
console = Console()


def slugify(text: str) -> str:
    """Convert text to a safe filename."""
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")


@app.command()
def analyze(
    artist: str = typer.Argument(..., help="Artist name"),
    title: str = typer.Argument(..., help="Song title"),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path (default: output/{artist}_{title}.json)",
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        "-m",
        help="Ollama model to use for analysis",
    ),
):
    """Analyze a song's lyrics and generate flashcards."""

    # Fetch lyrics
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Fetching lyrics...", total=None)
        try:
            song = fetch_lyrics(artist, title)
        except LyricsError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print(
        Panel(
            f"[green]Found:[/green] {song.title} by {song.artist}\n"
            f"[dim]Lyrics length: {len(song.lyrics)} characters[/dim]",
            title="Song Info",
        )
    )

    # Analyze with LLM
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(
            description=f"Analyzing lyrics with {model}...",
            total=None,
        )
        try:
            result = analyze_lyrics(song, model=model)
        except AnalyzerError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Display results
    table = Table(title=f"Flashcards ({len(result.flashcards)} expressions)")
    table.add_column("Expression", style="cyan")
    table.add_column("Meaning", style="green")
    table.add_column("Difficulty", style="yellow")

    for card in result.flashcards:
        table.add_row(card.expression, card.meaning, card.difficulty.value)

    console.print(table)

    # Save to file
    if output is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        filename = f"{slugify(song.artist)}_{slugify(song.title)}.json"
        output = output_dir / filename

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        result.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )

    console.print(f"\n[green]Saved to:[/green] {output}")


@app.command()
def version():
    """Show version information."""
    console.print("LyricForge v0.1.0")


if __name__ == "__main__":
    app()
