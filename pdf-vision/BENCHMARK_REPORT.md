# pdf-expert E2E Benchmark Report

- **Date**: 2026-03-04
- **Test PDF**: `air 프로모션.pdf` (2.7 MB, 13 pages)
- **Platform**: macOS Darwin 25.2.0, Apple Silicon
- **Model**: Claude Opus 4.6

---

## 0. Dependency Check

| Dependency | Status | Version / Detail |
|---|---|---|
| pdfplumber | OK | 0.11.9 |
| pdftoppm | OK | 26.02.0 (Poppler) |
| swift | OK | Apple Swift 6.2 (swiftlang-6.2.0.19.9) |
| GEMINI_API_KEY | NOT SET | Step 3, 4 실행 불가 |

---

## Step 1 - pdf_check (PDF 분석 및 페이지 분류)

| Metric | Value |
|---|---|
| Elapsed Time | **0.294s** |
| Total Pages | 13 |
| Text Pages | 0 (0%) |
| OCR Pages | 13 (100%) |
| Exit Code | 0 (성공) |

### 상세 결과

- 모든 13개 페이지가 `ocr_pages`로 분류됨
- 이 PDF는 웹 페이지 캡처/스크린샷 형태로, 텍스트 레이어가 없는 이미지 기반 PDF
- pdfplumber 경고: `Could not get FontBBox from font descriptor` (6회 발생) - 동작에 영향 없음

### 발견된 이슈

- **경고 메시지**: FontBBox 파싱 경고가 stderr로 출력됨. 기능에는 영향 없으나, JSON 파싱 시 stderr와 stdout이 혼합되지 않도록 주의 필요
- **버그 없음**: 정상 동작 확인

---

## Step 2 - OCR (Vision Framework 기반 텍스트 인식)

### 2a. PNG 추출 (pdftoppm)

| Metric | Value |
|---|---|
| Elapsed Time | **7.787s** |
| Resolution | 300 DPI |
| Output Files | 13 PNG (총 3.9 MB) |
| Exit Code | 0 (성공) |

### 2b. Swift Vision OCR

| Metric | Value |
|---|---|
| Elapsed Time | **4.626s** |
| Concurrency | 3 |
| Pages Processed | 13/13 |
| Error Pages | 0 |
| Total Characters | 3,452 |
| Total Lines | 224 |
| Exit Code | 0 (성공) |

### 페이지별 OCR 결과

| Page | Chars | Lines | Quality |
|---|---|---|---|
| 01 | 157 | 13 | Good - 메인 타이틀, 요금 정보 |
| 02 | 136 | 10 | Good - 이벤트 코드 (SEMOT02) |
| 03 | 68 | 4 | Sparse - 이미지 위주 (헤더/푸터만) |
| 04 | 162 | 15 | Good - 무제한 요금제 가격 |
| 05 | 160 | 15 | Good - 100GB 요금제 가격 |
| 06 | 268 | 21 | Good - 공통 혜택 (eSIM, 친구초대, 만보기) |
| 07 | 326 | 34 | Good - 나머지 요금제 상세 (7GB~71GB) |
| 08 | 68 | 4 | Sparse - 이미지 위주 (헤더/푸터만) |
| 09 | 283 | 22 | Good - USIM/eSIM 이벤트, 에이닷 |
| 10 | 279 | 24 | Good - 에이닷 기능, 포인트 교환 |
| 11 | 69 | 4 | Sparse - 이미지 위주 (헤더/푸터만) |
| 12 | 733 | 30 | Excellent - 유의사항 상세 |
| 13 | 743 | 28 | Excellent - 유의사항 (친구초대/eSIM/USIM) |

### OCR 품질 분석

- **한글 인식 정확도**: 높음. "요금제", "포인트", "프로모션" 등 핵심 키워드 정확히 인식
- **숫자/가격 인식**: `월14,000원`, `월10,000원`, `월 58,000원` 등 정확히 인식
- **부분 인식 실패**: Page 4, 5에서 실 체감가가 `1^^^^임`으로 OCR됨 (장식 폰트/이미지 합성 영역)
- **Sparse Pages**: 3, 8, 11번 페이지는 이미지/그래픽 위주로 텍스트가 거의 없음 (정상)
- **레이아웃**: 단일 컬럼 텍스트 인식에 적합, 복잡한 테이블은 없음

