---
name: doc-coauthoring
description: Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration, and verify the doc works for readers. Trigger when user mentions writing docs, creating proposals, drafting specs, or similar documentation tasks.
---

# Doc Co-Authoring Workflow

Three-stage workflow: Context Gathering → Refinement & Structure → Reader Testing.

Offer the workflow when user starts a writing task. If declined, work freeform.

## Stage 1: Context Gathering

Goal: Close the knowledge gap so you can guide effectively later.

### Initial Questions

Ask for meta-context:

1. Document type (technical spec, decision doc, proposal, etc.)
2. Primary audience
3. Desired impact on the reader
4. Template or format requirements
5. Other constraints

Accept shorthand answers or info dumps.

If a template or existing doc is provided, read it. For docs with images lacking alt-text, offer to generate alt-text — images are invisible to future AI readers.

### Context Dump

Encourage the user to share everything relevant:
- Project/problem background
- Related discussions or documents
- Why alternatives were rejected
- Organizational context, timeline, dependencies, stakeholder concerns

Offer to pull context via available integrations (Slack, Drive, etc.). If none available, suggest enabling connectors or pasting content directly.

### Clarifying Questions

After the initial dump, generate 5–10 numbered questions targeting gaps.

Let users answer in shorthand (e.g., "1: yes, 2: see #channel, 3: no").

Track what's learned vs. what's still unclear. Address gaps immediately.

**Exit condition:** Questions show understanding of edge cases and trade-offs without needing basics explained.

Transition: ask if there's more to add, or if it's time to draft.

## Stage 2: Refinement & Structure

Goal: Build the document section by section through brainstorm → curate → draft → refine.

Per-section process:
1. Clarifying questions about what to include
2. Brainstorm 5–20 options
3. User curates (keep/remove/combine)
4. Draft the section
5. Refine through surgical edits

### Establish Structure

If structure is clear: ask which section to start with. Suggest starting with the most uncertain section.

If structure is unclear: propose 3–5 sections based on doc type and adjust per feedback.

Create the scaffold (artifact or markdown file) with section headers and `[To be written]` placeholders.

### Per-Section Workflow

#### 1. Clarifying Questions
Ask 5–10 questions specific to the section's purpose.

#### 2. Brainstorming
Generate 5–20 numbered options. Surface forgotten context and unconsidered angles. Offer to brainstorm more.

#### 3. Curation
Ask which points to keep, remove, or combine. Accept numbered or freeform feedback — parse preferences and apply.

#### 4. Gap Check
Ask if anything important is missing.

#### 5. Drafting
Replace placeholder with drafted content using `str_replace`.

On the first section, instruct: "Tell me what to change instead of editing directly — this helps me learn your style for later sections."

#### 6. Iterative Refinement
- Use `str_replace` for edits — never reprint the whole doc
- If user edits directly, note their preferences for future sections
- After 3 iterations with no substantial changes, ask what can be removed
- Continue until user is satisfied

### Near Completion

At 80%+ sections done, re-read the full document checking for:
- Flow and consistency across sections
- Redundancy or contradictions
- Generic filler — every sentence should carry weight

Provide feedback, then ask if ready for Reader Testing.

## Stage 3: Reader Testing

Goal: Test the document with a context-free reader to catch blind spots.

### Step 1: Predict Reader Questions

Generate 5–10 questions readers would realistically ask when discovering this document.

### Step 2: Test

**With sub-agents:** For each question, invoke a sub-agent with only the document and the question (no conversation context). Summarize what it got right/wrong.

**Without sub-agents:** Instruct user to open a fresh conversation, paste the doc, and ask the generated questions. Have the reader report: answer, ambiguities, assumed knowledge.

### Step 3: Additional Checks

Check (via sub-agent or fresh conversation) for:
- Ambiguity or unclear phrasing
- Assumed reader knowledge
- Internal contradictions

### Step 4: Fix

If issues found, loop back to Stage 2 refinement for affected sections.

**Exit condition:** Reader consistently answers questions correctly with no new gaps.

## Final Review

When reader testing passes:

1. Recommend a personal read-through — user owns the document's quality
2. Suggest verifying facts, links, and technical details
3. Ask if it achieves the intended impact

Tips: link this conversation in an appendix, use appendices for depth, update as real reader feedback arrives.
