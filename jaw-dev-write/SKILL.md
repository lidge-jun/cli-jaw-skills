---
name: jaw-dev-write
description: "MUST USE when revising Korean prose the agent is about to send or has already written — 윤문, removing translationese and AI idioms, fixing register/tone breaks, varying rhythm, replacing abstract endings, while preserving meaning exactly. Applies to chat answers, docs, READMEs, release notes, commit bodies, issue/PR text, and UI copy. Generation for a specific platform/audience belongs to k-writing; this skill revises. Triggers: 윤문, 다듬어, 다듬어줘, 자연스럽게, 매끄럽게, 교정, 고쳐줘, AI투, 번역투, 어색해, Korean polish, proofread Korean, dev-write."
metadata:
  short-description: "Korean prose revision: AI-tell removal, register consistency, meaning-exact editing."
  keywords: "윤문, 번역투, AI투, 교정, register, tone, Korean, polish, revision, proofread"
  last-verified: "2026-08-25"
---

# Dev Write — 한국어 윤문

이 스킬은 **이미 있는 한국어 텍스트를 고치는** 일을 맡는다. 사용자가 명시적으로
윤문을 요청했을 때뿐 아니라, 에이전트가 한국어로 답을 내보내기 직전에도 적용한다.
뜻은 그대로 두고, 기계가 쓴 티만 걷어낸다.

> **경계**: 특정 플랫폼·독자·포맷을 겨냥한 **새 글 생성**은 `k-writing` 이 소유한다
> (홍보 쓰레드, 카드뉴스, 링크드인, 블로그). `k-writing` 이 초안을 만들면 이 스킬이
> 그 초안을 고친다. 순서는 생성 → 윤문이고, 반대가 아니다.

## 대원칙

1. **뜻은 얼린다.** 사실, 주장, 숫자, 고유명사, 인용, 인과 관계는 글자 그대로 보존한다.
   모호한 부분을 지어내서 해소하지 않는다.
2. **잡힌 구간만 고친다.** 패턴이 검출되지 않은 문장은 건드리지 않는다. 윤문은 재작성이 아니다.
3. **과윤문 금지.** 원문의 30%를 넘게 바꾸고 있다면 멈추고 다시 본다. 그건 재작성이다.
4. **문체도 뜻이다.** 문어체는 문어체로, 구어체는 구어체로, 존댓말은 존댓말로 남는다.
   문체 안에서 깨진 곳을 고치는 것이지 다른 문체로 옮기는 게 아니다.

## 윤문 프로토콜 (순서대로, 고친 뒤 그 패스를 다시 돌린다)

### 패스 1 — 문체·어조 일관성 (S1)

첫 문장과 마지막 문장의 문체와 높임 수준이 같아야 한다. 반말 글 안에 "~합니다" 섬이
없어야 하고, 존댓말 글 안에 "~해/~야"가 없어야 하며, 편한 글에 "~하겠습니다" 격식
스파이크가 튀지 않아야 한다.

### 패스 2 — 번역투 + AI 관용구 (S1)

[references/ai-tell-taxonomy.md](references/ai-tell-taxonomy.md) 의 CAT-1(번역투),
CAT-3(AI 관용구), CAT-5(톤 파괴)로 훑는다. S1은 즉시 고친다. 표에 문체별 대안이 있다.

### 패스 3 — 기계적 구조 (S2)

"첫째/둘째/셋째" 나열, "A, B, 그리고 C" 병렬, 같은 문장 틀 연속(CAT-2). 문두 접속사
쌓기 — 또한/한편/더불어/아울러/이에 따라(CAT-4), 기본 처방은 삭제. 아는 걸 다시 말하는
과잉 설명과 "다시 말해"/"즉" 반복(CAT-7).

### 패스 4 — 리듬과 문말 (S2)

문장 길이가 균일하거나 같은 어미가 세 번 연속이면 짧은 문장으로 끊고 어미를 바꾼다(CAT-8).
기대된다/주목된다/~할 것으로 보인다 같은 추상적 도피 마무리(CAT-6)는 구체적인 사실이나
결과로 끝내거나, 그냥 끝낸다.

## 판정

네 패스가 전부 깨끗하면 출력한다. 하나라도 걸리면 그 구간을 고치고 그 패스를 다시 돌린다.
사용자가 윤문을 명시적으로 요청했으면 바꾼 곳을 짧게 알린다. 자기 출력을 다듬는 경우에는
조용히 적용한다.

## 개발 산출물에 적용할 때

커밋 본문, 이슈/PR 설명, 릴리스 노트, README, 에러 메시지, UI 문구가 전부 대상이다.
다만 코드 식별자, 로그 문자열, 테스트 픽스처, 영어 원문은 건드리지 않는다. 코드 블록
안쪽도 마찬가지다. 한국어 산문만 고친다.

기술 문서에서는 정확성이 매끄러움을 이긴다. 용어를 부드럽게 만들려다 의미가 흐려지면
원래 용어를 남긴다.

## 범위 밖

한국어가 아닌 텍스트. 혼용 문서에서는 한국어 산문만 고치고 코드와 영어는 그대로 둔다.
새 글을 처음부터 쓰는 일은 `k-writing` 또는 해당 표면을 소유한 스킬의 몫이다.
