#!/usr/bin/env python3
"""
Alternative methods to convert LoRA adapters to GGUF format

This script provides practical alternatives to the current full-model conversion approach.
"""

import os
import torch
import json
from pathlib import Path
import subprocess
import sys

def method_1_export_lora_weights(lora_path: str, output_dir: str):
    """
    Method 1: Export LoRA weights in a format ready for GGUF conversion

    This extracts just the LoRA adapters without the base model weights.
    """
    print("Method 1: Export LoRA weights separately")
    print("-" * 40)

    lora_path = Path(lora_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Check if LoRA path exists
    if not lora_path.exists():
        print(f"❌ LoRA path does not exist: {lora_path}")
        print("Make sure to run training first: python umbuzo_fine_tune.py")
        return False

    if not lora_path.is_dir():
        print(f"❌ LoRA path is not a directory: {lora_path}")
        return False

    # List files in the directory for debugging
    files = list(lora_path.iterdir())
    print(f"Files in LoRA directory ({len(files)} files):")
    for f in sorted(files)[:10]:  # Show first 10 files
        print(f"  {f.name}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")

    try:
        # Load adapter config - try multiple possible locations/patterns
        config_path = None
        config_candidates = [
            lora_path / "adapter_config.json",
            lora_path / "config.json",
            lora_path / "peft_config.json"
        ]

        for candidate in config_candidates:
            if candidate.exists():
                config_path = candidate
                break

        if not config_path:
            print("❌ No adapter config found. Looked for:")
            for candidate in config_candidates:
                print(f"   - {candidate}")
            print("\nThis suggests the LoRA training hasn't completed successfully.")
            print("Make sure to run: python umbuzo_fine_tune.py")
            return False

        print(f"Found config file: {config_path}")
        with open(config_path, 'r') as f:
            config = json.load(f)

        print(f"LoRA config: r={config.get('r')}, alpha={config.get('lora_alpha')}")

        # Load adapter weights - try multiple patterns
        adapter_path = None
        weight_candidates = [
            lora_path / "adapter_model.bin",
            lora_path / "adapter_model.safetensors",
            lora_path / "pytorch_model.bin",
            lora_path / "model.bin"
        ]

        for candidate in weight_candidates:
            if candidate.exists():
                adapter_path = candidate
                break

        if not adapter_path:
            print("❌ No adapter weights found. Looked for:")
            for candidate in weight_candidates:
                print(f"   - {candidate}")
            print("\nAvailable files:")
            for f in files:
                if f.suffix in ['.bin', '.safetensors']:
                    print(f"   - {f.name}")
            return False

        print(f"Loading adapter weights from: {adapter_path}")

        if adapter_path.suffix == '.bin':
            weights = torch.load(adapter_path, map_location='cpu')
        elif adapter_path.suffix == '.safetensors':
            # Handle safetensors
            try:
                from safetensors import safe_open
                weights = {}
                with safe_open(adapter_path, framework="pt", device="cpu") as f:
                    for key in f.keys():
                        weights[key] = f.get_tensor(key)
            except ImportError:
                print("❌ safetensors not available. Install with: pip install safetensors")
                return False
        else:
            print(f"❌ Unsupported weight file format: {adapter_path.suffix}")
            return False

        print(f"Found {len(weights)} adapter tensors")

        # Filter to only LoRA parameters (optional - helps reduce size)
        lora_weights = {}
        for key, tensor in weights.items():
            if any(lora_keyword in key.lower() for lora_keyword in ['lora', 'adapter']):
                lora_weights[key] = tensor

        if lora_weights:
            print(f"Filtered to {len(lora_weights)} LoRA-specific parameters")
            weights = lora_weights
        else:
            print("No LoRA-specific parameters found, using all weights")

        # Save weights in a format suitable for conversion
        output_weights = output_dir / "lora_weights.pt"
        torch.save(weights, output_weights)

        # Save config
        output_config = output_dir / "lora_config.json"
        with open(output_config, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Exported LoRA weights to: {output_dir}")
        print(f"   Weights: {output_weights}")
        print(f"   Config: {output_config}")

        # Calculate size
        total_params = sum(w.numel() for w in weights.values())
        size_mb = sum(w.numel() * w.element_size() for w in weights.values()) / (1024*1024)
        print(f"   Size: {size_mb:.2f} MB ({total_params:,} parameters)")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def method_2_use_llama_cpp_lora(base_model: str, lora_path: str, output_path: str):
    """
    Method 2: Use llama.cpp's built-in LoRA support

    Instead of converting to GGUF, use llama.cpp's native LoRA loading.
    """
    print("\nMethod 2: Use llama.cpp native LoRA support")
    print("-" * 40)

    try:
        import llama_cpp

        print("Loading base model with LoRA adapter...")
        print(f"Base model: {base_model}")
        print(f"LoRA path: {lora_path}")

        # Create model with LoRA
        model = llama_cpp.Llama(
            model_path=base_model,
            lora_path=lora_path,
            n_ctx=2048,
            verbose=False
        )

        print("✅ Successfully loaded model with LoRA adapter")
        print("This approach keeps the base model and adapter separate,")
        print("avoiding the need to convert to GGUF altogether.")

        # Test inference
        print("\nTesting inference with LoRA adapter...")
        output = model("Question: What are the main challenges facing African economies? Answer:", max_tokens=100)
        print(f"Response: {output['choices'][0]['text'][:200]}...")

        return True

    except ImportError:
        print("❌ llama_cpp not available")
        return False
    except Exception as e:
        print(f"❌ Error loading with LoRA: {e}")
        return False


def method_3_merge_then_convert(base_model: str, lora_path: str, output_path: str):
    """
    Method 3: Merge LoRA into base model, then convert to GGUF

    This creates a full fine-tuned model but is more memory efficient than the current approach.
    """
    print("\nMethod 3: Merge LoRA then convert to GGUF")
    print("-" * 40)

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        print(f"Loading base model: {base_model}")
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map="auto"
        )

        print(f"Loading LoRA adapter: {lora_path}")
        model = PeftModel.from_pretrained(model, lora_path)

        print("Merging LoRA weights into base model...")
        merged_model = model.merge_and_unload()

        # Save merged model to temporary directory
        temp_dir = Path(output_path).parent / "temp_merged"
        temp_dir.mkdir(exist_ok=True)

        print(f"Saving merged model to: {temp_dir}")
        merged_model.save_pretrained(temp_dir)

        # Save tokenizer if needed
        try:
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            tokenizer.save_pretrained(temp_dir)
        except:
            print("Warning: Could not save tokenizer")

        # Convert to GGUF using llama.cpp
        print("Converting to GGUF format...")
        cmd = [
            sys.executable, "-m", "llama_cpp.convert",
            str(temp_dir),
            output_path
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            print("✅ Successfully converted merged model to GGUF")

            # Show sizes
            if os.path.exists(output_path):
                gguf_size = os.path.getsize(output_path) / (1024*1024)
                print(".2f")

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

            return True
        else:
            print(f"❌ Conversion failed: {result.stderr}")
            return False

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install transformers peft")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def method_4_quantized_conversion(base_model: str, lora_path: str, output_path: str):
    """
    Method 4: Use quantized conversion with automatic GGUF quantization
    """
    print("\nMethod 4: Quantized GGUF conversion")
    print("-" * 40)

    try:
        # First merge the model
        from transformers import AutoModelForCausalLM
        from peft import PeftModel

        print("Loading and merging model...")
        model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16)
        model = PeftModel.from_pretrained(model, lora_path)
        merged_model = model.merge_and_unload()

        # Save temporarily
        temp_dir = Path(output_path).parent / "temp_quantized"
        temp_dir.mkdir(exist_ok=True)
        merged_model.save_pretrained(temp_dir)

        # Use llama.cpp convert with quantization options
        print("Converting with quantization...")
        cmd = [
            sys.executable, "-m", "llama_cpp.convert",
            "--quantize", "Q4_K_M",  # Use Q4_K_M quantization
            str(temp_dir),
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Successfully created quantized GGUF")

            if os.path.exists(output_path):
                size = os.path.getsize(output_path) / (1024*1024)
                print(".2f")

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

            return True
        else:
            print(f"❌ Quantization failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_inference_script(base_model_path: str, adapter_path: str, output_script: str):
    """
    Create a Python script for inference using LoRA adapters
    """
    script_content = f'''#!/usr/bin/env python3
"""
Inference script using LoRA adapters with llama.cpp

This script demonstrates how to use LoRA adapters without converting to GGUF.
"""

import llama_cpp
import os

def main():
    # Base model path
    base_model = r"{base_model_path}"

    # LoRA adapter path
    lora_path = r"{adapter_path}"

    print("Loading model with LoRA adapter...")
    print(f"Base model: {{base_model}}")
    print(f"LoRA adapter: {{lora_path}}")

    # Create model with LoRA
    model = llama_cpp.Llama(
        model_path=base_model,
        lora_path=lora_path,
        n_ctx=4096,
        n_threads=4,
        verbose=False
    )

    print("Model loaded successfully!")
    print("\\nExample inference:")

    prompt = "Question about African economics: What are the main challenges facing African economies today?"
    print(f"Prompt: {{prompt}}")

    output = model(prompt, max_tokens=200, temperature=0.7)
    response = output["choices"][0]["text"]

    print(f"Response: {{response}}")

if __name__ == "__main__":
    main()
'''

    with open(output_script, 'w') as f:
        f.write(script_content)

    print(f"✅ Created inference script: {output_script}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Alternative LoRA to GGUF conversion methods")
    parser.add_argument("--base-model", help="Path to base model (required for native, merge, quantize methods)")
    parser.add_argument("--lora-path", help="Path to LoRA adapter directory (required)")
    parser.add_argument("--output", help="Output path for GGUF file or export directory")
    parser.add_argument("--method", choices=["export", "native", "merge", "quantize", "inference"],
                       default="export", help="Conversion method")
    parser.add_argument("--create-inference", action="store_true",
                       help="Create inference script instead of converting")

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Validate required arguments based on method
    if not args.lora_path:
        print("❌ --lora-path is required for all methods")
        parser.print_help()
        return

    if args.method in ["native", "merge", "quantize"] and not args.base_model:
        print(f"❌ --base-model is required for {args.method} method")
        return

    print("LoRA Adapter Conversion Alternatives")
    print("=" * 50)
    print(f"LoRA path: {args.lora_path}")
    if args.base_model:
        print(f"Base model: {args.base_model}")
    print(f"Method: {args.method}")
    print()

    if args.create_inference:
        if not args.base_model:
            print("❌ --base-model required for inference script creation")
            return
        script_path = args.output or "lora_inference.py"
        create_inference_script(args.base_model, args.lora_path, script_path)
        return

    if args.method == "export":
        output_dir = args.output or "./lora_export"
        method_1_export_lora_weights(args.lora_path, output_dir)

    elif args.method == "native":
        method_2_use_llama_cpp_lora(args.base_model, args.lora_path, args.output or "test_lora.gguf")

    elif args.method == "merge":
        if not args.output:
            print("❌ --output required for merge method")
            return
        method_3_merge_then_convert(args.base_model, args.lora_path, args.output)

    elif args.method == "quantize":
        if not args.output:
            print("❌ --output required for quantize method")
            return
        method_4_quantized_conversion(args.base_model, args.lora_path, args.output)

    elif args.method == "inference":
        if not args.base_model:
            print("❌ --base-model required for inference method")
            return
        script_path = args.output or "lora_inference.py"
        create_inference_script(args.base_model, args.lora_path, script_path)

    print("\\n" + "=" * 50)
    print("Alternative Methods Summary:")
    print("1. export   - Extract LoRA weights separately (smallest)")
    print("2. native   - Use llama.cpp's built-in LoRA support (recommended)")
    print("3. merge    - Merge then convert to GGUF")
    print("4. quantize - Merge and quantize to GGUF")
    print("5. inference- Create inference script using LoRA")


if __name__ == "__main__":
    main()
