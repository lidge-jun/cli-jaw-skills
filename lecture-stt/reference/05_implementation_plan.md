# 05. 구현 계획 — `lecture-stt` 스킬

## 목표

cli-jaw 스킬 `lecture-stt`로 **강의 전사 + 노트 생성** 도구를 만든다.
- 메인 엔진: Gemini 3.1 Flash-Lite (멀티모달 — 오디오+PDF+프롬프트)
- 폴백: mlx-whisper (로컬, 오프라인)
- 선택: OpenAI transcribe-diarize (화자분리 필요시)

## 핵심 컨셉: 제목 기반 프롬프트 자동 생성

사용자가 제공하는 것은 **최소 2가지**:
1. 오디오 파일 (필수)
2. 제목 or 과목명 (필수) — 예: "거시경제학", "데이터구조", "헌법 강의"

스킬이 제목으로부터 **도메인, 핵심 용어, 출력 포맷**을 자동 유추한다.

```
사용자 입력: "거시경제학"
     ↓ 자동 유추
컨텍스트: 거시경제학(Macroeconomics) 대학 강의
핵심 용어: GDP, multiplier, MPC, fiscal policy, IS-LM, ...
출력 형식: 수식 KaTeX, 문장별 줄바꿈, 영어 전문용어 유지
```

### PDF가 있으면 → 함께 제출 (최고 품질)
### PDF가 없으면 → 프롬프트만으로도 충분히 고품질

## 실측 근거 (2026-03-04 벤치마크)

| 모드 | 속도 (44분) | 크기 | 품질 | KaTeX | 커버리지 |
|------|-----------|------|------|-------|---------|
| PDF + 상세 + Non-essential 마킹 | **32s** | 18KB | 🏆 최고 | ✅ | 100% + 비핵심 요약 |
| PDF + 상세 + 보강설명 | 20.4s | 13KB | 최고 | ✅ | 100% |
| 오디오 + 상세 프롬프트 (PDF 없음) | 11.6s | 1.2KB | 좋음 | ✅ | 75% (FOCUS 누락) |
| 필러 verbatim 마킹 | 161s | 297KB | ❌ | 0 | ❌ 루프 (안티패턴) |
| 오디오만 (프롬프트 없음) | 181s | 283KB | ❌ | 0 | ❌ 환각 + 루프 |

## 스킬 구조

```
skills/lecture-stt/
├── SKILL.md                # 스킬 가이드 (에이전트가 읽는 문서)
├── scripts/
│   └── transcribe.py       # 메인 CLI 스크립트
└── references/
    ├── models.md            # 모델별 상세 스펙 + 가격
    ├── prompt_patterns.md   # 도메인별 프롬프트 템플릿
    └── benchmarks.md        # 실측 벤치마크 데이터
```

## CLI 인터페이스 설계

### 기본 사용 (제목만으로 시작)
```bash
# 최소 입력 — 제목 + 오디오
lecture-stt "거시경제학" lecture.m4a

# PDF 슬라이드 함께 제출 (최고 품질)
lecture-stt "거시경제학" lecture.m4a --pdf slides.pdf

# 출력 파일 지정
lecture-stt "데이터구조" algo_lecture.mp3 -o notes.md

# 사용자 용어 추가 (자동 유추 + 수동 보강)
lecture-stt "헌법" constitutional.m4a --terms "위헌법률심판,헌법소원,기본권"
```

### 고급 사용
```bash
# 로컬 모드 (오프라인)
lecture-stt "물리학" physics.m4a --local

# 날것 전사 (filler 포함)
lecture-stt "미팅" meeting.m4a --mode raw

# 화자분리 (OpenAI)
lecture-stt "세미나" seminar.m4a --diarize

# 보강 설명 포함
lecture-stt "거시경제학" lecture.m4a --pdf slides.pdf --supplement
```

### 주요 옵션

| 옵션 | 기본값 | 설명 |
|------|-------|------|
| 첫번째 인자 | (필수) | 제목/과목명 — 프롬프트 자동 생성에 사용 |
| 두번째 인자 | (필수) | 오디오 파일 경로 |
| `--pdf` | 없음 | PDF 슬라이드 경로 (있으면 멀티모달) |
| `--terms` | 자동 유추 | 추가 용어 힌트 (쉼표 구분) |
| `--mode` | `lecture` | `lecture` / `raw` |
| `--supplement` | **true** | PDF에 있으나 설명 안 한 내용 *이탤릭* 보강 |
| `--model` | `gemini-3.1-flash-lite` | 사용 모델 |
| `--local` | false | mlx-whisper 사용 |
| `--language` | auto | 언어 (auto: 오디오에서 감지) |
| `-o` / `--output` | `{제목}_notes.md` | 출력 파일 경로 |
| `--diarize` | false | 화자분리 (OpenAI만) |

