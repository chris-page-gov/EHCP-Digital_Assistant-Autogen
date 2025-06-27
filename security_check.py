#!/usr/bin/env python3
"""
Security check script for MAD - Multi-Agentic Document Generator.

This script runs various security checks on the codebase:
- Dependency vulnerability scanning with pip-audit
- Security vulnerability checks with safety
- Code security analysis with bandit
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report the results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error running {description}: {e}")
        return 1

def main():
    """Run all security checks."""
    print("MAD Security Check Suite")
    print("=" * 60)
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("WARNING: Not running in a virtual environment!")
        print("It's recommended to run this in the project's virtual environment.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    failures = []
    
    # 1. Run pip-audit
    print("\n1. Checking for known vulnerabilities in dependencies...")
    if run_command("pip-audit", "pip-audit vulnerability scan") != 0:
        failures.append("pip-audit")
    
    # 2. Run safety check
    print("\n2. Running safety vulnerability check...")
    if run_command("safety check", "safety vulnerability scan") != 0:
        failures.append("safety")
    
    # 3. Run bandit on Python files
    print("\n3. Running bandit security linter...")
    python_files = ["main.py", "writer.py", "validator.py", "utils.py", "config.py"]
    existing_files = [f for f in python_files if Path(f).exists()]
    
    if existing_files:
        files_str = " ".join(existing_files)
        if run_command(f"bandit -r {files_str}", "bandit security analysis") != 0:
            failures.append("bandit")
    else:
        print("No Python files found to analyze!")
        failures.append("bandit")
    
    # Summary
    print("\n" + "="*60)
    print("SECURITY CHECK SUMMARY")
    print("="*60)
    
    if not failures:
        print("✅ All security checks passed!")
        return 0
    else:
        print("❌ The following checks failed:")
        for check in failures:
            print(f"  - {check}")
        print("\nPlease review the output above and address any security issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())