# LyricForge

영어 노래 가사 분석 → 플래시카드 생성 CLI 도구

## 기술 스택

- Python 3.9+
- lyricsgenius: Genius API 가사 크롤링
- ollama: 로컬 LLM (gemma3:27b 기본)
- typer + rich: CLI
- pydantic: 데이터 모델

## 프로젝트 구조

```
lyricforge/
├── __init__.py      # 패키지 초기화
├── models.py        # Pydantic 데이터 모델 (Song, Flashcard, AnalysisResult)
├── lyrics.py        # Genius API 연동, 가사 크롤링
├── analyzer.py      # Ollama LLM 분석, 프롬프트 처리
└── cli.py           # Typer CLI 진입점
```

## 환경 설정

- `.env` 파일에 `GENIUS_ACCESS_TOKEN` 필요
- Ollama 서버 실행 필요 (`ollama serve`)

## 주요 명령어

```bash
# 가상환경 활성화
source .venv/bin/activate

# 실행
lyricforge analyze "아티스트" "노래제목"
lyricforge analyze "아티스트" "노래제목" -o output/파일명.json
lyricforge analyze "아티스트" "노래제목" --model gemma3:12b
lyricforge analyze "아티스트" "노래제목" -a  # 기존 표현 제외 + 병합

# 도움말
lyricforge --help
lyricforge analyze --help
```

## 코드 컨벤션

- 한국어 주석/문서 사용
- 타입 힌트 필수
- Pydantic 모델로 데이터 검증
- 에러는 커스텀 Exception 클래스 사용 (LyricsError, AnalyzerError)

## 작업 시 참고사항

- Mac + Homebrew 환경
- 가상환경(.venv) 사용
- .env 파일은 gitignore에 포함됨
- output/ 디렉토리에 생성된 JSON 저장
- GitHub CLI 필요: `brew install gh` (PR 생성 등)
- 한국어 응답 시 반말 사용 (토큰 절약, 예의는 지키면서)
