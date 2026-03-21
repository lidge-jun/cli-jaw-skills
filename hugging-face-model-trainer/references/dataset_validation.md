# Dataset Validation

Validate dataset format before launching GPU training to prevent format mismatches — the #1 cause of training failures.

## When to Validate

**Validate for:**
- Unknown or custom datasets
- DPO training (most datasets need column mapping)
- Any dataset not explicitly TRL-compatible

**Skip for known TRL datasets:**
- `trl-lib/ultrachat_200k`, `trl-lib/Capybara`, `HuggingFaceH4/ultrachat_200k`, etc.

## Usage

```python
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "username/dataset-name", "--split", "train"]
})
```

The script runs on CPU (~$0.01, <1 min) and usually completes synchronously.

## Reading Results

The output shows compatibility for each training method:

- **`✓ READY`** — Dataset is compatible, use directly
- **`✗ NEEDS MAPPING`** — Compatible but needs preprocessing (mapping code provided)
- **`✗ INCOMPATIBLE`** — Cannot be used for this method

When mapping is needed, the output includes a **MAPPING CODE** section with copy-paste ready Python code.

## Example Workflow

```python
# 1. Inspect dataset
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "argilla/distilabel-math-preference-dpo", "--split", "train"]
})

# 2. Check output markers:
#    ✓ READY → proceed with training
#    ✗ NEEDS MAPPING → apply mapping code below
#    ✗ INCOMPATIBLE → choose different method/dataset

# 3. If mapping needed, apply before training:
def format_for_dpo(example):
    return {
        'prompt': example['instruction'],
        'chosen': example['chosen_response'],
        'rejected': example['rejected_response'],
    }
dataset = dataset.map(format_for_dpo, remove_columns=dataset.column_names)

# 4. Launch training job with confidence
```

## Common Scenario: DPO Format Mismatch

Most DPO datasets use non-standard column names:

```
Dataset has: instruction, chosen_response, rejected_response
DPO expects: prompt, chosen, rejected
```

The validator detects this and provides exact mapping code.
