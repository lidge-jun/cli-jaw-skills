# macOS System Approvals

Applies to cli-jaw desktop tests that meet TCC, Gatekeeper, Keychain,
administrator, login/background item or Automation prompts. Record their
state in `native-desktop-acceptance.md`'s evidence matrix.

## §1 Human gestures (`MACOS-APPROVAL-HUMAN-01`)

Privacy grants and first-launch decisions belong to the person at the Mac.
The agent does not click them through UI automation or ask to click on the
person's behalf. This includes Accessibility, Screen and System Audio
Recording, Automation/Apple Events, Input Monitoring, Full Disk Access,
Camera/Microphone, Gatekeeper Open Anyway, Keychain Always Allow, admin
authentication, and any actual login/background item approval.

## §2 Bypasses (`MACOS-APPROVAL-BYPASS-01`)

Do not edit `TCC.db`, remove the tested artifact's quarantine, disable
Gatekeeper or SIP, ad-hoc re-sign a Developer ID artifact to force launch,
or script an Allow/Open click. A managed-device configuration profile requires
an explicitly authorized test-host setup. A row requiring a bypass stays
`fail` or `needs_human`.

## §3 Read-only checks (`MACOS-APPROVAL-READ-01`)

On an authorized execution host, inspect the final artifact with
`codesign -dv`, `codesign -vvv --deep --strict`,
`codesign -d --entitlements -`, `spctl --assess -vv`, and
`xcrun stapler validate` as applicable. A permitted launch may record the
prompt and exact text; launching can itself change app state. If local runs
are barred, mark the row `hosted_required` or `not_verified`.

## §4 Authorized changes (`MACOS-APPROVAL-AUTH-01`)

`tccutil reset`, notary submission, temporary CI keychains and installing or
removing login items, agents or daemons require task and host authorization.
A generic app test does not authorize resetting someone's existing privacy
decisions. Do not claim cli-jaw uses a login-item API merely because the
platform supports one.

## §5 Actual menu or tray item (`MACOS-APPROVAL-MENUBAR-01`)

Only if the app has such an item, capture its popup and any prompt it triggers.
Record the app/process named in the prompt. If the item is not visible, report
that observation; do not change system UI settings to reveal it.

## §6 `needs_human` evidence (`MACOS-APPROVAL-RECORD-01`)

A blocked row records the exact gesture requested, artifact hash, observed
prompt text or setting, who confirmed the approval and when, and a post-approval
recapture of the behavior. Until confirmation and recapture exist, keep
`needs_human`. Ask for the target environment using
`cross-platform-release.md` §3 when no authorized native session exists.
