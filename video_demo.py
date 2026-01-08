#!/usr/bin/env python3
"""
Video Analysis Demo - Enhanced Control

Process videos with custom frame extraction settings.
"""

import sys
from pathlib import Path
import config
from video_processor import VideoProcessor
from object_detector import ObjectDetector
from compliance_analyzer import ComplianceAnalyzer
from visualizer import ViolationVisualizer

def analyze_video(video_path: str, num_frames: int = 5):
    """
    Analyze a video file for ADA compliance.
    
    Args:
        video_path: Path to video file
        num_frames: Number of frames to extract and analyze
    """
    print("=" * 80)
    print(f"  VIDEO ANALYSIS: {Path(video_path).name}")
    print("=" * 80)
    
    # Step 1: Extract frames from video
    print(f"\n[1/4] Extracting {num_frames} frames from video...")
    print("-" * 80)
    
    try:
        processor = VideoProcessor(video_path)
        frames = processor.extract_frames(num_frames)
        
        # Save extracted frames
        frame_paths = processor.save_frames(frames)
        print(f"\n✓ Extracted {len(frames)} frames")
        print(f"✓ Frames saved to: {config.OUTPUTS_DIR}/")
        
    except Exception as e:
        print(f"❌ Error processing video: {e}")
        return
    
    # Step 2: Analyze each frame
    print(f"\n[2/4] Analyzing each frame for objects...")
    print("-" * 80)
    
    detector = ObjectDetector(use_mock=False)  # Use real YOLO!
    analyzer = ComplianceAnalyzer(use_mock=True)  # Mock compliance for now
    
    all_detections = []
    all_violations = []
    
    for i, frame in enumerate(frames):
        print(f"\n  Frame {i+1}/{len(frames)}:")
        
        # Detect objects
        detections = detector.detect(frame)
        relevant = detector.filter_relevant_objects(detections)
        all_detections.append(relevant)
        
        if relevant:
            print(f"    Found {len(relevant)} relevant objects")
            
            # Analyze for violations
            violations = analyzer.analyze_all_detections(frame, relevant)
            all_violations.append(violations)
        else:
            print("    No relevant objects found")
            all_violations.append({})
    
    # Step 3: Compile results
    print(f"\n[3/4] Compiling results across all frames...")
    print("-" * 80)
    
    total_detections = sum(len(d) for d in all_detections)
    total_violations = sum(
        sum(len(v['violations']) for v in frame_violations.values())
        for frame_violations in all_violations
    )
    
    print(f"✓ Total objects detected: {total_detections}")
    print(f"✓ Total violations found: {total_violations}")
    
    # Count unique violation types
    violation_types = set()
    for frame_violations in all_violations:
        for det_violations in frame_violations.values():
            for v in det_violations['violations']:
                violation_types.add(v['type'])
    
    if violation_types:
        print(f"\nViolation types found:")
        for vtype in sorted(violation_types):
            print(f"  - {vtype}")
    
    # Step 4: Create summary visualization
    print(f"\n[4/4] Creating summary visualization...")
    print("-" * 80)
    
    visualizer = ViolationVisualizer()
    video_name = Path(video_path).stem
    
    # Annotate each frame and save
    for i, (frame, detections, violations) in enumerate(
        zip(frames, all_detections, all_violations)
    ):
        if detections:
            output_path = config.OUTPUTS_DIR / f"{video_name}_frame{i+1}_annotated.jpg"
            visualizer.create_detailed_report(
                frame, detections, violations, str(output_path)
            )
    
    print(f"✓ Annotated frames saved to: {config.OUTPUTS_DIR}/")
    
    # Summary
    print("\n" + "=" * 80)
    print("  VIDEO ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nVideo: {Path(video_path).name}")
    print(f"Frames analyzed: {len(frames)}")
    print(f"Objects detected: {total_detections}")
    print(f"Violations found: {total_violations}")
    print(f"\n✓ Check {config.OUTPUTS_DIR}/ for:")
    print(f"  - Extracted frames (*_frame_*.jpg)")
    print(f"  - Annotated analysis (*_frame*_annotated.jpg)")
    print("=" * 80 + "\n")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 video_demo.py <video_path> [num_frames]")
        print("\nExamples:")
        print("  python3 video_demo.py test_images/store_tour.mp4")
        print("  python3 video_demo.py test_images/store_tour.mp4 10")
        print("\nSupported formats: .mp4, .mov, .avi, .mkv, .webm")
        sys.exit(1)
    
    video_path = sys.argv[1]
    num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Verify file exists
    if not Path(video_path).exists():
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    analyze_video(video_path, num_frames)

if __name__ == "__main__":
    main()
