#!/usr/bin/env python3
"""
Complete End-to-End Integration Test

This demonstrates the FULL pipeline:
1. Load image
2. Detect objects (YOLOv8 mock)
3. Analyze for ADA compliance (Claude mock)
4. Generate visual report
5. Save results

This is what will run during your competition demo!
"""

import json
import config
from video_processor import process_image_file
from object_detector import ObjectDetector, visualize_detections
from compliance_analyzer import ComplianceAnalyzer


def run_full_analysis(image_path: str, use_real_models: bool = False):
    """
    Run complete ADA compliance analysis on an image.
    
    Args:
        image_path: Path to image file
        use_real_models: If True, use real YOLO + Claude API
                        If False, use mock versions (for testing)
    
    Returns:
        Dictionary with all results
    """
    print("=" * 80)
    print("ADA COMPLIANCE DETECTION SYSTEM - FULL ANALYSIS")
    print("=" * 80)
    
    # STEP 1: Load Image
    print("\n[STEP 1/5] Loading image...")
    print("-" * 80)
    image = process_image_file(image_path)
    print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
    
    # STEP 2: Object Detection
    print("\n[STEP 2/5] Detecting accessibility features...")
    print("-" * 80)
    detector = ObjectDetector(use_mock=not use_real_models)
    all_detections = detector.detect(image)
    print(f"✓ Total detections: {len(all_detections)}")
    
    # Filter for ADA-relevant objects
    relevant_detections = detector.filter_relevant_objects(all_detections)
    print(f"✓ ADA-relevant objects: {len(relevant_detections)}")
    
    if relevant_detections:
        print("\nDetected ADA-relevant objects:")
        for i, det in enumerate(relevant_detections, 1):
            print(f"  {i}. {det.class_name:15s} confidence: {det.confidence:.2f} "
                  f"at ({det.x}, {det.y})")
    
    # STEP 3: ADA Compliance Analysis
    print("\n[STEP 3/5] Analyzing for ADA violations...")
    print("-" * 80)
    analyzer = ComplianceAnalyzer(use_mock=not use_real_models)
    analysis_results = analyzer.analyze_all_detections(image, relevant_detections)
    
    # Count total violations
    total_violations = sum(len(r['violations']) for r in analysis_results.values())
    print(f"\n✓ Analysis complete: {total_violations} potential violation(s) found")
    
    # STEP 4: Generate Visual Report
    print("\n[STEP 4/5] Generating visualization...")
    print("-" * 80)
    
    # Create annotated image with detections
    output_image_path = str(config.OUTPUTS_DIR / "full_analysis_annotated.jpg")
    annotated_image = visualize_detections(image, relevant_detections, output_image_path)
    print(f"✓ Annotated image saved: {output_image_path}")
    
    # STEP 5: Save Results
    print("\n[STEP 5/5] Saving analysis results...")
    print("-" * 80)
    
    # Compile full report
    report = {
        "image_path": image_path,
        "image_dimensions": {
            "width": image.shape[1],
            "height": image.shape[0]
        },
        "detection_summary": {
            "total_detections": len(all_detections),
            "ada_relevant_detections": len(relevant_detections),
            "total_violations": total_violations
        },
        "detections": [
            {
                "class_name": det.class_name,
                "confidence": det.confidence,
                "bbox": det.bbox,
                "center": det.center
            }
            for det in relevant_detections
        ],
        "violations_by_detection": analysis_results
    }
    
    # Save as JSON
    report_path = config.OUTPUTS_DIR / "full_analysis_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ JSON report saved: {report_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Image analyzed:       {image_path}")
    print(f"Objects detected:     {len(relevant_detections)}")
    print(f"Violations found:     {total_violations}")
    print(f"Annotated image:      {output_image_path}")
    print(f"Full report:          {report_path}")
    
    # Show violation details
    if total_violations > 0:
        print("\n" + "-" * 80)
        print("VIOLATIONS DETAIL:")
        print("-" * 80)
        
        for det_key, result in analysis_results.items():
            if result['violations']:
                print(f"\n{result['object'].upper()} - {len(result['violations'])} violation(s):")
                for v in result['violations']:
                    severity_emoji = {
                        "Critical": "🔴",
                        "Moderate": "🟠", 
                        "Minor": "🟡"
                    }.get(v['severity'], "⚪")
                    
                    print(f"  {severity_emoji} [{v['severity']}] {v['type']}")
                    print(f"     ADA Code: {v['ada_code']}")
                    print(f"     Issue: {v['description']}")
                    print(f"     Fix: {v['recommendation']}")
                    print(f"     Confidence: {v['confidence']:.0%}")
    else:
        print("\n✓ No violations detected - location appears ADA compliant!")
    
    print("\n" + "=" * 80)
    
    return report


if __name__ == "__main__":
    """
    Run the full analysis on test image.
    
    This is essentially your demo script!
    """
    import sys
    
    # Check for test images
    test_images = list(config.TEST_IMAGES_DIR.glob("*.jpg")) + \
                 list(config.TEST_IMAGES_DIR.glob("*.png"))
    
    if not test_images:
        print("No test images found in test_images/")
        print("Please add some test images and try again.")
        sys.exit(1)
    
    # Use the first test image (or specify one)
    test_image = test_images[0]
    
    print(f"Running full analysis on: {test_image.name}\n")
    
    # Run analysis (using mock models for demo)
    report = run_full_analysis(str(test_image), use_real_models=False)
    
    print("\n✓ Full pipeline test complete!")
    print("\nFor your competition demo:")
    print("  1. Set use_real_models=True")
    print("  2. Make sure ANTHROPIC_API_KEY is set")
    print("  3. Run this script on your actual test images")
