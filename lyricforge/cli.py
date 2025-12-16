import json
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .analyzer import DEFAULT_MODEL, AnalyzerError, analyze_lyrics
from .database import DatabaseError, check_song_exists, upload_analysis
from .lyrics import LyricsError, fetch_lyrics
from .models import AnalysisResult, Flashcard

app = typer.Typer(
    name="lyricforge",
    help="Analyze English song lyrics and generate flashcards for language learning",
    add_completion=False,
)
console = Console()


def slugify(text: str) -> str:
    """Convert text to a safe filename."""
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")


def load_existing_data(file_path: Path) -> Optional[AnalysisResult]:
    """Load existing analysis result from a JSON file."""
    if not file_path.exists():
        return None
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return AnalysisResult.model_validate(data)
    except (json.JSONDecodeError, Exception):
        return None


def get_expressions(result: Optional[AnalysisResult]) -> List[str]:
    """Get expression list from analysis result."""
    if not result:
        return []
    return [card.expression for card in result.flashcards]


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
    append: bool = typer.Option(
        False,
        "-a",
        "--append",
        help="Append new expressions to existing file (excludes duplicates)",
    ),
):
    """Analyze a song's lyrics and generate flashcards."""
    # Determine output path early for append mode
    if output is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output = output_dir / f"{slugify(artist)}_{slugify(title)}.json"

    # Load existing data if append mode
    existing_result: Optional[AnalysisResult] = None
    exclude_expressions: List[str] = []
    if append:
        existing_result = load_existing_data(output)
        exclude_expressions = get_expressions(existing_result)
        if exclude_expressions:
            console.print(
                f"[dim]Appending mode: excluding {len(exclude_expressions)} existing expressions[/dim]"
            )

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
            result = analyze_lyrics(
                song, model=model, exclude_expressions=exclude_expressions
            )
        except AnalyzerError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Merge with existing if append mode
    if append and existing_result:
        merged_flashcards = existing_result.flashcards + result.flashcards
        # 기존 summary 유지
        result = AnalysisResult(
            song=result.song,
            summary=existing_result.summary,
            flashcards=merged_flashcards,
        )
        console.print(
            f"[dim]Merged: {len(existing_result.flashcards)} existing + {len(result.flashcards) - len(existing_result.flashcards)} new[/dim]"
        )

    # Display summary
    if result.summary:
        console.print(Panel(result.summary, title="Summary"))

    # Display results
    table = Table(title=f"Flashcards ({len(result.flashcards)} expressions)")
    table.add_column("Expression", style="cyan")
    table.add_column("Meaning", style="green")
    table.add_column("Difficulty", style="yellow")

    for card in result.flashcards:
        table.add_row(card.expression, card.meaning, card.difficulty.value)

    console.print(table)

    # Save to file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        result.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )

    console.print(f"\n[green]Saved to:[/green] {output}")


@app.command()
def upload(
    file_path: Path = typer.Argument(..., help="JSON file path to upload"),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Upload even if song already exists in database",
    ),
):
    """Upload analysis result to Supabase."""
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(1)

    # Load JSON file
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        result = AnalysisResult.model_validate(data)
    except (json.JSONDecodeError, Exception) as e:
        console.print(f"[red]Error:[/red] Invalid JSON file: {e}")
        raise typer.Exit(1)

    # Check if song already exists
    if not force:
        existing_id = check_song_exists(result.song.artist, result.song.title)
        if existing_id:
            console.print(
                f"[yellow]Warning:[/yellow] Song already exists (id: {existing_id})\n"
                "Use --force to upload anyway"
            )
            raise typer.Exit(1)

    # Upload to Supabase
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Uploading to Supabase...", total=None)
        try:
            # summary 필드가 있으면 사용 (AnalysisResult에 없으면 data에서 직접 가져옴)
            summary = data.get("summary")
            song_id = upload_analysis(result, summary=summary)
        except DatabaseError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print(
        Panel(
            f"[green]Uploaded:[/green] {result.song.title} by {result.song.artist}\n"
            f"[dim]Song ID: {song_id}[/dim]\n"
            f"[dim]Flashcards: {len(result.flashcards)}[/dim]",
            title="Upload Complete",
        )
    )


@app.command()
def version():
    """Show version information."""
    console.print("LyricForge v0.1.0")


if __name__ == "__main__":
    app()
