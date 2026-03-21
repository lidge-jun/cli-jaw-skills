---
name: deep-research
description: Run autonomous multi-step research via Google Gemini Deep Research Agent. Produces cited reports from web sources.
license: Apache-2.0
metadata:
  author: sanjay3290
  version: "1.0"
---

# Gemini Deep Research

Autonomous research agent that plans searches, reads sources, and synthesizes cited reports.

## When to Use

- Questions requiring synthesis across many sources (market analysis, literature reviews, competitive landscape)
- Due diligence or technical research where breadth matters more than speed
- NOT for quick factual lookups (use `search` skill instead)

Trade-off: higher cost and latency in exchange for comprehensive, cited coverage.

## Requirements

- Python 3.8+, httpx (`pip install -r requirements.txt`)
- `GEMINI_API_KEY` environment variable

## CLI Reference

```bash
python3 scripts/research.py --query "..." [options]
```

| Flag | Effect |
|------|--------|
| `--query "..."` | Research question (required for new tasks) |
| `--format "..."` | Output structure template |
| `--stream` | Stream progress in real-time |
| `--no-wait` | Start task and return immediately |
| `--status <id>` | Check status of a running task |
| `--wait <id>` | Block until task completes |
| `--continue <id>` | Follow-up on previous research |
| `--list` | List recent research tasks |
| `--json` | Output as structured JSON |
| `--raw` | Output raw API response |

## Cost and Latency

Costs and times vary by query complexity and source count. Expect minutes, not seconds. Check actual token usage in the output metadata for accurate billing.

## Exit Codes

- **0**: Success
- **1**: Error (API, config, or timeout)
- **130**: Cancelled (Ctrl+C)
