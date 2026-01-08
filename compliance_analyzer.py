"""
Compliance Analyzer - Factory Pattern

This module provides a unified interface for different analyzer types.
It acts as a factory that creates the appropriate analyzer based on configuration.

Key Concept - Factory Pattern:
Instead of hardcoding which analyzer to use, this "factory" creates
the right analyzer based on a parameter. This makes it easy to swap
analyzers without changing other code.
"""

from typing import List, Dict
import numpy as np

from base_analyzer import BaseAnalyzer


class ComplianceAnalyzer:
    """
    Factory class that creates and wraps the appropriate analyzer.
    
    This maintains backward compatibility with existing code while
    allowing easy switching between analyzer types.
    
    Usage:
        # Rule-based (computer vision)
        analyzer = ComplianceAnalyzer(analyzer_type='rule_based')
        
        # Claude API
        analyzer = ComplianceAnalyzer(analyzer_type='claude')
        
        # Hybrid (both)
        analyzer = ComplianceAnalyzer(analyzer_type='hybrid')
    """
    
    def __init__(self, 
                 use_mock: bool = False,
                 analyzer_type: str = 'rule_based'):
        """
        Initialize the compliance analyzer.
        
        Args:
            use_mock: For backward compatibility (used by claude analyzer)
            analyzer_type: Type of analyzer to use
                          Options: 'rule_based', 'claude', 'hybrid'
        
        The factory creates the appropriate analyzer instance.
        """
        self.analyzer_type = analyzer_type
        self.use_mock = use_mock
        
        # Create the appropriate analyzer
        self.analyzer = self._create_analyzer(analyzer_type, use_mock)
        
        print(f"✓ Compliance analyzer initialized: {self.analyzer.name}")
    
    def _create_analyzer(self, analyzer_type: str, use_mock: bool) -> BaseAnalyzer:
        """
        Factory method to create the appropriate analyzer.
        
        Args:
            analyzer_type: Type of analyzer
            use_mock: Whether to use mock mode
            
        Returns:
            Instance of BaseAnalyzer subclass
        """
        if analyzer_type == 'rule_based':
            try:
                from rule_based_analyzer import RuleBasedAnalyzer
                return RuleBasedAnalyzer()
            except ImportError:
                print("⚠ Rule-based analyzer not available yet, using Claude API")
                analyzer_type = 'claude'
        
        if analyzer_type == 'claude':
            from claude_analyzer import ClaudeAPIAnalyzer
            return ClaudeAPIAnalyzer(use_mock=use_mock)
        
        elif analyzer_type == 'hybrid':
            try:
                from hybrid_analyzer import HybridAnalyzer
                return HybridAnalyzer()
            except ImportError:
                print("⚠ Hybrid analyzer not available yet, using rule-based")
                from rule_based_analyzer import RuleBasedAnalyzer
                return RuleBasedAnalyzer()
        
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")
    
    def analyze_detection(self, image: np.ndarray, detection) -> List:
        """
        Analyze a single detected object.
        
        Args:
            image: Full image
            detection: DetectionResult object
            
        Returns:
            List of violations (as dicts for backward compatibility)
        
        This delegates to the underlying analyzer.
        """
        violations = self.analyzer.analyze_detection(image, detection)
        # Convert ViolationResult objects to dicts for backward compatibility
        return [v.to_dict() if hasattr(v, 'to_dict') else v for v in violations]
    
    def analyze_all_detections(self,
                               image: np.ndarray,
                               detections: List) -> Dict:
        """
        Analyze all detected objects in an image.
        
        Args:
            image: Full image
            detections: List of DetectionResult objects
            
        Returns:
            Dictionary mapping detection IDs to analysis results
        
        This is the main method used by demo.py and other code.
        """
        return self.analyzer.analyze_all_detections(image, detections)
    
    def get_analyzer_info(self) -> Dict:
        """
        Get information about the current analyzer.
        
        Returns:
            Dictionary with analyzer metadata
        """
        return {
            "analyzer_type": self.analyzer_type,
            "analyzer_name": self.analyzer.name,
            "use_mock": self.use_mock,
            "total_analyses": self.analyzer.analysis_count
        }


# Convenience function for creating analyzers
def create_analyzer(analyzer_type: str = 'rule_based', 
                   use_mock: bool = False) -> ComplianceAnalyzer:
    """
    Convenience function to create a compliance analyzer.
    
    Args:
        analyzer_type: Type of analyzer ('rule_based', 'claude', 'hybrid')
        use_mock: Whether to use mock mode
        
    Returns:
        ComplianceAnalyzer instance
    """
    return ComplianceAnalyzer(use_mock=use_mock, analyzer_type=analyzer_type)


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("Compliance Analyzer Factory - Test")
    print("=" * 70)
    
    # Test creating different analyzer types
    print("\nTest 1: Create Claude analyzer")
    claude_analyzer = ComplianceAnalyzer(analyzer_type='claude', use_mock=True)
    info = claude_analyzer.get_analyzer_info()
    print(f"  Type: {info['analyzer_type']}")
    print(f"  Name: {info['analyzer_name']}")
    
    print("\nTest 2: Try to create rule-based analyzer")
    try:
        rule_analyzer = ComplianceAnalyzer(analyzer_type='rule_based')
        print(f"  ✓ Created: {rule_analyzer.analyzer.name}")
    except Exception as e:
        print(f"  Expected: Rule-based not implemented yet")
    
    print("\nTest 3: Using convenience function")
    analyzer = create_analyzer('claude', use_mock=True)
    print(f"  ✓ Created via convenience function")
    
    print("\n✓ Factory pattern test complete!")
