# CLI and TUI QA (QA-CLI-01)

Drive the real terminal surface. Check `jaw` or `cli-jaw` help before citing
a command or flag. Record the exact invocation, environment, output, exit
code, and cleanup. [Manual surface QA](manual-surface-qa.md) owns the shared
scenario and verdict matrix.

## CLI capture

Capture stdout and stderr separately when the claim distinguishes them;
retain a merged capture as well if ordering matters. Record the exit code
immediately. Test the mode actually claimed: a pipe for non-TTY behavior,
a PTY for interactive behavior. Probe applicable flag/environment/config
conflicts, empty stdin, malformed input, locale or color settings, and
repeat invocation. Do not infer universal `--help` or `--version` semantics
without checking the chosen subcommand. For a long-running process, send
the relevant signal and verify that processes and temporary resources close.

## TUI session

Use a fixed terminal size and record its columns and rows. On POSIX, tmux is
one optional PTY method; Windows may use a native equivalent. Wait for an
observable marker with a bound before taking a capture, rather than sleeping
for an assumed duration. Inspect → act → re-inspect each keypress or resize.
Keep plain text and ANSI captures when styling matters. Check line overflow,
wide CJK characters, box borders, and stale fragments after resize. Close
the session and record observable teardown proof.
