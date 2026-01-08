#!/usr/bin/env python3
"""
ADA COMPLIANCE DETECTION SYSTEM - DEMO SCRIPT

Updated to use modular analyzer architecture.
Can now easily switch between different analyzer types.

Usage:
    python3 demo.py <path_to_image> [--analyzer rule_based|claude|hybrid]
    
Example:
    python3 demo.py test_images/store_entrance.jpg
    python3 demo.py test_images/store_entrance.jpg --analyzer rule_based
"""

import sys
from pathlib import Path
import json
import argparse

import config
from video_processor import process_image_file
from object_detector import ObjectDetector
from compliance_analyzer import ComplianceAnalyzer
from visualizer import ViolationVisualizer


def print_header():
    """Print nice header for demo."""
    print("\n" + "=" * 80)
    print(" " * 20 + "ADA COMPLIANCE DETECTION SYSTEM")
    print(" " * 25 + "AI-Powered Accessibility Auditing")
    print("=" * 80 + "\n")


def print_section(title):
    """Print section header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print('─' * 80)


def run_demo(image_path: str, 
             use_real_yolo: bool = True,
             analyzer_type: str = 'rule_based'):
    """
    Run the complete ADA compliance analysis demo.
    
    Args:
        image_path: Path to image to analyze
        use_real_yolo: If True, use real YOLOv8 (set to True for competition!)
        analyzer_type: Type of analyzer to use
                      Options: 'rule_based', 'claude', 'hybrid'
    """
    print_header()
    
    # Verify file exists
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"❌ Error: Image not found: {image_path}")
        return
    
    print(f"📸 Analyzing: {img_path.name}")
    print(f"📍 Location: {img_path.parent}")
    print(f"🔧 Analyzer: {analyzer_type}")
    
    # STEP 1: Load Image
    print_section("STEP 1: Loading Image")
    try:
        image = process_image_file(str(image_path))
        print(f"✓ Image loaded successfully")
        print(f"  Size: {image.shape[1]} x {image.shape[0]} pixels")
        print(f"  Format: {image.shape[2]} channels (BGR)")
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return
    
    # STEP 2: Object Detection
    print_section("STEP 2: Detecting Accessibility Features (YOLOv8)")
    print("Running object detection model...")
    
    detector = ObjectDetector(use_mock=not use_real_yolo)
    all_detections = detector.detect(image)
    
    print(f"\n✓ Detection complete!")
    print(f"  Total objects detected: {len(all_detections)}")
    
    # Filter for ADA-relevant
    relevant_detections = detector.filter_relevant_objects(all_detections)
    print(f"  ADA-relevant objects: {len(relevant_detections)}")
    
    if relevant_detections:
        print("\n  Detected objects:")
        for i, det in enumerate(relevant_detections, 1):
            print(f"    {i}. {det.class_name:15s} (confidence: {det.confidence:.1%})")
    else:
        print("  ⚠ No ADA-relevant objects detected")
        print("  Try a different image with doors, parking, or pathways")
        return
    
    # STEP 3: Compliance Analysis
    print_section(f"STEP 3: Analyzing for ADA Violations ({analyzer_type})")
    print(f"Analyzing each detected feature using {analyzer_type} analyzer...")
    
    # Create analyzer with specified type
    analyzer = ComplianceAnalyzer(
        use_mock=False,
        analyzer_type=analyzer_type
    )
    
    violations_data = analyzer.analyze_all_detections(image, relevant_detections)
    
    # Count violations
    total_violations = sum(
        len(d['violations']) for d in violations_data.values()
    )
    
    print(f"\n✓ Analysis complete!")
    print(f"  Total violations found: {total_violations}")
    
    # Show violation details
    if total_violations > 0:
        print("\n  Violation Summary:")
        severity_counts = {"Critical": 0, "Moderate": 0, "Minor": 0}
        
        for det_data in violations_data.values():
            for v in det_data['violations']:
                severity = v['severity']
                severity_counts[severity] += 1
        
        print(f"    🔴 Critical:  {severity_counts['Critical']}")
        print(f"    🟠 Moderate:  {severity_counts['Moderate']}")
        print(f"    🟡 Minor:     {severity_counts['Minor']}")
        
        print("\n  Detailed Violations:")
        for det_key, det_data in violations_data.items():
            if det_data['violations']:
                print(f"\n    {det_data['object'].upper()}:")
                for v in det_data['violations']:
                    icon = {"Critical": "🔴", "Moderate": "🟠", "Minor": "🟡"}[v['severity']]
                    print(f"      {icon} [{v['severity']}] {v['type']}")
                    print(f"         ADA Code: {v['ada_code']}")
                    print(f"         Issue: {v['description']}")
                    print(f"         Fix: {v['recommendation']}")
                    print(f"         Method: {v.get('detection_method', 'unknown')}")
    else:
        print("  ✓ No violations detected - location appears compliant!")
    
    # STEP 4: Generate Visual Report
    print_section("STEP 4: Generating Visual Reports")
    print("Creating annotated images...")
    
    visualizer = ViolationVisualizer()
    
    # Create detailed report
    report_path = config.OUTPUTS_DIR / f"{img_path.stem}_report.jpg"
    visualizer.create_detailed_report(
        image, relevant_detections, violations_data, str(report_path)
    )
    print(f"✓ Visual report saved: {report_path}")
    
    # Create comparison
    annotated = visualizer.annotate_image(image, relevant_detections, violations_data)
    comparison_path = config.OUTPUTS_DIR / f"{img_path.stem}_comparison.jpg"
    visualizer.create_side_by_side(image, annotated, str(comparison_path))
    print(f"✓ Comparison saved: {comparison_path}")
    
    # STEP 5: Save JSON Report
    print_section("STEP 5: Saving Analysis Report")
    
    # Get analyzer info
    analyzer_info = analyzer.get_analyzer_info()
    
    report_data = {
        "image": str(img_path),
        "dimensions": {"width": image.shape[1], "height": image.shape[0]},
        "analyzer_used": analyzer_info,
        "detections": len(relevant_detections),
        "violations": total_violations,
        "severity_breakdown": {
            "critical": sum(1 for d in violations_data.values() 
                          for v in d['violations'] if v['severity'] == 'Critical'),
            "moderate": sum(1 for d in violations_data.values() 
                          for v in d['violations'] if v['severity'] == 'Moderate'),
            "minor": sum(1 for d in violations_data.values() 
                       for v in d['violations'] if v['severity'] == 'Minor')
        },
        "detailed_results": violations_data
    }
    
    json_path = config.OUTPUTS_DIR / f"{img_path.stem}_report.json"
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"✓ JSON report saved: {json_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("  ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\n  📊 Results:")
    print(f"     Objects detected:     {len(relevant_detections)}")
    print(f"     Violations found:     {total_violations}")
    print(f"     Analyzer used:        {analyzer_type}")
    print(f"     Visual report:        {report_path.name}")
    print(f"     JSON report:          {json_path.name}")
    print(f"\n  📁 All outputs saved to: {config.OUTPUTS_DIR}/")
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='ADA Compliance Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 demo.py test_images/store.jpg
  python3 demo.py test_images/store.jpg --analyzer rule_based
  python3 demo.py test_images/store.jpg --analyzer claude
  python3 demo.py test_images/store.jpg --yolo mock --analyzer claude
        """
    )
    
    parser.add_argument('image', 
                       help='Path to image file to analyze')
    
    parser.add_argument('--analyzer', 
                       choices=['rule_based', 'claude', 'hybrid'],
                       default='rule_based',
                       help='Type of analyzer to use (default: rule_based)')
    
    parser.add_argument('--yolo',
                       choices=['real', 'mock'],
                       default='real',
                       help='YOLO mode: real or mock (default: real)')
    
    args = parser.parse_args()
    
    # Check if image exists
    if not Path(args.image).exists():
        print(f"❌ Error: Image not found: {args.image}")
        print("\nAvailable test images:")
        
        test_images = list(config.TEST_IMAGES_DIR.glob("*.jpg")) + \
                     list(config.TEST_IMAGES_DIR.glob("*.png"))
        
        if test_images:
            for img in test_images:
                print(f"  - {img}")
        else:
            print("  (no test images found in test_images/)")
        
        sys.exit(1)
    
    # Run demo
    use_real_yolo = (args.yolo == 'real')
    
    run_demo(
        args.image,
        use_real_yolo=use_real_yolo,
        analyzer_type=args.analyzer
    )


if __name__ == "__main__":
    main()
