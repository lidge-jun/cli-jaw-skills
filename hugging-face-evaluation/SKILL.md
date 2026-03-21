---
name: hugging-face-evaluation
description: Add and manage evaluation results in Hugging Face model cards. Supports extracting eval tables from README content, importing scores from Artificial Analysis API, and running custom model evaluations with vLLM/lighteval. Works with the model-index metadata format.
---

# Hugging Face Evaluation Skill

> All paths are relative to this SKILL.md's directory. `cd` here or use full paths before running scripts.

## PR Safety — Check Before Creating

Before using `--create-pr`, check for existing open PRs to avoid duplicating work for maintainers:

```bash
uv run scripts/evaluation_manager.py get-prs --repo-id "username/model-name"
```

If open PRs exist:
1. Warn the user and show existing PR URLs
2. Only proceed if the user explicitly confirms creating another PR

## Core Workflow

Use `--help` for the latest workflow guidance:
```bash
uv run scripts/evaluation_manager.py --help
```

Standard flow:
1. `get-prs` → check for existing open PRs
2. `inspect-tables` → find table numbers/columns
3. `extract-readme --table N` → prints YAML (preview by default)
4. Add `--apply` (push) or `--create-pr` to write changes

## Prerequisites

- Use `uv run` (PEP 723 header auto-installs deps)
- Set `HF_TOKEN` env var with write-access token
- For Artificial Analysis: set `AA_API_KEY` env var
- `.env` is loaded automatically if `python-dotenv` is installed

## Commands Reference

**Inspect tables (start here):**
```bash
uv run scripts/evaluation_manager.py inspect-tables --repo-id "username/model-name"
```

**Extract from README:**
```bash
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "username/model-name" \
  --table N \
  [--model-column-index N] \
  [--model-name-override "Exact Column Header"] \
  [--task-type "text-generation"] \
  [--dataset-name "Custom Benchmarks"] \
  [--apply | --create-pr]
```

**Import from Artificial Analysis:**
```bash
AA_API_KEY=... uv run scripts/evaluation_manager.py import-aa \
  --creator-slug "creator-name" \
  --model-name "model-slug" \
  --repo-id "username/model-name" \
  [--create-pr]
```

**View / Validate:**
```bash
uv run scripts/evaluation_manager.py show --repo-id "username/model-name"
uv run scripts/evaluation_manager.py validate --repo-id "username/model-name"
```

**Run evaluation job (inference providers):**
```bash
hf jobs uv run scripts/inspect_eval_uv.py \
  --flavor "cpu-basic|t4-small|a10g-small" \
  --secret HF_TOKEN=$HF_TOKEN \
  -- --model "model-id" --task "task-name"
```

**Run vLLM evaluation (custom models):**
```bash
# lighteval with vLLM
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --tasks "leaderboard|mmlu|5"

# inspect-ai with vLLM
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --task mmlu

# Helper script (auto hardware selection)
uv run scripts/run_vllm_eval_job.py \
  --model "model-id" \
  --task "leaderboard|mmlu|5" \
  --framework lighteval
```

## vLLM Evaluation

Requires `uv` installed and sufficient GPU memory. Verify with `nvidia-smi`.

Two frameworks available:
- **lighteval** — HuggingFace's library; task format: `suite|task|num_fewshot` (e.g. `leaderboard|mmlu|5`)
- **inspect-ai** — UK AISI framework; tasks: `mmlu`, `gsm8k`, `hellaswag`, `arc_challenge`, `truthfulqa`, `winogrande`, `humaneval`

Key flags:
- `--backend accelerate` or `--backend hf` for non-vLLM inference
- `--use-chat-template` for instruction-tuned models
- `--trust-remote-code` for models with custom code (e.g. Phi-2, Qwen)
- `--tensor-parallel-size N` for multi-GPU

Hardware sizing: <3B → `t4-small`, 3-13B → `a10g-small`, 13-34B → `a10g-large`, 34B+ → `a100-large`

Submit via HF Jobs by prefixing with `hf jobs uv run` and adding `--flavor`/`--secrets`.

## Model-Index Format

```yaml
model-index:
  - name: Model Name
    results:
      - task:
          type: text-generation
        dataset:
          name: Benchmark Dataset
          type: benchmark_type
        metrics:
          - name: MMLU
            type: mmlu
            value: 85.2
        source:
          name: Source Name
          url: https://source-url.com
```

- Use plain text for model name (no markdown formatting)
- URLs belong only in `source.url`

## Best Practices

1. Run `get-prs` before creating any PR
2. Start with `inspect-tables` to see table structure
3. Preview YAML output before using `--apply` or `--create-pr`
4. Prefer `--model-column-index` over `--model-name-override`; if using override, match column header text exactly
5. For multi-table READMEs, specify `--table N`
6. Use `--create-pr` when updating models you don't own
7. One model per repo — only add the main model's results

## References

- [CLI examples and detailed usage](references/cli-examples.md) — full Method 1-4 walkthroughs, common patterns, model name matching
- [Troubleshooting](references/troubleshooting.md) — error messages and solutions
