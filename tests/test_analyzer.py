"""Tests for analyzer module."""
from unittest.mock import MagicMock, patch

import pytest

from lyricforge.analyzer import (
    AnalyzerError,
    analyze_lyrics,
    extract_json_from_response,
)
from lyricforge.models import Song


class TestExtractJsonFromResponse:
    def test_valid_json_array(self):
        response = '[{"expression": "test", "meaning": "테스트"}]'
        result = extract_json_from_response(response)
        assert result == [{"expression": "test", "meaning": "테스트"}]

    def test_json_with_surrounding_text(self):
        response = 'Here is the result:\n[{"expression": "test"}]\nDone!'
        result = extract_json_from_response(response)
        assert result == [{"expression": "test"}]

    def test_invalid_json(self):
        response = "This is not JSON"
        with pytest.raises(AnalyzerError) as exc_info:
            extract_json_from_response(response)
        assert "Could not parse JSON" in str(exc_info.value)

    def test_empty_array(self):
        response = "[]"
        result = extract_json_from_response(response)
        assert result == []


class TestAnalyzeLyrics:
    @pytest.fixture
    def sample_song(self):
        return Song(
            title="Test Song",
            artist="Test Artist",
            lyrics="I had a dream, we were sipping whiskey neat",
        )

    @pytest.fixture
    def mock_llm_response(self):
        return {
            "message": {
                "content": """[
                    {
                        "expression": "sipping whiskey neat",
                        "meaning": "위스키를 스트레이트로 마시다",
                        "example": "He was sipping whiskey neat at the bar.",
                        "context": "we were sipping whiskey neat",
                        "difficulty": "intermediate"
                    }
                ]"""
            }
        }

    @patch("lyricforge.analyzer.ollama.chat")
    def test_successful_analysis(self, mock_chat, sample_song, mock_llm_response):
        mock_chat.return_value = mock_llm_response

        result = analyze_lyrics(sample_song)

        assert result.song == sample_song
        assert len(result.flashcards) == 1
        assert result.flashcards[0].expression == "sipping whiskey neat"

    @patch("lyricforge.analyzer.ollama.chat")
    def test_with_exclude_expressions(self, mock_chat, sample_song, mock_llm_response):
        mock_chat.return_value = mock_llm_response

        result = analyze_lyrics(
            sample_song, exclude_expressions=["see eye to eye", "on your own"]
        )

        # 프롬프트에 제외 표현이 포함되었는지 확인
        call_args = mock_chat.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert "see eye to eye" in prompt
        assert "on your own" in prompt

    @patch("lyricforge.analyzer.ollama.chat")
    def test_ollama_connection_error(self, mock_chat, sample_song):
        mock_chat.side_effect = Exception("Connection refused")

        with pytest.raises(AnalyzerError) as exc_info:
            analyze_lyrics(sample_song)
        assert "Failed to communicate with Ollama" in str(exc_info.value)

    @patch("lyricforge.analyzer.ollama.chat")
    def test_no_valid_flashcards(self, mock_chat, sample_song):
        mock_chat.return_value = {"message": {"content": "[]"}}

        with pytest.raises(AnalyzerError) as exc_info:
            analyze_lyrics(sample_song)
        assert "No valid flashcards" in str(exc_info.value)

    @patch("lyricforge.analyzer.ollama.chat")
    def test_invalid_flashcard_skipped(self, mock_chat, sample_song):
        # 하나는 유효, 하나는 invalid difficulty
        mock_chat.return_value = {
            "message": {
                "content": """[
                    {
                        "expression": "valid",
                        "meaning": "유효",
                        "example": "example",
                        "context": "context",
                        "difficulty": "beginner"
                    },
                    {
                        "expression": "invalid",
                        "meaning": "무효",
                        "example": "example",
                        "context": "context",
                        "difficulty": "wrong_difficulty"
                    }
                ]"""
            }
        }

        result = analyze_lyrics(sample_song)
        assert len(result.flashcards) == 1
        assert result.flashcards[0].expression == "valid"

    @patch("lyricforge.analyzer.ollama.chat")
    def test_custom_model(self, mock_chat, sample_song, mock_llm_response):
        mock_chat.return_value = mock_llm_response

        analyze_lyrics(sample_song, model="gemma3:12b")

        call_args = mock_chat.call_args
        assert call_args[1]["model"] == "gemma3:12b"
