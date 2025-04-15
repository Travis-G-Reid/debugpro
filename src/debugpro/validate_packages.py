""" This is run with hardcoded values in packages_to_check. This is intended to provide a simple way to gather rapid feedback about package availability.
"""
import importlib
import sys

def check_package_structure():
    """Verify all expected modules are importable"""
    packages_to_check = [
        "your_package",
        "your_package.module1",
        "your_package.module2",
    ]
    
    results = []
    for package in packages_to_check:
        try:
            importlib.import_module(package)
            results.append(f"✓ {package}: Successfully imported")
        except ImportError as e:
            results.append(f"✗ {package}: Failed - {e}")
            
    return results

if __name__ == "__main__":
    results = check_package_structure()
    for result in results:
        print(result)
    
    # Exit with error code if any imports failed
    if any(result.startswith("✗") for result in results):
        sys.exit(1)
