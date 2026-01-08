#!/usr/bin/env python3
"""
Simple Interactive Demo - Updated with Analyzer Selection

Now lets you choose which analyzer to use!
"""

import os
from pathlib import Path
import config
from demo import run_demo


def list_test_images():
    """Show all available test images."""
    test_images = list(config.TEST_IMAGES_DIR.glob("*.jpg")) + \
                 list(config.TEST_IMAGES_DIR.glob("*.png"))
    
    if not test_images:
        print("❌ No test images found in test_images/ folder")
        print("\nTo add images:")
        print("1. Copy any JPG or PNG file to the test_images/ folder")
        print("2. Run this script again")
        return []
    
    print(f"\n📸 Found {len(test_images)} test image(s):\n")
    for i, img in enumerate(test_images, 1):
        size = os.path.getsize(img) / 1024  # KB
        print(f"  {i}. {img.name:30s} ({size:.1f} KB)")
    
    return test_images


def choose_analyzer():
    """Let user choose analyzer type."""
    print("\n" + "-" * 80)
    print("Choose analyzer type:")
    print("  1. Rule-Based (Computer Vision) - Recommended for competition")
    print("  2. Claude API (AI-powered)")
    print("  3. Hybrid (Both)")
    print("-" * 80)
    
    choice = input("Enter analyzer number (1-3, or press Enter for rule-based): ").strip()
    
    if choice == '2':
        return 'claude'
    elif choice == '3':
        return 'hybrid'
    else:
        return 'rule_based'  # Default


def interactive_demo():
    """Run interactive demo with image and analyzer selection."""
    print("=" * 80)
    print("  ADA COMPLIANCE DETECTION - INTERACTIVE DEMO")
    print("=" * 80)
    
    # Choose analyzer first
    analyzer_type = choose_analyzer()
    print(f"\n✓ Selected analyzer: {analyzer_type}")
    
    # List available images
    test_images = list_test_images()
    
    if not test_images:
        return
    
    # Let user choose image
    print("\n" + "-" * 80)
    choice = input("\nEnter image number to analyze (or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        print("Goodbye!")
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(test_images):
            selected_image = test_images[idx]
            print(f"\n✓ Selected: {selected_image.name}\n")
            
            # Run the demo with chosen analyzer
            run_demo(
                str(selected_image),
                use_real_yolo=True,  # ⚠️ Using real YOLO as configured
                analyzer_type=analyzer_type
            )
            
            print("\n" + "=" * 80)
            print("  DONE! Check the outputs/ folder for results")
            print("=" * 80)
            
            # Ask if they want to analyze another
            print("\n" + "-" * 80)
            again = input("Analyze another image? (y/n): ").strip().lower()
            if again == 'y':
                print("\n")
                interactive_demo()
        else:
            print("❌ Invalid number. Please try again.")
            interactive_demo()
    except ValueError:
        print("❌ Please enter a valid number.")
        interactive_demo()


def quick_test_all(analyzer_type='rule_based'):
    """Quickly test all images with chosen analyzer."""
    test_images = list(config.TEST_IMAGES_DIR.glob("*.jpg")) + \
                 list(config.TEST_IMAGES_DIR.glob("*.png"))
    
    if not test_images:
        print("❌ No test images found")
        return
    
    print(f"\n🚀 Testing all {len(test_images)} images with {analyzer_type} analyzer...\n")
    
    for i, img in enumerate(test_images, 1):
        print(f"\n{'=' * 80}")
        print(f"  [{i}/{len(test_images)}] Processing: {img.name}")
        print('=' * 80)
        
        try:
            run_demo(
                str(img),
                use_real_yolo=True,
                analyzer_type=analyzer_type
            )
        except Exception as e:
            print(f"❌ Error processing {img.name}: {e}")
            continue
    
    print("\n✓ All images processed! Check outputs/ folder.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # Test all with optional analyzer choice
            analyzer = sys.argv[2] if len(sys.argv) > 2 else 'rule_based'
            quick_test_all(analyzer)
        else:
            print("Usage:")
            print("  python3 simple_demo.py              # Interactive mode")
            print("  python3 simple_demo.py --all        # Test all images")
            print("  python3 simple_demo.py --all claude # Test all with Claude")
    else:
        # Interactive mode
        interactive_demo()
