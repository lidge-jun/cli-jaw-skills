# Recall lookup scope (`DEV-RECALL-01`)

Canonical owner: `jaw-dev`. Extracted from the router so it stays under its line
budget; the rule is unchanged.

## Recall lookup scope (DEV-RECALL-01, MUST)

When a prior term, file, or decision is unfamiliar — or context was lost to a
compaction — search the durable record **before** asking the user:

| Trigger | Route |
|---|---|
| A prior term, file, or decision is unfamiliar | `cli-jaw chat search <query>` |
| Context was lost and you need the memory store | `cli-jaw memory search <query> [--chat]` |
| Both miss | Ask the user, and state exactly what you searched for |

Reporting the search terms on a miss is the part that matters: it lets the user
correct the vocabulary instead of re-explaining something already on disk under a
name you did not try.

Also search the owning implementation unit (`devlog/_plan/YYMMDD_slug/`), the
worklog, and the commit that introduced the term. A reconstructed decision
presented as a recalled one is a FAMILY-PROOF-01 violation.
