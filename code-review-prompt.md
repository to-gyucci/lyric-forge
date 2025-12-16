# Code Review Prompt Template

## 기본 리뷰 요청

```
다음 코드를 리뷰해줘.

[코드 붙여넣기]

확인 사항:
1. 버그나 논리적 오류
2. 성능 이슈
3. 가독성/유지보수성
4. 개선 제안
```

---

## 보안 / 시크릿 체크

```
다음 코드의 보안 취약점을 검토해줘.

[코드 붙여넣기]

체크리스트:
- [ ] API 키가 하드코딩 되어있지 않은가?
- [ ] .env 파일이 .gitignore에 포함되어 있는가?
- [ ] 로그에 민감 정보가 출력되지 않는가?
- [ ] 에러 메시지에 내부 정보가 노출되지 않는가?
- [ ] 사용자 입력 검증이 적절한가?
```

---

## PR 전 최종 체크

```
PR 올리기 전 다음 코드를 검토해줘.

[코드 붙여넣기]

최종 체크리스트:
- [ ] 불필요한 print / console.log 제거
- [ ] 주석 처리된 코드 제거
- [ ] TODO 주석 확인
- [ ] 테스트 코드 작성 여부
- [ ] README 업데이트 필요 여부
- [ ] 하드코딩된 값 → 환경 변수 전환
- [ ] 에러 핸들링 완료
```

---

## LyricForge 프로젝트 전용

```
LyricForge 프로젝트 코드를 리뷰해줘.

[코드 붙여넣기]

프로젝트 컨텍스트:
- Python 3.9+ / typer + rich CLI
- Genius API (lyricsgenius) + Ollama LLM (gemma3:27b)
- Pydantic 데이터 모델 사용
- 커스텀 Exception: LyricsError, AnalyzerError

확인 사항:
- [ ] GENIUS_ACCESS_TOKEN이 .env로 처리되었는가?
- [ ] Ollama 연결 실패 시 에러 핸들링 (AnalyzerError)
- [ ] 가사 없는 곡 처리 (LyricsError)
- [ ] LLM 응답 JSON 파싱 실패 처리
- [ ] 타입 힌트 사용 여부
- [ ] JSON 출력 포맷 일관성 (AnalysisResult 모델)
```
