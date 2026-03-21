---
name: dev-debugging
description: "Systematic debugging methodology for all orchestrated sub-agents. 4-phase root cause analysis: investigate → analyze → hypothesize → implement. Injected when encountering errors or during debugging phase."
---

# Dev-Debugging — Systematic Root Cause Analysis

This skill is the **thinking process** for fixing bugs. It enforces a structured
4-phase methodology that MUST be followed for every technical issue — test failures,
runtime errors, build failures, performance regressions, integration bugs.

**Boundary**: This skill teaches HOW TO THINK about bugs. For test harness,
reproduction frameworks, and verification tooling, see `dev-testing`. For
domain-specific context (API errors, hydration issues, query performance),
consult `dev-backend` or `dev-frontend`.

```
dev-debugging = root cause methodology (the thinking)
dev-testing   = test harness for reproducing/verifying (the tooling)
dev §2        = summary pointer to this skill (the overview)
```

---

## The Iron Law

```
┌─────────────────────────────────────────────────────┐
│  NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.   │
│  If you haven't completed Phase 1, you CANNOT       │
│  propose fixes. No exceptions.                      │
└─────────────────────────────────────────────────────┘
```

---

## When to Activate

- Test failures, runtime errors, build failures, performance regressions
- Integration issues (API, database, third-party), CI pipeline failures
- **Especially**: when under time pressure or when "just one quick fix" seems obvious

---

## The Four Phases

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read the full error** — stack trace, line numbers, error code, surrounding
   context. Do not skim. The answer is often in the error message itself.

2. **Reproduce consistently** — exact steps to trigger the bug. If intermittent,
   document frequency, conditions, and environment state. A bug you cannot
   reproduce is a bug you cannot verify as fixed.

3. **Check recent changes** — run `git log --oneline -10` and `git diff`. Check
   new dependencies, config changes, environment variables. Bugs correlate with
   recent changes ~80% of the time.

4. **Trace data flow** — where does the bad value originate? Trace backward from
   the failure point through the call stack until you find the source. Fix at the
   source, not the symptom.

5. **Instrument component boundaries** — for multi-layer systems (API → service →
   database, CI → build → deploy), log input/output at each boundary BEFORE
   proposing fixes.

```
For EACH component boundary:
  - Log what data enters the component
  - Log what data exits the component
  - Verify environment/config propagation
Run once → analyze evidence → identify failing layer → investigate THAT layer
```

Do NOT proceed to Phase 2 until all 5 steps above are done.

### Phase 2: Pattern Analysis

1. **Find working examples** — similar working code in the same codebase. If it
   worked before, use `git bisect` to find the breaking commit (see
   `references/tool-guides.md`).

2. **Compare systematically** — list EVERY difference between working and broken
   code. No matter how small. Don't assume "that can't matter."

3. **Read reference docs completely** — official documentation for the library,
   API, or framework involved. Don't skim — read the full relevant section.

4. **Check known issues** — GitHub Issues, changelogs, migration guides. Someone
   may have hit the same bug. Search with the exact error message.

### Phase 3: Hypothesis and Testing

1. **State hypothesis explicitly** — "X is the root cause because evidence Y
   shows Z." Write it down. If you can't articulate it clearly, you don't
   understand it yet.

2. **Design a test to disprove** — falsification is stronger than confirmation.
   What would you expect to see if your hypothesis is WRONG?

3. **Test one variable** — smallest possible change, one variable at a time.
   Never fix multiple things at once.

4. **If it didn't work** → form a NEW hypothesis. Do NOT pile fixes on top.
   Revert the failed change and start from clean state.

5. **Admit ignorance** — "I don't understand X" is a valid finding. Research
   further rather than guessing. Say it out loud.

### Phase 4: Implementation

1. **Write a failing test first** — the test reproduces the bug. It MUST fail
   before the fix. Use `dev-testing` for TDD patterns and test harness setup.

2. **Make the minimal fix** — address the root cause, not symptoms. One logical
   change only.

3. **Verify**: the test passes, no regressions (run the full test suite:
   `npm test` / `pytest` / equivalent).

4. **Check for similar patterns** — does the same bug class exist elsewhere in
   the codebase? Search for it. Fix all instances, not just the one you found.

5. **Document** — commit message explains root cause AND fix. Not "fixed bug"
   but "fix: race condition in session middleware caused by missing await on
   Redis write."

---

## Red Flags — STOP and Return to Phase 1

If you catch yourself doing or thinking any of these, STOP immediately.
You have skipped root cause investigation.

