# LyricForge MVP Spec

## 프로젝트 개요
영어 노래 가사를 분석해서 플래시카드를 생성하는 앱.

## MVP 범위 (Phase 1: Mac CLI 도구)

### 목표
노래 제목/아티스트를 입력하면 가사를 가져와서 LLM으로 분석하고, 플래시카드용 JSON을 출력한다.

### 기술 스택
- Python 3.9+
- 가사: `lyricsgenius` 라이브러리 (Genius API + 스크래핑)
- LLM: Ollama (아래 모델 권장)
- 출력: JSON 파일

### LLM 모델 선택 가이드 (2025년 기준)

| 모델 | 파라미터 | VRAM/RAM | 특징 | 적합도 |
|------|----------|----------|------|--------|
| gemma3:4b | 4B | ~5GB | 성능/효율 균형, 128K 컨텍스트, 한중일 토크나이저 개선 | 저사양 |
| gemma3:12b | 12B | ~10GB | 더 정교한 분석, 복잡한 관용표현 설명에 유리 | 고품질 |
| **gemma3:27b** | 27B | ~20GB | 최고 품질, LMArena 상위권 | ⭐ **추천** |
| llama3.1:8b | 8B | ~8GB | 코딩/추론 강점, 다국어는 Gemma3보다 약함 | 대안 |

**권장**: `gemma3:27b` (기본, 고사양 환경) 또는 `gemma3:12b` (중간 사양)

**Gemma 3 주요 특징** (2025년 3월 출시)
- 128K 컨텍스트 윈도우
- 한국어/일본어/중국어 토크나이저 대폭 개선
- 멀티모달 지원 (4B 이상)

### 핵심 기능

#### 1. 가사 가져오기
```
입력: 아티스트명, 노래 제목
출력: 가사 텍스트
방법: lyricsgenius 라이브러리 (Genius API + 웹 스크래핑)
```

```python
from lyricsgenius import Genius

genius = Genius("ACCESS_TOKEN")
song = genius.search_song("It Ain't Me", "Kygo")
print(song.lyrics)
```

#### 2. 가사 분석 (LLM)
```
입력: 가사 텍스트
출력: 
  - 핵심 표현 리스트 (5~15개)
  - 각 표현별: 원문, 의미(한국어), 예문, 난이도
```

#### 3. JSON 출력
```json
{
  "song": {
    "title": "It Ain't Me",
    "artist": "Kygo & Selena Gomez",
    "lyrics": "전체 가사..."
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

### 디렉토리 구조
```
lyricforge/
├── lyricforge/
│   ├── __init__.py
│   ├── cli.py           # CLI 진입점
│   ├── lyrics.py        # 가사 크롤링/API
│   ├── analyzer.py      # LLM 분석
│   └── models.py        # 데이터 모델
├── output/              # 생성된 JSON 저장
├── pyproject.toml
└── README.md
```

### CLI 사용 예시
```bash
# 기본 사용 (gemma3:27b 기본)
lyricforge analyze "Kygo" "It Ain't Me"

# 출력 파일 지정
lyricforge analyze "Kygo" "It Ain't Me" -o output/it_aint_me.json

# 고품질 모델 지정
lyricforge analyze "Kygo" "It Ain't Me" --model gemma3:12b
```

### LLM 프롬프트 (참고용)
```
다음 영어 노래 가사를 분석해서 영어 학습에 유용한 표현들을 추출해줘.

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
```

## 향후 계획 (Phase 2+)

### Phase 2: Supabase 연동
- 생성된 카드를 Supabase에 저장
- 노래/카드 중복 체크

### Phase 3: Flutter 앱
- Supabase에서 카드 불러오기
- 플래시카드 UI (스와이프)
- 간격 반복 학습 (Anki 스타일)
- Apple Music/Spotify 연동 (선택)

## 참고사항
- Genius 계정 필요 (무료): https://genius.com/api-clients
- Ollama 설치 필요: https://ollama.ai
- **권장 모델**: `gemma3:27b` (기본) 또는 `gemma3:12b` (중간 사양)

## 설치
```bash
# Python 패키지
pip install lyricsgenius

# Ollama 모델
ollama pull gemma3:27b
```

---

## TODO

### Phase 1: Mac CLI 도구 ✅
- [x] Genius 계정 생성 및 Access Token 발급
- [x] Ollama 설치 및 gemma3:27b 모델 다운로드
- [x] Python 프로젝트 초기화 (pyproject.toml)
- [x] lyricsgenius로 가사 가져오기 구현
- [x] Ollama 연동 및 LLM 분석 구현
- [x] JSON 출력 구현
- [x] CLI 인터페이스 구현 (typer)
- [ ] 테스트 (Kygo - It Ain't Me)

### Phase 2: Supabase 연동
- [ ] Supabase 프로젝트 생성
- [ ] 테이블 스키마 설계 (songs, flashcards)
- [ ] CLI에서 Supabase 업로드 기능 추가
- [ ] 중복 체크 로직

### Phase 3: Flutter 앱
- [ ] Flutter 프로젝트 초기화
- [ ] Supabase 연동
- [ ] 플래시카드 UI 구현
- [ ] 간격 반복 학습 로직
