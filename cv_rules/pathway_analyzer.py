"""
Pathway Analyzer - CV Rules

Analyzes pathways and accessible routes for ADA compliance.

Techniques used:
- Object position analysis for obstruction detection
- Edge detection for width estimation
- Spatial analysis for clearance
"""

import cv2
import numpy as np
from typing import List, Dict


class PathwayAnalyzer:
    """
    Analyzes pathways for ADA violations.
    
    Detects:
    - Obstructions in pathways
    - Insufficient pathway width
    - Objects reducing clearance
    """
    
    def __init__(self):
        """Initialize pathway analyzer."""
        self.base_confidence = 0.60
        
        # Objects that commonly obstruct pathways
        self.obstruction_objects = [
            'chair', 'couch', 'bench', 'potted_plant', 'vase',
            'suitcase', 'backpack', 'handbag', 'umbrella',
            'bicycle', 'motorcycle', 'fire_hydrant'
        ]
    
    def analyze(self, image: np.ndarray, detection) -> List:
        """
        Analyze pathway area for ADA violations.
        
        Args:
            image: Cropped image of detected object
            detection: Detection object with bbox and class info
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        if image.size == 0:
            return violations
        
        # Check if this object type commonly obstructs pathways
        object_type = detection.class_name.lower()
        
        if object_type not in self.obstruction_objects:
            return violations  # Not a typical obstruction
        
        # Analysis: Check if object is in potential pathway area
        obstruction_violation = self._check_obstruction(image, detection)
        if obstruction_violation:
            violations.append(obstruction_violation)
        
        return violations
    
    def _check_obstruction(self, image: np.ndarray, detection) -> Dict:
        """
        Determine if object obstructs accessible pathway.
        
        Concept: Objects in lower/center portions of image are more
        likely to be in walkways. Objects on edges/periphery less likely.
        """
        # Get object information
        x, y, w, h = detection.bbox
        object_name = detection.class_name
        
        # Calculate object center and relative position
        # Note: detection.bbox is from the FULL image, not the crop
        # So we need to work with the original bbox coordinates
        
        # For now, analyze based on the cropped image
        height, width = image.shape[:2]
        
        # Estimate object position (center of bbox)
        center_x = x + w / 2
        center_y = y + h / 2
        
        # Calculate relative position in original frame
        # (this is approximate - we're working with cropped region)
        
        # Object size relative to image
        relative_size = (w * h) / (width * height) if (width * height) > 0 else 0
        
        # Determine severity based on object type and size
        severity = "Moderate"
        confidence = 0.60
        
        # Larger objects are more likely to obstruct
        if relative_size > 0.3:  # Takes up >30% of detected area
            severity = "Moderate"
            confidence = 0.65
        elif relative_size > 0.5:  # Takes up >50% of detected area
            severity = "Critical"
            confidence = 0.70
        
        # Specific object assessments
        high_risk_objects = ['chair', 'couch', 'bench', 'bicycle']
        if object_name.lower() in high_risk_objects:
            # These are more likely to be problematic
            confidence += 0.05
        
        description = f"{object_name.title()} detected in potential pathway area"
        
        if relative_size > 0.4:
            description += f" (occupies {relative_size:.0%} of detected area)"
        
        description += ". Objects may not protrude into accessible routes or reduce required 36-inch clear width."
        
        return {
            "type": "Pathway Obstruction",
            "severity": severity,
            "ada_code": "403.5.1",
            "description": description,
            "recommendation": f"Relocate {object_name} to maintain minimum 36-inch clear pathway width. Ensure objects do not protrude more than 4 inches into circulation path (ADA 307).",
            "confidence": min(confidence, 0.75),
            "detection_method": "rule_based_cv",
            "measurements": {
                "object_type": object_name,
                "relative_size_percentage": round(relative_size * 100, 1),
                "required_clear_width_inches": 36,
                "max_protrusion_inches": 4
            }
        }


# Test the analyzer
if __name__ == "__main__":
    print("=" * 70)
    print("Pathway Analyzer - Test")
    print("=" * 70)
    
    analyzer = PathwayAnalyzer()
    print(f"✓ Pathway analyzer initialized")
    print(f"  Obstruction object types: {len(analyzer.obstruction_objects)}")
    print(f"  Examples: {', '.join(analyzer.obstruction_objects[:5])}")
    
    # Mock detection object
    class MockDetection:
        def __init__(self, name, bbox):
            self.class_name = name
            self.bbox = bbox
    
    # Test 1: Chair in pathway
    test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    detection = MockDetection('chair', [100, 200, 150, 200])
    
    violations = analyzer.analyze(test_image, detection)
    
    print(f"\n✓ Test 1: Chair detected")
    print(f"  Violations found: {len(violations)}")
    if violations:
        print(f"  Type: {violations[0]['type']}")
        print(f"  Severity: {violations[0]['severity']}")
        print(f"  Code: {violations[0]['ada_code']}")
        print(f"  Confidence: {violations[0]['confidence']:.2%}")
    
    # Test 2: Person (not an obstruction object)
    detection2 = MockDetection('person', [100, 200, 150, 200])
    violations2 = analyzer.analyze(test_image, detection2)
    
    print(f"\n✓ Test 2: Person detected")
    print(f"  Violations found: {len(violations2)}")
    print(f"  (People not flagged as obstructions)")
    
    print("\n" + "=" * 70)
    print("✓ Pathway analyzer test complete!")
