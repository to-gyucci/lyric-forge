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
│   └── cli.py           # CLI 인터페이스
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
# ollama pull gemma3:12b   # 고품질 모델 (~8GB, 선택사항)

# 4. 환경변수 설정
cp .env.example .env
# .env 파일에 Genius API 토큰 입력
# 토큰 발급: https://genius.com/api-clients
```

## 실행

```bash
# 기본 사용
lyricforge analyze "Kygo" "It Ain't Me"

# 출력 파일 지정
lyricforge analyze "Kygo" "It Ain't Me" -o output/it_aint_me.json

# 다른 모델 사용
lyricforge analyze "Kygo" "It Ain't Me" --model gemma3:12b
```

## 출력 예시

```json
{
  "song": {
    "title": "It Ain't Me",
    "artist": "Kygo & Selena Gomez",
    "lyrics": "..."
  },
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

## 향후 계획

- **테스트 코드**: 실사용 후 필요 시 추가
- **Rate limiting**: Genius API 호출 제한 처리
- **캐싱**: 같은 곡 재분석 방지 (Phase 2 Supabase 연동 시)
