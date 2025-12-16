"""Tests for CLI module."""
import json
from pathlib import Path

import pytest

from lyricforge.cli import get_expressions, load_existing_data, slugify
from lyricforge.models import AnalysisResult, Flashcard, Song


class TestSlugify:
    def test_simple_text(self):
        assert slugify("Hello World") == "hello_world"

    def test_special_characters(self):
        assert slugify("It Ain't Me") == "it_ain_t_me"

    def test_numbers(self):
        assert slugify("Song 123") == "song_123"

    def test_korean(self):
        # 한글은 isalnum()이 True라서 유지됨
        assert slugify("한글 Test") == "한글_test"

    def test_multiple_spaces(self):
        assert slugify("Hello   World") == "hello___world"


class TestLoadExistingData:
    def test_file_not_exists(self, tmp_path):
        result = load_existing_data(tmp_path / "nonexistent.json")
        assert result is None

    def test_valid_json(self, tmp_path):
        data = {
            "song": {"title": "Test", "artist": "Artist", "lyrics": "lyrics"},
            "summary": "테스트 요약",
            "flashcards": [
                {
                    "expression": "test",
                    "meaning": "테스트",
                    "example": "example",
                    "context": "context",
                    "difficulty": "beginner",
                }
            ],
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        result = load_existing_data(file_path)
        assert result is not None
        assert result.song.title == "Test"
        assert result.summary == "테스트 요약"
        assert len(result.flashcards) == 1

    def test_invalid_json(self, tmp_path):
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json", encoding="utf-8")

        result = load_existing_data(file_path)
        assert result is None

    def test_missing_fields(self, tmp_path):
        data = {"song": {"title": "Test"}}  # missing required fields
        file_path = tmp_path / "incomplete.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        result = load_existing_data(file_path)
        assert result is None


class TestGetExpressions:
    def test_with_flashcards(self):
        song = Song(title="Test", artist="Artist", lyrics="lyrics")
        cards = [
            Flashcard(
                expression="expr1",
                meaning="m1",
                example="e1",
                context="c1",
                difficulty="beginner",
            ),
            Flashcard(
                expression="expr2",
                meaning="m2",
                example="e2",
                context="c2",
                difficulty="intermediate",
            ),
        ]
        result = AnalysisResult(song=song, summary="테스트", flashcards=cards)

        expressions = get_expressions(result)
        assert expressions == ["expr1", "expr2"]

    def test_with_none(self):
        expressions = get_expressions(None)
        assert expressions == []

    def test_empty_flashcards(self):
        song = Song(title="Test", artist="Artist", lyrics="lyrics")
        result = AnalysisResult(song=song, summary="", flashcards=[])

        expressions = get_expressions(result)
        assert expressions == []
