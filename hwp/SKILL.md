---
name: hwp
description: "HWP/HWPX create, read, edit, review. Triggers: 한글, .hwp, .hwpx, HWP, HWPX, Korean documents."
---

# HWPX Document Skill

Use this skill for any `.hwpx` task: create, read, edit, review, template-fill, or QA verification.
Triggers: `"한글"`, `".hwpx"`, `"HWP"`, `"HWPX"`, Korean documents, 한컴오피스, OWPML.
Primary tool: **officecli** (`build-local/officecli` or `~/.local/bin/officecli`).
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
| officecli (fork) | `700_projects/cli-jaw/build-local/officecli` | Primary — full HWPX support |

---

## Quick Decision

| Task | Command | Notes |
|------|---------|-------|
| Read text | `officecli view doc.hwpx text` | `text`, `annotated`, `outline`, `stats`, `html`, `styles`, `forms` |
| Add paragraph | `officecli add doc.hwpx /section --type paragraph --prop text="내용"` | First add replaces empty p[1] |
| Edit paragraph | `officecli set doc.hwpx /section/p[1] --prop bold=true --prop align=CENTER` | |
| Add table | `officecli add doc.hwpx /section --type table --prop rows=3 --prop cols=4` | |
| Edit cell | `officecli set doc.hwpx '/section/p[N]/tbl[1]/tr[1]/tc[1]' --prop text="값"` | |
| Add heading | `officecli add doc.hwpx /section --type paragraph --prop text="제목" --prop styleidref=2 --prop bold=true` | styleidref=2 = 개요 1 |
| Add image | `officecli add doc.hwpx /section --type picture --prop src=image.png` | |
| Add shape | `officecli add doc.hwpx /section --type rect --prop width=20000 --prop height=10000 --prop fillcolor=#4472C4` | `line`, `rect`, `ellipse`, `textbox`, `polygon`, `triangle`, `pentagon`, `arrow` |
| Add field | `officecli add doc.hwpx /section --type clickhere` | `clickhere`, `filepath`, `summary`, `date` |
| Add TOC | `officecli add doc.hwpx /section --type toc` | `--prop mode=field` for field-based |
| Add section | `officecli add doc.hwpx / --type section --prop orientation=LANDSCAPE` | Multi-section |
| Find/replace | `officecli set doc.hwpx / --prop find="old" --prop replace="new"` | Regex: `find=regex:\d+` |
| Remove | `officecli remove doc.hwpx /section/p[3]` | Also: `/toc`, `/watermark`, `/section[2]` |
| Set metadata | `officecli set doc.hwpx / --prop title="문서제목" --prop author="작성자"` | |
| HTML preview | `officecli view doc.hwpx html --browser` | A4 미리보기 |
| Validate | `officecli validate doc.hwpx` | ZIP/XML/IDRef 검증 |
| Raw XML | `officecli raw doc.hwpx Contents/section0.xml` | 디버깅용 |
| Form value | `officecli set doc.hwpx '/formfield[ID]' --prop value="홍길동"` | 누름틀 값 설정 |

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

**If you ever edit HWPX XML directly** (not via officecli), you MUST delete `<hp:linesegarray>` from
any paragraph whose text content changed. Stale cache causes:
- Text compressed into single line (characters overlap)
- Visible in Hancom only (officecli text view looks correct)

### charPr height is centi-points
`fontsize=16` (pt) → internally stored as `height=1600`. officecli handles conversion.

### Orientation values are counterintuitive
- `WIDELY` = 세로 (portrait) — default
- `NARROWLY` = 가로 (landscape)
- Page dimensions (width/height) do NOT change

### CLICK_HERE field type
- Must be `type="CLICK_HERE"` (with underscore), not `"CLICKHERE"`
- Hancom uses `"SUMMERY"` (not `"SUMMARY"`)

---

## QA Verification

```bash
officecli validate doc.hwpx
officecli view doc.hwpx stats
officecli view doc.hwpx text
officecli view doc.hwpx html --browser
```

### Checklist
- [ ] `validate` passes
- [ ] `view ... text` matches expected content
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
