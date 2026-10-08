# Employee skill guidance and skill discovery

Canonical owner: `jaw-dev`. Extracted from the router so it stays under its line
budget; the rules are unchanged.

## 9. Employee Skill Guidance (DEV-SKILL-INJECT-01, DEFAULT)

Name `jaw-dev` and every relevant surface skill explicitly in the dispatch
brief for a governed employee. `jaw dispatch` has no skill-attachment flag;
the brief identifies the policy to read and does not automatically inject it.
Verify that the employee can resolve the named skill before relying on it.

- Prefer a resolvable installed skill name or path. When none resolves, include
  the relevant policy text in the brief rather than naming an unreadable skill.
- The external-evidence policy binds delegated agents too — restate it in the
  dispatch prompt.
- Surface-to-owner mappings are in `skill-ownership.md`.

## 10. Skill Discovery (DEV-SKILL-DISCOVERY-01, DEFAULT)

For a capability none of the loaded skills covers, check what the runtime's skill
registry already offers before improvising a procedure or adding tooling. Load only
the result you need — a speculative load costs the same tokens as a used one.

Two invariants hold regardless of where a discovered skill came from:

- **`jaw-dev` keeps authority.** A loaded third-party skill supplies domain procedure; it
  does not override §0.2 rule classes, the §3 verification gate, or §5 safety rules.
- **The family wins name conflicts.** When a discovered skill shares a rule area with
  a `jaw-dev-*` skill, the Skill Ownership Map names the canonical owner and the
  discovered skill is the stub.

If the runtime exposes no discovery surface, say so rather than inventing a skill
name — this rule governs how a discovered skill is treated, not whether discovery
exists.


---
