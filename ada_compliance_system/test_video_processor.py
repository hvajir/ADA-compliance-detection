#!/usr/bin/env python3
"""
Quick test of video processor with our test image
"""

from video_processor import process_image_file
import config

# Test loading an image
test_image_path = config.TEST_IMAGES_DIR / "test_store_entrance.jpg"

if test_image_path.exists():
    print("Testing image processing...\n")
    image = process_image_file(str(test_image_path))
    
    print(f"\n✓ Image details:")
    print(f"  Shape: {image.shape}")
    print(f"  Type: {image.dtype}")
    print(f"  Size: {image.shape[1]}x{image.shape[0]} pixels")
    print(f"  Channels: {image.shape[2]} (BGR - Blue, Green, Red)")
    
    print("\n✓ Video processor is working correctly!")
else:
    print(f"Test image not found at: {test_image_path}")
