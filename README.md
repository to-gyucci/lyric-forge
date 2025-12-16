# LyricForge

영어 노래 가사를 분석해서 플래시카드를 생성하는 CLI 도구

## 프로젝트 구조

```
lyric-forge/
├── lyricforge/
│   ├── __init__.py      # 패키지 초기화
│   ├── models.py        # 데이터 모델
│   ├── lyrics.py        # Genius API 가사 크롤링
│   ├── analyzer.py      # Ollama LLM 분석
│   ├── database.py      # Supabase 연동
│   └── cli.py           # CLI 인터페이스
├── tests/               # 테스트 코드
├── output/              # 생성된 JSON 저장
├── pyproject.toml
└── .env                 # API 토큰 (직접 생성)
```

## 설치

```bash
# 1. 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install -e .

# 3. Ollama 설치 및 모델 다운로드
brew install ollama
ollama serve  # 터미널에서 Ollama 서버 실행 (백그라운드 유지)

# 새 터미널에서 모델 다운로드
ollama pull gemma3:27b     # 기본 모델 (~17GB)
# ollama pull gemma3:12b   # 경량 모델 (~8GB, 선택사항)

# 4. 환경변수 설정
cp .env.example .env
# .env 파일에 API 토큰 입력:
# - GENIUS_ACCESS_TOKEN: https://genius.com/api-clients
# - SUPABASE_URL, SUPABASE_KEY: https://supabase.com (선택)
```

## 사용법

```bash
# 가사 분석 및 플래시카드 생성
lyricforge analyze "Kygo" "It Ain't Me"

# 출력 파일 지정
lyricforge analyze "Kygo" "It Ain't Me" -o output/it_aint_me.json

# 다른 모델 사용
lyricforge analyze "Kygo" "It Ain't Me" --model gemma3:12b

# 재분석 (기존 표현 제외 + 병합)
lyricforge analyze "Kygo" "It Ain't Me" -a

# Supabase에 업로드
lyricforge upload output/kygo_it_ain_t_me.json

# 도움말
lyricforge --help
lyricforge analyze --help
lyricforge upload --help
```

## 출력 예시

```json
{
  "song": {
    "title": "It Ain't Me",
    "artist": "Kygo & Selena Gomez",
    "lyrics": "..."
  },
  "summary": "이 노래는 이별 후 상대방이 혼자 힘든 시간을 보낼 것을 예상하며...",
  "flashcards": [
    {
      "expression": "see eye to eye",
      "meaning": "의견이 일치하다",
      "example": "We don't see eye to eye on this issue.",
      "context": "We stopped seeing eye to eye",
      "difficulty": "intermediate"
    }
  ]
}
```

## 테스트

```bash
# 개발 의존성 설치
pip install -e ".[dev]"

# 테스트 실행 (커버리지 포함)
pytest
```

## 기술 스택

- Python 3.9+
- lyricsgenius: Genius API
- ollama: 로컬 LLM (gemma3:27b)
- typer + rich: CLI
- pydantic: 데이터 모델
- supabase: 데이터베이스
- pytest: 테스트
