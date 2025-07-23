#!/usr/bin/env python3
"""
Chunk Monkey Setup Verification
==============================

A simple script to verify that Chunk Monkey is properly set up and ready to use.
This script checks all essential components and provides clear feedback.

Usage:
    uv run python verify_setup.py

Author: Chunk Monkey Team
"""

import sys
import subprocess
from pathlib import Path

def check_emoji():
    """Check if terminal supports emojis."""
    try:
        print("🐒", end="")
        return True
    except:
        return False

def print_status(message, status, use_emoji=True):
    """Print status message with appropriate indicator."""
    if use_emoji:
        if status:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    else:
        if status:
            print(f"[OK] {message}")
        else:
            print(f"[FAIL] {message}")

def check_directory_structure():
    """Check if we're in the right directory with correct structure."""
    current_dir = Path.cwd()
    required_files = [
        "main.py",
        "pyproject.toml",
        "src/__init__.py",
        "src/processors/__init__.py",
        "src/generators/__init__.py",
        "src/utils/__init__.py",
        "src/config/__init__.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)

    return len(missing_files) == 0, missing_files

def check_uv_installation():
    """Check if uv is installed and working."""
    try:
        result = subprocess.run(["uv", "--version"],
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, None

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    is_compatible = version.major == 3 and version.minor >= 8
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    return is_compatible, version_str

def check_dependencies():
    """Check if key dependencies are available."""
    dependencies = {
        "docling": "Document processing",
        "rich": "Terminal formatting",
        "pathlib": "Path handling (built-in)",
        "json": "JSON processing (built-in)",
        "argparse": "CLI argument parsing (built-in)"
    }

    results = {}
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            results[dep] = (True, description)
        except ImportError:
            results[dep] = (False, description)

    return results

def check_core_modules():
    """Check if our core modules can be imported."""
    # Add src to path
    src_path = Path.cwd() / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))

    modules = {
        "processors.pdf_processor": "PDF processing",
        "generators.html_generator": "HTML generation",
        "utils.file_utils": "File utilities",
        "utils.text_utils": "Text processing",
        "config.settings": "Configuration"
    }

    results = {}
    for module, description in modules.items():
        try:
            # Try to import and access a key class/function
            mod = __import__(module, fromlist=[''])

            # Check for expected classes/functions
            if module == "processors.pdf_processor":
                getattr(mod, 'PDFProcessor')
            elif module == "generators.html_generator":
                getattr(mod, 'HTMLGenerator')
            elif module == "utils.file_utils":
                getattr(mod, 'FileManager')
            elif module == "utils.text_utils":
                getattr(mod, 'TextProcessor')
            elif module == "config.settings":
                getattr(mod, 'get_config')

            results[module] = (True, description)
        except (ImportError, AttributeError) as e:
            results[module] = (False, f"{description} - {str(e)}")

    return results

def main():
    """Run all verification checks."""
    use_emoji = check_emoji()

    if use_emoji:
        print("🐒 Chunk Monkey Setup Verification")
    else:
        print("Chunk Monkey Setup Verification")

    print("=" * 50)

    # Check 1: Directory structure
    print("\n1. Checking directory structure...")
    structure_ok, missing = check_directory_structure()
    print_status("Project structure", structure_ok, use_emoji)
    if not structure_ok:
        print("   Missing files:")
        for file in missing:
            print(f"     - {file}")
        print("   Make sure you're in the chunk_monkey directory")

    # Check 2: UV installation
    print("\n2. Checking uv installation...")
    uv_ok, uv_version = check_uv_installation()
    print_status(f"UV package manager", uv_ok, use_emoji)
    if uv_ok:
        print(f"   Version: {uv_version}")
    else:
        print("   Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh")

    # Check 3: Python version
    print("\n3. Checking Python version...")
    python_ok, python_version = check_python_version()
    print_status(f"Python {python_version}", python_ok, use_emoji)
    if not python_ok:
        print("   Requires Python 3.8 or higher")

    # Check 4: Dependencies
    print("\n4. Checking dependencies...")
    deps = check_dependencies()
    all_deps_ok = True
    for dep, (status, desc) in deps.items():
        print_status(f"{dep}: {desc}", status, use_emoji)
        if not status:
            all_deps_ok = False

    if not all_deps_ok:
        print("   Run: uv sync")

    # Check 5: Core modules
    print("\n5. Checking core modules...")
    modules = check_core_modules()
    all_modules_ok = True
    for module, (status, desc) in modules.items():
        print_status(f"{module}: {desc}", status, use_emoji)
        if not status:
            all_modules_ok = False

    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)

    all_checks = [
        ("Directory structure", structure_ok),
        ("UV installation", uv_ok),
        ("Python version", python_ok),
        ("Dependencies", all_deps_ok),
        ("Core modules", all_modules_ok)
    ]

    passed = sum(1 for _, status in all_checks if status)
    total = len(all_checks)

    print(f"Checks passed: {passed}/{total}")

    if passed == total:
        if use_emoji:
            print("\n🎉 Setup verification PASSED!")
        else:
            print("\n[SUCCESS] Setup verification PASSED!")
        print("Chunk Monkey is ready to use!")
        print("\nNext steps:")
        print("  uv run python main.py validate")
        print("  uv run python quick_test.py")
        print("  uv run python main.py process your_document.pdf")
        return True
    else:
        if use_emoji:
            print("\n❌ Setup verification FAILED!")
        else:
            print("\n[FAILED] Setup verification FAILED!")
        print(f"{total - passed} issue(s) need to be fixed.")
        print("\nTroubleshooting:")

        if not structure_ok:
            print("- Make sure you're in the chunk_monkey project directory")
        if not uv_ok:
            print("- Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        if not python_ok:
            print("- Upgrade Python to 3.8 or higher")
        if not all_deps_ok:
            print("- Install dependencies: uv sync")
        if not all_modules_ok:
            print("- Check for import errors and missing files")

        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
