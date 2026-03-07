# HWP Reference Libraries Analysis Report

> 2026-03-08 기준, 12개 GitHub 리포지토리 분석 결과

## Tier 1 — Primary (스킬 핵심)

### 1. airmang/python-hwpx ★★★★★
- **언어**: Pure Python (lxml only)
- **라이선스**: MIT
- **기능**: HWPX 읽기/쓰기/편집 완전 지원
- **API**: `HwpxDocument` — paragraphs, tables, memos, sections, headers/footers, styles, export (text/HTML/MD)
- **특이사항**: 50+ 사용 예제, Sphinx 문서, XSD 스키마 검증 CLI (`hwpx-validate`)
- **제약**: HWPX만 지원 (.hwp 미지원), 이미지 삽입 일부 제한, 암호화 미지원

### 2. KimDaehyeon6873/hwp-hwpx-parser ★★★★★
- **언어**: Pure Python (olefile only)
- **라이선스**: Apache 2.0
- **기능**: HWP + HWPX 읽기 전용. 텍스트/표/이미지/각주/미주/메모 추출
- **API**: 통합 `Reader` — `.text`, `.tables`, `.get_memos()`, `.get_images()`, `.get_tables_as_markdown()`
- **특이사항**: JVM 불필요, 경량, 중첩 표/이미지 위치 마커 지원
- **제약**: 읽기 전용 (편집은 hwp-hwpx-editor 별도 패키지)

### 3. HariFatherKR/hwp-parser (hwpparser) ★★★★☆
- **언어**: Python
- **라이선스**: MIT (but AGPL dependency via pyhwp)
- **기능**: CLI 변환 (HWP→Text/HTML/ODT/PDF, MD/HTML/DOCX→HWPX), LangChain loader, RAG chunking
- **API**: `hwpparser.convert()`, `hwpparser.read_hwp()`, `hwpparser.markdown_to_hwpx()`
- **특이사항**: Claude/ChatGPT/Gemini 스킬 템플릿 내장, 배치 변환, JSONL 인덱싱
- **제약**: pyhwp(AGPL) 의존 → 상용 서비스 주의

---

## Tier 2 — Specialized

### 4. iyulab/unhwp ★★★★
- **언어**: Rust + Python FFI + C# NuGet
- **라이선스**: MIT
- **기능**: HWP/HWPX → Markdown/Text/JSON 고속 변환
- **특이사항**: Rayon 병렬 처리, self-update, CLI pre-built binaries

### 5. Indosaram/hwpers ★★★★☆
- **언어**: Rust
- **라이선스**: MIT/Apache 2.0
- **기능**: HWP 5.0 파서 + 풀 레이아웃 렌더링 + SVG export + HWP 쓰기 (v0.3+)
- **특이사항**: 제로카피 파싱, 테이블/이미지/하이퍼링크/머리말까지 쓰기 지원

### 6. mete0r/pyhwp ★★★★☆
- **언어**: Python
- **라이선스**: AGPL v3 ⚠️
- **기능**: 레거시 HWP v5 파싱 + ODT 변환 (가장 오래된 표준)
- **특이사항**: 1k+ 스타, ReadTheDocs 문서, 안정적
- **제약**: AGPL 라이선스 (카피레프트)

---

## Tier 3 — Niche

### 7. volexity/hwp-extract ★★★★
- **보안 특화**: 패스워드 보호 HWP 추출 + 메타데이터
- **CLI**: `hwp-extract --extract-files --password 1234`

### 8. openhwp/openhwp ★★★☆
- **Rust 올인원**: hwp crate (parser) + hwpx crate (XML) + ir crate (중간 표현) + document (에디터용)
- **HWP↔HWPX 변환** 지원 (IR 경유)

### 9. hahnlee/hwp-rs ★★★★
- **Rust 저수준 파서**: Python `libhwp` 바인딩 존재
- **한국 개발자** 커뮤니티 활성

### 10. nonbanana/pyhwpx ★★★
- **경량 HWPX 파서**: 간단한 텍스트 추출

### 11. jongwony/python_hwp ★★★☆
- **python-docx 스타일 API**: ML 데이터 전처리 목적
- **HWP 5.0 전용**, 2020년 개발

### 12. BOB-APT-Solution/hwp-parser ★★☆
- **보안 특화**: HWP 내 JavaScript 매크로 추출
- **실습/연구용**: BOB(Best of the Best) 프로그램 결과물

---

## 스킬 조합 추천

| 용도                 | 1순위             | 2순위             |
| -------------------- | ----------------- | ----------------- |
| HWPX 문서 생성/편집  | python-hwpx       | (직접 XML 편집)   |
| HWP/HWPX 텍스트 읽기 | hwp-hwpx-parser   | hwpparser         |
| HWP→HWPX 변환        | hwpparser convert | unhwp             |
| MD/HTML→HWPX 변환    | hwpparser         | python-hwpx (API) |
| 고속 Markdown 변환   | unhwp (Rust)      | hwpparser         |
| 보안 분석            | hwp-extract       | bob-hwp-parser    |
| HWP 레이아웃 렌더링  | hwpers (Rust)     | —                 |
