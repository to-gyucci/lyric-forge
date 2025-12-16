"""Tests for lyrics module."""
from unittest.mock import MagicMock, patch

import pytest

from lyricforge.lyrics import LyricsError, clean_lyrics, fetch_lyrics, get_genius_client


class TestCleanLyrics:
    def test_remove_header(self):
        lyrics = "Song Title Lyrics\nFirst line of the song"
        result = clean_lyrics(lyrics)
        assert result == "First line of the song"

    def test_remove_embed(self):
        lyrics = "First line\nSecond line123Embed"
        result = clean_lyrics(lyrics)
        assert result == "First line\nSecond line"

    def test_remove_you_might_also_like(self):
        lyrics = "First line\nYou might also likeSecond line"
        result = clean_lyrics(lyrics)
        assert result == "First line\nSecond line"

    def test_clean_all(self):
        lyrics = "Song Lyrics\nFirst lineYou might also likeSecond line456Embed"
        result = clean_lyrics(lyrics)
        # "You might also like"가 제거되면 붙어버림
        assert result == "First lineSecond line"

    def test_already_clean(self):
        lyrics = "This is already clean lyrics"
        result = clean_lyrics(lyrics)
        assert result == "This is already clean lyrics"


class TestGetGeniusClient:
    @patch.dict("os.environ", {"GENIUS_ACCESS_TOKEN": "test_token"})
    @patch("lyricforge.lyrics.Genius")
    def test_with_valid_token(self, mock_genius):
        client = get_genius_client()
        mock_genius.assert_called_once_with(
            "test_token", verbose=False, remove_section_headers=True
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_token(self):
        with pytest.raises(LyricsError) as exc_info:
            get_genius_client()
        assert "GENIUS_ACCESS_TOKEN" in str(exc_info.value)


class TestFetchLyrics:
    @patch("lyricforge.lyrics.get_genius_client")
    def test_successful_fetch(self, mock_get_client):
        mock_genius = MagicMock()
        mock_song = MagicMock()
        mock_song.title = "It Ain't Me"
        mock_song.artist = "Kygo"
        mock_song.lyrics = "Song Lyrics\nI had a dream123Embed"
        mock_genius.search_song.return_value = mock_song
        mock_get_client.return_value = mock_genius

        result = fetch_lyrics("Kygo", "It Ain't Me")

        assert result.title == "It Ain't Me"
        assert result.artist == "Kygo"
        assert result.lyrics == "I had a dream"
        mock_genius.search_song.assert_called_once_with("It Ain't Me", "Kygo")

    @patch("lyricforge.lyrics.get_genius_client")
    def test_song_not_found(self, mock_get_client):
        mock_genius = MagicMock()
        mock_genius.search_song.return_value = None
        mock_get_client.return_value = mock_genius

        with pytest.raises(LyricsError) as exc_info:
            fetch_lyrics("Unknown", "Unknown Song")
        assert "Could not find lyrics" in str(exc_info.value)
