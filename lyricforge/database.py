"""Supabase 데이터베이스 연동 모듈."""

import os
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from .models import AnalysisResult

# 환경변수 로드
load_dotenv()


class DatabaseError(Exception):
    """데이터베이스 연동 관련 에러."""

    pass


def get_client() -> Client:
    """Supabase 클라이언트 생성."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise DatabaseError(
            "SUPABASE_URL and SUPABASE_KEY must be set in .env file"
        )

    return create_client(url, key)


def upload_analysis(result: AnalysisResult) -> str:
    """분석 결과를 Supabase에 업로드.

    Args:
        result: 분석 결과 (Song + summary + Flashcards)

    Returns:
        생성된 song_id (UUID)
    """
    client = get_client()

    # 1. songs 테이블에 삽입
    song_data = {
        "title": result.song.title,
        "artist": result.song.artist,
        "lyrics": result.song.lyrics,
        "summary": result.summary,
    }

    song_response = client.table("songs").insert(song_data).execute()

    if not song_response.data:
        raise DatabaseError("Failed to insert song")

    song_id = song_response.data[0]["id"]

    # 2. flashcards 테이블에 삽입
    if result.flashcards:
        flashcards_data = [
            {
                "song_id": song_id,
                "expression": card.expression,
                "meaning": card.meaning,
                "example": card.example,
                "context": card.context,
                "difficulty": card.difficulty.value,
            }
            for card in result.flashcards
        ]

        cards_response = client.table("flashcards").insert(flashcards_data).execute()

        if not cards_response.data:
            raise DatabaseError("Failed to insert flashcards")

    return song_id


def check_song_exists(artist: str, title: str) -> Optional[str]:
    """아티스트+제목으로 기존 노래 존재 여부 확인.

    Returns:
        존재하면 song_id, 없으면 None
    """
    client = get_client()

    response = (
        client.table("songs")
        .select("id")
        .eq("artist", artist)
        .eq("title", title)
        .execute()
    )

    if response.data:
        return response.data[0]["id"]
    return None
