"""
Door Analyzer - CV Rules

Analyzes doors and entrances for ADA compliance using computer vision.

Techniques used:
- Aspect ratio analysis for width estimation
- Edge detection for threshold identification
- Contour analysis for hardware detection
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple


class DoorAnalyzer:
    """
    Analyzes doors and entrances for ADA violations.
    
    Detects:
    - Door width violations (< 32 inches)
    - Threshold violations (> 0.5 inches)
    - Hardware accessibility issues
    """
    
    def __init__(self):
        """Initialize door analyzer with detection thresholds."""
        # Aspect ratio thresholds
        # Standard door: 80" tall / 36" wide = 2.2
        # Narrow door: 80" tall / 28" wide = 2.9
        self.narrow_door_ratio = 2.5
        self.very_narrow_ratio = 3.0
        
        # Edge detection parameters
        self.canny_low = 50
        self.canny_high = 150
        
        # Confidence adjustments
        self.base_confidence = 0.65
    
    def analyze(self, image: np.ndarray, detection) -> List:
        """
        Analyze a door image for ADA violations.
        
        Args:
            image: Cropped door image (numpy array)
            detection: Detection object with bbox info
            
        Returns:
            List of ViolationResult objects
        """
        violations = []
        
        if image.size == 0:
            return violations
        
        height, width = image.shape[:2]
        
        # Analysis 1: Width estimation via aspect ratio
        width_violation = self._check_width(image, height, width)
        if width_violation:
            violations.append(width_violation)
        
        # Analysis 2: Threshold detection via edge detection
        threshold_violation = self._check_threshold(image, height, width)
        if threshold_violation:
            violations.append(threshold_violation)
        
        # Analysis 3: Hardware detection
        hardware_violation = self._check_hardware(image, height, width)
        if hardware_violation:
            violations.append(hardware_violation)
        
        return violations
    
    def _check_width(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Estimate door width using aspect ratio analysis.
        
        Concept: Standard doors are ~80" tall. By measuring the
        height-to-width ratio, we can estimate if the door is too narrow.
        """
        aspect_ratio = height / width if width > 0 else 0
        
        # Determine severity based on aspect ratio
        if aspect_ratio > self.very_narrow_ratio:
            # Very narrow - likely < 28 inches
            severity = "Critical"
            confidence = 0.70
            estimated_width = 28
            description = f"Door aspect ratio ({aspect_ratio:.2f}) suggests width significantly below required 32 inches (estimated ~{estimated_width}\")"
        
        elif aspect_ratio > self.narrow_door_ratio:
            # Narrow - possibly < 32 inches
            severity = "Critical"
            confidence = 0.60
            estimated_width = 30
            description = f"Door aspect ratio ({aspect_ratio:.2f}) suggests width may be below required 32 inches (estimated ~{estimated_width}\")"
        
        else:
            # Acceptable ratio
            return None
        
        return {
            "type": "Door Width",
            "severity": severity,
            "ada_code": "404.2.3",
            "description": description,
            "recommendation": "Verify actual door width with physical measurement. If below 32 inches clear width, widen opening or install wider door.",
            "confidence": confidence,
            "detection_method": "rule_based_cv",
            "measurements": {
                "aspect_ratio": round(aspect_ratio, 2),
                "estimated_width_inches": estimated_width,
                "required_width_inches": 32
            }
        }
    
    def _check_threshold(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Detect raised thresholds using edge detection.
        
        Concept: Thresholds appear as horizontal edges at the bottom
        of the door frame. We use Canny edge detection to find them.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        
        # Focus on bottom 15% of image (where threshold would be)
        bottom_section = edges[int(height * 0.85):, :]
        
        # Count strong horizontal edges
        horizontal_edges = 0
        for row in bottom_section:
            # Count continuous horizontal edges
            edge_pixels = np.sum(row > 0)
            if edge_pixels > width * 0.3:  # At least 30% of width
                horizontal_edges += 1
        
        # If we detect strong horizontal edges at the bottom
        edge_density = horizontal_edges / bottom_section.shape[0] if bottom_section.shape[0] > 0 else 0
        
        if edge_density > 0.3:  # Significant horizontal features
            confidence = min(0.55 + (edge_density * 0.2), 0.75)
            
            return {
                "type": "Door Threshold",
                "severity": "Moderate",
                "ada_code": "404.2.5",
                "description": f"Detected horizontal edge features at door base (density: {edge_density:.2f}), suggesting possible raised threshold exceeding 1/2 inch maximum",
                "recommendation": "Verify threshold height with physical measurement. If over 1/2 inch, install beveled threshold or remove raised threshold.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "edge_density": round(edge_density, 2),
                    "max_threshold_height_inches": 0.5
                }
            }
        
        return None
    
    def _check_hardware(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Detect door hardware using contour analysis.
        
        Concept: Door handles, knobs, and levers create distinct
        contours in the middle section of the door.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Focus on middle section (40-60% of height - typical handle location)
        middle_start = int(height * 0.4)
        middle_end = int(height * 0.6)
        middle_section = gray[middle_start:middle_end, :]
        
        # Apply edge detection
        edges = cv2.Canny(middle_section, self.canny_low, self.canny_high)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for hardware-like shapes (compact, not too small, not too large)
        hardware_contours = []
        min_area = (width * height) * 0.002  # At least 0.2% of image
        max_area = (width * height) * 0.05   # At most 5% of image
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Check if relatively compact (not a long line)
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
                if aspect_ratio < 3:  # Relatively square/compact
                    hardware_contours.append(contour)
        
        # If very few hardware-like features detected
        if len(hardware_contours) < 2:
            confidence = 0.50  # Lower confidence - hard to detect from image
            
            return {
                "type": "Door Hardware",
                "severity": "Minor",
                "ada_code": "404.2.7",
                "description": f"Limited hardware features detected ({len(hardware_contours)} features found). Door hardware should be operable with one hand without tight grasping.",
                "recommendation": "Verify door hardware is lever-style or push-type, operable with closed fist. Replace round knobs or twist-style hardware.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "hardware_features_detected": len(hardware_contours)
                }
            }
        
        return None


# Test the analyzer
if __name__ == "__main__":
    print("=" * 70)
    print("Door Analyzer - Test")
    print("=" * 70)
    
    analyzer = DoorAnalyzer()
    print(f"✓ Door analyzer initialized")
    print(f"  Narrow door ratio threshold: {analyzer.narrow_door_ratio}")
    print(f"  Very narrow ratio threshold: {analyzer.very_narrow_ratio}")
    
    # Create a test image (narrow door simulation)
    # Tall and narrow = high aspect ratio
    test_image = np.ones((800, 250, 3), dtype=np.uint8) * 128
    
    class MockDetection:
        bbox = [0, 0, 250, 800]
    
    violations = analyzer.analyze(test_image, MockDetection())
    
    print(f"\n✓ Analyzed test image (800x250 - narrow)")
    print(f"  Violations found: {len(violations)}")
    
    for v in violations:
        print(f"\n  Type: {v['type']}")
        print(f"  Severity: {v['severity']}")
        print(f"  Code: {v['ada_code']}")
        print(f"  Confidence: {v['confidence']:.2%}")
    
    print("\n" + "=" * 70)
    print("✓ Door analyzer test complete!")
