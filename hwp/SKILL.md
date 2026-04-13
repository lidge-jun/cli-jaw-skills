---
name: hwp
description: "HWP/HWPX create, read, edit, review. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents."
---

# HWPX Document Skill

Use this skill for any `.hwpx` task: create, read, edit, review, template-fill, or QA verification.
Triggers: `"한글"`, `".hwpx"`, `"HWP"`, `"HWPX"`, Korean documents, 한컴오피스, OWPML.
Primary tool: **officecli** (PATH — global install).
Fallback: **Legacy Python scripts** only when officecli does not cover the operation.
Do NOT use this skill for PDFs, spreadsheets, or DOCX files.

---

## Tool Discovery

Always confirm syntax from help before guessing:

```bash
officecli --help
officecli hwpx add
officecli hwpx set
officecli hwpx view --help
```

### Binary Location

| Binary | Path | Notes |
|--------|------|-------|
| officecli | `officecli` (PATH) | Primary — full HWPX support via global install |

---

## Legacy Python Fallback (officecli 미지원 기능)

officecli가 지원하지 않는 작업은 `skills_ref/hwp/scripts/` Python 스크립트를 사용.
스크립트 경로: `~/.cli-jaw/skills_ref/hwp/scripts/`

| Task | Tool | Command |
|------|------|---------|
| **HWP 5.0 바이너리 읽기** | `hwp_reader.py` | `python scripts/hwp_reader.py input.hwp` |
| **HWP→HWPX 변환** | `hwp_convert.py` | `python scripts/hwp_convert.py input.hwp output.hwpx` |
| **HWPX 생성 (템플릿)** | `build_hwpx.py` | `python scripts/build_hwpx.py --template report --output out.hwpx` |
| **텍스트 추출 (Python)** | `text_extract.py` | `python scripts/text_extract.py input.hwpx` |
| **HWPX 언팩/편집/리팩** | `hwpx_cli.py` | `python scripts/hwpx_cli.py open input.hwpx work/` → edit → `save work/ out.hwpx` |
| **검색/치환** | `hwpx_cli.py` | `python scripts/hwpx_cli.py replace input.hwpx "old" "new" -o out.hwpx` |
| **배치 치환** | `hwpx_cli.py` | `python scripts/hwpx_cli.py batch-replace input.hwpx map.json -o out.hwpx` |
| **테이블 조작** | `hwpx_cli.py` | `python scripts/hwpx_cli.py fill-table input.hwpx IDX '{"label>dir":"val"}' -o out.hwpx` |
| **HWPX→PDF 변환** | `soffice` | `soffice --headless --convert-to pdf --outdir /tmp input.hwpx` |
| **시각 QA** | PDF→이미지 | `pdftoppm -jpeg -r 150 out.pdf preview` → 서브에이전트 검수 |
| **검증 (Python)** | `validate.py` | `python scripts/validate.py input.hwpx` |
| **페이지 수 보호** | `page_guard.py` | `python scripts/page_guard.py -r ref.hwpx -o out.hwpx` |
| **문서 구조** | `hwpx_cli.py` | `python scripts/hwpx_cli.py structure input.hwpx` |
| **수리** | `hwpx_cli.py` | `python scripts/hwpx_cli.py repair input.hwpx --apply` |

### Python 환경 의존성

```bash
pip install pyhwp lxml   # HWP 읽기 + XML 처리
# soffice: LibreOffice 설치 필요 (macOS: brew install --cask libreoffice)
# H2Orestart: Java 기반 HWP 변환 엔진 (PDF 변환 시 필요)
```

### 포맷 판별

```bash
file doc.hwpx   # "Zip archive" → HWPX
file doc.hwp    # "HWP Document" → HWP 5.0 (binary, read-only)
```

> **우선순위**: officecli로 가능하면 officecli 사용. Python은 officecli가 못 하는 작업(HWP 바이너리 읽기, 변환, PDF 출력, 템플릿 기반 생성)에만 사용.

---

## Quick Decision

