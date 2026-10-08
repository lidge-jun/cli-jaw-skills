# Safe text and public-boundary handling

## DEV-SHELL-TEXT-01 (STRICT)

Write generated Markdown, plans, PR bodies, and replacement strings through a
patch, a file, a quoted heredoc (`<<'EOF'`), or `--body-file`. An employee brief
can use `jaw dispatch --agent <employee> --task-file <path>`. Do not interpolate
untrusted or generated backticks and `$()` into double-quoted shell arguments or
`sh -c` payloads; the shell executes them before the intended command runs.

## DEV-PRIVACY-01 (STRICT)

Keep raw client and personal data and credentials out of public code, fixtures,
sample assets, and commit history. Private records belong outside the public
checkout. Before a public push, review outgoing content and run the repository's
private-boundary gates where present. For cli-jaw, these are
`npm run check:private-boundary` for the index and
`node scripts/check-private-boundary.mjs --range <remote-base> HEAD` for every
outgoing commit tree. Search the outgoing range for identifiers specific to the
task; resolve a leak in unpushed history before publishing it.
