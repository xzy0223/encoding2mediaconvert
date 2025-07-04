#!/usr/bin/env python3
"""
Simple script to validate setup.py configuration
"""

import sys
import os
import ast

def validate_setup_syntax():
    """Validate setup.py syntax without importing it."""
    try:
        with open('setup.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, "Setup.py syntax is valid"
    except SyntaxError as e:
        return False, f"Syntax error in setup.py: {e}"
    except Exception as e:
        return False, f"Error reading setup.py: {e}"

def check_version_file():
    """Check if version file exists and is readable."""
    version_path = "src/e2mc_assistant/__version__.py"
    try:
        if os.path.exists(version_path):
            with open(version_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '__version__' in content:
                    # Extract version using regex
                    import re
                    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return True, f"Version: {match.group(1)}"
                    else:
                        return False, "Version format not recognized"
                else:
                    return False, "__version__ not found in version file"
        else:
            return False, "Version file not found"
    except Exception as e:
        return False, f"Error reading version file: {e}"

def check_readme():
    """Check if README.md exists and is readable."""
    try:
        if os.path.exists('README.md'):
            with open('README.md', 'r', encoding='utf-8') as f:
                content = f.read()
                return True, f"README length: {len(content)} characters"
        else:
            return False, "README.md not found"
    except Exception as e:
        return False, f"Error reading README.md: {e}"

def check_package_structure():
    """Check if package structure is correct."""
    required_dirs = [
        "src",
        "src/e2mc_assistant",
        "src/e2mc_assistant/converter",
        "src/e2mc_assistant/analyzer", 
        "src/e2mc_assistant/requester",
        "src/e2mc_assistant/workflow"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        return False, f"Missing directories: {missing_dirs}"
    else:
        return True, "Package structure is correct"

def check_critical_files():
    """Check if critical files exist."""
    critical_files = [
        "src/e2mc_assistant/__init__.py",
        "src/e2mc_assistant/__version__.py",
        "README.md",
        "LICENSE",
        "MANIFEST.in"
    ]
    
    results = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            results.append(f"✓ {file_path}")
        else:
            results.append(f"⚠ {file_path} missing")
    
    return True, "\n   ".join(results)

def main():
    """Main validation function."""
    print("🔍 Validating setup.py configuration...\n")
    
    tests = [
        ("Setup.py syntax", validate_setup_syntax),
        ("Version file", check_version_file),
        ("README file", check_readme),
        ("Package structure", check_package_structure),
        ("Critical files", check_critical_files),
    ]
    
    all_passed = True
    
    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"{i}. Testing {test_name}...")
        try:
            success, message = test_func()
            if success:
                print(f"   ✓ {message}")
            else:
                print(f"   ❌ {message}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error during {test_name}: {e}")
            all_passed = False
        print()
    
    if all_passed:
        print("✅ All validation tests passed!")
    else:
        print("⚠️  Some validation tests failed.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)