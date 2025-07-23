#!/usr/bin/env python3
"""
Chunk Monkey - Simple Test Runner
=================================

A standalone test runner that doesn't rely on complex imports.
This script tests the new implementation by running commands directly.

Usage:
    uv run python run_tests.py

Author: Chunk Monkey Team
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description, timeout=30):
    """Run a command and return success status."""
    print(f"Testing: {description}")
    print(f"Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd()
        )

        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return True
        else:
            print("❌ FAILED")
            print(f"   Error: {result.stderr.strip()[:200]}...")
            return False

    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        print()

def test_basic_imports():
    """Test basic Python imports."""
    print("="*60)
    print("Testing Basic Imports")
    print("="*60)

    # Test core Python modules
    commands = [
        ("python -c \"import sys; print('Python version:', sys.version)\"", "Python installation"),
        ("python -c \"import json; print('JSON module working')\"", "JSON module"),
        ("python -c \"import pathlib; print('Pathlib module working')\"", "Pathlib module"),
        ("python -c \"import argparse; print('Argparse module working')\"", "Argparse module"),
    ]

    passed = 0
    for cmd, desc in commands:
        if run_command(f"uv run {cmd}", desc):
            passed += 1

    return passed, len(commands)

def test_dependencies():
    """Test key dependencies."""
    print("="*60)
    print("Testing Dependencies")
    print("="*60)

    commands = [
        ("python -c \"import docling; print('Docling version:', getattr(docling, '__version__', 'unknown'))\"", "Docling library"),
        ("python -c \"import rich; print('Rich version:', rich.__version__)\"", "Rich library"),
        ("python -c \"from pathlib import Path; print('Path working')\"", "Path utilities"),
    ]

    passed = 0
    for cmd, desc in commands:
        if run_command(f"uv run {cmd}", desc):
            passed += 1

    return passed, len(commands)

def test_project_structure():
    """Test project file structure."""
    print("="*60)
    print("Testing Project Structure")
    print("="*60)

    required_files = [
        "main.py",
        "pyproject.toml",
        "src/__init__.py",
        "src/config/settings.py",
        "src/processors/pdf_processor.py",
        "src/generators/html_generator.py",
        "src/utils/file_utils.py",
        "src/utils/text_utils.py"
    ]

    passed = 0
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
            passed += 1
        else:
            print(f"❌ {file_path} missing")

    print()
    return passed, len(required_files)

def test_module_imports():
    """Test our custom module imports."""
    print("="*60)
    print("Testing Module Imports")
    print("="*60)

    # Add src to Python path and test imports
    commands = [
        ("python -c \"import sys; sys.path.insert(0, 'src'); from config.settings import get_config; print('Config module working')\"", "Configuration module"),
        ("python -c \"import sys; sys.path.insert(0, 'src'); from utils.file_utils import FileManager; print('FileManager working')\"", "File utilities"),
        ("python -c \"import sys; sys.path.insert(0, 'src'); from utils.text_utils import TextProcessor; print('TextProcessor working')\"", "Text utilities"),
        ("python -c \"import sys; sys.path.insert(0, 'src'); from processors.pdf_processor import PDFProcessor; print('PDFProcessor working')\"", "PDF processor"),
        ("python -c \"import sys; sys.path.insert(0, 'src'); from generators.html_generator import HTMLGenerator; print('HTMLGenerator working')\"", "HTML generator"),
    ]

    passed = 0
    for cmd, desc in commands:
        if run_command(f"uv run {cmd}", desc):
            passed += 1

    return passed, len(commands)

def test_cli_commands():
    """Test CLI commands."""
    print("="*60)
    print("Testing CLI Commands")
    print("="*60)

    commands = [
        ("python main.py --help", "CLI help system"),
        ("python main.py validate", "Installation validation"),
    ]

    passed = 0
    for cmd, desc in commands:
        if run_command(f"uv run {cmd}", desc):
            passed += 1

    return passed, len(commands)

def test_basic_functionality():
    """Test basic functionality without PDF files."""
    print("="*60)
    print("Testing Basic Functionality")
    print("="*60)

    # Test configuration loading
    test_config = """
