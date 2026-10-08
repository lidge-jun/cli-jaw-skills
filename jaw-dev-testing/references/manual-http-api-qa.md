# HTTP API QA (QA-HTTP-01)

Drive the real Jaw endpoint and capture what the wire returns. Test strategy
and harness choice live in `jaw-dev-testing`; response contracts belong to
the documented route and `jaw-dev-backend`. Do not assume one universal
response envelope across Jaw routes.

Use `curl -i` to retain status, headers, and body. Use `-v` when TLS or
redirect behavior is the claim, and retain every hop in a multi-step flow.
For SSE, use bounded `curl -N --max-time <seconds>` and state the event/time
cutoff. Capture each request and response, including errors. Redact tokens,
cookies, and private payloads in evidence without erasing the status or
response shape being checked.

Choose applicable cells from this matrix:

| Axis | What to observe |
| --- | --- |
| Authentication | Anonymous, valid, expired, or wrong-scope credentials; documented status and no protected payload leak |
| Contract | Documented success and error bodies, headers, and status for this route |
| Repeat | Double submit or retry; documented idempotency or conflict behavior |
| Boundary | Empty/missing field, size limit, invalid JSON/type, wrong `Content-Type` |
| Negotiation | `Accept` and `Accept-Encoding` behavior where supported |
| CORS | Browser-facing `OPTIONS` with `Origin` and `Access-Control-Request-Method` |
| Status cells | Each claimed method/auth combination has its own captured result |

Assert the route's documented response, including its actual error shape and
limits. A successful SDK call is not wire evidence because it can retry or
normalize. Record the exact command, expected behavior, observed capture,
verdict, and teardown via [manual surface QA](manual-surface-qa.md).