| Task | Command | Notes |
|------|---------|-------|
| Read text | `officecli view doc.hwpx text` | `text`, `annotated`, `outline`, `stats`, `html`, `styles`, `forms`, `tables`, `markdown`, `objects` |
| Add paragraph | `officecli add doc.hwpx /section --type paragraph --prop text="내용"` | First add replaces empty p[1] |
| Edit paragraph | `officecli set doc.hwpx /section/p[1] --prop bold=true --prop align=CENTER` | |
| Add table | `officecli add doc.hwpx /section --type table --prop rows=3 --prop cols=4` | |
| Edit cell | `officecli set doc.hwpx '/section/p[N]/tbl[1]/tr[1]/tc[1]' --prop text="값"` | |
| Add heading | `officecli add doc.hwpx /section --type paragraph --prop text="제목" --prop styleidref=2 --prop bold=true` | styleidref=2 = 개요 1 |
| Add image | `officecli add doc.hwpx /section --type picture --prop src=image.png` | |
| Add shape | `officecli add doc.hwpx /section --type rect --prop width=20000 --prop height=10000 --prop fillcolor=#4472C4` | `line`, `rect`, `ellipse`, `textbox`, `polygon`, `triangle`, `pentagon`, `arrow` |
| Add field | `officecli add doc.hwpx /section --type clickhere` | `clickhere`, `filepath`, `summary`, `date` |
| New form field creation | `officecli add doc.hwpx /section[1] --type formfield --prop type=text` | **Blocked** — source prototype exists, but Hancom golden/manual verification and published binary parity are not closed |
| Add TOC | `officecli add doc.hwpx /section --type toc` | `--prop mode=field` for field-based |
| Add section | `officecli add doc.hwpx / --type section --prop orientation=LANDSCAPE` | Multi-section |
| Find/replace | `officecli set doc.hwpx / --prop find="old" --prop replace="new"` | Regex: `find=regex:\d+` |
| **Label fill** | `officecli set doc.hwpx / --prop 'fill:대표자=홍길동'` | 라벨 옆 셀 자동 채우기 |
| Label fill (방향) | `officecli set doc.hwpx / --prop 'fill:주소>down=서울시'` | right(기본), down, left, up |
| Label fill (batch) | `officecli set doc.hwpx /table/fill --prop '대표자=홍길동' --prop '직위=이사'` | fill: prefix 생략 |
| Form recognize | `officecli view doc.hwpx forms --auto` | 테이블 label-value 자동 인식 (Plan 70.1) |
| Form recognize JSON | `officecli view doc.hwpx forms --auto --json` | AI 파이프라인: recognize → map → fill |
| **Table map** | `officecli view doc.hwpx tables` | 테이블 2D 그리드 + 라벨 맵 (Plan 71) |
| **Markdown export** | `officecli view doc.hwpx markdown` | GFM 마크다운 변환 (Plan 72) |
| **Object finder** | `officecli view doc.hwpx objects` | picture/field/bookmark/equation 목록 (Plan 82) |
| Object filter | `officecli view doc.hwpx objects --object-type picture` | 특정 타입만 필터 |
| **Expanded query** | `officecli query doc.hwpx 'tc[text~=홍길동]'` | `=`, `!=`, `~=`, `>=`, `<=`, `:has()`, `:contains()`, `>` combinator (Plan 75) |
| **MD→HWPX import** | `officecli create out.hwpx --from-markdown input.md` | 마크다운 → HWPX 변환 (Plan 85) |
| MD import (왼쪽정렬) | `officecli create out.hwpx --from-markdown input.md --align left` | justify(기본), left, center, right |
| **Template merge** | `officecli merge tpl.hwpx out.hwpx --data '{"key":"val"}'` | `{{key}}` 플레이스홀더 치환 (Plan 95) |
| Template merge (JSON) | `officecli merge tpl.hwpx out.hwpx --data data.json` | JSON 파일도 가능 |
| **Document diff** | `officecli compare a.hwpx b.hwpx` | text/outline/table diff (Plan 84) |
| Diff (mode) | `officecli compare a.hwpx b.hwpx --mode outline --json` | --mode text\|outline\|table, --json |
| **Swap** | `officecli swap doc.hwpx '/section[1]/p[1]' '/section[1]/p[2]'` | 두 요소 순서 교환 (Plan 96) |
| **Column break** | `officecli add doc.hwpx /section[1] --type columnbreak --prop cols=2` | 2단/3단 레이아웃 (Plan 96) |
| **Image watermark** | `officecli add doc.hwpx /section[1] --type watermark --prop src=watermark.png` | Plan 98 재활성화. Opaque RGB 권장, light/simple asset은 `bright=0 --prop contrast=0` 권장 |
| **Image anchor** | `officecli add doc.hwpx /section[1] --type picture --prop anchor=page --prop halign=center --prop valign=middle` | Plan 98B. 페이지/문단 기준 floating, 계산형 위치 지원 |
| **Author field** | `officecli add doc.hwpx /section[1] --type author` | 만든 사람 필드 (Plan 97) |
| Title field | `officecli add doc.hwpx /section[1] --type title` | 문서 제목 필드 |
| Filename field | `officecli add doc.hwpx /section[1] --type filename` | 파일명 필드 |
| Watch HWPX | `officecli watch doc.hwpx` | 라이브 HTML 프리뷰 (Plan 74) |
| Remove | `officecli remove doc.hwpx /section/p[3]` | Also: `/toc`, `/watermark`, `/section[2]` |
| Set metadata | `officecli set doc.hwpx / --prop title="문서제목" --prop author="작성자"` | |
| HTML preview | `officecli view doc.hwpx html --browser` | A4 미리보기 |
| Validate | `officecli validate doc.hwpx` | 9-level: ZIP, package, XML, IDRef, table, NS, BinData, field pair |
| Raw XML | `officecli raw doc.hwpx Contents/section0.xml` | 디버깅용 |
| Form value | `officecli set doc.hwpx '/formfield[ID]' --prop value="홍길동"` | 누름틀 값 설정 |

---

## Legacy Python Fallback (officecli 미지원 기능)

officecli가 지원하지 않는 작업은 `skills_ref/hwp/scripts/` Python 스크립트를 사용.
스크립트 경로: `~/.cli-jaw/skills_ref/hwp/scripts/`

