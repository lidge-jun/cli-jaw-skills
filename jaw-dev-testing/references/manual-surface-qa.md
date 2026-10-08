# Manual surface QA

Drive the changed surface and inspect what it returns. Automated test strategy
and regression suites remain in `jaw-dev-testing`; browser capability selection
remains in `../../jaw-dev/references/browse-qa-ladders.md`.

## Faithful channels

Choose the channel before each scenario. Name the exact invocation and surface:

| Surface | Drive and inspect | Detail |
| --- | --- | --- |
| HTTP API | Real endpoint with `curl -i`; capture headers and body | [HTTP API QA](manual-http-api-qa.md) |
| CLI | Real `jaw` or `cli-jaw` invocation; capture streams and exit status | [CLI and TUI QA](manual-cli-tui-qa.md) |
| TUI | Controlled PTY at stated dimensions; inspect each asserted state | [CLI and TUI QA](manual-cli-tui-qa.md) |
| Web UI | Browser interaction at stated viewport; read screenshots and state | [Visual QA](manual-visual-qa.md) |
| Electron GUI | Launch the packaged app for a packaging claim; capture native interaction and identity | [Native desktop acceptance](../../jaw-dev-devops/references/native-desktop-acceptance.md) |

The `cli-jaw browser snapshot --interactive`, `click`, and `screenshot`
commands can drive web UI. A browser pass alone cannot establish a packaged
Electron claim. Use inspect → act → re-inspect, and read each artifact back.

## Scenario and verdict

Make a small matrix before driving. Include the happy path, an error or
boundary case, repeat or concurrent action when applicable, narrow viewport
or terminal width and CJK text for visual surfaces, and cleanup. Probe empty
input, malformed input, and size limits where the changed behavior accepts
them. Mark an inapplicable class N-A with its structural reason.

| Scenario | Surface and invocation | Expected behavior | Observed artifact | Verdict |
| --- | --- | --- | --- | --- |
| Example: empty input | Exact command or action | Documented response | Capture path and observation | PASS / FAIL / N-A |

Every PASS points to a nonempty artifact captured after the last relevant
source edit. Inspect the raw response, terminal capture, or pixels before
deciding. A FAIL records the observed result and blocker; inaccessible surfaces
remain a verification gap. Note the source checkout, revision, dirty state,
and capture time so a later edit cannot borrow an older PASS. Record paths
without imposing a required evidence directory or JSON schema.

For visual findings, use [grounded visual verdicts](manual-visual-qa.md).
For packaged desktop artifact criteria, use the single owner at
[native desktop acceptance](../../jaw-dev-devops/references/native-desktop-acceptance.md).

## Teardown

List each server, port, PTY/session, browser runtime or tab, container, and
temporary resource started for QA. Record the stop action and observable
proof that it closed. If the pass started no resources, say so explicitly.
Keep the verdict tied to the actual run and its completed teardown.
