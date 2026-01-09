"""
Rule-Based Analyzer - Main Coordinator

Coordinates all CV-based analyzers for ADA compliance detection.
Uses traditional computer vision techniques (no neural networks).

This is the main entry point that routes detections to specialized analyzers.
"""

import numpy as np
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from base_analyzer import BaseAnalyzer, ViolationResult
from cv_rules.door_analyzer import DoorAnalyzer
from cv_rules.parking_analyzer import ParkingAnalyzer
from cv_rules.pathway_analyzer import PathwayAnalyzer
from cv_rules.ramp_analyzer import RampAnalyzer
from cv_rules.signage_analyzer import SignageAnalyzer


class RuleBasedAnalyzer(BaseAnalyzer):
    """
    Main rule-based analyzer using computer vision techniques.
    
    Routes detected objects to appropriate specialized analyzers:
    - Doors → DoorAnalyzer
    - Parking → ParkingAnalyzer
    - Obstructions → PathwayAnalyzer
    - Ramps → RampAnalyzer
    - Signs → SignageAnalyzer
    """
    
    def __init__(self):
        """Initialize all specialized analyzers."""
        super().__init__(name="rule_based_cv")
        
        # Initialize all specialized analyzers
        self.door_analyzer = DoorAnalyzer()
        self.parking_analyzer = ParkingAnalyzer()
        self.pathway_analyzer = PathwayAnalyzer()
        self.ramp_analyzer = RampAnalyzer()
        self.signage_analyzer = SignageAnalyzer()
        
        # Object type mappings
        self.door_objects = ['door', 'entrance']
        self.parking_objects = ['car', 'truck', 'bus', 'parking']
        self.ramp_objects = ['ramp', 'stairs', 'steps']
        self.sign_objects = ['sign', 'signage', 'stop_sign', 'street_sign']
        
        print(f"✓ Rule-based analyzer initialized with 5 specialized analyzers")
    
    def analyze_detection(self, image: np.ndarray, detection) -> List[ViolationResult]:
        """
        Analyze a detected object using appropriate CV analyzer.
        
        Args:
            image: Full image (numpy array)
            detection: DetectionResult object from YOLO
            
        Returns:
            List of ViolationResult objects
        """
        object_type = detection.class_name.lower()
        
        # Get cropped region of detected object
        try:
            cropped = detection.get_crop(image)
        except Exception as e:
            print(f"  ⚠ Error cropping image: {e}")
            return []
        
        # Route to appropriate analyzer
        violations_dicts = []
        
        if object_type in self.door_objects:
            violations_dicts = self.door_analyzer.analyze(cropped, detection)
        
        elif object_type in self.parking_objects:
            violations_dicts = self.parking_analyzer.analyze(cropped, detection)
        
        elif object_type in self.ramp_objects:
            violations_dicts = self.ramp_analyzer.analyze(cropped, detection)
        
        elif object_type in self.sign_objects:
            violations_dicts = self.signage_analyzer.analyze(cropped, detection)
        
        else:
            # Check if object might obstruct pathways
            violations_dicts = self.pathway_analyzer.analyze(cropped, detection)
        
        # Convert dictionaries to ViolationResult objects
        violations = []
        for v_dict in violations_dicts:
            try:
                violation = ViolationResult(
                    type=v_dict['type'],
                    severity=v_dict['severity'],
                    ada_code=v_dict['ada_code'],
                    description=v_dict['description'],
                    recommendation=v_dict['recommendation'],
                    confidence=v_dict['confidence'],
                    detection_method=v_dict.get('detection_method', 'rule_based_cv'),
                    measurements=v_dict.get('measurements', {})
                )
                violations.append(violation)
            except Exception as e:
                print(f"  ⚠ Error creating ViolationResult: {e}")
        
        return violations
    
    def get_analyzer_info(self) -> dict:
        """Get information about this analyzer and its capabilities."""
        info = super().get_analyzer_info()
        info['specialized_analyzers'] = {
            'door': 'Aspect ratio analysis, edge detection, hardware detection',
            'parking': 'Color detection (HSV), sign position analysis',
            'pathway': 'Obstruction detection, clearance analysis',
            'ramp': 'Slope estimation, handrail detection',
            'signage': 'Contrast analysis, tactile feature detection'
        }
        return info


# Test the complete system
if __name__ == "__main__":
    print("=" * 70)
    print("Rule-Based Analyzer System - Integration Test")
    print("=" * 70)
    
    analyzer = RuleBasedAnalyzer()
    
    print(f"\n✓ System initialized")
    print(f"  Analyzer name: {analyzer.name}")
    
    # Mock detection class
    class MockDetection:
        def __init__(self, class_name, bbox):
            self.class_name = class_name
            self.bbox = bbox
            self.confidence = 0.85
        
        def get_crop(self, image):
            x, y, w, h = self.bbox
            return image[y:y+h, x:x+w]
    
    # Test with different object types
    test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    test_cases = [
        ('door', [100, 100, 80, 300]),  # Narrow door
        ('car', [200, 200, 150, 100]),  # Parking
        ('chair', [300, 300, 100, 100]), # Obstruction
    ]
    
    print(f"\n{'='*70}")
    print("Running test cases:")
    print('='*70)
    
    for obj_type, bbox in test_cases:
        detection = MockDetection(obj_type, bbox)
        violations = analyzer.analyze_detection(test_image, detection)
        
        print(f"\n✓ Tested: {obj_type}")
        print(f"  Violations found: {len(violations)}")
        
        for v in violations:
            print(f"    - {v.type} ({v.severity}) - Confidence: {v.confidence:.0%}")
    
    print("\n" + "=" * 70)
    print("✓ Integration test complete!")
    print("=" * 70)
