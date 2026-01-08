#!/usr/bin/env python3
"""
Environment Setup Test Script

This script verifies that all dependencies are installed correctly
and the project structure is set up properly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import cv2
        print(f"  ✓ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"  ✗ OpenCV: {e}")
        return False
    
    try:
        import numpy as np
        print(f"  ✓ NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"  ✗ NumPy: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"  ✓ Pillow (PIL) imported successfully")
    except ImportError as e:
        print(f"  ✗ Pillow: {e}")
        return False
    
    try:
        import matplotlib
        print(f"  ✓ Matplotlib version: {matplotlib.__version__}")
    except ImportError as e:
        print(f"  ✗ Matplotlib: {e}")
        return False
    
    return True

def test_config():
    """Test that config file loads correctly"""
    print("\nTesting configuration...")
    
    try:
        import config
        print(f"  ✓ Config loaded")
        print(f"  ✓ Project root: {config.PROJECT_ROOT}")
        print(f"  ✓ Test images dir: {config.TEST_IMAGES_DIR}")
        print(f"  ✓ Outputs dir: {config.OUTPUTS_DIR}")
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False

def test_directories():
    """Test that project directories exist"""
    print("\nTesting directory structure...")
    
    dirs_to_check = [
        "test_images",
        "outputs"
    ]
    
    all_exist = True
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ✗ {dir_name}/ missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADA Compliance System - Environment Setup Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Directory Structure", test_directories),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ ALL TESTS PASSED - Environment is ready!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Add test images to test_images/ directory")
        print("2. Set ANTHROPIC_API_KEY environment variable")
        print("3. Run: python3 video_processor.py (once created)")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Please fix issues above")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