| 🚩 Red Flag | Why It's Wrong |
|-------------|----------------|
| "Quick fix for now, investigate later" | First fix sets the pattern. Tech debt compounds. You won't investigate later. |
| "Just try changing X and see" | Guessing guarantees rework. You'll be back here within the hour. |
| "Add multiple changes, run tests" | Can't isolate cause if multiple variables changed. Revert, change ONE thing. |
| "It's probably X, let me fix that" | "Probably" without evidence = Phase 1 not done. Go back and trace it. |
| "I don't fully understand but this might work" | Seeing symptoms ≠ understanding root cause. Your "fix" hides the real bug. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = question the architecture, not symptoms. See escalation below. |
| "It works on my machine" | Reproduce in the SAME environment as the failure. Local success proves nothing. |
| "Let me add a try/catch around it" | Suppressing errors is not fixing them. Find WHY it throws. |

**The 3-Strike Rule**: If 3 consecutive fix attempts fail, STOP completely.
Each fix revealing a new problem in a different place is a sign of
**architectural issues**, not simple bugs. Discuss with the user before
attempting more fixes.

---

## Anti-Slop Debugging

Slop debugging is spray-and-pray: guess, patch, pray, repeat. Every row below
is a concrete behavior to catch and correct.

| ❌ Banned Pattern | ✅ Required Pattern |
|-------------------|---------------------|
| Proposing fixes before investigation | Complete Phase 1 checklist first |
| "Might be X" without evidence | "Evidence shows X because [log/trace/diff]" |
| Multiple simultaneous changes | One change at a time, revert between attempts |
| Ignoring error messages or skimming stack traces | Read every line of stack trace, note line numbers |
| Silent `catch` blocks that suppress errors | Log with context (`[module] error.message`), re-throw or handle |
| Deleting or modifying failing tests to pass | Fix the code, not the test. A failing test is evidence. |
| Claiming "fixed" without running verification | Run full test suite, show green output, verify the original symptom |
| Copy-pasting a Stack Overflow fix without understanding | Understand WHY the fix works, then adapt to your codebase |
| Wrapping `try/catch` around the crash site | Fix at the source — trace upstream to where the bad data originates |
| Guessing at types, nulls, or undefined values | Add diagnostic logging, inspect actual runtime values |
| "It works now" after changing something unrelated | Correlation ≠ causation. Revert the change and test again. |

---

## Concrete Debugging Scenarios

### Scenario A: API Returns 500

```
Phase 1: Read server logs → find stack trace → identify failing line and function
Phase 1: Reproduce with curl/httpie: exact endpoint, method, headers, body
         $ curl -X POST http://localhost:3000/api/users \
           -H "Content-Type: application/json" \
           -d '{"email": "test@example.com"}'
Phase 1: git log --oneline -5 on the affected route file
Phase 1: Instrument boundaries:
         - Controller: log req.body on entry
         - Service: log input params + DB query params
         - Repository: log query + result
         → Run once → "Service receives userId=undefined because
            controller destructures { userId } from empty body"

Phase 2: Find a working POST endpoint → compare middleware chain
         Working endpoint validates body with zod schema first.
         Broken endpoint skips validation and destructures directly.

Phase 3: "Missing input validation causes TypeError on undefined.
          Controller destructures { userId } but client sends {}."
         Test: send {} body → expect 400 (validation error), not 500.

Phase 4: Write test:
           it('returns 400 when required fields missing', async () => {
             const res = await request(app).post('/api/users').send({});
             expect(res.status).toBe(400);
             expect(res.body.error).toMatch(/userId.*required/);
           });
         Add zod validation → test passes → check other routes for same gap.
```

### Scenario B: React Hydration Mismatch

```
Phase 1: Read browser console → "Text content does not match server-rendered HTML"
Phase 1: Identify component: <ProfileHeader /> renders user's local time
Phase 1: Check: does the component use Date.now(), new Date(), or window.*?
         → Yes: new Date().toLocaleDateString() in server component

Phase 2: Find a similar component that renders dates without hydration errors
         → <PostTimestamp /> uses 'use client' + useEffect for client-only dates
         Difference: ProfileHeader renders date on server; PostTimestamp defers.

Phase 3: "Server renders at build time (UTC), client renders with user timezone.
          Date formatting differs between UTC and Asia/Seoul → hydration mismatch."
         Prediction: forcing UTC on both sides eliminates mismatch → confirmed.

Phase 4: Move date formatting to a client component with 'use client' directive:
           'use client';
           export function LocalDate({ iso }: { iso: string }) {
             const [display, setDisplay] = useState('');
             useEffect(() => {
               setDisplay(new Date(iso).toLocaleDateString());
             }, [iso]);
             return <time dateTime={iso}>{display}</time>;
           }
         Hydration warning gone → no regressions in other date components.
```

### Scenario C: N+1 Query Performance

