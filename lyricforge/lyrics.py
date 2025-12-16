import os
import re

from dotenv import load_dotenv
from lyricsgenius import Genius

from .models import Song

load_dotenv()


class LyricsError(Exception):
    """Exception raised when lyrics cannot be fetched."""

    pass


def get_genius_client() -> Genius:
    """Get Genius API client with access token from environment."""
    token = os.environ.get("GENIUS_ACCESS_TOKEN")
    if not token:
        raise LyricsError(
            "GENIUS_ACCESS_TOKEN environment variable is not set. "
            "Get your token at https://genius.com/api-clients"
        )
    genius = Genius(token, verbose=False, remove_section_headers=True)
    return genius


def clean_lyrics(lyrics: str) -> str:
    """Clean up lyrics text by removing unwanted elements."""
    # Remove "XXX Lyrics" header at the beginning
    lyrics = re.sub(r"^.*Lyrics\n", "", lyrics)
    # Remove "XXXEmbed" at the end
    lyrics = re.sub(r"\d*Embed$", "", lyrics)
    # Remove "You might also like" text
    lyrics = lyrics.replace("You might also like", "")
    return lyrics.strip()


def fetch_lyrics(artist: str, title: str) -> Song:
    """Fetch lyrics for a song from Genius.

    Args:
        artist: Artist name
        title: Song title

    Returns:
        Song object with lyrics

    Raises:
        LyricsError: If lyrics cannot be fetched
    """
    genius = get_genius_client()

    song = genius.search_song(title, artist)
    if song is None:
        raise LyricsError(f"Could not find lyrics for '{title}' by {artist}")

    cleaned_lyrics = clean_lyrics(song.lyrics)

    return Song(
        title=song.title,
        artist=song.artist,
        lyrics=cleaned_lyrics,
    )