| Task | Tool | Command |
|------|------|---------|
| **HWP 5.0 바이너리 읽기** | `hwp_reader.py` | `python scripts/hwp_reader.py input.hwp` |
| **HWP→HWPX 변환** | `hwp_convert.py` | `python scripts/hwp_convert.py input.hwp output.hwpx` |
| **HWPX 생성 (템플릿)** | `build_hwpx.py` | `python scripts/build_hwpx.py --template report --output out.hwpx` |
| **텍스트 추출 (Python)** | `text_extract.py` | `python scripts/text_extract.py input.hwpx` |
| **HWPX 언팩/편집/리팩** | `hwpx_cli.py` | `python scripts/hwpx_cli.py open input.hwpx work/` → edit → `save work/ out.hwpx` |
| **검색/치환** | `hwpx_cli.py` | `python scripts/hwpx_cli.py replace input.hwpx "old" "new" -o out.hwpx` |
| **배치 치환** | `hwpx_cli.py` | `python scripts/hwpx_cli.py batch-replace input.hwpx map.json -o out.hwpx` |
| **테이블 조작** | `hwpx_cli.py` | `python scripts/hwpx_cli.py fill-table input.hwpx IDX '{"label>dir":"val"}' -o out.hwpx` |
| **HWPX→PDF 변환** | `soffice` | `soffice --headless --convert-to pdf --outdir /tmp input.hwpx` |
| **시각 QA** | PDF→이미지 | `pdftoppm -jpeg -r 150 out.pdf preview` → 서브에이전트 검수 |
| **검증 (Python)** | `validate.py` | `python scripts/validate.py input.hwpx` |
| **페이지 수 보호** | `page_guard.py` | `python scripts/page_guard.py -r ref.hwpx -o out.hwpx` |
| **문서 구조** | `hwpx_cli.py` | `python scripts/hwpx_cli.py structure input.hwpx` |
| **수리** | `hwpx_cli.py` | `python scripts/hwpx_cli.py repair input.hwpx --apply` |

### Python 환경 의존성

```bash
pip install pyhwp lxml   # HWP 읽기 + XML 처리
# soffice: LibreOffice 설치 필요 (macOS: brew install --cask libreoffice)
# H2Orestart: Java 기반 HWP 변환 엔진 (PDF 변환 시 필요)
```

### 포맷 판별

```bash
file doc.hwpx   # "Zip archive" → HWPX
file doc.hwp    # "HWP Document" → HWP 5.0 (binary, read-only)
```

> **우선순위**: officecli로 가능하면 officecli 사용. Python은 officecli가 못 하는 작업(HWP 바이너리 읽기, 변환, PDF 출력, 템플릿 기반 생성)에만 사용.

---

## Core Command Model

officecli syntax is **file-first**:

```bash
officecli view FILE MODE
officecli add FILE PARENT --type TYPE --prop key=value
officecli set FILE PATH --prop key=value
officecli remove FILE PATH
officecli query FILE "selector"
officecli get FILE PATH
officecli raw FILE ENTRY_PATH
```

### PATH Syntax

```text
/section                    # First section (shortcut for /section[1])
/section[N]                 # Nth section (1-based)
/section/p[N]               # Nth paragraph
/section/p[N]/tbl[1]        # Table inside paragraph N (auto-traverses run)
/section/p[N]/tbl[1]/tr[R]/tc[C]  # Cell at row R, column C
/header/style[N]            # Nth style in header
/formfield[ID]              # Form field by instId
/                           # Document root
/toc                        # TOC (for remove)
/watermark                  # Page background (for remove)
```

---

## Common Workflows

### Create and populate a document

```bash
officecli add doc.hwpx /section --type paragraph --prop text="분기별 보고서" --prop styleidref=2 --prop bold=true --prop fontsize=20
officecli add doc.hwpx /section --type paragraph --prop text="매출이 전년 대비 15% 증가했습니다."
officecli add doc.hwpx /section --type paragraph --prop text="상세 내용" --prop italic=true --prop color=#FF0000
```

### Tables

```bash
officecli add doc.hwpx /section --type table --prop rows=3 --prop cols=3
officecli set doc.hwpx '/section/p[2]/tbl[1]/tr[1]/tc[1]' --prop text="항목" --prop align=CENTER
officecli set doc.hwpx '/section/p[2]/tbl[1]/tr[1]/tc[2]' --prop text="값"
officecli set doc.hwpx '/section/p[2]/tbl[1]/tr[1]' --prop height=3000
officecli set doc.hwpx '/section/p[2]/tbl[1]' --prop colwidth1=20000
```

### Shapes and drawings

```bash
officecli add doc.hwpx /section --type line --prop width=30000
officecli add doc.hwpx /section --type rect --prop width=20000 --prop height=8000 --prop fillcolor=#4472C4 --prop text="사각형"
officecli add doc.hwpx /section --type ellipse --prop width=15000 --prop height=10000 --prop fillcolor=#FFC000
officecli add doc.hwpx /section --type textbox --prop width=25000 --prop height=5000 --prop text="텍스트 상자"
officecli add doc.hwpx /section --type triangle --prop width=15000 --prop height=13000 --prop fillcolor=#FF6347
officecli add doc.hwpx /section --type arrow --prop width=25000 --prop color=#FF0000
```

### Fields and forms

```bash
officecli add doc.hwpx /section --type clickhere --prop direction="이름을 입력하세요"
officecli add doc.hwpx /section --type filepath
officecli add doc.hwpx /section --type summary --prop command='$createtime'
officecli view doc.hwpx forms
officecli set doc.hwpx '/formfield[2019709239]' --prop value="홍길동"
```

