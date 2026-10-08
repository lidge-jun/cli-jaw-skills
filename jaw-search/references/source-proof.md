# Source proof for search

Use this with `jaw-search/SKILL.md`. Its four-tier ladder and evidence statuses
remain the execution contract. The shared browser capability policy is in
`jaw-dev/references/browser-routing.md`; this reference specifies search decisions.

## SEARCH-DEPTH-01 — Choose the needed depth

Classify the question before selecting a lane. This is separate from choosing
local file search versus external search.

| Question | First proof target |
| --- | --- |
| Current fact (version, price, date, status) | Discover, then open a dated primary source; state the exact date or its absence. |
| Official documentation fact | Prefer the official documentation for the relevant version and open the passage. |
| Implementation or source fact | Read the relevant code, repository, or original artifact; a summary is a lead. |
| Comprehensive or contested research | Use `deep-research.md` for the scope, waves, ledger, and stop rule. |

A current lookup alone does not enter the deep-research protocol. A deep-research
request does not make a heavier provider's summary sufficient evidence.

## SEARCH-PROOF-01 — Confirm the requested claim

Read the claim in the opened page, original PDF, official record, or source. Check
the URL, publisher or source identity, relevant publication/update date (or say
it is absent), and whether the source actually supports the requested claim.
Record corroboration separately. An `ok` envelope, matching title, RSS feed,
search snippet, or navigation shell proves only that a reader reached something.
If the claim is missing, try an appropriate reader or rendered view; otherwise
mark that claim `browse-needed`, `partial`, or `insufficient` under the SKILL.md
status rules. Never promote agreement among snippets to opened-source proof.

## SEARCH-BROWSE-VERIFY-01 — Verify the read after acting

For a known candidate URL, inspect the response, act through
`cli-jaw browser fetch <url> --json` or an available browser view, then inspect
the resulting content again for the exact claim. For a rendered or interactive
page, re-inspect after navigation or control actions. A tool success or loaded
title does not establish the content, account, or date.

Distinguish a CDP connection failure from an HTTP error, authentication gate,
empty page, truncated content, or missing claim. For a confirmed connection
failure, check `cli-jaw browser status`, start one task-owned session with
`cli-jaw browser start --agent` if needed, then retry status/fetch once. For
HTTP/auth/content failures, change the source or reader or report the blocked
claim; restarting the browser does not repair those failures. Preserve the
signed-in profile, verify account access on any reader switch, and never assume
cookies transfer. Before repeating an action that may have changed state, inspect
whether it already happened. Follow the shared browser-routing policy for
task-owned tabs and permissions.

## SEARCH-ATTACH-01 — Give delegated lanes the policy

Every delegated research brief names `jaw-search` as its policy and asks the
worker to run `cli-jaw skill read jaw-search` before research. `cli-jaw dispatch`
has no skill-attachment flag, so mentioning the skill in the brief does not
claim automatic injection. For a multiline brief, use
`cli-jaw dispatch --agent "<employee>" --task-file <brief>` when a suitable
employee is available and delegation is authorized.

State the lane question, source boundary, output shape, and stop condition.
Require each returned claim to include title, publisher, URL, source date (or
`date absent`), and `opened` or `candidate` status, plus contradictions and gaps.
An unopenable source returns as `candidate — unverified snippet`; the parent
must open it before using it as load-bearing proof. Merge lanes into the one
evidence matrix described in SKILL.md.
