# GGUF Adapter Conversion Alternatives

This guide provides alternative methods to convert LoRA adapters to GGUF format instead of converting entire fine-tuned models.

## Current Problem

The current approach:
```bash
python -m llama_cpp.convert ./umbuzo_fine_tuned ./umbuzo_fine_tuned.gguf
```

This converts the **entire fine-tuned model** (~7GB) to GGUF format, which is:
- Large file size
- Redundant (base model weights are included)
- Inefficient for distribution

## Better Alternatives

### Method 1: Use LoRA Adapters Directly (Recommended)

Instead of converting to GGUF, use llama.cpp's native LoRA support:

```python
import llama_cpp

# Load base model with LoRA adapter
model = llama_cpp.Llama(
    model_path="path/to/base/model.gguf",
    lora_path="./umbuzo_fine_tuned",  # LoRA adapter directory
    n_ctx=4096
)

# Use for inference
response = model("Question about African economics:", max_tokens=200)
```

**Advantages:**
- ✅ Keeps base model and adapter separate
- ✅ Much smaller adapter size (~50-200MB vs 7GB)
- ✅ Can use different adapters with same base model
- ✅ No conversion needed

### Method 2: Export LoRA Weights Separately

Extract just the LoRA adapter weights:

```bash
python lora_adapter_alternatives.py \
    --method export \
    --lora-path ./umbuzo_fine_tuned \
    --output ./umbuzo_adapter_export
```

This creates:
- `lora_weights.pt` - Adapter weights only (~50MB)
- `lora_config.json` - Adapter configuration

### Method 3: Merge then Convert (Smaller GGUF)

Merge LoRA into base model first, then convert:

```bash
python lora_adapter_alternatives.py \
    --method merge \
    --base-model mistralai/Mistral-7B-v0.1 \
    --lora-path ./umbuzo_fine_tuned \
    --output ./umbuzo_fine_tuned.gguf
```

**Result:** Smaller GGUF file since merging is done efficiently.

### Method 4: Quantized Conversion

Create a quantized GGUF directly:

```bash
python lora_adapter_alternatives.py \
    --method quantize \
    --base-model mistralai/Mistral-7B-v0.1 \
    --lora-path ./umbuzo_fine_tuned \
    --output ./umbuzo_fine_tuned_q4.gguf
```

**Result:** Even smaller quantized GGUF (~2-4GB vs 7GB).

### Method 5: Custom GGUF Adapter Format

Convert LoRA to a custom GGUF adapter format:

```bash
python convert_lora_to_gguf.py \
    --base-model mistralai/Mistral-7B-v0.1 \
    --lora-path ./umbuzo_fine_tuned \
    --output ./umbuzo_adapter.gguf \
    --method custom
```

## File Size Comparison

| Method | File Size | Description |
|--------|-----------|-------------|
| Full Model GGUF | ~7GB | Current approach |
| Merged GGUF | ~7GB | Same as above |
| Quantized GGUF | ~2-4GB | Smaller, same quality |
| LoRA Adapter Only | ~50-200MB | Much smaller |
| Native LoRA | ~0MB extra | Uses existing base model |

## Usage Examples

### 1. Native LoRA Inference

```python
# Create inference script
python lora_adapter_alternatives.py \
    --create-inference \
    --base-model ./mistral_base.gguf \
    --lora-path ./umbuzo_fine_tuned \
    --output inference_script.py

# Run inference
python inference_script.py
```

### 2. Export for Distribution

```python
# Export adapter for sharing
python lora_adapter_alternatives.py \
    --method export \
    --lora-path ./umbuzo_fine_tuned \
    --output ./umbuzo_adapter_v1

# Share only the adapter directory (~50MB)
# Others can use it with their base Mistral model
```

### 3. Convert to GGUF Adapter

```python
# Create GGUF adapter file
python convert_lora_to_gguf.py \
    --base-model mistralai/Mistral-7B-v0.1 \
    --lora-path ./umbuzo_fine_tuned \
    --output ./umbuzo_adapter.gguf
```

## Integration with Umbuzo Chatbot

Update your `umbuzo_chatbot.py` to use LoRA adapters:

```python
import llama_cpp
from pathlib import Path

class UmbuzoChatbot:
    def __init__(self):
        # Use LoRA adapter instead of converted model
        model_path = "./mistral_base.gguf"  # Base model
        lora_path = "./umbuzo_fine_tuned"   # LoRA adapter

        self.model = llama_cpp.Llama(
            model_path=model_path,
            lora_path=lora_path,
            n_ctx=4096,
            n_threads=4
        )
```

## Benefits of LoRA Adapters

1. **Smaller Size:** 50-200MB instead of 7GB
2. **Flexibility:** Use different adapters with same base model
3. **Faster Distribution:** Download only adapters for updates
4. **Memory Efficient:** Load base model once, swap adapters
5. **Version Control:** Track adapter changes separately

## Requirements

Install additional dependencies:

```bash
pip install llama-cpp-python[convert] transformers peft
# Optional: pip install safetensors
```

## Troubleshooting

### "No module named 'llama_cpp.convert'"
```bash
pip install 'llama-cpp-python[convert]'
```

### CUDA/GPU Issues
```bash
# For CPU-only conversion
export CUDA_VISIBLE_DEVICES=""
python convert_lora_to_gguf.py --method custom ...
```

### Large Memory Usage
- Use quantized base models
- Process adapters in smaller batches
- Use CPU conversion for large models

## Performance Comparison

| Method | Load Time | Inference Speed | Memory Usage | File Size |
|--------|-----------|-----------------|--------------|-----------|
| Full GGUF | Fast | Fastest | High | Large |
| LoRA Native | Medium | Fast | Medium | Small |
| Quantized GGUF | Fast | Medium | Low | Medium |

## Recommended Approach

For production use, **Method 1 (Native LoRA)** is recommended:

1. Keep the base Mistral model in GGUF format
2. Store/distribute only the LoRA adapter (~50MB)
3. Load both at runtime for inference
4. Update only the adapter for model improvements

This approach saves storage, bandwidth, and provides maximum flexibility.
