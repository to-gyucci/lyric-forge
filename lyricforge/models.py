from enum import Enum
from pydantic import BaseModel


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Flashcard(BaseModel):
    expression: str
    meaning: str
    example: str
    context: str
    difficulty: Difficulty


class Song(BaseModel):
    title: str
    artist: str
    lyrics: str


class AnalysisResult(BaseModel):
    song: Song
    flashcards: list[Flashcard]