import sys
sys.path.insert(0, 'src')
from config.settings import get_config, validate_config
config = get_config()
print('Config loaded with keys:', list(config.keys())[:3])
valid = validate_config()
print('Config valid:', valid)
"""

    # Test file utilities
    test_file_utils = """
import sys
sys.path.insert(0, 'src')
from utils.file_utils import FileManager
import tempfile
manager = FileManager()
with tempfile.TemporaryDirectory() as temp_dir:
    test_dir = manager.ensure_directory(temp_dir + '/test')
    print('Directory created:', test_dir.exists())
"""

    # Test text utilities
    test_text_utils = """
import sys
sys.path.insert(0, 'src')
from utils.text_utils import TextProcessor
processor = TextProcessor()
clean = processor.clean_text('  messy   text  ')
print('Text cleaned:', repr(clean))
"""

    commands = [
        (f"python -c \"{test_config.replace(chr(10), '; ')}\"", "Configuration system"),
        (f"python -c \"{test_file_utils.replace(chr(10), '; ')}\"", "File utilities"),
        (f"python -c \"{test_text_utils.replace(chr(10), '; ')}\"", "Text utilities"),
    ]

    passed = 0
    for cmd, desc in commands:
        if run_command(f"uv run {cmd}", desc, timeout=60):
            passed += 1

    return passed, len(commands)

def main():
    """Run all tests."""
    print("🐒 Chunk Monkey - Simple Test Runner")
    print("="*60)
    print("Testing the implementation with direct commands...")
    print()

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found!")
        print("Please run this script from the chunk_monkey project directory.")
        sys.exit(1)

    # Run test suites
    test_suites = [
        ("Basic Imports", test_basic_imports),
        ("Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("Module Imports", test_module_imports),
        ("CLI Commands", test_cli_commands),
        ("Basic Functionality", test_basic_functionality),
    ]

    total_passed = 0
    total_tests = 0
    suite_results = []

    for suite_name, test_func in test_suites:
        try:
            passed, total = test_func()
            total_passed += passed
            total_tests += total
            suite_results.append((suite_name, passed, total))
        except Exception as e:
            print(f"❌ Test suite '{suite_name}' crashed: {e}")
            suite_results.append((suite_name, 0, 1))
            total_tests += 1

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)

    for suite_name, passed, total in suite_results:
        success_rate = (passed / total * 100) if total > 0 else 0
        status = "✅" if passed == total else "❌" if passed == 0 else "⚠️"
        print(f"{status} {suite_name}: {passed}/{total} ({success_rate:.0f}%)")

    overall_success = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\nOverall: {total_passed}/{total_tests} tests passed ({overall_success:.1f}%)")

    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)

    if total_passed == total_tests:
        print("🎉 All tests passed! The implementation is working correctly.")
        print("\nNext steps:")
        print("  1. Try processing a PDF: uv run python main.py process your_file.pdf")
        print("  2. Run examples: uv run python examples/basic_usage.py")
        print("  3. Check the documentation in README.md")
    elif overall_success >= 80:
        print("✅ Most tests passed! The implementation is mostly working.")
        print("\nYou can likely proceed with basic usage:")
        print("  uv run python main.py validate")
    else:
        print("❌ Many tests failed. Please fix the issues:")
        print("\n1. Make sure you're in the chunk_monkey directory")
        print("2. Install dependencies: uv sync")
        print("3. Check that all files are present")
        print("4. Verify Python version is 3.8+")

    if overall_success < 100:
        failed_suites = [name for name, passed, total in suite_results if passed < total]
        if failed_suites:
            print(f"\nFailed test suites: {', '.join(failed_suites)}")

    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
