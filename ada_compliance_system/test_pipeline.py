#!/usr/bin/env python3
"""
Integrated Test: Video Processing + Object Detection

This script demonstrates the complete pipeline so far:
1. Load an image (or extract frames from video)
2. Detect objects in the image
3. Filter for ADA-relevant objects
4. Visualize the results
"""

import config
from video_processor import process_image_file
from object_detector import ObjectDetector, visualize_detections

def test_full_pipeline():
    """Test the complete detection pipeline"""
    
    print("=" * 70)
    print("INTEGRATED TEST: Image Processing → Object Detection")
    print("=" * 70)
    
    # Step 1: Load image
    print("\n[Step 1] Loading test image...")
    test_image = config.TEST_IMAGES_DIR / "realistic_store.jpg"
    
    if not test_image.exists():
        print(f"⚠ Test image not found: {test_image}")
        print("Creating a test image...")
        import cv2
        import numpy as np
        
        # Quick test image
        img = np.ones((400, 600, 3), dtype=np.uint8) * 200
        cv2.rectangle(img, (100, 100), (500, 300), (100, 100, 200), -1)
        cv2.putText(img, "TEST ENTRANCE", (150, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.imwrite(str(test_image), img)
    
    image = process_image_file(str(test_image))
    print(f"✓ Loaded image: {image.shape[1]}x{image.shape[0]} pixels")
    
    # Step 2: Initialize detector
    print("\n[Step 2] Initializing object detector...")
    detector = ObjectDetector(use_mock=True)
    print("✓ Detector ready")
    
    # Step 3: Detect objects
    print("\n[Step 3] Running object detection...")
    all_detections = detector.detect(image)
    print(f"✓ Raw detections: {len(all_detections)} objects found")
    
    if all_detections:
        print("\nAll detected objects:")
        for i, det in enumerate(all_detections, 1):
            print(f"  {i}. {det.class_name:12s} "
                  f"bbox: ({det.x:3d}, {det.y:3d}, {det.width:3d}, {det.height:3d}) "
                  f"conf: {det.confidence:.2f}")
    
    # Step 4: Filter for ADA-relevant objects
    print("\n[Step 4] Filtering for ADA-relevant objects...")
    relevant_detections = detector.filter_relevant_objects(all_detections)
    print(f"✓ Relevant objects: {len(relevant_detections)}")
    
    # Step 5: Visualize results
    print("\n[Step 5] Creating visualization...")
    output_path = str(config.OUTPUTS_DIR / "pipeline_test_result.jpg")
    annotated = visualize_detections(image, all_detections, output_path)
    print(f"✓ Saved to: {output_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE TEST COMPLETE")
    print("=" * 70)
    print(f"Total detections:    {len(all_detections)}")
    print(f"Relevant objects:    {len(relevant_detections)}")
    print(f"Output saved:        {output_path}")
    print("\nNext step: Send relevant objects to Claude for ADA analysis!")
    print("=" * 70)
    
    return image, all_detections, relevant_detections


if __name__ == "__main__":
    test_full_pipeline()
