# Alternative Submission Methods

## HF Jobs CLI (Direct Terminal Commands)

Use `hf jobs` CLI when the `hf_jobs()` MCP tool is unavailable.

### Syntax Rules

```bash
# ✅ Correct — flags BEFORE script URL
hf jobs uv run --flavor a10g-large --timeout 2h --secrets HF_TOKEN "https://example.com/train.py"

# ❌ "run uv" instead of "uv run"
hf jobs run uv "https://example.com/train.py" --flavor a10g-large

# ❌ Flags AFTER script URL (will be ignored)
hf jobs uv run "https://example.com/train.py" --flavor a10g-large

# ❌ "--secret" instead of "--secrets" (plural)
hf jobs uv run --secret HF_TOKEN "https://example.com/train.py"
```

Key rules:
1. Command order: `hf jobs uv run` (not `hf jobs run uv`)
2. All flags (`--flavor`, `--timeout`, `--secrets`) before the script URL
3. Use `--secrets` (plural)
4. Script URL is the last positional argument

### Job Management

```bash
hf jobs ps                        # List all jobs
hf jobs logs <job-id>             # View logs
hf jobs inspect <job-id>          # Job details
hf jobs cancel <job-id>           # Cancel a job
```

## TRL Jobs Package (Simplified Training)

The `trl-jobs` package provides optimized defaults and one-liner training.

```bash
pip install trl-jobs

trl-jobs sft \
  --model_name Qwen/Qwen2.5-0.5B \
  --dataset_name trl-lib/Capybara
```

Benefits: Pre-configured settings, automatic Trackio integration, automatic Hub push.
When to use: Terminal-direct usage (not Claude Code context), quick local experimentation.

Repository: https://github.com/huggingface/trl-jobs

In Claude Code context, prefer `hf_jobs()` MCP tool.

## TRL Maintained Scripts

TRL provides battle-tested scripts for all methods, runnable from URLs:

```python
hf_jobs("uv", {
    "script": "https://github.com/huggingface/trl/blob/main/trl/scripts/sft.py",
    "script_args": [
        "--model_name_or_path", "Qwen/Qwen2.5-0.5B",
        "--dataset_name", "trl-lib/Capybara",
        "--output_dir", "my-model",
        "--push_to_hub",
        "--hub_model_id", "username/my-model"
    ],
    "flavor": "a10g-large",
    "timeout": "2h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

Available scripts: https://github.com/huggingface/trl/tree/main/examples/scripts

## Working with the `script` Parameter

The `script` parameter accepts inline code or URLs. Local file paths do not work — jobs run in isolated Docker containers.

```python
# ✅ Inline code (recommended)
hf_jobs("uv", {"script": "# /// script\n# dependencies = [...]\n# ///\n\n<your code>"})

# ✅ From Hugging Face Hub
hf_jobs("uv", {"script": "https://huggingface.co/user/repo/resolve/main/train.py"})

# ✅ From GitHub
hf_jobs("uv", {"script": "https://raw.githubusercontent.com/user/repo/main/train.py"})
```

To use local scripts, upload to HF Hub first:
```bash
huggingface-cli repo create my-training-scripts --type model
huggingface-cli upload my-training-scripts ./train.py train.py
# Use: https://huggingface.co/USERNAME/my-training-scripts/resolve/main/train.py
```

## Finding UV Scripts on Hub

The `uv-scripts` organization provides ready-to-use UV scripts as datasets:

```python
dataset_search({"author": "uv-scripts", "sort": "downloads", "limit": 20})
hub_repo_details(["uv-scripts/classification"], repo_type="dataset", include_readme=True)
```

Popular collections: ocr, classification, synthetic-data, vllm, dataset-creation