### Multi-section

```bash
officecli add doc.hwpx / --type section --prop orientation=LANDSCAPE
officecli add doc.hwpx '/section[2]' --type paragraph --prop text="가로 페이지"
officecli set doc.hwpx /section --prop margintop=8504
officecli remove doc.hwpx '/section[2]'
```

### Label-based table fill (Plan 70)

```bash
# 라벨 기반 자동 채우기 — 테이블에서 라벨 텍스트를 찾아 인접 셀에 값 입력
officecli set form.hwpx / --prop 'fill:대표자=홍길동' --prop 'fill:주소=서울시 강남구'
officecli set form.hwpx / --prop 'fill:설립일>down=2025년 9월' # 아래 방향
officecli set form.hwpx /table/fill --prop '이름=김서준' --prop '학번=2023156789' # prefix 생략
```

### Form recognize → fill 파이프라인 (Plan 70.2-70.4 ✅)

```bash
# AI 자동 양식 채우기 워크플로우 (3-step)
# Step 1: 테이블 label-value 자동 인식
officecli view form.hwpx forms --auto --json > fields.json
# Output: {"clickHere": [...], "autoRecognized": [{"label":"성 명","value":"","path":"...", ...}]}

# Step 2: AI가 인식된 라벨에 값 매핑 (label 그대로 사용 — NormalizeLabel 동일)

# Step 3: fill (인식된 라벨 → 동일 셀 매칭)
officecli set form.hwpx /table/fill --prop '성 명=홍길동' --prop '학 번=2024123456'
```

### Table map — 테이블 구조 한눈에 파악 (Plan 71 ✅)

```bash
# 이전: 30+ 명령어로 수동 cellAddr 매핑 → 이제 한 줄
officecli view doc.hwpx tables
# Table 1 (/section[1]/tbl[1], 8×4):
#   [0] 접수번호  2026-0412-001  접수일자  2026.04.12
#   [1] 동아리명  넥스트레벨    사업분야  AI/소프트웨어
#   Labels: 21
#     접수번호: 2026-0412-001 (r0,c0)
#     대표자: 이지은 (r2,c0)

# JSON 출력 (AI 파이프라인용)
officecli view doc.hwpx tables --json
```

### Markdown export (Plan 72 ✅)

```bash
officecli view doc.hwpx markdown
# **고려대학교 창업동아리 참가신청서**
# | 접수번호 | 2026-0412-001 | 접수일자 | 2026.04.12 |
# | --- | --- | --- | --- |
# ...
```

### Object finder — 특정 타입 객체 검색 (Plan 82 ✅)

```bash
officecli view doc.hwpx objects                      # 전체: picture, field, bookmark, equation
officecli view doc.hwpx objects --object-type field   # 필드만
officecli view doc.hwpx objects --json                # JSON
```

### Image watermark — Hancom validated recipe (Plan 98 재활성화, 2026-04-13)

```bash
officecli add doc.hwpx /section[1] \
  --type watermark \
  --prop src=/path/to/watermark.png \
  --prop bright=0 \
  --prop contrast=0
```

실전 규칙:
- **Opaque RGB PNG 우선** — 투명 PNG(RGBA)는 한컴 page background 경로에서 불안정할 수 있음
- **단순한 흰 배경 + 연한 회색 텍스트는 기본 필터(`bright=70`, `contrast=-50`)에서 사라질 수 있음**
- **간단한 텍스트 워터마크는 2112×1162 캔버스의 미리 렌더링된 PNG로 전달하는 것이 안전**
- **`build-local/officecli` 1.0.42에서는 동작 확인**, `~/.local/bin/officecli`가 `Unsupported element type: watermark`를 내면 바이너리 재빌드/동기화 필요

### Image anchor / floating picture (Plan 98B ✅)

```bash
# 기본: inline (글자처럼 취급)
officecli add doc.hwpx /section[1] --type picture --prop path=image.png

# 페이지 기준 정중앙
officecli add doc.hwpx /section[1] --type picture \
  --prop path=image.png \
  --prop anchor=page \
  --prop halign=center \
  --prop valign=middle \
  --prop width=10000 \
  --prop height=5000

# 페이지 기준 우하단 근처
officecli add doc.hwpx /section[1] --type picture \
  --prop path=image.png \
  --prop anchor=page \
  --prop halign=right \
  --prop valign=bottom \
  --prop x=-1200 \
  --prop y=-800

# 문단 기준 floating
officecli add doc.hwpx /section[1] --type picture \
  --prop path=image.png \
  --prop anchor=para \
  --prop wrap=square \
  --prop halign=center \
  --prop y=1200

# 글 뒤로
officecli add doc.hwpx /section[1] --type picture \
  --prop path=image.png \
  --prop wrap=behind

# 생성 후 위치/잠금 수정
officecli set doc.hwpx '/section[1]/p[2]/run[1]/pic[1]' \
  --prop x=1111 --prop y=2222 --prop lock=1 --prop wrap=topbottom
```

