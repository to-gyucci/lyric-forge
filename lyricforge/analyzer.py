import json
import re
from typing import List, Optional

import ollama

from .models import AnalysisResult, Flashcard, Song

DEFAULT_MODEL = "gemma3:27b"

ANALYSIS_PROMPT = """다음 영어 노래 가사를 분석해줘.

가사:
{lyrics}

다음 두 가지를 JSON 형식으로 응답해:

1. summary: 노래의 주제와 줄거리를 2-3문장으로 한국어 요약

2. flashcards: 영어 학습에 유용한 표현들 (5~15개)
   - expression: 표현 원문
   - meaning: 한국어 의미
   - example: 다른 상황에서의 예문
   - context: 가사에서 사용된 원문
   - difficulty: beginner/intermediate/advanced

관용표현, 구동사, 일상회화 표현 위주로 추출해줘.
단순한 단어(love, night 등)는 제외하고 학습 가치가 있는 표현만 선별해.
{exclude_instruction}
반드시 아래와 같은 JSON 형식으로만 응답해:
{{
  "summary": "이 노래는 이별 후 혼자 남겨진 상대방에 대한 이야기...",
  "flashcards": [
    {{
      "expression": "see eye to eye",
      "meaning": "의견이 일치하다",
      "example": "We don't see eye to eye on this issue.",
      "context": "We stopped seeing eye to eye",
      "difficulty": "intermediate"
    }}
  ]
}}
"""


class AnalyzerError(Exception):
    """Exception raised when analysis fails."""

    pass


def extract_json_from_response(response: str) -> dict:
    """Extract JSON object from LLM response."""
    # Try to find JSON object in the response
    json_match = re.search(r"\{[\s\S]*\}", response)
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


def analyze_lyrics(
    song: Song,
    model: str = DEFAULT_MODEL,
    exclude_expressions: Optional[List[str]] = None,
) -> AnalysisResult:
    """Analyze lyrics using Ollama LLM.

    Args:
        song: Song object containing lyrics to analyze
        model: Ollama model to use (default: gemma3:27b)
        exclude_expressions: List of expressions to exclude from analysis

    Returns:
        AnalysisResult with song and extracted flashcards

    Raises:
        AnalyzerError: If analysis fails
    """
    exclude_instruction = ""
    if exclude_expressions:
        expressions_list = ", ".join(f'"{e}"' for e in exclude_expressions)
        exclude_instruction = f"\n다음 표현들은 이미 추출했으니 제외해줘: {expressions_list}\n"

    prompt = ANALYSIS_PROMPT.format(
        lyrics=song.lyrics,
        exclude_instruction=exclude_instruction,
    )

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_ctx": 8192,  # 컨텍스트 윈도우 확장
                "num_gpu": 99,  # GPU 레이어 최대화 (M3 Max)
            },
            keep_alive="10m",  # 모델 메모리 상주 (재호출 시 로딩 생략)
        )
    except Exception as e:
        raise AnalyzerError(f"Failed to communicate with Ollama: {e}")

    content = response["message"]["content"]
    data = extract_json_from_response(content)

    summary = data.get("summary", "")
    flashcard_data = data.get("flashcards", [])

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

    return AnalysisResult(song=song, summary=summary, flashcards=flashcards)
