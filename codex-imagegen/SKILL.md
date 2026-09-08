---
name: codex-imagegen
description: "Use only on the Codex CLI for native image generation or image editing without an API key. Save final PNG files under ~/.cli-jaw/uploads, report web-ready absolute-path markdown, and send to Telegram or Discord only when explicitly requested."
---

# Codex Native Image Generation

Use Codex's native image-generation capability. This skill is separate from the
API-based `imagegen` skill and must never fall back to that workflow.

## Preconditions

1. Confirm the assigned runtime CLI from the employee/runtime context.
2. If the CLI is not `codex`, stop and report exactly:

   `precondition failed: not codex - codex-imagegen requires Codex native image generation`

3. Do not re-dispatch, call another image skill, or ask for an API key.
4. If Codex does not expose native image generation in the current session, stop
   and report `precondition failed: codex native image generation unavailable`.

## Native Workflow

1. Derive a short lowercase ASCII kebab-case slug from the subject.
2. Use a local timestamp in `YYYYMMDD-HHMMSS` form.
3. Ensure the default output directory exists:

   `~/.cli-jaw/uploads`

   If `CLI_JAW_HOME` is explicitly set for this runtime, use its `uploads`
   directory instead so the running server and the output path share one JAW_HOME.
4. Set the final output path to:

   `~/.cli-jaw/uploads/<slug>-<timestamp>.png`

5. Perform the user's image generation or edit directly with Codex's native
   image-generation capability. No API key, Python image script, OpenAI SDK, or
   `skills_ref/imagegen` workflow is required.
6. Materialize the final artifact at the output path and verify that the file
   exists and is a non-empty PNG before reporting success.
7. For an edit, preserve every user-named invariant and inspect the final result
   before reporting it.

## Web Report

Unless direct channel delivery was explicitly requested and completed, the final
answer must contain the expanded absolute path in Markdown image syntax:

`![concise descriptive alt](/absolute/path/to/.cli-jaw/uploads/<slug>-<timestamp>.png)`

Do not use `~`, a relative path, `file://`, a remote URL, or a data URL in this
Markdown. The absolute local path is the cli-jaw web inlay trigger.

## Explicit Channel Delivery

Call `POST /api/channel/send` only when the user explicitly asks to send the
image to Telegram, Discord, or both. Use the final absolute path:

```json
{
  "channel": "telegram",
  "type": "photo",
  "file_path": "/absolute/path/to/.cli-jaw/uploads/<slug>-<timestamp>.png",
  "caption": "Optional concise caption"
}
```

For Discord, send the same shape with `"channel": "discord"`. If both channels
were requested, make two calls, one per channel. Do not use `channel: "active"`
as a substitute for an explicit two-channel request.

A request that merely originated in Telegram or Discord is not permission to make
an extra direct API call. The host may relay the normal final Markdown itself.

## Duplicate Prevention

Choose exactly one final reporting mode:

- No direct channel send: include the Markdown image from **Web Report**.
- Direct channel send completed: do not include Markdown image syntax. Report only
  `Saved: <absolute path>` and the channel names that succeeded.

Never both call `/api/channel/send` and leave the same image as `![...](...)` in
the final answer. If a channel call fails, report the failed channel and error;
do not claim delivery.

## Hard Boundaries

- Never require or inspect `OPENAI_API_KEY`.
- Never invoke `scripts/image_gen.py` or the API-based `imagegen` skill.
- Never save the final artifact outside the active JAW_HOME uploads directory.
- Never send to a channel that the user did not explicitly name.
- Never report success before the local file existence/non-empty check passes.