핵심 규칙:
- `anchor=page`는 **용지 전체(PAPER)** 기준
- 중앙/우측/하단 정렬은 새 enum이 아니라 offset 계산으로 구현됨
- `anchor=para`는 V1에서 본문 폭 기준 가로 배치 + `y` explicit only
- `wrap=behind`, `wrap=front`, `wrap=square`, `wrap=topbottom` 지원
- set 경로는 현재 `x`, `y`, `lock`, `wrap=topbottom`까지만 문서화
- picture path는 `'/section[1]/p[N]/run[1]/pic[1]'` 형태를 사용

### Expanded query — 확장 셀렉터 문법 (Plan 75 ✅)

```bash
officecli query doc.hwpx 'run[bold=true]'              # 굵은 글씨 run
officecli query doc.hwpx 'tc[text~=홍길동]'            # 셀 텍스트 검색
officecli query doc.hwpx 'p:has(tbl)'                  # 테이블 포함 단락
officecli query doc.hwpx 'tbl > tr > tc[colSpan!=1]'   # 병합 셀
officecli query doc.hwpx 'p[heading=1]'                # heading level 1
officecli query doc.hwpx 'run[fontsize>=20]'           # 20pt 이상 run
```

### 기존 문서 편집 — 테이블 구조 파악 필수 워크플로우

```bash
# 1단계: 전체 테이블 맵 (Plan 71 — 수동 매핑 대체)
officecli view doc.hwpx tables

# 2단계: 특정 셀 검색 (Plan 75 — 확장 쿼리)
officecli query doc.hwpx 'tc[text~=대표자]'

# 3단계: 편집 (label fill 또는 직접 경로)
officecli set doc.hwpx /table/fill --prop '대표자=홍길동'
# 또는
officecli set doc.hwpx '/section/p[N]/tbl[1]/tr[R]/tc[C]' --prop 'text=값'

# 4단계: PDF로 시각 검증
soffice --headless --convert-to pdf --outdir /tmp doc.hwpx
```

### Find/replace (basic, regex, scoped)

```bash
officecli set doc.hwpx / --prop find="중요" --prop replace="핵심"
officecli set doc.hwpx / --prop 'find=regex:\d{3}-\d{4}' --prop 'replace=***-****'
officecli set doc.hwpx '/section[1]' --prop find="가" --prop replace="나"
```

### Read and inspect

```bash
officecli view doc.hwpx text
officecli view doc.hwpx annotated
officecli view doc.hwpx outline
officecli view doc.hwpx stats
officecli view doc.hwpx html --browser
officecli view doc.hwpx styles
officecli view doc.hwpx forms
officecli get doc.hwpx /
officecli query doc.hwpx "p:contains(검색어)"
```

### Styles

```bash
officecli view doc.hwpx styles
officecli add doc.hwpx / --type style --prop name="강조체" --prop engname=Emphasis
officecli set doc.hwpx '/section/p[3]' --prop style=강조체
officecli set doc.hwpx '/header/style[2]' --prop fontsize=16 --prop bold=true
```

### Metadata

```bash
officecli set doc.hwpx / --prop title="보고서" --prop author="홍길동" --prop subject="분기보고"
officecli view doc.hwpx stats   # Title/Creator 표시
```

### Remove with cascade

```bash
officecli remove doc.hwpx /section/p[3]           # 단락 삭제
officecli remove doc.hwpx /section/p[5]            # 표 wrapper 삭제
officecli remove doc.hwpx /toc                     # 목차 삭제 (V1+V2)
officecli remove doc.hwpx /watermark               # 배경색 삭제
officecli remove doc.hwpx '/section[2]'            # 섹션 삭제
```

---

## Settable Properties

### Paragraph-level

| Property | Example | Notes |
|----------|---------|-------|
| `text` | `text=안녕하세요` | |
| `bold` | `bold=true` | |
| `italic` | `italic=true` | |
| `underline` | `underline=true` | |
| `strikeout` | `strikeout=true` | |
| `fontsize` | `fontsize=16` | **pt 단위** (16 = 16pt → height=1600) |
| `color` | `color=#FF0000` | |
| `align` | `align=CENTER` | LEFT, CENTER, RIGHT, JUSTIFY |
| `charspacing` | `charspacing=-5` | 자간 (%) |
| `hangingindent` | `hangingindent=500` | 내어쓰기 (HWPML units, 283≈1mm) |
| `keepnext` | `keepnext=true` | 다음 문단과 함께 |
| `pagebreakbefore` | `pagebreakbefore=true` | 페이지 나눔 |
| `style` | `style=강조체` | 스타일 이름 적용 |
| `highlight` | `highlight=#FFFF00` | 형광펜 |

### Section-level

| Property | Example | Notes |
|----------|---------|-------|
| `pagebackground` | `pagebackground=#F5F5DC` | 배경색 |
| `orientation` | `orientation=LANDSCAPE` | NARROWLY (가로), WIDELY (세로) |
| `margintop` | `margintop=8504` | HWPML units |
| `pagewidth` | `pagewidth=59528` | |

### Table/Cell-level

| Property | Target | Example |
|----------|--------|---------|
| `text` | tc | 셀 텍스트 |
| `align` | tc | 수평 정렬 |
| `valign` | tc | 수직 정렬 (TOP, CENTER, BOTTOM) |
| `colspan` | tc | 셀 병합 |
| `height` | tr | 행 높이 |
| `colwidth1` | tbl | 개별 열 너비 (1-based) |

### Shape-level