## 모듈 설계

### transcribe.py (~400줄)
```
main()
├── parse_args()
├── detect_engine()            # API 키 여부로 엔진 자동 선택
├── infer_domain(title)        # 제목 → 도메인/용어/포맷 유추
├── build_prompt(domain, terms, mode, has_pdf, supplement)
│   ├── mode=lecture  → 슬라이드 구조 + KaTeX + blockquote
│   └── mode=raw      → 날것 전사
├── load_inputs(audio, pdf?)   # base64 인코딩
├── transcribe_gemini()        # Gemini API 호출 (PDF 있으면 멀티모달)
├── transcribe_whisper()       # mlx-whisper 로컬 폴백
├── transcribe_openai()        # OpenAI (화자분리용)
└── save_output()              # md 파일 저장 + 메타데이터 헤더
```

### 핵심: infer_domain(title) — 제목에서 프롬프트 자동 유추

```python
DOMAIN_MAP = {
    "경제": {
        "context": "경제학 대학 강의",
        "terms": ["GDP", "인플레이션", "통화정책", "재정정책", "IS-LM", "multiplier"],
        "katex": True,
    },
    "거시경제": {
        "context": "거시경제학(Macroeconomics) 대학 강의",
        "terms": ["GDP", "multiplier", "MPC", "fiscal policy", "IS-LM",
                  "aggregate demand", "equilibrium output", "consumption function"],
        "katex": True,
    },
    "물리": {
        "context": "물리학 대학 강의",
        "terms": ["뉴턴 법칙", "에너지 보존", "운동량", "전자기학"],
        "katex": True,
    },
    "법학|헌법": {
        "context": "법학/헌법학 대학 강의",
        "terms": ["위헌법률심판", "헌법소원", "기본권", "법률유보"],
        "katex": False,
    },
    "프로그래밍|코딩|CS": {
        "context": "컴퓨터과학/프로그래밍 강의",
        "terms": ["알고리즘", "시간복잡도", "Big-O", "자료구조"],
        "katex": True,  # Big-O notation 등
    },
}

def infer_domain(title):
    for pattern, config in DOMAIN_MAP.items():
        if re.search(pattern, title, re.IGNORECASE):
            return config
    # 매칭 없으면 Gemini에게 유추 요청 (1회 사전 호출)
    return ask_gemini_for_domain(title)
```

### 엔진 선택 로직
```
GEMINI_API_KEY 있음?
├─ Yes → Gemini 3.1 Flash-Lite
│   └─ 실패시 → 2.5 Flash-Lite 폴백
├─ No, OPENAI_API_KEY 있음?
│   └─ Yes → OpenAI gpt-4o-mini-transcribe
└─ No → mlx-whisper 로컬
```

## 프롬프트 조립 (build_prompt)

### mode=lecture + pdf + supplement (기본 모드 — 최고 품질)
```
You are a lecture note assistant. You are given a PDF slide deck
and an audio recording of a {context}.

## Task
1. Transcribe ALL lecture content as detailed as possible — capture
   every explanation, example, and nuance the professor gives.
2. Follow the PDF slide structure (one section per slide).
3. Be THOROUGH — include all details, side stories, real-world examples.
4. For each slide, if there was non-essential speech (off-topic remarks,
   admin announcements, repetitive filler), write ONE summary line:
   *(Non-essential: [brief description])*
   - Maximum ONE line per slide section
   - Only if there actually was non-essential content

## Supplementary Notes
- If the professor did NOT explain a PDF concept, add *[Supplementary: ...]*

## Output Format
- `---` dividers + slide title per slide
- Professor's examples in `> ` blockquote — be detailed
- Supplementary in *italics*
- Non-essential summary in *(italics with parentheses)* at end of slide
- Math in KaTeX
- Sentence-level line breaks
- English for technical terms
- FOCUS boxes, case studies, warnings: include ALL

## Key Terms
{자동 유추 terms + 사용자 추가 terms}
```

