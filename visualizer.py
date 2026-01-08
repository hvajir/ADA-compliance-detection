"""
Enhanced Visualizer Module

Creates professional-looking annotated images showing:
1. Detected objects with bounding boxes
2. Violation severity color coding
3. Violation labels and descriptions
4. Summary statistics

This makes the demo visually impressive!
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path

import config
from object_detector import DetectionResult
from base_analyzer import ViolationResult


class ViolationVisualizer:
    """
    Creates annotated images showing ADA violations.
    
    Architecture: Takes raw detection + violation data and creates
    professional visual reports.
    """
    
    def __init__(self):
        """Initialize the visualizer with color schemes and fonts."""
        # Color schemes (BGR format for OpenCV)
        self.colors = {
            "Critical": (0, 0, 255),      # Red
            "Moderate": (0, 165, 255),    # Orange  
            "Minor": (0, 255, 255),       # Yellow
            "Compliant": (0, 255, 0),     # Green
            "Detection": (255, 200, 0)    # Cyan (for objects without violations)
        }
        
        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.font_thickness = 2
        self.line_thickness = 3
    
    def annotate_image(self,
                      image: np.ndarray,
                      detections: List[DetectionResult],
                      violations_by_detection: Dict) -> np.ndarray:
        """
        Create fully annotated image with detections and violations.
        
        Args:
            image: Original image
            detections: List of detected objects
            violations_by_detection: Dict mapping detection to violations
            
        Returns:
            Annotated image
            
        This is the main method that creates the visual report.
        """
        # Make a copy to avoid modifying original
        annotated = image.copy()
        
        # Add semi-transparent overlay for better visibility
        overlay = annotated.copy()
        
        # Process each detection
        for i, detection in enumerate(detections):
            det_key = f"detection_{i}"
            
            # Get violations for this detection (if any)
            violations = []
            if det_key in violations_by_detection:
                violation_dicts = violations_by_detection[det_key].get('violations', [])
                violations = [ViolationResult(v) for v in violation_dicts]
            
            # Determine severity color
            if violations:
                # Use highest severity
                severity_order = {"Critical": 3, "Moderate": 2, "Minor": 1}
                max_severity = max(violations, key=lambda v: severity_order.get(v.severity, 0))
                color = self.colors[max_severity.severity]
            else:
                color = self.colors["Compliant"]
            
            # Draw bounding box
            x, y, w, h = detection.bbox
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, self.line_thickness)
            
            # Create label
            label_parts = [detection.class_name]
            if violations:
                label_parts.append(f"{len(violations)} violation(s)")
            label = " - ".join(label_parts)
            
            # Draw label background
            (label_w, label_h), baseline = cv2.getTextSize(
                label, self.font, self.font_scale, self.font_thickness
            )
            
            label_y = y - 10 if y > 30 else y + h + 25
            cv2.rectangle(annotated, 
                         (x, label_y - label_h - 5),
                         (x + label_w + 10, label_y + 5),
                         color, -1)
            
            # Draw label text
            cv2.putText(annotated, label,
                       (x + 5, label_y),
                       self.font, self.font_scale,
                       (255, 255, 255), self.font_thickness)
            
            # Add violation details if any
            if violations:
                self._add_violation_details(annotated, detection, violations)
        
        return annotated
    
    def _add_violation_details(self,
                               image: np.ndarray,
                               detection: DetectionResult,
                               violations: List[ViolationResult]):
        """
        Add detailed violation information near the detection.
        
        Args:
            image: Image being annotated (modified in place)
            detection: The detected object
            violations: List of violations for this object
        """
        x, y, w, h = detection.bbox
        
        # Position for violation details (to the right of bbox)
        detail_x = x + w + 10
        detail_y = y + 20
        
        for i, violation in enumerate(violations):
            # Create violation text
            violation_text = f"{violation.type}: {violation.severity}"
            
            # Get color for this severity
            color = self.colors[violation.severity]
            
            # Draw small icon/marker
            icon_size = 8
            cv2.circle(image, (detail_x, detail_y + i * 25), 
                      icon_size, color, -1)
            
            # Draw violation text
            text_x = detail_x + icon_size + 5
            text_y = detail_y + i * 25 + 5
            
            cv2.putText(image, violation_text,
                       (text_x, text_y),
                       self.font, 0.5,
                       (255, 255, 255), 1)
    
    def create_summary_panel(self,
                            image: np.ndarray,
                            detections: List[DetectionResult],
                            violations_by_detection: Dict) -> np.ndarray:
        """
        Add summary panel to the image showing overall statistics.
        
        Args:
            image: Annotated image
            detections: All detections
            violations_by_detection: All violations
            
        Returns:
            Image with summary panel
        """
        # Count violations by severity
        severity_counts = {"Critical": 0, "Moderate": 0, "Minor": 0}
        total_violations = 0
        
        for det_data in violations_by_detection.values():
            for v in det_data.get('violations', []):
                severity = v.get('severity', 'Minor')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                total_violations += 1
        
        # Create panel at top of image
        panel_height = 100
        panel = np.zeros((panel_height, image.shape[1], 3), dtype=np.uint8)
        panel[:] = (40, 40, 40)  # Dark gray background
        
        # Add title
        title = "ADA COMPLIANCE ANALYSIS SUMMARY"
        cv2.putText(panel, title, (20, 30),
                   self.font, 0.8, (255, 255, 255), 2)
        
        # Add statistics
        stats_y = 60
        stats = [
            f"Objects Detected: {len(detections)}",
            f"Total Violations: {total_violations}",
            f"Critical: {severity_counts['Critical']}",
            f"Moderate: {severity_counts['Moderate']}",
            f"Minor: {severity_counts['Minor']}"
        ]
        
        x_offset = 20
        for i, stat in enumerate(stats):
            cv2.putText(panel, stat, (x_offset, stats_y),
                       self.font, 0.5, (200, 200, 200), 1)
            x_offset += 180
        
        # Combine panel with image
        result = np.vstack([panel, image])
        return result
    
    def create_detailed_report(self,
                              image: np.ndarray,
                              detections: List[DetectionResult],
                              violations_by_detection: Dict,
                              save_path: str) -> str:
        """
        Create a comprehensive visual report with multiple views.
        
        Args:
            image: Original image
            detections: All detections
            violations_by_detection: All violations
            save_path: Where to save the report
            
        Returns:
            Path to saved report
        """
        # Step 1: Annotate image
        annotated = self.annotate_image(image, detections, violations_by_detection)
        
        # Step 2: Add summary panel
        with_summary = self.create_summary_panel(annotated, detections, 
                                                 violations_by_detection)
        
        # Save
        cv2.imwrite(save_path, with_summary)
        return save_path
    
    def create_side_by_side(self,
                           original: np.ndarray,
                           annotated: np.ndarray,
                           save_path: str) -> str:
        """
        Create side-by-side comparison of original vs annotated.
        
        Args:
            original: Original image
            annotated: Annotated image  
            save_path: Where to save
            
        Returns:
            Path to saved comparison
        """
        # Resize if needed to same height
        if original.shape != annotated.shape:
            h = min(original.shape[0], annotated.shape[0])
            original = cv2.resize(original, 
                                 (int(original.shape[1] * h / original.shape[0]), h))
            annotated = cv2.resize(annotated,
                                  (int(annotated.shape[1] * h / annotated.shape[0]), h))
        
        # Add labels
        original_labeled = original.copy()
        annotated_labeled = annotated.copy()
        
        cv2.putText(original_labeled, "ORIGINAL", (20, 40),
                   self.font, 1.2, (255, 255, 255), 3)
        cv2.putText(annotated_labeled, "ANALYSIS", (20, 40),
                   self.font, 1.2, (255, 255, 255), 3)
        
        # Combine side by side
        comparison = np.hstack([original_labeled, annotated_labeled])
        
        # Save
        cv2.imwrite(save_path, comparison)
        return save_path


# Demo/test code
if __name__ == "__main__":
    """Test the enhanced visualizer."""
    print("=" * 70)
    print("Enhanced Visualizer - Demo")
    print("=" * 70)
    
    from video_processor import process_image_file
    from object_detector import ObjectDetector
    from compliance_analyzer import ComplianceAnalyzer
    
    # Load test image
    test_image_path = config.TEST_IMAGES_DIR / "realistic_store.jpg"
    
    if test_image_path.exists():
        print("\nLoading image and running full analysis...")
        
        # Full pipeline
        image = process_image_file(str(test_image_path))
        detector = ObjectDetector(use_mock=True)
        detections = detector.detect(image)
        relevant = detector.filter_relevant_objects(detections)
        
        analyzer = ComplianceAnalyzer(use_mock=True)
        violations = analyzer.analyze_all_detections(image, relevant)
        
        # Create visualizations
        print("\nCreating enhanced visualizations...")
        visualizer = ViolationVisualizer()
        
        # Detailed report
        report_path = str(config.OUTPUTS_DIR / "enhanced_report.jpg")
        visualizer.create_detailed_report(image, relevant, violations, report_path)
        print(f"✓ Detailed report: {report_path}")
        
        # Side-by-side comparison
        annotated = visualizer.annotate_image(image, relevant, violations)
        comparison_path = str(config.OUTPUTS_DIR / "comparison.jpg")
        visualizer.create_side_by_side(image, annotated, comparison_path)
        print(f"✓ Comparison: {comparison_path}")
        
        print("\n✓ Enhanced visualizations complete!")
    else:
        print(f"Test image not found: {test_image_path}")
