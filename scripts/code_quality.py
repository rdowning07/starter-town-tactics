#!/usr/bin/env python3
"""
Code Quality Checker - Automated tool to maintain coding standards.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def fix_imports():
    """Fix import order using isort."""
    return run_command(
        ["isort", "--profile", "black", "--line-length", "120", "."],
        "Fixing import order",
    )


def format_code():
    """Format code using black."""
    return run_command(["black", "--line-length", "120", "."], "Formatting code")


def check_pylint():
    """Run pylint checks."""
    return run_command(
        [
            "python",
            "-m",
            "pylint",
            "game/",
            "tests/",
            "cli/",
            "--max-line-length=120",
            "--disable=C0114,C0115,C0116",
        ],
        "Running pylint checks",
    )


def check_flake8():
    """Run flake8 checks."""
    return run_command(
        ["flake8", "--max-line-length=120", "--extend-ignore=E203,W503", "."],
        "Running flake8 checks",
    )


def run_tests():
    """Run unit tests."""
    return run_command(["python", "-m", "pytest", "tests/", "-v"], "Running unit tests")


def main():
    """Main quality check workflow."""
    print("🚀 Starting Code Quality Check...")

    # Step 1: Fix imports
    if not fix_imports():
        print("❌ Import fixing failed")
        return False

    # Step 2: Format code
    if not format_code():
        print("❌ Code formatting failed")
        return False

    # Step 3: Run linting
    pylint_ok = check_pylint()
    flake8_ok = check_flake8()

    if not pylint_ok or not flake8_ok:
        print("❌ Linting failed")
        return False

    # Step 4: Run tests
    if not run_tests():
        print("❌ Tests failed")
        return False

    print("🎉 All quality checks passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
