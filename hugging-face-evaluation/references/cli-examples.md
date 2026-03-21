# CLI Examples & Detailed Usage

## Method 1: Extract from README (Full Workflow)

```bash
# 1) Inspect tables to get table numbers and column hints
uv run scripts/evaluation_manager.py inspect-tables --repo-id "username/model"

# 2) Extract a specific table (prints YAML by default)
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "username/model" \
  --table 1 \
  [--model-column-index <column index shown by inspect-tables>] \
  [--model-name-override "<column header/model name>"]

# 3a) Apply changes (push directly)
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "username/model" \
  --table 1 \
  --apply

# 3b) Or open a PR
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "username/model" \
  --table 1 \
  --create-pr
```

Validation checklist:
- YAML is printed by default; compare against the README table before applying.
- Prefer `--model-column-index`; if using `--model-name-override`, the column header text must be exact.
- For transposed tables (models as rows), ensure only one row is extracted.

## Method 2: Import from Artificial Analysis

```bash
# Basic
AA_API_KEY="your-api-key" uv run scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "username/model-name"

# With .env file
echo "AA_API_KEY=your-api-key" >> .env
echo "HF_TOKEN=your-hf-token" >> .env

uv run scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "username/model-name"

# Create PR
uv run scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "username/model-name" \
  --create-pr
```

## Method 3: Run Evaluation Job (Inference Providers)

```bash
# Direct CLI
HF_TOKEN=$HF_TOKEN \
hf jobs uv run hf-evaluation/scripts/inspect_eval_uv.py \
  --flavor cpu-basic \
  --secret HF_TOKEN=$HF_TOKEN \
  -- --model "meta-llama/Llama-2-7b-hf" \
     --task "mmlu"

# GPU Example (A10G)
HF_TOKEN=$HF_TOKEN \
hf jobs uv run hf-evaluation/scripts/inspect_eval_uv.py \
  --flavor a10g-small \
  --secret HF_TOKEN=$HF_TOKEN \
  -- --model "meta-llama/Llama-2-7b-hf" \
     --task "gsm8k"

# Python helper
uv run scripts/run_eval_job.py \
  --model "meta-llama/Llama-2-7b-hf" \
  --task "mmlu" \
  --hardware "t4-small"
```

## Method 4: vLLM Custom Model Evaluation

### When to Use vLLM vs Inference Providers

| Feature | vLLM Scripts | Inference Provider Scripts |
|---------|-------------|---------------------------|
| Model access | Any HF model | Models with API endpoints |
| Hardware | Your GPU (or HF Jobs GPU) | Provider's infrastructure |
| Cost | HF Jobs compute cost | API usage fees |
| Speed | vLLM optimized | Depends on provider |
| Offline | Yes (after download) | No |

### Option A: lighteval with vLLM Backend

```bash
# MMLU 5-shot with vLLM
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --tasks "leaderboard|mmlu|5"

# Multiple tasks
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --tasks "leaderboard|mmlu|5,leaderboard|gsm8k|5"

# Accelerate backend instead of vLLM
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --tasks "leaderboard|mmlu|5" \
  --backend accelerate

# Chat/instruction-tuned models
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B-Instruct \
  --tasks "leaderboard|mmlu|5" \
  --use-chat-template

# Via HF Jobs
hf jobs uv run scripts/lighteval_vllm_uv.py \
  --flavor a10g-small \
  --secrets HF_TOKEN=$HF_TOKEN \
  -- --model meta-llama/Llama-3.2-1B \
     --tasks "leaderboard|mmlu|5"
```

**lighteval task format:** `suite|task|num_fewshot`
- `leaderboard|mmlu|5`, `leaderboard|gsm8k|5`, `lighteval|hellaswag|0`, `leaderboard|arc_challenge|25`
- Full list: https://github.com/huggingface/lighteval/blob/main/examples/tasks/all_tasks.txt
- Multiple tasks: comma-separated `--tasks "leaderboard|mmlu|5,leaderboard|gsm8k|5"`

Common suites: `leaderboard` (Open LLM Leaderboard), `lighteval`, `bigbench`, `original`

### Option B: inspect-ai with vLLM Backend

```bash
# MMLU with vLLM
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --task mmlu

# HuggingFace Transformers backend
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --task mmlu \
  --backend hf

# Multi-GPU with tensor parallelism
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-70B \
  --task mmlu \
  --tensor-parallel-size 4

# Via HF Jobs
hf jobs uv run scripts/inspect_vllm_uv.py \
  --flavor a10g-small \
  --secrets HF_TOKEN=$HF_TOKEN \
  -- --model meta-llama/Llama-3.2-1B \
     --task mmlu
```

**Available inspect-ai tasks:** `mmlu`, `gsm8k`, `hellaswag`, `arc_challenge`, `truthfulqa`, `winogrande`, `humaneval`

### Option C: Python Helper Script

```bash
# Auto-detect hardware based on model size
uv run scripts/run_vllm_eval_job.py \
  --model meta-llama/Llama-3.2-1B \
  --task "leaderboard|mmlu|5" \
  --framework lighteval

# Explicit hardware selection
uv run scripts/run_vllm_eval_job.py \
  --model meta-llama/Llama-3.2-70B \
  --task mmlu \
  --framework inspect \
  --hardware a100-large \
  --tensor-parallel-size 4

# HF Transformers backend
uv run scripts/run_vllm_eval_job.py \
  --model microsoft/phi-2 \
  --task mmlu \
  --framework inspect \
  --backend hf
```

### Hardware Recommendations

| Model Size | Recommended Hardware |
|------------|---------------------|
| < 3B params | `t4-small` |
| 3B - 13B | `a10g-small` |
| 13B - 34B | `a10g-large` |
| 34B+ | `a100-large` |

## Common Patterns

**Update your own model:**
```bash
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/your-model" \
  --task-type "text-generation"
```

**Update someone else's model:**
```bash
# Step 1: Check for existing PRs first
uv run scripts/evaluation_manager.py get-prs \
  --repo-id "other-username/their-model"

# Step 2: If no open PRs, create one
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "other-username/their-model" \
  --create-pr
```

**Import fresh benchmarks:**
```bash
# Step 1: Check for existing PRs
uv run scripts/evaluation_manager.py get-prs \
  --repo-id "anthropic/claude-sonnet-4"

# Step 2: If no PRs, import from Artificial Analysis
AA_API_KEY=... uv run scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "anthropic/claude-sonnet-4" \
  --create-pr
```

## Model Name Matching

When extracting tables with multiple models, the script uses exact normalized token matching:

- Removes markdown formatting (bold `**`, links `[]()`)
- Normalizes names (lowercase, replace `-` and `_` with spaces)
- Compares token sets: `"OLMo-3-32B"` → `{"olmo", "3", "32b"}` matches `"**Olmo 3 32B**"`
- Only extracts if tokens match exactly (handles different word orders and separators)
- Fails if no exact match found (rather than guessing)

**Column-based tables** (benchmarks as rows, models as columns):
- Finds the column header matching the model name; extracts scores from that column only

**Transposed tables** (models as rows, benchmarks as columns):
- Finds the row in the first column matching the model name; extracts all scores from that row only
