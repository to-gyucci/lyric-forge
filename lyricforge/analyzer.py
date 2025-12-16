import json
import re

import ollama

from .models import AnalysisResult, Flashcard, Song

DEFAULT_MODEL = "gemma3:27b"

ANALYSIS_PROMPT = """다음 영어 노래 가사를 분석해서 영어 학습에 유용한 표현들을 추출해줘.

가사:
{lyrics}

각 표현에 대해 다음을 포함해서 JSON 형식으로 응답해:
- expression: 표현 원문
- meaning: 한국어 의미
- example: 다른 상황에서의 예문
- context: 가사에서 사용된 원문
- difficulty: beginner/intermediate/advanced

관용표현, 구동사, 일상회화 표현 위주로 5~15개 추출해줘.
단순한 단어(love, night 등)는 제외하고 학습 가치가 있는 표현만 선별해.

반드시 아래와 같은 JSON 배열 형식으로만 응답해:
[
  {{
    "expression": "see eye to eye",
    "meaning": "의견이 일치하다",
    "example": "We don't see eye to eye on this issue.",
    "context": "We stopped seeing eye to eye",
    "difficulty": "intermediate"
  }}
]
"""


class AnalyzerError(Exception):
    """Exception raised when analysis fails."""

    pass


def extract_json_from_response(response: str) -> list[dict]:
    """Extract JSON array from LLM response."""
    # Try to find JSON array in the response
    json_match = re.search(r"\[[\s\S]*\]", response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Try parsing the entire response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise AnalyzerError(
            f"Could not parse JSON from LLM response. Response:\n{response}"
        )


def analyze_lyrics(song: Song, model: str = DEFAULT_MODEL) -> AnalysisResult:
    """Analyze lyrics using Ollama LLM.

    Args:
        song: Song object containing lyrics to analyze
        model: Ollama model to use (default: gemma3:27b)

    Returns:
        AnalysisResult with song and extracted flashcards

    Raises:
        AnalyzerError: If analysis fails
    """
    prompt = ANALYSIS_PROMPT.format(lyrics=song.lyrics)

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise AnalyzerError(f"Failed to communicate with Ollama: {e}")

    content = response["message"]["content"]
    flashcard_data = extract_json_from_response(content)

    flashcards = []
    for item in flashcard_data:
        try:
            flashcard = Flashcard(
                expression=item.get("expression", ""),
                meaning=item.get("meaning", ""),
                example=item.get("example", ""),
                context=item.get("context", ""),
                difficulty=item.get("difficulty", "intermediate"),
            )
            flashcards.append(flashcard)
        except Exception:
            # Skip invalid flashcard entries
            continue

    if not flashcards:
        raise AnalyzerError("No valid flashcards extracted from response")

    return AnalysisResult(song=song, flashcards=flashcards)