| Property | Target | Example |
|----------|--------|---------|
| `wrap` | shape | `char` (글자처럼), `square`, `behind`, `front` |
| `x` | pic/shape | `x=1111` |
| `y` | pic/shape | `y=2222` |
| `lock` | pic/shape | `lock=1` |
| `width` | shape | 크기 |
| `height` | shape | 크기 |

---

## HWPX-Specific Notes

### Units
- Font size: **pt** (fontsize=16 = 16pt, internally stored as 1600 centi-points)
- Page dimensions: HWPML units (59528 = A4 width, 84186 = A4 height)
- Margins: HWPML units (8504 ≈ 30mm)
- 283 units ≈ 1mm

### Orientation
- `WIDELY` = 세로 (portrait) — 한컴 기본
- `NARROWLY` = 가로 (landscape)
- 치수(width/height)는 바뀌지 않음 — landscape 속성만 변경

### 글자처럼 취급 (Inline)
- `<hp:pos treatAsChar="1">` = 글자처럼 취급
- `officecli set doc.hwpx '/section/p[3]/rect[1]' --prop wrap=char`

### Image anchor / picture path
- 그림 객체는 실제 XML에서 `<hp:pic>` 이다
- set/get 경로는 `'/section[1]/p[N]/run[1]/pic[1]'` 형태를 사용
- `anchor=page`는 `PAPER/PAPER`, `anchor=para`는 `PARA/PARA`
- 중앙 정렬은 `halign=center`, `valign=middle` + offset 계산

### 누름틀 (CLICK_HERE)
- `type="CLICK_HERE"` (underscore 포함)
- 빨간 이탤릭 charPr 자동 생성
- `dirty="0"` for fresh, `"1"` after user edit

### TOC
- **V1 (static)**: `--type toc` — 텍스트 기반, 즉시 표시
- **V2 (field)**: `--type toc --prop mode=field` — 한컴에서 "필드 업데이트" 가능

---

## Critical Gotchas

### linesegarray (Layout Cache)
HWPX paragraphs contain `<hp:linesegarray>` — Hancom's **layout cache** storing line break positions.
When modifying text via `officecli set`, this cache is automatically invalidated (removed).
Hancom recalculates layout on open.

**If you ever edit HWPX XML directly** (not via officecli), you MUST delete ALL `<hp:linesegarray>` elements
from every section XML. Stripping ALL (not just changed paragraphs) is safe and simplest — Hancom
fully recalculates layout on open. Stale cache causes:
- Text compressed into single line (characters overlap)
- Visible in Hancom only (officecli text view looks correct)

**Verified on 3 document types** (2026-04-13):
- KICE exam template: 193 lineseg stripped, full edit (year/subject/period/equation/text) — Hancom OK
- University application form (참가신청서): 472 paragraphs, lineseg stripped — Hancom OK
- Regulation document (운영지침, HWP→HWPX converted): 599 lineseg stripped, 6 edits (year/name/phone/email) — Hancom OK

**Python strip pattern** (from pack.py, regex-based for namespace safety):
```python
re.sub(r'<(?:hp:)?linesegarray[^>]*>.*?</(?:hp:)?linesegarray>', '', xml, flags=re.DOTALL)
re.sub(r'<(?:hp:)?linesegarray[^/]*/>', '', result)  # self-closing
```

### charPr height is centi-points
`fontsize=16` (pt) → internally stored as `height=1600`. officecli handles conversion.

### Orientation values are counterintuitive
- `WIDELY` = 세로 (portrait) — default
- `NARROWLY` = 가로 (landscape)
- Page dimensions (width/height) do NOT change

### CLICK_HERE field type
- Must be `type="CLICK_HERE"` (with underscore), not `"CLICKHERE"`
- Hancom uses `"SUMMERY"` (not `"SUMMARY"`)

### Form field creation (Plan 100) is not release-closed
- `text/checkbox/dropdown` formfield creation has a source prototype, but the feature is still blocked
- Reason: Hancom golden template diff and manual verification are not closed
- If a local binary reports `Unsupported element type: formfield`, treat that as expected until the build is republished and acceptance is complete

### charPr 공유 오염 — fontsize는 반드시 모든 단락에 명시
`add --prop fontsize=22`는 charPr ID 0 (전역 기본)을 22pt로 수정한다.
이후 fontsize를 지정하지 않은 모든 단락이 22pt로 생성됨.
**해결**: 모든 `add` 호출에 반드시 `fontsize=N`을 명시. 테이블 셀도 마찬가지 — 기본 charPr를 공유하므로 의도하지 않은 크기가 적용될 수 있음.
```bash
# BAD: fontsize 미지정 → charPr 0의 크기 상속 (오염 시 22pt)
officecli add doc.hwpx /section --type paragraph --prop 'text=본문'
# GOOD: 항상 명시
officecli add doc.hwpx /section --type paragraph --prop 'text=본문' --prop fontsize=11
```

### Image anchor는 alignment enum이 아니라 offset 계산
- `anchor=page --prop halign=center --prop valign=middle` 은 `horzOffset` / `vertOffset` 계산으로 저장됨
- `anchor=para`는 V1에서 세로 중앙 정렬을 일반화하지 않음 — `y`를 명시적으로 주는 것이 안전
- `wrap=char`가 아니거나 `anchor/page/para`, `x/y`, `halign/valign`이 들어오면 floating picture 경로로 본다

