# Logging discipline — CLI, scripts, libraries

What to emit and where, for surfaces that are **not** production services.

## Scope

| Surface | Owner | Example |
| --- | --- | --- |
| One-shot CLI | this document | a command that prints a map, a doctor report, a query result |
| Long-running local server | process stdout/stderr transport: this document's `LOG-CONSUMER-01` / `LOG-ONCE-01` only. HTTP and request instrumentation: `jaw-dev-backend` | a local jaw-dev server |
| Production-deployed service | `jaw-dev-backend` `references/core/observability.md` (JSON, traceId, OTel conventions) | a deployed API |

Where they overlap on a deployed service, `jaw-dev-backend` wins.

## Rules

**LOG-CONSUMER-01 (DEFAULT).** Before emitting, answer "who reads this line, and
what do they do with it?". If you cannot answer, do not emit. Do not introduce
logging into a module that had none — the absence is also a decision.

**LOG-STREAM-01 (DEFAULT, one-shot CLI only).** For a command whose output others
may pipe: stdout is the successful command output; stderr is diagnostics,
progress, warnings, and errors. Do not put piped values on stderr, and do not mix
diagnostics into stdout. `--help` and `--version` are successful output and
belong on stdout.

An expected usage error — a bad flag, bad input — is not error-level *telemetry*,
but in a CLI it still gets **stderr plus a nonzero exit**. The two ideas are
separate and conflating them produces either a silent failure or a log line
nobody needs.

A long-running local server is outside this rule. A server process's stdout is a
log stream, not pipeline output, so a lifecycle logger writing there is correct.
Do not apply the stdout/stderr split to it retroactively.

**LOG-ONCE-01 (DEFAULT).** Judge duplication by **consumer and sink**, not by
event identity. The same event may be recorded once per distinct consumer — one
durable telemetry record plus one human-facing diagnostic is legitimate. What is
forbidden is indistinguishable repetition into the same sink for the same
consumer. Boundary log-and-rethrow that adds context is allowed; `jaw-dev-debugging`
explicitly permits it.

The rule is stated this way because the intuitive version — "log each event once"
— deletes the wrong line. A durable event record and an operator-facing stderr
message for the same failure look like a duplicate and are not: different sink,
different reader, different purpose. Removing either one loses a consumer.

## Owned elsewhere

This document does not redefine any of these:

- Following existing conventions — `jaw-dev/SKILL.md` §Conventions.
- Where log statements belong — `jaw-dev-debugging/references/methodologies.md`.
- Surfacing async failures at a clear boundary — `jaw-dev/SKILL.md` §5 Safety Rules.
- Service log levels, JSON transport, trace fields, logger libraries —
  `jaw-dev-backend/references/core/observability.md`.
