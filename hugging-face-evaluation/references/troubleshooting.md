# Troubleshooting

**"No evaluation tables found in README"**
→ Check if README contains markdown tables with numeric scores.

**"Could not find model 'X' in transposed table"**
→ The script displays available models. Use `--model-name-override` with the exact name from the list.
Example: `--model-name-override "**Olmo 3-32B**"`

**"AA_API_KEY not set"**
→ Set environment variable or add to `.env` file.

**"Token does not have write access"**
→ Ensure `HF_TOKEN` has write permissions for the repository.

**"Model not found in Artificial Analysis"**
→ Verify `creator-slug` and `model-name` match API values.

**"Payment required for hardware"**
→ Add a payment method to your Hugging Face account for non-CPU hardware.

**"vLLM out of memory" / CUDA OOM**
→ Use a larger hardware flavor, reduce `--gpu-memory-utilization`, or use `--tensor-parallel-size` for multi-GPU.

**"Model architecture not supported by vLLM"**
→ Use `--backend hf` (inspect-ai) or `--backend accelerate` (lighteval) for HuggingFace Transformers.

**"Trust remote code required"**
→ Add `--trust-remote-code` flag for models with custom code (e.g., Phi-2, Qwen).

**"Chat template not found"**
→ Only use `--use-chat-template` for instruction-tuned models that include a chat template.
