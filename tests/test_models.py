"""Tests for Pydantic models."""
import pytest
from pydantic import ValidationError

from lyricforge.models import AnalysisResult, Difficulty, Flashcard, Song


class TestDifficulty:
    def test_difficulty_values(self):
        assert Difficulty.BEGINNER.value == "beginner"
        assert Difficulty.INTERMEDIATE.value == "intermediate"
        assert Difficulty.ADVANCED.value == "advanced"


class TestFlashcard:
    def test_valid_flashcard(self):
        card = Flashcard(
            expression="see eye to eye",
            meaning="의견이 일치하다",
            example="We don't see eye to eye.",
            context="We stopped seeing eye to eye",
            difficulty=Difficulty.INTERMEDIATE,
        )
        assert card.expression == "see eye to eye"
        assert card.difficulty == Difficulty.INTERMEDIATE

    def test_flashcard_with_string_difficulty(self):
        card = Flashcard(
            expression="test",
            meaning="테스트",
            example="example",
            context="context",
            difficulty="beginner",
        )
        assert card.difficulty == Difficulty.BEGINNER

    def test_invalid_difficulty(self):
        with pytest.raises(ValidationError):
            Flashcard(
                expression="test",
                meaning="테스트",
                example="example",
                context="context",
                difficulty="invalid",
            )


class TestSong:
    def test_valid_song(self):
        song = Song(
            title="It Ain't Me",
            artist="Kygo",
            lyrics="I had a dream...",
        )
        assert song.title == "It Ain't Me"
        assert song.artist == "Kygo"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            Song(title="Test", artist="Artist")  # missing lyrics


class TestAnalysisResult:
    def test_valid_result(self):
        song = Song(title="Test", artist="Artist", lyrics="lyrics")
        card = Flashcard(
            expression="test",
            meaning="테스트",
            example="example",
            context="context",
            difficulty="intermediate",
        )
        result = AnalysisResult(song=song, flashcards=[card])
        assert result.song == song
        assert len(result.flashcards) == 1

    def test_empty_flashcards(self):
        song = Song(title="Test", artist="Artist", lyrics="lyrics")
        result = AnalysisResult(song=song, flashcards=[])
        assert len(result.flashcards) == 0
