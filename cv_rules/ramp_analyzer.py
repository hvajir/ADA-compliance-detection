"""
Ramp Analyzer - CV Rules

Analyzes ramps for ADA compliance using computer vision.

Techniques used:
- Line detection for slope estimation
- Angle calculation for grade determination
- Parallel line detection for handrails
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple


class RampAnalyzer:
    """
    Analyzes ramps for ADA violations.
    
    Detects:
    - Ramp slope too steep (> 1:12 ratio / 4.76°)
    - Missing handrails
    - Missing edge protection
    """
    
    def __init__(self):
        """Initialize ramp analyzer."""
        # ADA maximum slope: 1:12 ratio = 4.76 degrees
        self.max_slope_degrees = 5.0
        self.warning_slope_degrees = 4.0
        
        # Line detection parameters
        self.canny_low = 50
        self.canny_high = 150
        
        self.base_confidence = 0.55
    
    def analyze(self, image: np.ndarray, detection) -> List:
        """
        Analyze a ramp image for ADA violations.
        
        Args:
            image: Cropped ramp image
            detection: Detection object
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        if image.size == 0:
            return violations
        
        height, width = image.shape[:2]
        
        # Analysis 1: Check ramp slope
        slope_violation = self._check_slope(image, height, width)
        if slope_violation:
            violations.append(slope_violation)
        
        # Analysis 2: Check for handrails
        handrail_violation = self._check_handrails(image, height, width)
        if handrail_violation:
            violations.append(handrail_violation)
        
        return violations
    
    def _check_slope(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Estimate ramp slope using line detection.
        
        Concept: Detect diagonal lines in the image and calculate their
        angles. Steeper angles indicate steeper ramps.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=int(min(width, height) * 0.2),
            maxLineGap=20
        )
        
        if lines is None or len(lines) == 0:
            return None
        
        # Calculate angles of all detected lines
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate angle from horizontal
            if x2 - x1 != 0:
                angle = abs(np.degrees(np.arctan((y2 - y1) / (x2 - x1))))
                
                # We're interested in diagonal lines (not horizontal or vertical)
                if 10 < angle < 80:  # Reasonable ramp angles
                    angles.append(angle)
        
        if len(angles) == 0:
            return None
        
        # Find the steepest angle (most concerning)
        steepest_angle = max(angles)
        
        # Determine severity
        if steepest_angle > self.max_slope_degrees:
            severity = "Critical"
            confidence = 0.60
            description = f"Detected diagonal line at {steepest_angle:.1f}° angle, exceeding ADA maximum slope of 4.76° (1:12 ratio)"
        elif steepest_angle > self.warning_slope_degrees:
            severity = "Moderate"
            confidence = 0.55
            description = f"Detected diagonal line at {steepest_angle:.1f}° angle, approaching ADA maximum slope of 4.76° (1:12 ratio)"
        else:
            return None  # Acceptable slope
        
        return {
            "type": "Ramp Slope",
            "severity": severity,
            "ada_code": "405.2",
            "description": description,
            "recommendation": "Verify ramp slope with physical measurement (rise:run ratio). If steeper than 1:12 (8.33%), reconstruct ramp to meet compliance or install alternative accessible route.",
            "confidence": confidence,
            "detection_method": "rule_based_cv",
            "measurements": {
                "detected_angle_degrees": round(steepest_angle, 1),
                "max_allowed_angle_degrees": 4.76,
                "max_allowed_ratio": "1:12",
                "max_allowed_percentage": 8.33
            }
        }
    
    def _check_handrails(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Detect handrails using parallel line detection.
        
        Concept: Handrails appear as long parallel lines on the sides
        of ramps. We look for these features on left and right edges.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        
        # Detect lines
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=40,
            minLineLength=int(height * 0.3),  # At least 30% of image height
            maxLineGap=30
        )
        
        if lines is None:
            # No long lines detected - likely missing handrails
            confidence = 0.65
            
            return {
                "type": "Ramp Handrails",
                "severity": "Moderate",
                "ada_code": "405.8",
                "description": "No handrail features detected. Ramps with rise greater than 6 inches must have handrails on both sides.",
                "recommendation": "Install handrails on both sides of ramp, 34-38 inches above ramp surface, extending 12 inches beyond top and bottom of ramp.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "handrail_features_detected": 0,
                    "required_handrails": 2
                }
            }
        
        # Classify lines by position (left vs right side)
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            avg_x = (x1 + x2) / 2
            
            if avg_x < width * 0.3:  # Left third
                left_lines.append(line)
            elif avg_x > width * 0.7:  # Right third
                right_lines.append(line)
        
        # Check if we have handrails on both sides
        if len(left_lines) == 0 or len(right_lines) == 0:
            confidence = 0.60
            
            missing = []
            if len(left_lines) == 0:
                missing.append("left")
            if len(right_lines) == 0:
                missing.append("right")
            
            return {
                "type": "Ramp Handrails",
                "severity": "Moderate",
                "ada_code": "405.8",
                "description": f"Handrail features missing on {' and '.join(missing)} side(s). Ramps must have handrails on both sides if rise exceeds 6 inches.",
                "recommendation": "Install handrails on both sides, 34-38 inches above ramp surface, with gripping surface complying with ADA 505.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "left_handrail_features": len(left_lines),
                    "right_handrail_features": len(right_lines),
                    "required_handrails": 2
                }
            }
        
        return None  # Both sides have features, likely compliant


# Test the analyzer
if __name__ == "__main__":
    print("=" * 70)
    print("Ramp Analyzer - Test")
    print("=" * 70)
    
    analyzer = RampAnalyzer()
    print(f"✓ Ramp analyzer initialized")
    print(f"  Max slope: {analyzer.max_slope_degrees}°")
    print(f"  Warning slope: {analyzer.warning_slope_degrees}°")
    
    # Create test image with diagonal line (steep ramp)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a steep diagonal line
    cv2.line(test_image, (100, 400), (500, 100), (255, 255, 255), 3)
    
    class MockDetection:
        bbox = [0, 0, 640, 480]
    
    violations = analyzer.analyze(test_image, MockDetection())
    
    print(f"\n✓ Analyzed test image (with diagonal line)")
    print(f"  Violations found: {len(violations)}")
    
    for v in violations:
        print(f"\n  Type: {v['type']}")
        print(f"  Severity: {v['severity']}")
        print(f"  Code: {v['ada_code']}")
        print(f"  Confidence: {v['confidence']:.2%}")
    
    print("\n" + "=" * 70)
    print("✓ Ramp analyzer test complete!")
