# Check phase

Read the actual changed files and saved artifacts, run the class-appropriate targeted checks,
and sync the repository's source-of-truth documents selected in P (SOT-SYNC-01). A TypeScript
project may need `npx tsc --noEmit`; use its real build/test commands and observe the changed
target. For hosted CI results and tested commit identity use
[DEV-CI-EVIDENCE-01](../../jaw-dev/references/hosted-ci-evidence.md). A passing unrelated gate
does not establish this work-phase.

## Rendered and binary output (C-RENDER-GROUNDING-01)

For a page, UI, SVG, game, chart, animation, generated document, or other artifact whose
correctness appears only when run or rendered: run it in its natural environment, inspect the
rendered output or first interaction, fix observed defects, then rerun until one clean
observation. Use a real jaw/browser/CLI/API invocation as applicable and read back the
screenshot, console, document pages or output. Static type/lint checks and an unread screenshot
are insufficient. For paged documents inspect representative pages, typography, glyphs and
clipping. Record the invocation, observed result and artifact at the repository-approved
evidence location; C4 keeps durable evidence there. Do not place private screenshots or audit
records in a public checkout.

## Conditional paths (C-ACTIVATION-GROUNDING-01)

For a new or changed error handler, fallback, retry, cache, guard, feature gate, mode switch,
migration handler or threshold branch, trigger the condition for real with a test, fixture or
controlled fault. Observe the intended effect through an assertion, log, counter or trace. Fix
and retrigger if the observation contradicts the plan. A green happy-path suite is insufficient
when it never exercises the condition; byte-identical output may signal a dead path. P names the
activation scenario and A checks reachability.

## Fresh-reader check

For a user-facing report or document, follow the canonical [reader
documents](../../jaw-dev/references/reader-documents.md) (C-READER-01). Record what a fresh
reader misunderstood, what was fixed, and the verified rendered result. Keep raw verification
evidence separate from the reader-facing summary.

Long external gates can use the verified `jaw bgtask add --cmd '<json argv>' --prompt
'<completion text>'` wake path; check that the task is registered before yielding. Local checks
normally run to completion. C→D requires a real nonempty `checkOutput`, with zero `exitCode`
when supplied; cite the observed command and output in `did`.