### SetCellText clears ALL paragraphs
`officecli set ... --prop text=값`은 셀 내 **모든 단락**을 제거하고 새 텍스트를 넣는다.
가이드 텍스트(※ 내용을 입력하세요)가 자동 삭제됨. 여러 줄을 보존해야 하면 find/replace 사용.

### Table cell mapping — cellAddr 필수 확인
HWPX 테이블은 복잡한 병합 구조를 가짐. `tc[N]`은 **물리적 순서**, `cellAddr`는 **논리적 그리드 좌표**.
편집 전 반드시 cellAddr 매핑:
```bash
officecli get doc.hwpx '/section/p[N]/tbl[1]/tr[R]/tc[C]'
# → row: X, col: Y, rowSpan: M, colSpan: N
```
**주의**: 같은 `tr[R]`의 `tc[3]`과 `tc[4]`가 시각적으로 인접하지 않을 수 있음 (colSpan 때문).
병합된 행의 하단 row는 셀 수가 적음 (나머지는 rowSpan으로 가려짐).

### find/replace 스코프 주의
`officecli set doc.hwpx / --prop 'find=X' --prop 'replace=Y'` 는 **전체 문서** 대상.
동일 패턴이 여러 곳에 있으면 **모두 치환됨**. 특정 영역만 치환하려면 스코프 지정:
```bash
officecli set doc.hwpx '/section/p[2]' --prop 'find=□' --prop 'replace=■'     # 해당 테이블만
officecli set doc.hwpx '/section/p[10]/tbl[1]/tr[4]/tc[3]' --prop 'find=□ 학부' --prop 'replace=■ 학부'  # 특정 셀만
```

### charPr 0 (전역 기본 스타일)은 자동 보호
officecli는 charPr ID=0 (전역 기본)을 직접 수정하지 않고 항상 clone한다.
`add --prop fontsize=22`로 제목을 만들어도 테이블/본문의 기본 폰트 크기에 영향 없음.
이전에 테이블 셀이 24pt로 생성되던 버그가 이것으로 해결됨.

### File locking — Finder/한컴 열린 상태에서도 편집 가능
officecli는 `FileShare.ReadWrite`로 파일을 여므로 Finder 미리보기나 한컴이 열려 있어도 편집 가능.

### Form recognize → fill 파이프라인 라벨 계약 (Plan 70.2-70.4 ✅)
`forms --auto` (인식)과 `/table/fill` (채우기) 모두 내부적으로 `NormalizeLabel()`을 호출:
trim → 공백 축소 → 콜론 제거. 인식 결과의 label을 그대로 fill에 전달하면 동일 셀을 찾음.
```bash
# Step 1: 인식 → JSON
officecli view form.hwpx forms --auto --json > fields.json
# Step 2: AI가 label-value 매핑 생성 (label 그대로 사용)
# Step 3: fill (NormalizeLabel 동일 → 같은 셀 매칭)
officecli set form.hwpx /table/fill --prop '성 명=홍길동' --prop '학 번=2024123456'
```

### BuildTableGrid — 2D 그리드 공유 인프라 (Plan 70.1 ✅)
`FindCellInTable()`에서 추출된 `BuildTableGrid(tbl)` 헬퍼.
Plan 70 (label fill), Plan 70.2 (form recognize), Plan 71 (table map view), Plan 82 (object finder)에서 공유.
cellAddr + rowSpan/colSpan 기반 2D `XElement?[,]` 배열 반환.

### Corpus smoke testing (Plan 86 ✅)
16개 실전 HWPX (jakal-hwpx 샘플)로 open→view→validate smoke path 자동 실행.
xUnit `[Theory]` + `[MemberData]`로 corpus 디렉토리 자동 스캔. corpus 없으면 skip.

### Expanded query — virtual attributes (Plan 75 ✅)
`query` 셀렉터가 `text`, `bold`, `italic`, `fontsize`, `colSpan`, `rowSpan`, `heading` 가상 속성 지원.
연산자: `=`, `!=`, `~=` (contains), `>=`, `<=`. Child combinator: `parent > child`.
실제 XML attribute와 가상 attribute 모두 같은 `[attr op value]` 문법으로 접근.

### HashSet vs string[] for Korean keyword matching
Korean has no case distinction → `StringComparer.OrdinalIgnoreCase` 무의미.
키워드 매칭은 substring `.Contains()` 사용 → HashSet의 O(1) lookup 이점 없음.
`string[]` + `.Any(kw => text.Contains(kw))` 가 의미적으로 정확.

### Transport parity — CLI/Resident/MCP 동일 동작 (Plan 93 ✅)
`tables`, `markdown`, `objects`, `styles` view 모드가 CLI뿐 아니라 ResidentServer, McpServer에서도 동작.
에이전트 자동화 시 transport에 따라 결과가 달라지지 않음.

### Validate = ViewAsIssues 통합 (Plan 94 ✅)
`officecli validate`가 9-level 전부 수행: ZIP, package (mimetype STORED, rootfile, version.xml),
XML, IDRef, table, namespace, BinData 무결성, field pair, section count.
`view issues`와 동일한 검사 범위.

