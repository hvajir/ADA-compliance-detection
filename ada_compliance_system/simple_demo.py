#!/usr/bin/env python3
"""
Simple Interactive Demo - Upload and Test Photos

This script makes it easy to test different images without
typing long commands.
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

def interactive_demo():
    """Run interactive demo with image selection."""
    print("=" * 80)
    print("  ADA COMPLIANCE DETECTION - INTERACTIVE DEMO")
    print("=" * 80)

    # List available images
    test_images = list_test_images()

    if not test_images:
        return

    # Let user choose
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

            # Run the demo
            run_demo(
                str(selected_image),
                use_real_yolo=True,  # ⚠️ Change to True for competition!
                use_real_claude=False
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

def quick_test_all():
    """Quickly test all images in test_images folder."""
    test_images = list(config.TEST_IMAGES_DIR.glob("*.jpg")) + \
                 list(config.TEST_IMAGES_DIR.glob("*.png"))

    if not test_images:
        print("❌ No test images found")
        return

    print(f"\n🚀 Testing all {len(test_images)} images...\n")

    for i, img in enumerate(test_images, 1):
        print(f"\n{'=' * 80}")
        print(f"  [{i}/{len(test_images)}] Processing: {img.name}")
        print('=' * 80)

        try:
            run_demo(
                str(img),
                use_real_yolo=False,
                use_real_claude=False
            )
        except Exception as e:
            print(f"❌ Error processing {img.name}: {e}")
            continue

    print("\n✓ All images processed! Check outputs/ folder.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # Test all images
        quick_test_all()
    else:
        # Interactive mode
        interactive_demo()
