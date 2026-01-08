"""
Base Analyzer Interface

This defines the standard interface that all compliance analyzers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np
from dataclasses import dataclass


@dataclass
class ViolationResult:
    """Standard format for a detected ADA violation."""
    type: str
    severity: str
    ada_code: str
    description: str
    recommendation: str
    confidence: float
    detection_method: str = "unknown"
    measurements: Dict = None
    
    def __post_init__(self):
        if self.measurements is None:
            self.measurements = {}
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "ada_code": self.ada_code,
            "description": self.description,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "detection_method": self.detection_method,
            "measurements": self.measurements
        }


class BaseAnalyzer(ABC):
    """Abstract base class for all compliance analyzers."""
    
    def __init__(self, name: str = "BaseAnalyzer"):
        self.name = name
        self.analysis_count = 0
    
    @abstractmethod
    def analyze_detection(self, image: np.ndarray, detection) -> List[ViolationResult]:
        """Analyze a single detected object for ADA violations."""
        pass
    
    def analyze_all_detections(self, image: np.ndarray, detections: List) -> Dict:
        """Analyze all detected objects in an image."""
        results = {}
        
        print(f"\n{'='*60}")
        print(f"Analyzing {len(detections)} objects using {self.name}")
        print('='*60)
        
        for i, detection in enumerate(detections):
            print(f"\nAnalyzing {detection.class_name}...")
            violations = self.analyze_detection(image, detection)
            violations_dict = [v.to_dict() for v in violations]
            
            results[f"detection_{i}"] = {
                "object": detection.class_name,
                "bbox": list(detection.bbox),
                "violations": violations_dict,
                "analysis_metadata": {
                    "analyzer_type": self.name,
                    "detection_index": i
                }
            }
            
            if violations:
                print(f"  Found {len(violations)} violation(s)")
                for v in violations:
                    print(f"    - {v.type} ({v.severity})")
            else:
                print(f"  No violations detected")
            
            self.analysis_count += 1
        
        return results