### Rootfile-aware loader (Plan 80 ✅)
`HwpxManifest.Parse(ZipArchive)`가 `META-INF/container.xml` → rootfile → OPF manifest 순으로 로딩.
`Contents/content.hpf` 직접 접근은 fallback으로만. `_doc.RootfilePath`에 선택 경로 저장.

### MD→HWPX frontmatter/fence 자동 스킵 (Plan 85 ✅)
`ImportMarkdown()`이 YAML frontmatter (`---...---`), 코드 펜스 (` ``` `), 이미지 (`![]()`),
수평선 (`---`) 자동 스킵. 리스트 (`- item`)는 일반 단락으로 fallback.

### Pattern-Match Editing (Python fallback, Plan 90.999 + 99.7)

officecli의 `set`/`find-replace`로 커버되지 않는 **복잡한 양식 편집**(KICE 시험지, 규정/운영지침 등)은
Python 패턴매칭 + lineseg strip 전략을 사용한다.

**핵심 원리**: lineseg strip → 패턴매칭 편집 → 리팩 (ZIP 재생성). 한컴이 열 때 레이아웃 자동 재계산.

**문서 분류** (5가지 유형):
| 유형 | 판별 기준 | 예시 |
|------|-----------|------|
| `exam` | equation 10+, rect 존재 | KICE 수능/모의고사 |
| `form` | table 3+, checkbox(□/■) 존재 | 신청서, 지원서, 이력서 |
| `regulation` | ○ 10+, 별첨/조항 참조, table 10+ | 운영지침, 내규, 시행세칙 |
| `report` | table 2이하, 긴 텍스트 20+ | 보고서, 논문 |
| `mixed` | 위 기준 미충족 | 사업계획서 등 |

**검증 완료 문서** (3종):
1. KICE 수학 양식 — 연도/과목/교시/수식/텍스트 전체 편집 OK
2. KU 창업동아리 참가신청서 — 17 테이블, 13 필드, 체크박스 파싱 OK
3. KU 창업동아리 운영지침 (HWP→HWPX) — 36 테이블, 57 체크박스, 6개 편집 OK

**Regex 인벤토리**: 25개 패턴 (R1-R25). 상세 → Plan 99.7.
주요 패턴: lineseg strip(R1), checkbox(R6), label detect(R7-R8), uniform space(R10),
checkbox hierarchy(R21), appendix ref(R22), digit-title concat(R23).

**Python 도구**: `hwpx_form_edit.py` (범용 CLI, 미구현), `hwpx_form_patterns.py` (패턴 함수).
기존 재사용: `pack.py` (strip/minify/repack), `hwpx_cli.py` (NS/text helpers).

---

## QA Verification

```bash
officecli validate doc.hwpx
officecli view doc.hwpx stats
officecli view doc.hwpx text
officecli view doc.hwpx html --browser
```

### PDF 변환 검증 (필수)
한컴이 없는 환경이나 시각 검증이 필요할 때 soffice로 PDF 변환:
```bash
soffice --headless --convert-to pdf --outdir /tmp doc.hwpx
```
PDF에서 반드시 확인할 항목:
- [ ] 표 셀이 정확한 위치에 채워졌는지 (cellAddr 매핑 오류 가장 흔함)
- [ ] 가이드 텍스트(※, 예시 등)가 완전히 제거되었는지
- [ ] 체크박스 □/■ 변환이 의도한 곳에만 적용되었는지
- [ ] 병합셀 안의 텍스트가 올바른 행에 있는지 (가이드 행 vs 내용 행)
- [ ] 총원, 학년별 인원 등 숫자가 전역 치환으로 오염되지 않았는지

### Checklist
- [ ] `validate` passes
- [ ] `view ... text` matches expected content
- [ ] **soffice PDF 변환 후 표 시각 검증** (셀 위치, 가이드 제거, 체크박스)
- [ ] HTML preview renders correctly
- [ ] 한컴에서 정상 열림

---

## Format Overview

| Format | Ext | Structure | Read | Write | Notes |
|--------|-----|-----------|------|-------|-------|
| HWPX | `.hwpx` | ZIP + XML (OWPML) | ✅ | ✅ | Korean gov standard, cross-platform |
| HWP | `.hwp` | OLE2 compound binary | ❌ | ❌ | 한컴에서 .hwpx로 변환 후 사용 |

---

## Legacy Python CLI (Fallback)

Use these only when officecli does not cover the requirement:

| Script | Role | Status |
|--------|------|--------|
| `python scripts/hwpx_cli.py text input.hwpx` | Text extraction fallback | Legacy |
| `python scripts/office/unpack.py input.hwpx work/` | Pretty-print XML | Legacy |
| `python scripts/office/pack.py work/ output.hwpx` | Repack with minify | Legacy |
| `python scripts/validate.py output.hwpx` | Structural validation | Legacy |
| `python scripts/page_guard.py --reference ref.hwpx --output out.hwpx` | Page count guard | Legacy |

> Most legacy operations are now covered by officecli: `view text`, `raw`, `validate`, `set find/replace`.

---

## Dependencies

| Tool | Why | Required? |
|------|-----|-----------|
| `officecli` (fork binary) | Primary HWPX CLI | **Required** |
| `dotnet` | Build officecli from source | Required for builds |
| `python3` | Legacy fallback scripts | Optional |
| `soffice` | PDF conversion | Optional |
