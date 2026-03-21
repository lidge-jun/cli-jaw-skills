---
name: hugging-face-model-trainer
description: Train/fine-tune LLMs using TRL on Hugging Face Jobs infrastructure. Covers SFT, DPO, GRPO, reward modeling, GGUF conversion, dataset validation, hardware selection, cost estimation, Trackio monitoring, and model persistence. Invoke for cloud GPU training or GGUF conversion.
license: Complete terms in LICENSE.txt
---

# TRL Training on Hugging Face Jobs

Train language models using TRL on managed Hugging Face infrastructure. Models train on cloud GPUs and results save to Hugging Face Hub automatically.

## Key Rules

1. **Submit via `hf_jobs()` MCP tool** — use `hf_jobs("uv", {...})` with inline Python code in the `script` parameter. Local file paths do not work (jobs run in isolated Docker containers). When a user asks to train a model, create the script and submit immediately.
2. **Include Trackio** in every training script for real-time monitoring. Use example scripts in `scripts/` as templates.
3. **Enable Hub push** — the training environment is ephemeral; unpushed results are lost. Set `push_to_hub=True`, `hub_model_id`, and `secrets={"HF_TOKEN": "$HF_TOKEN"}`.
4. **Set adequate timeout** — default 30 min is too short for most training. Add 20-30% buffer to estimated time.
5. **Validate unknown datasets** before GPU training to prevent format failures. See `references/dataset_validation.md`.
6. **Report after submission** — provide job ID, monitoring URL, estimated time. Wait for user to request status checks.

## Training Methods

| Method | Use Case | Dataset Format |
|--------|----------|---------------|
| **SFT** | Instruction tuning | `messages` / text / prompt-completion |
| **DPO** | Preference alignment | `prompt`, `chosen`, `rejected` |
| **GRPO** | Online RL training | prompt-only |
| **Reward** | RLHF reward models | preference pairs |

For method details: `references/training_methods.md` or `hf_doc_search("query", product="trl")`

### When to Use Unsloth

Use **Unsloth** when VRAM is limited, speed matters, training large models (>13B), or training VLMs. ~2x faster, ~60% less VRAM. See `references/unsloth.md`.

## Prerequisites