```
Phase 1: Enable query logging (Prisma: DEBUG=prisma:query, Django: LOGGING)
         Load page with 50 users → observe 51 queries in log (1 + 50)
Phase 1: Trace: User.findAll() returns 50 users, then for each user,
         user.getPosts() fires a separate SELECT. Classic N+1.

Phase 2: Find a similar list endpoint that uses eager loading
         → /api/teams uses { include: { members: true } } and runs 2 queries.
         Difference: /api/users omits the include clause.

Phase 3: "User.findAll() lazy-loads posts per user. 50 users = 50 extra
          queries. Adding include/joinedload reduces to 2 queries."
         Prediction: adding { include: { posts: true } } → query count ≤ 3.

Phase 4: Write performance test:
           it('loads users with posts in ≤5 queries', async () => {
             const queryLog = captureQueries();
             await getUsers({ limit: 50 });
             expect(queryLog.count).toBeLessThanOrEqual(5);
           });
         Add eager loading → query count drops to 2 → verify response shape.
```

### Scenario D: Flaky Test (Intermittent Failure)

```
Phase 1: Run test 20 times in isolation → passes 20/20
         Run test in full suite → fails 3/20 times
         → Failure depends on test execution order (shared state)
Phase 1: Check test for: shared database state, global variables, time-dependent
         logic, async operations without proper await, uncleared mocks
         → Test reads from a database table that previous test writes to

Phase 2: Find stable tests with similar DB patterns → all use beforeEach
         with transaction rollback. Flaky test uses no setup/teardown.

Phase 3: "Test relies on database state from previous test. Shared connection
          pool doesn't reset between test files. When test-A runs first and
          inserts a user, test-B's COUNT(*) assertion fails."

Phase 4: Add proper isolation:
           beforeEach(async () => {
             await db.query('BEGIN');
           });
           afterEach(async () => {
             await db.query('ROLLBACK');
           });
         Run 50 times in full suite → 0 failures.
         Search for other tests missing beforeEach cleanup → fix 3 more.
```

---

## When to Escalate vs When to Keep Digging

### Keep Digging When:

- You have untested hypotheses from Phase 2
- You haven't read the full error message or stack trace
- You haven't checked recent changes (`git log`, `git diff`)
- You haven't found working comparison code yet
- The bug is in YOUR code (not a third-party library)
- You've made fewer than 3 fix attempts

### Escalate When:

- **3+ fix attempts failed** — likely architectural; needs human judgment
- **Undocumented library behavior** — file an issue upstream, work around it
- **Environment-specific** — requires access you don't have (prod DB, cloud IAM)
- **Security-sensitive** — don't debug auth/crypto/payment alone; flag for human review
- **Multi-team dependency** — bug is in another team's service or API contract
- **Time-boxed**: you've spent >30 min on Phase 1 with zero progress

### How to Escalate Well

Don't just say "I'm stuck." Provide: **symptom** (exact error), **reproduction
steps**, **evidence gathered** (logs, traces, bisect results), **hypotheses
tested** (what you tried, why it failed), **remaining hypotheses** (untested),
and your **recommendation** for next steps.

---

## Post-Mortem Discipline

After resolving any bug that:
- Was user/customer-impacting
- Took >1 hour to diagnose
- Involved 3+ failed fix attempts
- Revealed a systemic issue (same bug class exists elsewhere)

Fill out `references/postmortem-template.md` and include it in the PR or commit.
The goal is **learning, not blame**. Every postmortem must produce at least one
action item that prevents the same class of bug from recurring.

---

## Modular References

| File | When to Read | What It Covers |
|------|-------------|----------------|
| `references/tool-guides.md` | When you need stack-specific debugger commands | Node.js inspector, Python pdb/debugpy, Chrome DevTools, git bisect, database EXPLAIN |
| `references/postmortem-template.md` | After resolving a significant incident | Blameless postmortem template with filled example |

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `dev` §2 | Summary of this methodology. This skill is the full version. |
| `dev-testing` | Phase 4 "write failing test first" → use `dev-testing` for test patterns and harness. `dev-testing` provides the tooling; this skill provides the thinking. |
| `dev-backend` | Server-side debugging context: API errors, database issues, middleware chains. |
| `dev-frontend` | Client-side debugging context: hydration, rendering, DevTools, layout shifts. |
| `dev-code-reviewer` | Code review catches bugs before they ship — prevention beats debugging. |

---

## Compact Summary

When context is limited, preserve: (1) Iron Law — no fixes without root cause,
(2) 4 Phases — investigate → analyze → hypothesize → implement,
(3) 3-Strike Rule — 3 failures = escalate, (4) one variable at a time,
(5) evidence over intuition, (6) failing test first.