### mode=lecture (pdf 없음)
```
You are a lecture note assistant. This audio is a {context}.

## Task
1. Transcribe ALL lecture content as structured notes.
2. Remove filler but keep ALL explanations, examples, analogies.
3. Organize into sections with `## 제목`.

## Output Format
- Math in KaTeX
- Sentence-level line breaks
- English for technical terms

## Key Terms
{terms}
```

### mode=raw
```
Transcribe this audio verbatim. Include all speech as-is.
Sentence-level line breaks. No formatting.
```

## 청크 분할 전략

Gemini 오디오 제한: 8.4시간 (실질 1M 토큰)
실측: 44분 ≈ 66K input tokens → 1M 토큰 ≈ ~11시간

| 오디오 길이 | 전략 |
|-----------|------|
| < 2시간 | 단일 요청 (충분) |
| 2~8시간 | 2~4 청크, overlap 10초 |
| 8시간+ | 30분 청크, 순차 처리 |

```python
def chunk_audio(path, chunk_min=30, overlap_sec=10):
    duration = get_duration(path)
    if duration < 2 * 3600:
        return [path]
    chunks = []
    for start in range(0, int(duration), chunk_min * 60 - overlap_sec):
        chunk_path = f"/tmp/chunk_{start}.mp3"
        ffmpeg_split(path, start, chunk_min * 60, chunk_path)
        chunks.append(chunk_path)
    return chunks
```

## 출력 파일 형식

```markdown
# {제목} — Lecture Notes

- Model: Gemini 3.1 Flash-Lite Preview
- Time: {elapsed}s
- Tokens: {in} → {out}
- Cost: ~${cost}
- Source: {audio_filename} {+ pdf_filename}
- Mode: {lecture|raw}
- Legend: > = professor examples, *italic* = supplementary, *(Non-essential: ...)* = omitted speech

---

{전사 내용}
```

## 의존성

### 필수
```
pip install google-genai   # Gemini API
```

### 선택
```
pip install mlx-whisper    # 로컬 Whisper (Apple Silicon)
pip install openai         # OpenAI 화자분리
brew install ffmpeg        # 오디오 변환/분할 (청크용)
```

## 마일스톤

- [ ] Phase 1: 핵심 — Gemini STT + 제목 기반 프롬프트 자동 생성 + PDF 멀티모달
- [ ] Phase 2: mlx-whisper 폴백 + 엔진 자동 선택
- [ ] Phase 3: mode 분기 (lecture / raw)
- [ ] Phase 4: 긴 오디오 청크 분할
- [ ] Phase 5: OpenAI 화자분리 통합
- [ ] Phase 6: cli-jaw skill 패키징 (`lecture-stt`) + SKILL.md 작성

## API 키 설정

```bash
# Gemini (Google AI Studio) — 메인
export GEMINI_API_KEY="AIza..."

# 또는 Vertex AI (서비스 계정)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# OpenAI (화자분리용, 선택)
export OPENAI_API_KEY="sk-..."
```

## 사용 시나리오

### 시나리오 1: 학생이 수업 끝나고 바로 노트 생성
```bash
lecture-stt "거시경제학" recording.m4a --pdf chapter3.pdf --supplement -o ch3_notes.md
# → 20초 만에 KaTeX 수식 포함 완벽한 강의 노트
```

### 시나리오 2: 회의 전사 (날것)
```bash
lecture-stt "팀미팅" meeting.m4a --mode raw -o meeting_raw.md
# → filler 포함 전체 전사
```

### 시나리오 3: 오프라인 (비행기 안)
```bash
lecture-stt "물리학" physics.m4a --local
# → mlx-whisper로 로컬 전사 (무료, 4분/44분강의)
```

## 참고 자료

- [Gemini Audio 문서](https://ai.google.dev/gemini-api/docs/audio)
- [mlx-whisper GitHub](https://github.com/ml-explore/mlx-examples)
- [OpenAI Transcription API](https://platform.openai.com/docs/guides/speech-to-text)
- cli-jaw 기존 스킬: `skills_ref/transcribe/` (OpenAI 전용)
- 벤치마크 데이터: `03_model_comparison.md`, `04_contextual_prompt.md`
- 최종 테스트 결과: `MACROECON1_filler_summary.md` (기본 모드 — 상세 + 비핵심 요약)
