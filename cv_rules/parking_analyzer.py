"""
Parking Analyzer - CV Rules

Analyzes parking areas for ADA compliance using computer vision.

Techniques used:
- HSV color space analysis for sign detection
- Blue/white color detection for handicap signs
- Position analysis for sign height
"""

import cv2
import numpy as np
from typing import List, Dict


class ParkingAnalyzer:
    """
    Analyzes parking areas for ADA violations.
    
    Detects:
    - Missing handicap signage
    - Improper sign colors
    - Sign placement issues
    """
    
    def __init__(self):
        """Initialize parking analyzer with color thresholds."""
        # HSV ranges for blue (handicap sign background)
        # Blue in HSV: Hue ~100-130, Saturation >100, Value >50
        self.blue_lower = np.array([90, 80, 50])
        self.blue_upper = np.array([135, 255, 255])
        
        # HSV ranges for white (wheelchair symbol)
        self.white_lower = np.array([0, 0, 180])
        self.white_upper = np.array([180, 50, 255])
        
        # Detection thresholds
        self.min_blue_percentage = 0.05  # At least 5% blue
        self.min_white_percentage = 0.02  # At least 2% white
        
        self.base_confidence = 0.75
    
    def analyze(self, image: np.ndarray, detection) -> List:
        """
        Analyze a parking area image for ADA violations.
        
        Args:
            image: Cropped parking image (numpy array)
            detection: Detection object with bbox info
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        if image.size == 0:
            return violations
        
        height, width = image.shape[:2]
        
        # Analysis 1: Check for blue handicap sign
        sign_violation = self._check_signage(image, height, width)
        if sign_violation:
            violations.append(sign_violation)
        
        # Analysis 2: Check sign position (if blue detected)
        position_violation = self._check_sign_position(image, height, width)
        if position_violation:
            violations.append(position_violation)
        
        return violations
    
    def _check_signage(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Detect handicap signage using color analysis.
        
        Concept: Handicap signs have distinctive blue background with
        white wheelchair symbol. We detect these colors in HSV space.
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create mask for blue pixels
        blue_mask = cv2.inRange(hsv, self.blue_lower, self.blue_upper)
        blue_pixels = np.sum(blue_mask > 0)
        blue_percentage = blue_pixels / blue_mask.size
        
        # Create mask for white pixels
        white_mask = cv2.inRange(hsv, self.white_lower, self.white_upper)
        white_pixels = np.sum(white_mask > 0)
        white_percentage = white_pixels / white_mask.size
        
        # Determine if signage is present
        has_blue = blue_percentage >= self.min_blue_percentage
        has_white = white_percentage >= self.min_white_percentage
        
        if not has_blue:
            # No blue detected - likely missing sign
            confidence = 0.80
            
            return {
                "type": "Parking Signage",
                "severity": "Critical",
                "ada_code": "502.6",
                "description": f"No blue signage detected (found {blue_percentage:.1%} blue pixels). Accessible parking spaces must display the International Symbol of Accessibility on a sign.",
                "recommendation": "Install accessible parking sign with International Symbol of Accessibility (blue background, white wheelchair symbol) at 60 inches minimum height above ground.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "blue_percentage": round(blue_percentage * 100, 1),
                    "white_percentage": round(white_percentage * 100, 1),
                    "required_blue_percentage": self.min_blue_percentage * 100
                }
            }
        
        elif has_blue and not has_white:
            # Has blue but no white symbol
            confidence = 0.70
            
            return {
                "type": "Wheelchair Symbol",
                "severity": "Critical",
                "ada_code": "502.6",
                "description": f"Blue sign detected but missing white wheelchair symbol (found {white_percentage:.1%} white). Sign must include International Symbol of Accessibility.",
                "recommendation": "Verify sign includes white wheelchair symbol. Replace if symbol is missing or obscured.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "blue_percentage": round(blue_percentage * 100, 1),
                    "white_percentage": round(white_percentage * 100, 1)
                }
            }
        
        # If has both blue and white, signage appears present
        return None
    
    def _check_sign_position(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Check if sign is mounted at proper height.
        
        Concept: Signs should be in upper portion of image (mounted high).
        If blue is detected in lower portion, sign may be too low.
        """
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create blue mask
        blue_mask = cv2.inRange(hsv, self.blue_lower, self.blue_upper)
        
        # Find where blue pixels are located
        blue_positions = np.where(blue_mask > 0)
        
        if len(blue_positions[0]) > 0:
            # Calculate average vertical position (0 = top, height = bottom)
            avg_y_position = np.mean(blue_positions[0])
            relative_position = avg_y_position / height
            
            # Sign should be in upper 50% of image (mounted high)
            # If it's in the lower 40%, it might be too low
            if relative_position > 0.6:
                confidence = 0.60  # Lower confidence - height hard to judge from single image
                
                return {
                    "type": "Sign Height",
                    "severity": "Moderate",
                    "ada_code": "502.6",
                    "description": f"Sign appears in lower portion of image (position: {relative_position:.0%} from top). ADA requires signs at 60 inches minimum above ground.",
                    "recommendation": "Verify sign mounting height with physical measurement. If below 60 inches, raise sign to compliant height.",
                    "confidence": confidence,
                    "detection_method": "rule_based_cv",
                    "measurements": {
                        "vertical_position_percentage": round(relative_position * 100, 0),
                        "required_height_inches": 60
                    }
                }
        
        return None


# Test the analyzer
if __name__ == "__main__":
    print("=" * 70)
    print("Parking Analyzer - Test")
    print("=" * 70)
    
    analyzer = ParkingAnalyzer()
    print(f"✓ Parking analyzer initialized")
    print(f"  Blue detection threshold: {analyzer.min_blue_percentage:.1%}")
    print(f"  White detection threshold: {analyzer.min_white_percentage:.1%}")
    
    # Test 1: Image with no blue (missing sign)
    test_image_no_sign = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    class MockDetection:
        bbox = [0, 0, 640, 480]
    
    violations = analyzer.analyze(test_image_no_sign, MockDetection())
    
    print(f"\n✓ Test 1: No sign (gray image)")
    print(f"  Violations found: {len(violations)}")
    if violations:
        print(f"  Type: {violations[0]['type']}")
        print(f"  Severity: {violations[0]['severity']}")
        print(f"  Confidence: {violations[0]['confidence']:.2%}")
    
    # Test 2: Image with blue (has sign)
    test_image_with_sign = np.ones((480, 640, 3), dtype=np.uint8)
    test_image_with_sign[:,:,0] = 255  # Blue channel
    test_image_with_sign[100:200, 250:350, :] = [255, 255, 255]  # White square (symbol)
    
    violations2 = analyzer.analyze(test_image_with_sign, MockDetection())
    
    print(f"\n✓ Test 2: With blue sign")
    print(f"  Violations found: {len(violations2)}")
    
    print("\n" + "=" * 70)
    print("✓ Parking analyzer test complete!")
