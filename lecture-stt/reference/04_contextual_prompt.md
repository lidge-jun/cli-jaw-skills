# 04. 프롬프트 컨텍스트 — LLM STT의 킬러 피처

## 핵심 원리

전용 STT는 **오디오만** 보고 판단한다. LLM STT는 **오디오 + 텍스트 힌트**를 동시에 본다.

```
전용 STT:  "수...정...원" → 음소 매칭 → "수종원" (DB에 없으니 가장 가까운 것)
LLM STT:  "수...정...원" + 힌트("수정원병원") → "수정원" ✅
```

이건 인간이 STT하는 방식과 같다:
- 경제학 수업인 걸 알면 "GDP"를 "지디피"로 안 적음
- 발표자 이름을 알면 "김준"을 "김쥰"으로 안 적음

## 프롬프트 템플릿

### Level 1: 기본 (컨텍스트 없음)
```
이 오디오를 한국어로 전사해주세요. 전사 텍스트만 출력.
```
- 용도: 일반 대화, 도메인 불명확할 때
- 한계: 고유명사 오류, 포맷 일관성 없음

### Level 2: 도메인 힌트
```
이 오디오를 한국어로 전사해주세요. 전사 텍스트만 출력.

컨텍스트: {도메인 설명}
관련 용어: {쉼표로 구분된 용어 목록}
```
- 용도: 전문 분야 (의학, 법률, 스타트업 등)
- 효과: 고유명사 정확도 ↑, 속도 ↑

### Level 3: 도메인 + 포맷
```
이 오디오를 한국어로 전사해주세요.

컨텍스트: {도메인 설명}
관련 용어: {용어 목록}
화자: {화자 정보, 알고 있다면}

출력 형식:
- 문장 단위로 줄바꿈
- 숫자는 아라비아 숫자 (예: 12,000개)
- 영어 고유명사는 영어로 (예: MVP, TIPS)
- 전사 텍스트만 출력
```

### Level 4: 전사 + 후처리
```
이 오디오를 한국어로 전사하고, 아래 형식으로 정리해주세요.

컨텍스트: {도메인}

## 전사
{전체 전사 텍스트}

## 요약 (3줄)
{핵심 내용 요약}

## 키워드
{핵심 키워드 5개}
```

## 실측 비교 (2026-03-04)

| 실제 단어 | generic | context 힌트 |
|----------|---------|-------------|
| 수정원병원 | ❌ 수종원 병원 | ✅ 수정원 병원 |
| 예비창업패키지 | ❌ 예비 창업 패키지 | ✅ 예비창업패키지 |
| 댓글몽 | 댓글 몽 | 댓글몽 (붙여쓰기) |
| 10,000개 | 1만 개 | 10,000개 |
| 속도 | 3.37s | **2.09s** (-38%) |

## 도메인별 프롬프트 예시

### 의학 강의
```
컨텍스트: 내과학 강의 (순환기 파트)
관련 용어: 심근경색, 관상동맥, 스텐트, PCI, CABG, 좌전하행지, 트로포닌, CK-MB, 심전도, ST분절
```

### 법률 회의
```
컨텍스트: 의료광고 심의 관련 법률 미팅
관련 용어: 의료법 제56조, 의료광고심의위원회, 금지어, 비급여, 시술 전후 사진, 환자 후기
```

### 스타트업 피칭
```
컨텍스트: AI 스타트업 IR 피칭
관련 용어: Series A, MRR, CAC, LTV, PMF, TAM, burn rate, runway
```

### 경제학 수업
```
컨텍스트: 거시경제학 강의
관련 용어: GDP, 통화정책, 양적완화, 테일러 준칙, 필립스 곡선, NAIRU, 유동성 함정
```

## Level 5: 강의 모드 (PDF + 오디오 + 보강 + 비핵심 요약) ← 기본 모드

```
You are a lecture note assistant. You are given a PDF slide deck and an audio
recording of a {subject} university lecture.

## Task
1. Transcribe ALL lecture content as detailed as possible — capture every
   explanation, example, and nuance the professor gives.
2. Follow the PDF slide structure (one section per slide).
3. Be THOROUGH — include all details, side stories, real-world examples.
4. For each slide, if there was non-essential speech (off-topic remarks,
   admin announcements, repetitive filler), write ONE summary line:
   *(Non-essential: [brief description])*
   - Maximum ONE such line per slide section
   - Only include this if there actually was non-essential content

## Supplementary Notes
- If the professor did NOT explain a PDF concept, add *[Supplementary: ...]*

## Output Format
- `---` dividers + slide title per slide
- Professor's examples in `> ` blockquote — be detailed, capture full reasoning
- Math in KaTeX: $Y = C + I + G$
- Sentence-level line breaks
- FOCUS boxes, case studies, warnings: include ALL
- Non-essential summary in *(italics with parentheses)* at end of slide section

## Key Terms
{domain-specific terms}
```

- PDF가 구조 가이드 역할 → 슬라이드별로 자동 구분
- 교수 설명 = blockquote, PDF만의 내용 = *Supplementary*
- 비핵심 발언 = *(Non-essential: ...)* 1줄 요약으로 투명하게 표시
- **44분 강의 → 32초, 18KB** (v2 대비 38% 더 상세)

## ⚠️ 안티패턴: 필러 마킹

```
❌ "Do NOT remove filler words. Mark them as (uh), (um), (okay)..."
```

이 프롬프트를 주면 모델이 **verbatim 전사 모드**로 전환된다:
- 출력 23배 폭증 (13KB → 297KB)
- 속도 8배 느려짐 (20s → 161s)
- 구조/KaTeX/슬라이드 분류 전부 소실
- 끝 부분에서 반복 루프 발생

**이유**: "필러를 남겨라" = "있는 그대로 적어라"로 해석됨.
LLM의 구조화 능력이 비활성화되어 전용 STT와 동일한 결과물이 나옴.

→ 필러가 궁금하면 전용 STT(Whisper)를 쓰는 게 맞다. LLM STT는 **변환** 도구.

## 주의사항

1. **용어 목록은 20개 이내** — 너무 많으면 오히려 혼란
2. **실제 등장 용어만** — 안 나오는 용어를 넣으면 환각 유발 가능
3. **한국어+영어 혼용 OK** — Gemini는 다국어 네이티브
4. **화자 이름 힌트** — "발표자: 김준" 넣으면 이름 오인식 방지
5. **필러 마킹 금지** — 구조화 능력 상실 (위 안티패턴 참조)
6. **PDF 있으면 반드시 포함** — 구조 가이드 없으면 출력 품질 급락
