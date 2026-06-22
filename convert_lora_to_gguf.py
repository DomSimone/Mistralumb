#!/usr/bin/env python3
"""
Convert LoRA adapters to GGUF format - Alternative to full model conversion

This script provides multiple methods to convert PEFT/LoRA adapters to GGUF format
instead of converting the entire fine-tuned model.
"""

import os
import torch
import json
import struct
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

class LoRAGGUFConverter:
    """Convert LoRA adapters to GGUF format"""

    GGUF_MAGIC = 0x46554747  # "GGUF" in little endian
    GGUF_VERSION = 3

    def __init__(self, base_model_path: str, lora_path: str):
        self.base_model_path = Path(base_model_path)
        self.lora_path = Path(lora_path)
        self.adapter_config = None
        self.adapter_weights = {}

    def load_lora_adapter(self):
        """Load LoRA adapter from PEFT format"""
        try:
            from peft import PeftModel
            print(f"Loading LoRA adapter from {self.lora_path}")

            # Load adapter config
            config_path = self.lora_path / "adapter_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.adapter_config = json.load(f)
                print(f"Loaded adapter config: {self.adapter_config}")
            else:
                print("Warning: No adapter_config.json found")

            # Load adapter weights
            adapter_model_path = self.lora_path / "adapter_model.bin"
            if adapter_model_path.exists():
                self.adapter_weights = torch.load(adapter_model_path, map_location='cpu')
                print(f"Loaded {len(self.adapter_weights)} adapter weight tensors")
            else:
                # Try safetensors format
                adapter_model_path = self.lora_path / "adapter_model.safetensors"
                if adapter_model_path.exists():
                    try:
                        from safetensors import safe_open
                        with safe_open(adapter_model_path, framework="pt", device="cpu") as f:
                            self.adapter_weights = {k: f.get_tensor(k) for k in f.keys()}
                        print(f"Loaded {len(self.adapter_weights)} adapter weight tensors (safetensors)")
                    except ImportError:
                        print("safetensors not available, install with: pip install safetensors")
                        return False
                else:
                    print("No adapter_model.bin or adapter_model.safetensors found")
                    return False

            return True

        except Exception as e:
            print(f"Error loading LoRA adapter: {e}")
            return False

    def convert_to_gguf_adapter(self, output_path: str) -> bool:
        """Convert LoRA adapter to GGUF format"""
        try:
            print(f"Converting LoRA adapter to GGUF format: {output_path}")

            # Prepare GGUF metadata
            metadata = self._prepare_gguf_metadata()

            # Write GGUF file
            with open(output_path, 'wb') as f:
                self._write_gguf_header(f, metadata)
                self._write_gguf_tensors(f, self.adapter_weights)

            print(f"Successfully converted adapter to GGUF: {output_path}")
            print(f"Original adapter size: {self._get_adapter_size()} MB")
            print(f"GGUF adapter size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

            return True

        except Exception as e:
            print(f"Error converting to GGUF: {e}")
            return False

    def _prepare_gguf_metadata(self) -> Dict[str, Any]:
        """Prepare GGUF metadata"""
        metadata = {
            "general.architecture": "llama",
            "general.name": "umbuzo-lora-adapter",
            "general.description": "LoRA adapter for Umbuzo African affairs chatbot",
            "adapter.type": "lora",
            "adapter.base_model": str(self.base_model_path),
        }

        if self.adapter_config:
            # Add LoRA configuration
            metadata.update({
                "adapter.lora.r": self.adapter_config.get("r", 16),
                "adapter.lora.alpha": self.adapter_config.get("lora_alpha", 32),
                "adapter.lora.dropout": self.adapter_config.get("lora_dropout", 0.05),
                "adapter.lora.target_modules": self.adapter_config.get("target_modules", []),
            })

        return metadata

    def _write_gguf_header(self, f, metadata: Dict[str, Any]):
        """Write GGUF header"""
        # Magic number
        f.write(struct.pack('<I', self.GGUF_MAGIC))

        # Version
        f.write(struct.pack('<I', self.GGUF_VERSION))

        # Tensor count
        tensor_count = len(self.adapter_weights)
        f.write(struct.pack('<Q', tensor_count))

        # Metadata count
        metadata_count = len(metadata)
        f.write(struct.pack('<Q', metadata_count))

        # Write metadata
        for key, value in metadata.items():
            self._write_gguf_value(f, key, value)

    def _write_gguf_value(self, f, key: str, value: Any):
        """Write a GGUF value"""
        # Key string
        key_bytes = key.encode('utf-8')
        f.write(struct.pack('<Q', len(key_bytes)))
        f.write(key_bytes)

        # Value type and data
        if isinstance(value, str):
            f.write(struct.pack('<I', 8))  # GGUF_TYPE_STRING
            value_bytes = value.encode('utf-8')
            f.write(struct.pack('<Q', len(value_bytes)))
            f.write(value_bytes)
        elif isinstance(value, int):
            f.write(struct.pack('<I', 2))  # GGUF_TYPE_UINT32
            f.write(struct.pack('<I', value))
        elif isinstance(value, float):
            f.write(struct.pack('<I', 3))  # GGUF_TYPE_FLOAT32
            f.write(struct.pack('<f', value))
        elif isinstance(value, list):
            f.write(struct.pack('<I', 9))  # GGUF_TYPE_ARRAY
            f.write(struct.pack('<Q', len(value)))
            if value and isinstance(value[0], str):
                f.write(struct.pack('<I', 8))  # GGUF_TYPE_STRING
                for item in value:
                    item_bytes = item.encode('utf-8')
                    f.write(struct.pack('<Q', len(item_bytes)))
                    f.write(item_bytes)
            else:
                # Default to int array
                f.write(struct.pack('<I', 2))  # GGUF_TYPE_UINT32
                for item in value:
                    f.write(struct.pack('<I', item))

    def _write_gguf_tensors(self, f, tensors: Dict[str, torch.Tensor]):
        """Write GGUF tensors"""
        for name, tensor in tensors.items():
            # Tensor name
            name_bytes = name.encode('utf-8')
            f.write(struct.pack('<Q', len(name_bytes)))
            f.write(name_bytes)

            # Tensor dimensions
            dims = list(tensor.shape)
            f.write(struct.pack('<I', len(dims)))
            for dim in reversed(dims):  # GGUF uses reverse dimension order
                f.write(struct.pack('<Q', dim))

            # Tensor type (GGUF_TYPE_F32 = 0)
            f.write(struct.pack('<I', 0))

            # Tensor offset (placeholder)
            offset_pos = f.tell()
            f.write(struct.pack('<Q', 0))

            # Tensor data
            data_start = f.tell()
            tensor_data = tensor.detach().cpu().numpy().astype(np.float32)
            f.write(tensor_data.tobytes())

            # Update offset
            data_end = f.tell()
            f.seek(offset_pos)
            f.write(struct.pack('<Q', data_start))
            f.seek(data_end)

    def _get_adapter_size(self) -> float:
        """Get total size of adapter weights in MB"""
        total_size = 0
        for tensor in self.adapter_weights.values():
            total_size += tensor.numel() * tensor.element_size()
        return total_size / (1024 * 1024)


def convert_with_llamacpp(base_model: str, lora_path: str, output_path: str) -> bool:
    """Convert using llama.cpp's lora export functionality"""
    try:
        import llama_cpp

        print("Method 2: Using llama.cpp LoRA export")
        print(f"Base model: {base_model}")
        print(f"LoRA path: {lora_path}")
        print(f"Output: {output_path}")

        # This would require llama.cpp to support LoRA export
        # For now, return False as this needs to be implemented
        print("Note: llama.cpp direct LoRA export not yet implemented")
        print("Use Method 1 (custom GGUF conversion) instead")
        return False

    except ImportError:
        print("llama_cpp not available")
        return False


def convert_with_transformers(base_model: str, lora_path: str, output_path: str) -> bool:
    """Convert using transformers library"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        import llama_cpp

        print("Method 3: Using transformers + PEFT")

        # Load base model
        print(f"Loading base model: {base_model}")
        model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16)

        # Load LoRA adapter
        print(f"Loading LoRA adapter: {lora_path}")
        model = PeftModel.from_pretrained(model, lora_path)

        # Merge adapter (optional - creates full fine-tuned model)
        print("Merging LoRA adapter...")
        merged_model = model.merge_and_unload()

        # Save merged model temporarily
        temp_dir = Path(output_path).parent / "temp_merged_model"
        temp_dir.mkdir(exist_ok=True)
        merged_model.save_pretrained(temp_dir)

        # Convert to GGUF using llama.cpp
        print("Converting merged model to GGUF...")
        import subprocess
        cmd = [
            "python", "-m", "llama_cpp.convert",
            str(temp_dir),
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully converted to GGUF: {output_path}")
            # Cleanup temp directory
            import shutil
            shutil.rmtree(temp_dir)
            return True
        else:
            print(f"Conversion failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error in transformers conversion: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert LoRA adapters to GGUF format")
    parser.add_argument("--base-model", required=True, help="Path to base model")
    parser.add_argument("--lora-path", required=True, help="Path to LoRA adapter")
    parser.add_argument("--output", required=True, help="Output GGUF file path")
    parser.add_argument("--method", choices=["custom", "llamacpp", "transformers"],
                       default="custom", help="Conversion method")

    args = parser.parse_args()

    print("LoRA to GGUF Adapter Converter")
    print("=" * 40)

    if args.method == "custom":
        converter = LoRAGGUFConverter(args.base_model, args.lora_path)
        if converter.load_lora_adapter():
            success = converter.convert_to_gguf_adapter(args.output)
        else:
            success = False

    elif args.method == "llamacpp":
        success = convert_with_llamacpp(args.base_model, args.lora_path, args.output)

    elif args.method == "transformers":
        success = convert_with_transformers(args.base_model, args.lora_path, args.output)

    if success:
        print("\n✅ Conversion completed successfully!")
        print(f"Output file: {args.output}")

        # Show file size comparison
        if os.path.exists(args.output):
            gguf_size = os.path.getsize(args.output) / (1024*1024)
            print(".2f")
    else:
        print("\n❌ Conversion failed!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