### 발견된 이슈

1. **OCR 정확도 - 특수 폰트**: Page 4, 5에서 가격 `14,000원` / `10,000원`이 `1^^^^임`으로 인식됨. 이미지로 렌더링된 가격 영역은 Vision Framework가 인식 어려움
2. **Page 9 오타**: "개이 이저 과리까지" -> 원래 "개인 비서 관리까지" 추정. Vision OCR의 한계
3. **Page 10 오타**: "30,00C" -> "30,000" 추정. 숫자 C/0 혼동

---

## Step 3 - Embed (벡터 임베딩 생성)

| Metric | Value |
|---|---|
| Status | **FAILED** |
| Reason | `GEMINI_API_KEY` 미설정 |
| Pages Loaded | 13 |
| Chunks Created | 15 (모든 페이지 500자 이하 -> 페이지당 1 chunk) |
| Exit Code | 1 |

### 에러 메시지

```
ValueError: API key required for provider 'gemini'. Set GEMINI_API_KEY or OPENAI_API_KEY.
```

### 발견된 이슈

- **예상된 실패**: API 키 없이 실행 시 적절한 에러 메시지 출력 (정상적인 에러 핸들링)
- **개선 제안**: `--dry-run` 옵션이 있으면 API 키 없이도 청킹 결과만 미리 확인 가능

---

## Step 4 - Query (검색 테스트)

| Status | **SKIPPED** |
|---|---|
| Reason | Step 3 Embed 실패로 벡터 파일 미생성 |

### 테스트 예정 쿼리

1. `요금제 가격` - 요금 정보 검색
2. `프로모션 혜택` - 혜택 정보 검색
3. `가입 조건` - 가입 조건/유의사항 검색

> Step 3 성공 시 시맨틱 검색 + grep 검색 모두 테스트 가능.

---

## Summary

### Pipeline 전체 소요시간

| Step | Time | Status |
|---|---|---|
| pdf_check | 0.294s | SUCCESS |
| PNG extraction (pdftoppm) | 7.787s | SUCCESS |
| OCR (Swift Vision) | 4.626s | SUCCESS |
| Embed (Gemini API) | 0.079s | FAILED (no API key) |
| Query | - | SKIPPED |
| **Total (Step 1-2)** | **12.707s** | - |

### 성공 항목 (3/5)

1. pdf_check: PDF 분석 및 페이지 분류 정상
2. pdftoppm: 13페이지 PNG 추출 정상 (300 DPI)
3. Swift Vision OCR: 13페이지 한글 OCR 정상, 높은 인식률

### 실패/스킵 항목 (2/5)

4. pdf_embed: GEMINI_API_KEY 미설정으로 실패
5. pdf_query: 벡터 파일 없어 스킵

### 버그/이슈 목록

| # | Severity | Step | Description |
|---|---|---|---|
| 1 | Low | pdf_check | FontBBox 파싱 경고 (stderr). 기능 영향 없음 |
| 2 | Medium | OCR | 특수 폰트/이미지 합성 가격 영역 인식 실패 (`1^^^^임`) |
| 3 | Low | OCR | 한글 OCR 부분 오인식 (Page 9: "과리" -> "관리", Page 10: "30,00C") |
| 4 | Info | Embed | API 키 미설정 시 에러 핸들링 정상. `--dry-run` 옵션 추가 제안 |

### 개선 제안

1. **pdf_check**: stderr 경고 로그를 suppress 하거나, `warnings.filterwarnings`로 제어
2. **OCR**: Sparse 페이지(3, 8, 11)에 대해 OCR 스킵 옵션 (이미지 헤더/푸터만 있는 경우 불필요한 처리)
3. **pdf_embed**: `--dry-run` 모드 추가 - 청킹 결과만 미리 확인
4. **E2E**: 전체 파이프라인을 하나의 스크립트로 엮는 `pdf_pipeline.py` 제공 고려
