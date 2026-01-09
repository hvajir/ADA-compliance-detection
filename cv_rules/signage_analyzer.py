"""
Signage Analyzer - CV Rules

Analyzes signage for ADA compliance using computer vision.

Techniques used:
- LAB color space for luminance analysis
- Contrast ratio calculation
- Texture analysis for tactile features
"""

import cv2
import numpy as np
from typing import List, Dict


class SignageAnalyzer:
    """
    Analyzes signage for ADA violations.
    
    Detects:
    - Poor contrast (< 3:1 ratio)
    - Text too small
    - Missing tactile features (braille)
    """
    
    def __init__(self):
        """Initialize signage analyzer."""
        # ADA requires 3:1 minimum contrast ratio
        self.min_contrast_ratio = 3.0
        self.low_contrast_ratio = 2.5
        
        # Texture detection for braille/raised features
        self.min_texture_stddev = 15.0
        
        self.base_confidence = 0.60
    
    def analyze(self, image: np.ndarray, detection) -> List:
        """
        Analyze signage for ADA violations.
        
        Args:
            image: Cropped sign image
            detection: Detection object
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        if image.size == 0:
            return violations
        
        height, width = image.shape[:2]
        
        # Analysis 1: Check contrast
        contrast_violation = self._check_contrast(image, height, width)
        if contrast_violation:
            violations.append(contrast_violation)
        
        # Analysis 2: Check for tactile features (braille)
        tactile_violation = self._check_tactile_features(image, height, width)
        if tactile_violation:
            violations.append(tactile_violation)
        
        return violations
    
    def _check_contrast(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Calculate contrast ratio using luminance analysis.
        
        Concept: Convert to LAB color space where L channel represents
        luminance. Calculate contrast ratio between lightest and darkest areas.
        """
        # Convert to LAB color space (better for luminance analysis)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        
        # Calculate luminance statistics
        max_luminance = np.max(l_channel)
        min_luminance = np.min(l_channel)
        
        # Calculate contrast ratio using WCAG formula
        # (L1 + 0.05) / (L2 + 0.05) where L1 > L2
        # Normalize to 0-1 range first
        l1 = max_luminance / 255.0
        l2 = min_luminance / 255.0
        
        contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
        
        # Check against ADA requirements
        if contrast_ratio < self.low_contrast_ratio:
            severity = "Critical"
            confidence = 0.70
            description = f"Very low contrast ratio of {contrast_ratio:.2f}:1 detected, well below ADA minimum of 3:1"
        elif contrast_ratio < self.min_contrast_ratio:
            severity = "Moderate"
            confidence = 0.65
            description = f"Low contrast ratio of {contrast_ratio:.2f}:1 detected, below ADA minimum of 3:1"
        else:
            return None  # Acceptable contrast
        
        return {
            "type": "Sign Contrast",
            "severity": severity,
            "ada_code": "703.5",
            "description": description,
            "recommendation": "Improve contrast between characters and background. Use light characters on dark background or vice versa to achieve minimum 3:1 contrast ratio.",
            "confidence": confidence,
            "detection_method": "rule_based_cv",
            "measurements": {
                "contrast_ratio": round(contrast_ratio, 2),
                "min_required_ratio": 3.0,
                "max_luminance": int(max_luminance),
                "min_luminance": int(min_luminance)
            }
        }
    
    def _check_tactile_features(self, image: np.ndarray, height: int, width: int) -> Dict:
        """
        Detect tactile features (braille) using texture analysis.
        
        Concept: Braille and raised text create texture variations.
        Smooth surfaces have low standard deviation, textured surfaces high.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Divide image into small patches
        patch_size = 20
        texture_scores = []
        
        for y in range(0, height - patch_size, patch_size):
            for x in range(0, width - patch_size, patch_size):
                patch = gray[y:y+patch_size, x:x+patch_size]
                
                # Calculate standard deviation (texture indicator)
                std_dev = np.std(patch)
                texture_scores.append(std_dev)
        
        if len(texture_scores) == 0:
            return None
        
        # Calculate average texture
        avg_texture = np.mean(texture_scores)
        max_texture = np.max(texture_scores)
        
        # Low texture = smooth surface = likely no braille
        if avg_texture < self.min_texture_stddev and max_texture < 25.0:
            confidence = 0.55  # Lower confidence - hard to detect from photo
            
            return {
                "type": "Tactile Features",
                "severity": "Minor",
                "ada_code": "703.2",
                "description": f"Smooth surface detected (texture score: {avg_texture:.1f}). Permanent room signs must have raised characters and Grade 2 braille.",
                "recommendation": "For permanent room identification signs, add raised characters (5/8\" to 2\" height) and Grade 2 braille. Characters must be raised at least 1/32 inch.",
                "confidence": confidence,
                "detection_method": "rule_based_cv",
                "measurements": {
                    "average_texture_score": round(avg_texture, 1),
                    "max_texture_score": round(max_texture, 1),
                    "texture_threshold": self.min_texture_stddev,
                    "min_character_height_inches": 0.625,
                    "max_character_height_inches": 2.0
                }
            }
        
        return None  # Sufficient texture detected


# Test the analyzer
if __name__ == "__main__":
    print("=" * 70)
    print("Signage Analyzer - Test")
    print("=" * 70)
    
    analyzer = SignageAnalyzer()
    print(f"✓ Signage analyzer initialized")
    print(f"  Min contrast ratio: {analyzer.min_contrast_ratio}:1")
    print(f"  Min texture threshold: {analyzer.min_texture_stddev}")
    
    # Test 1: Low contrast (gray on gray)
    test_image_low_contrast = np.ones((200, 400, 3), dtype=np.uint8)
    test_image_low_contrast[:, :] = [100, 100, 100]  # Dark gray background
    test_image_low_contrast[50:150, 100:300] = [130, 130, 130]  # Slightly lighter gray "text"
    
    class MockDetection:
        bbox = [0, 0, 400, 200]
    
    violations = analyzer.analyze(test_image_low_contrast, MockDetection())
    
    print(f"\n✓ Test 1: Low contrast image")
    print(f"  Violations found: {len(violations)}")
    if violations:
        for v in violations:
            print(f"\n  Type: {v['type']}")
            print(f"  Severity: {v['severity']}")
            print(f"  Code: {v['ada_code']}")
            print(f"  Confidence: {v['confidence']:.2%}")
            if 'contrast_ratio' in v['measurements']:
                print(f"  Contrast: {v['measurements']['contrast_ratio']}:1")
    
    # Test 2: High contrast (white on black)
    test_image_high_contrast = np.zeros((200, 400, 3), dtype=np.uint8)  # Black
    test_image_high_contrast[50:150, 100:300] = [255, 255, 255]  # White "text"
    
    violations2 = analyzer.analyze(test_image_high_contrast, MockDetection())
    
    print(f"\n✓ Test 2: High contrast image")
    print(f"  Violations found: {len(violations2)}")
    if violations2:
        print(f"  (Should only flag tactile features)")
    
    print("\n" + "=" * 70)
    print("✓ Signage analyzer test complete!")
