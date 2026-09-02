# Sub-agent skill injection and skill discovery

Canonical owner: `jaw-dev`. Extracted from the router so it stays under its line
budget; the rules are unchanged.

## 9. Sub-Agent Skill Injection (DEV-SKILL-INJECT-01, DEFAULT)

Name `jaw-dev` and every relevant surface skill **explicitly** in the dispatch packet
for any governed sub-agent. A sub-agent gets its own skill context; it does not
inherit yours, and nothing infers a skill you left out. An omitted router produces
an ungoverned lane, not a lighter one.

- Prefer whatever resolvable skill reference the runtime supports — a path, a link,
  a registry id. When none resolves, inline the router body into the packet rather
  than naming a skill the child cannot load. A name the child cannot resolve is
  worse than no name: it reads as governed and behaves as ungoverned.
- The external-evidence policy binds delegated agents too — restate it in the
  dispatch prompt.
- Surface-to-owner mappings are canonical in the **Skill Ownership Map** above.

## 10. Skill Discovery (DEV-SKILL-DISCOVERY-01, DEFAULT)

For a capability none of the loaded skills covers, check what the runtime's skill
registry already offers before improvising a procedure or adding tooling. Load only
the result you need — a speculative load costs the same tokens as a used one.

Two invariants hold regardless of where a discovered skill came from:

- **`jaw-dev` keeps authority.** A loaded third-party skill supplies domain procedure; it
  does not override §0.2 rule classes, the §3 verification gate, or §5 safety rules.
- **The family wins name conflicts.** When a discovered skill shares a rule area with
  a `dev-*` skill, the Skill Ownership Map names the canonical owner and the
  discovered skill is the stub.

If the runtime exposes no discovery surface, say so rather than inventing a skill
name — this rule governs how a discovered skill is treated, not whether discovery
exists.


---