### Account & Auth
- HF account with [Pro](https://hf.co/pro), [Team](https://hf.co/enterprise), or [Enterprise](https://hf.co/enterprise) plan
- Authenticated: verify with `hf_whoami()`
- Token with write permissions; pass `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job config

### Dataset
- Dataset on Hub or loadable via `datasets.load_dataset()`
- Format matching training method (see table above)
- Validate unknown datasets before GPU training (see `references/dataset_validation.md`)
- Size appropriate for hardware (demo: 50-100 examples on t4-small; production: 1K-10K+ on a10g/a100)

## Job Submission: UV Scripts (Primary Approach)

UV scripts use PEP 723 inline dependencies for self-contained training:

```python
hf_jobs("uv", {
    "script": """
# /// script
# dependencies = ["trl>=0.12.0", "peft>=0.7.0", "trackio"]
# ///

from datasets import load_dataset
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
import trackio

dataset = load_dataset("trl-lib/Capybara", split="train")
dataset_split = dataset.train_test_split(test_size=0.1, seed=42)

trainer = SFTTrainer(
    model="Qwen/Qwen2.5-0.5B",
    train_dataset=dataset_split["train"],
    eval_dataset=dataset_split["test"],
    peft_config=LoraConfig(r=16, lora_alpha=32),
    args=SFTConfig(
        output_dir="my-model",
        push_to_hub=True,
        hub_model_id="username/my-model",
        num_train_epochs=3,
        eval_strategy="steps",
        eval_steps=50,
        report_to="trackio",
        project="meaningful_project_name",
        run_name="meaningful_run_name",
    )
)

trainer.train()
trainer.push_to_hub()
""",
    "flavor": "a10g-large",
    "timeout": "2h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

**Demo tip:** For quick demos on smaller GPUs (t4-small), omit `eval_dataset` and `eval_strategy` to save ~40% memory.

### Sequence Length

TRL config classes use `max_length` (not `max_seq_length`):

```python
SFTConfig(max_length=512)   # ✅ Truncate to 512 tokens
SFTConfig(max_seq_length=512)  # ❌ TypeError
```

Default `max_length=1024` works well for most training. Override for longer context, memory constraints, or vision models (`max_length=None`).

### Alternative Approaches

See `references/cli_usage.md` for:
- **TRL maintained scripts** — battle-tested official examples from URLs
- **HF Jobs CLI** — `hf jobs uv run` terminal commands (when MCP unavailable)
- **TRL Jobs package** — `trl-jobs sft` one-liner training
- **UV Scripts on Hub** — ready-to-use scripts from `uv-scripts` organization

## Hardware Selection

| Model Size | Hardware | Cost (approx/hr) | Use Case |
|------------|----------|------------------|----------|
| <1B params | `t4-small` | ~$0.75 | Demos, quick tests (skip eval) |
| 1-3B params | `t4-medium`, `l4x1` | ~$1.50-2.50 | Development |
| 3-7B params | `a10g-small`, `a10g-large` | ~$3.50-5.00 | Production |
| 7-13B params | `a10g-large`, `a100-large` | ~$5-10 | Large models (use LoRA) |
| 13B+ params | `a100-large`, `a10g-largex2` | ~$10-20 | Very large (use LoRA) |

Use LoRA/PEFT for models >7B. Multi-GPU is handled automatically by TRL/Accelerate.

**All flavors:** cpu-basic/upgrade/performance/xl, t4-small/medium, l4x1/x4, a10g-small/large/largex2/largex4, a100-large, h100/h100x8

See `references/hardware_guide.md` for detailed specifications.

## Hub Saving

The training environment is ephemeral — all files are deleted when the job ends.

**In training config:**
```python
SFTConfig(
    push_to_hub=True,
    hub_model_id="username/model-name",
    hub_strategy="every_save",  # optional: push checkpoints
)
```

**In job submission:**
```python
{"secrets": {"HF_TOKEN": "$HF_TOKEN"}}
```

**Checklist:** `push_to_hub=True` ✓ | `hub_model_id` set ✓ | `secrets` has HF_TOKEN ✓ | write access ✓

See `references/hub_saving.md` for troubleshooting.

## Timeout Guidelines

| Scenario | Recommended | Notes |
|----------|-------------|-------|
| Quick demo (50-100 examples) | 10-30 min | Verify setup |
| Development training | 1-2 hours | Small datasets |
| Production (3-7B model) | 4-6 hours | Full datasets |
| Large model with LoRA | 3-6 hours | Depends on dataset |

On timeout, the job is killed immediately and unsaved progress is lost. Add 20-30% buffer.

```python
{"timeout": "2h"}  # formats: "90m", "2h", "1.5h", or seconds as integer
```

## Cost Estimation

Offer to estimate cost when planning jobs with known parameters:

```bash
uv run scripts/estimate_cost.py \
  --model meta-llama/Llama-2-7b-hf \
  --dataset trl-lib/Capybara \
  --hardware a10g-large \
  --dataset-size 16000 \
  --epochs 3
```

Output: estimated time, cost, recommended timeout, optimization suggestions.

## Monitoring

Include Trackio in every script (`report_to="trackio"`). Default config:
- **Space ID**: `{username}/trackio`
- **Run naming**: descriptive of task, model, or purpose
- **Project name**: group related runs

See `references/trackio_guide.md` for complete setup and experiment grouping.

### Job Status

```python
hf_jobs("ps")                                    # List all jobs
hf_jobs("inspect", {"job_id": "your-job-id"})    # Job details
hf_jobs("logs", {"job_id": "your-job-id"})       # View logs
```

## Dataset Validation

Validate format before GPU training — the #1 cause of training failures:

```python
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "username/dataset-name", "--split", "train"]
})
```

Output markers: `✓ READY` (use directly) | `✗ NEEDS MAPPING` (code provided) | `✗ INCOMPATIBLE`

Skip validation for known TRL datasets (`trl-lib/Capybara`, `trl-lib/ultrachat_200k`, etc.).

See `references/dataset_validation.md` for full workflow and DPO mapping examples.

## GGUF Conversion

Convert trained models for local inference (Ollama, LM Studio, llama.cpp):

```python
hf_jobs("uv", {
    "script": "<see references/gguf_conversion.md for complete script>",
    "flavor": "a10g-large",
    "timeout": "45m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"},
    "env": {
        "ADAPTER_MODEL": "username/my-finetuned-model",
        "BASE_MODEL": "Qwen/Qwen2.5-0.5B",
        "OUTPUT_REPO": "username/my-model-gguf"
    }
})
```

See `references/gguf_conversion.md` for quantization options, hardware requirements, and troubleshooting.

## Common Failure Modes

| Problem | Fix |
|---------|-----|
| **OOM** | Reduce `per_device_train_batch_size=1`, increase `gradient_accumulation_steps=8`, enable `gradient_checkpointing=True`, upgrade GPU |
| **Dataset format** | Validate with dataset inspector first (see above) |
| **Job timeout** | Increase timeout with 30% buffer, reduce epochs/dataset, save checkpoints with `hub_strategy="every_save"` |
| **Hub push fails** | Add `secrets={"HF_TOKEN": "$HF_TOKEN"}`, verify `push_to_hub=True` and `hub_model_id`, check write permissions |
| **Missing deps** | Add to PEP 723 header: `# dependencies = ["trl>=0.12.0", "peft>=0.7.0", "trackio", "missing-pkg"]` |

See `references/troubleshooting.md` for detailed solutions.

## Local Script Dependencies

```bash
pip install -r requirements.txt
```

## References

### In This Skill
- `references/training_methods.md` — SFT, DPO, GRPO, KTO, PPO, Reward Modeling overview
- `references/training_patterns.md` — Common training patterns and examples
- `references/dataset_validation.md` — Dataset validation workflow
- `references/cli_usage.md` — CLI, TRL scripts, alternative submission methods
- `references/unsloth.md` — Unsloth for fast training (~2x speed, 60% less VRAM)
- `references/gguf_conversion.md` — GGUF conversion guide
- `references/trackio_guide.md` — Trackio monitoring setup
- `references/hardware_guide.md` — Hardware specs and selection
- `references/hub_saving.md` — Hub auth troubleshooting
- `references/troubleshooting.md` — Common issues and solutions

### Scripts
- `scripts/train_sft_example.py` — Production SFT template
- `scripts/train_dpo_example.py` — Production DPO template
- `scripts/train_grpo_example.py` — Production GRPO template
- `scripts/unsloth_sft_example.py` — Unsloth training template
- `scripts/estimate_cost.py` — Time and cost estimator
- `scripts/convert_to_gguf.py` — GGUF conversion script

### External
- [Dataset Inspector](https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py) — validate dataset format
- [TRL Documentation](https://huggingface.co/docs/trl)
- [TRL Jobs Training Guide](https://huggingface.co/docs/trl/en/jobs_training)
- [TRL Jobs Package](https://github.com/huggingface/trl-jobs)
- [HF Jobs Documentation](https://huggingface.co/docs/huggingface_hub/guides/jobs)
- [TRL Example Scripts](https://github.com/huggingface/trl/tree/main/examples/scripts)
- [UV Scripts Guide](https://docs.astral.sh/uv/guides/scripts/)
- [UV Scripts Organization](https://huggingface.co/uv-scripts)
