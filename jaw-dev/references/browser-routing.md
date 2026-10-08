# Browser routing

This reference owns capability selection for browser work (DEV-BROWSE-NATIVE-01).
The two exact ladders and their opposite ordering are in
`browse-qa-ladders.md`: public source proof starts with HTTP; QA of a surface just
built starts with a rendered, interactive view. Do not install a browser driver
for ad-hoc inspection. Maintained E2E suites belong to `jaw-dev-testing`.

| Need | Route |
|---|---|
| Public static source | Discover the URL, then use `jaw browser fetch <url>`; inspect content and escalate if it is incomplete. |
| Many independent public pages | Use bounded independent fetches or task-owned tabs. |
| Authenticated work | Use a signed-in browser that actually has the required account and permission. |
| Local interactive UI QA | Use an available rendering and action surface; inspect the result. |
| Native desktop or browser chrome | Use a suitable computer-use surface and report a specific capability gap if absent. |
| Maintained regression | Use repository-owned tests and fixtures. |

Inspect → act → re-inspect. Read screenshots you cite and verify the promised
interaction. Each parallel lane owns explicit tabs and, where needed, separate
profiles or contexts; never race a shared active tab or stop another lane's browser.
Cookies and permissions do not transfer between tools. Do not export credentials
to make a fallback work; reconfirm the account after switching.

Before retrying a side-effecting action after a timeout, check whether it already
happened. A tool's `ok`, title, or navigation success does not prove that the
requested content or action is present; check for shells, wrong accounts, and
truncated results. If access or rendering is unavailable, report that limit.
