"""
Claude API Analyzer

Uses Claude API for ADA compliance analysis.
This is the existing logic extracted into the new modular structure.
"""

import base64
import json
import os
from typing import List
import numpy as np
import cv2

from base_analyzer import BaseAnalyzer, ViolationResult
import prompts

# Try to import anthropic SDK
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeAPIAnalyzer(BaseAnalyzer):
    """
    Analyzer that uses Claude API for compliance analysis.
    
    This wraps the existing Claude API logic into the new
    BaseAnalyzer interface.
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize Claude API analyzer.
        
        Args:
            use_mock: If True, return mock responses instead of calling API
        """
        super().__init__(name="claude_api")
        
        self.use_mock = use_mock or not ANTHROPIC_AVAILABLE
        
        if not self.use_mock:
            # Get API key from environment
            api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if not api_key:
                print("⚠ ANTHROPIC_API_KEY not set, using mock mode")
                self.use_mock = True
            else:
                self.client = anthropic.Anthropic(api_key=api_key)
                print("✓ Claude API client initialized")
        
        if self.use_mock:
            print("ℹ Using mock Claude responses")
    
    def analyze_detection(self, image: np.ndarray, detection) -> List[ViolationResult]:
        """
        Analyze a detected object using Claude API.
        
        Args:
            image: Full image
            detection: DetectionResult object
            
        Returns:
            List of ViolationResult objects
        """
        # Get cropped region
        cropped = detection.get_crop(image)
        
        if cropped.size == 0:
            return []
        
        # Get appropriate prompt
        prompt_text = prompts.get_prompt_for_object(detection.class_name)
        
        # Get response (mock or real)
        if self.use_mock:
            response = self._mock_analyze(detection.class_name)
        else:
            response = self._claude_analyze(cropped, prompt_text)
        
        # Parse into ViolationResult objects
        violations = self._parse_response(response, detection.class_name)
        
        return violations
    
    def _encode_image(self, image: np.ndarray) -> str:
        """Convert image to base64 for API transmission."""
        success, buffer = cv2.imencode('.jpg', image)
        if not success:
            raise ValueError("Failed to encode image")
        return base64.b64encode(buffer).decode('utf-8')
    
    def _claude_analyze(self, image: np.ndarray, prompt: str) -> dict:
        """Send request to Claude API."""
        img_base64 = self._encode_image(image)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": img_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompts.SYSTEM_PROMPT + "\n\n" + prompt
                            }
                        ]
                    }
                ]
            )
            
            response_text = message.content[0].text
            return self._extract_json(response_text)
            
        except Exception as e:
            print(f"  ⚠ API error: {e}")
            return {
                "violations": [],
                "overall_assessment": "Error during analysis",
                "notes": str(e)
            }
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from Claude's response."""
        # Try parsing as-is
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Look for JSON in code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_text = text[start:end].strip()
        else:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != 0:
                json_text = text[start:end]
            else:
                json_text = text
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return {
                "violations": [],
                "overall_assessment": "Parse error",
                "notes": text[:200]
            }
    
    def _mock_analyze(self, object_name: str) -> dict:
        """Return mock responses for testing."""
        if object_name in ["door", "entrance"]:
            return {
                "violations": [
                    {
                        "type": "Door Width",
                        "severity": "Critical",
                        "ada_code": "404.2.3",
                        "description": "Door opening appears narrower than required 32-inch clear width",
                        "recommendation": "Widen door opening or replace with wider door unit",
                        "confidence": 0.7
                    }
                ],
                "overall_assessment": "Potential door width violation",
                "notes": "Mock analysis - requires verification"
            }
        
        elif object_name in ["car", "truck", "parking"]:
            return {
                "violations": [
                    {
                        "type": "Signage",
                        "severity": "Critical",
                        "ada_code": "502.6",
                        "description": "Missing or inadequate accessible parking signage",
                        "recommendation": "Install International Symbol of Accessibility sign at 60 inches minimum height",
                        "confidence": 0.8
                    }
                ],
                "overall_assessment": "Missing parking signage",
                "notes": "Mock analysis"
            }
        
        elif object_name in ["chair", "couch", "bench", "potted_plant"]:
            return {
                "violations": [
                    {
                        "type": "Obstruction",
                        "severity": "Moderate",
                        "ada_code": "403.5.1",
                        "description": "Object may obstruct required 36-inch clear pathway width",
                        "recommendation": "Relocate object to maintain minimum clear pathway",
                        "confidence": 0.6
                    }
                ],
                "overall_assessment": "Potential pathway obstruction",
                "notes": "Mock analysis"
            }
        
        else:
            return {
                "violations": [],
                "overall_assessment": "No obvious violations in this view",
                "notes": "Mock analysis"
            }
    
    def _parse_response(self, response: dict, object_name: str) -> List[ViolationResult]:
        """Convert Claude response to ViolationResult objects."""
        violations = []
        violations_data = response.get("violations", [])
        
        for v_dict in violations_data:
            try:
                violation = ViolationResult(
                    type=v_dict.get("type", "Unknown"),
                    severity=v_dict.get("severity", "Minor"),
                    ada_code=v_dict.get("ada_code", "N/A"),
                    description=v_dict.get("description", ""),
                    recommendation=v_dict.get("recommendation", ""),
                    confidence=v_dict.get("confidence", 0.5),
                    detection_method="claude_api"
                )
                violations.append(violation)
            except Exception as e:
                print(f"  ⚠ Error parsing violation: {e}")
        
        return violations


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("Claude API Analyzer - Test")
    print("=" * 70)
    
    # Create analyzer in mock mode
    analyzer = ClaudeAPIAnalyzer(use_mock=True)
    
    print(f"\nAnalyzer name: {analyzer.name}")
    print(f"Using mock mode: {analyzer.use_mock}")
    
    # Test mock response
    print("\nTesting mock response for 'door':")
    mock_response = analyzer._mock_analyze("door")
    print(f"Violations: {len(mock_response['violations'])}")
    
    if mock_response['violations']:
        v = mock_response['violations'][0]
        print(f"  Type: {v['type']}")
        print(f"  Severity: {v['severity']}")
        print(f"  Code: {v['ada_code']}")
    
    print("\n✓ Claude API analyzer test complete!")
