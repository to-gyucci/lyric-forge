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
    def test_valid_json_object(self):
        response = '{"summary": "요약", "flashcards": [{"expression": "test"}]}'
        result = extract_json_from_response(response)
        assert result == {"summary": "요약", "flashcards": [{"expression": "test"}]}

    def test_json_with_surrounding_text(self):
        response = 'Here is the result:\n{"summary": "요약", "flashcards": []}\nDone!'
        result = extract_json_from_response(response)
        assert result == {"summary": "요약", "flashcards": []}

    def test_invalid_json(self):
        response = "This is not JSON"
        with pytest.raises(AnalyzerError) as exc_info:
            extract_json_from_response(response)
        assert "Could not parse JSON" in str(exc_info.value)

    def test_empty_flashcards(self):
        response = '{"summary": "", "flashcards": []}'
        result = extract_json_from_response(response)
        assert result == {"summary": "", "flashcards": []}


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
                "content": """{
                    "summary": "이 노래는 이별에 대한 이야기입니다.",
                    "flashcards": [
                        {
                            "expression": "sipping whiskey neat",
                            "meaning": "위스키를 스트레이트로 마시다",
                            "example": "He was sipping whiskey neat at the bar.",
                            "context": "we were sipping whiskey neat",
                            "difficulty": "intermediate"
                        }
                    ]
                }"""
            }
        }

    @patch("lyricforge.analyzer.ollama.chat")
    def test_successful_analysis(self, mock_chat, sample_song, mock_llm_response):
        mock_chat.return_value = mock_llm_response

        result = analyze_lyrics(sample_song)

        assert result.song == sample_song
        assert result.summary == "이 노래는 이별에 대한 이야기입니다."
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
        mock_chat.return_value = {"message": {"content": '{"summary": "", "flashcards": []}'}}

        with pytest.raises(AnalyzerError) as exc_info:
            analyze_lyrics(sample_song)
        assert "No valid flashcards" in str(exc_info.value)

    @patch("lyricforge.analyzer.ollama.chat")
    def test_invalid_flashcard_skipped(self, mock_chat, sample_song):
        # 하나는 유효, 하나는 invalid difficulty
        mock_chat.return_value = {
            "message": {
                "content": """{
                    "summary": "테스트 요약",
                    "flashcards": [
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
                    ]
                }"""
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
