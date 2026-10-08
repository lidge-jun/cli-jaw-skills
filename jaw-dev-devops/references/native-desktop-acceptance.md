# Electron Desktop Acceptance

Applies to cli-jaw's Electron renderer, Manager, packaged Node sidecar, and
macOS distribution. This file owns all applicable `DESKTOP-*` rules. Desktop
acceptance follows the actual change and release claim, not a universal test list.

## §1 Scope (`DESKTOP-SCOPE-01`)

Name the affected boundary: UI, runtime, packaging or distribution. Include
the final packaged app when a claim depends on bundled behavior. A source test
cannot establish installed app behavior. Use an isolated desktop QA profile
where local UI execution is permitted; record the profile and app version.

## §2 Evidence matrix (`DESKTOP-MATRIX-01`)

Each row records `id | boundary and scenario | required level | achieved level |
state | artifact id | baseline class`. States are `pass`, `fail`,
`not_verified`, `needs_human`, `hosted_required`, and `na`. Evidence levels rise
from source review → host-only build → signed bundle inspection → bundled runtime
launch → native interaction → publication. A higher level does not erase a
failed lower-level check. Separate UI, runtime, packaging and distribution rows.
For hosted checks, link the exact run and head SHA using
`../../jaw-dev/references/hosted-ci-evidence.md`.

## §3 Downstream invalidation (`DESKTOP-DOWNSTREAM-01`)

When a build fails, launch and notarization remain unverified. When signing or
bundle inspection fails, installed behavior and publication remain unverified.
Do not promote downstream rows based on a prior artifact or a different SHA.

## §4 CI map (`DESKTOP-CI-MAP-01`)

Map each requirement to the event and artifact that actually exercises it.
cli-jaw's ordinary PR contract is a Linux minimum; `dev`, `preview`, and `main`
pushes run broader platform checks. The macOS desktop release path also checks
the packaged sidecar, signature, DMG and update metadata. Record the workflow
run and attempt; compare its head SHA to the artifact source. Hosted CI proves
its runner environment, and visible native interaction needs a real app session.

## §5 Baseline (`DESKTOP-BASELINE-01`)

Classify each row as unchanged, regressed, new, removed or repair-introduced
against an earlier packaged artifact actually inspected or run. If none exists,
write `baseline absent`; do not claim absence of regressions from memory.

## §6 Artifact identity (`DESKTOP-ARTIFACT-01`)

For every artifact-backed row, record code SHA; workflow run/attempt or local
builder; app bundle, executable, sidecar, DMG and update-metadata paths and
SHA-256 hashes where produced; exact architectures; signing identity and team;
entitlements; and the installed behavior observed. Mark unavailable components
with a reason. Hash the final artifact that was tested, not an earlier staging
copy. An ad-hoc arm64 app does not prove a signed DMG or a universal build.
The artifact id links all rows using the same bytes. This is a plain evidence
record; no special receipt schema or validator is implied.

## §7 Sidecar architecture (`DESKTOP-UNIVERSAL-01`)

cli-jaw's local `sidecar:bundle` currently targets Darwin arm64. Inspect each
embedded executable's actual architecture against the claimed target, then
execute the packaged sidecar from the final bundle. If a future release claims
multiple architectures, prove every embedded executable supports each one;
do not infer that from the outer app label. Record the exact path and output
of packaged smoke. No universal claim follows from a single-architecture build.

## §8 Native window and popup (`DESKTOP-POPUP-01`)

For a changed Electron window, menu or popup, capture the native app itself.
Check light and dark appearance, long content and scroll bounds, focus and
Escape/dismiss/reopen behavior, and display placement where applicable.
A browser screenshot of the Manager does not prove a native popup. A system
permission prompt is a `needs_human` row under `macos-system-approvals.md`.

## §9 Build and distribution (`DESKTOP-DIST-01`)

Use the project's declared commands for the stage being claimed:

```sh
npm run electron:dist:mac                 # local ad-hoc package
npm run check:electron-dist-mac-smoke     # packaged server tree
npm run electron:dist:mac:signed          # signed/notarized path with prerequisites
npm run verify:electron-update-metadata
npm run verify:mac-signature
npm run verify:mac-dmg
```

The signed path already calls the verifiers; separate invocations are useful
for diagnosis. Inspect signature, nested code, entitlements, notarization and
DMG on the artifact being distributed. Changing bundle bytes after signing
invalidates that proof. Notarization does not establish launch or interaction.
Where relevant, verify first launch, update and install behavior on a target
Mac, with the same artifact hash.

## §10 No local execution (`DESKTOP-NOLOCAL-01`)

If local execution is prohibited or unavailable, retain every affected row
as `hosted_required` or `not_verified`. A person's acceptance covers only the
scenario they confirmed. Source review, host build and CI logs cannot be
reported as native interaction. Name the environment and evidence still needed.
