#!/usr/bin/env python3
"""
Installation script to fix llama-cpp-python execfile issue
"""

import subprocess
import sys
import os

def install_llama_cpp():
    """Install llama-cpp-python with proper flags to avoid execfile error"""

    print("Attempting to install llama-cpp-python with fixes...")

    # Method 1: Try installing with --prefer-binary to use pre-compiled wheels
    try:
        print("Method 1: Installing with --prefer-binary flag...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "llama-cpp-python>=0.2.11",
            "--prefer-binary", "--no-build-isolation"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Successfully installed llama-cpp-python using pre-compiled wheel")
            return True
        else:
            print(f"Method 1 failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("Method 1 timed out")
    except Exception as e:
        print(f"Method 1 error: {e}")

    # Method 2: Try installing from conda-forge if conda is available
    try:
        print("Method 2: Trying conda installation...")
        # Check if conda is available
        conda_result = subprocess.run(["conda", "--version"], capture_output=True, text=True)
        if conda_result.returncode == 0:
            result = subprocess.run([
                "conda", "install", "-c", "conda-forge", "llama-cpp-python", "-y"
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("✅ Successfully installed llama-cpp-python via conda")
                return True
            else:
                print(f"Conda method failed: {result.stderr}")
    except Exception as e:
        print(f"Conda method error: {e}")

    # Method 3: Try installing with specific version and force upgrade (with convert tools)
    try:
        print("Method 3: Force installing specific version with convert tools...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall",
            "llama-cpp-python[convert]==0.2.11"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Successfully force-installed llama-cpp-python 0.2.11 with convert tools")
            return True
        else:
            print(f"Force install failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("Force install timed out")
    except Exception as e:
        print(f"Force install error: {e}")

    # Method 4: Try installing from source with Python 3 compatible setup
    try:
        print("Method 4: Installing from GitHub with Python 3 fixes...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "git+https://github.com/abetlen/llama-cpp-python.git"
        ], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            print("✅ Successfully installed llama-cpp-python from GitHub")
            return True
        else:
            print(f"GitHub install failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("GitHub install timed out")
    except Exception as e:
        print(f"GitHub install error: {e}")

    print("❌ All installation methods failed")
    return False

def test_import():
    """Test if llama_cpp can be imported successfully"""
    try:
        import llama_cpp
        print("✅ llama_cpp import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Fixing llama-cpp-python installation issue...")
    print("=" * 50)

    success = install_llama_cpp()

    if success:
        print("\nTesting import...")
        if test_import():
            print("\n🎉 Installation and import test successful!")
            sys.exit(0)
        else:
            print("\n⚠️ Installation succeeded but import failed")
            sys.exit(1)
    else:
        print("\n💥 All installation methods failed. You may need to:")
        print("1. Update pip: pip install --upgrade pip")
        print("2. Install build dependencies: pip install setuptools wheel")
        print("3. Try manual installation with: pip install llama-cpp-python --no-deps")
        print("4. Consider using a different LLM inference library")
        sys.exit(1)
