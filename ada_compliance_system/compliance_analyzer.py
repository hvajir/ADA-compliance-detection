"""
Compliance Analyzer Module

This module sends detected objects to Claude API for detailed ADA compliance analysis.

Key Concepts:
- API: Application Programming Interface - a way for programs to talk to each other
- REST API: Sends HTTP requests (like a web browser) and gets responses
- JSON: JavaScript Object Notation - a standard format for structured data
- Base64: A way to encode binary data (images) as text for sending over the internet
"""

import base64
import json
import os
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
import cv2

import config
import prompts
from object_detector import DetectionResult

# Try to import anthropic SDK, but don't fail if not available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠ anthropic package not installed - using mock mode")


class ViolationResult:
    """
    Stores information about a detected ADA violation.
    
    Similar to DetectionResult, but for violations instead of objects.
    """
    def __init__(self, violation_dict: Dict):
        """
        Initialize from Claude's JSON response.
        
        Args:
            violation_dict: Dictionary from Claude's JSON response
        """
        self.type = violation_dict.get("type", "Unknown")
        self.severity = violation_dict.get("severity", "Minor")
        self.ada_code = violation_dict.get("ada_code", "N/A")
        self.description = violation_dict.get("description", "")
        self.recommendation = violation_dict.get("recommendation", "")
        self.confidence = violation_dict.get("confidence", 0.5)
    
    def __repr__(self):
        return f"Violation(type={self.type}, severity={self.severity}, confidence={self.confidence:.2f})"
    
    def to_dict(self) -> Dict:
        """Convert back to dictionary for saving/serialization"""
        return {
            "type": self.type,
            "severity": self.severity,
            "ada_code": self.ada_code,
            "description": self.description,
            "recommendation": self.recommendation,
            "confidence": self.confidence
        }


class ComplianceAnalyzer:
    """
    Analyzes detected objects for ADA compliance using Claude API.
    
    Architecture:
    1. Takes a detected object (DetectionResult)
    2. Crops the region from the image
    3. Converts to base64 (for sending to API)
    4. Gets appropriate prompt for object type
    5. Sends to Claude API
    6. Parses JSON response into ViolationResult objects
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize the compliance analyzer.
        
        Args:
            use_mock: If True, simulate Claude responses (for testing)
                     If False, use real Claude API
        
        Why mock mode?
        - Test without API key
        - Develop without internet
        - Avoid API costs during development
        """
        self.use_mock = use_mock or not ANTHROPIC_AVAILABLE
        
        if not self.use_mock:
            # Get API key from environment variable
            api_key = os.getenv("ANTHROPIC_API_KEY") or config.ANTHROPIC_API_KEY
            
            if not api_key:
                print("⚠ ANTHROPIC_API_KEY not set, using mock mode")
                self.use_mock = True
            else:
                self.client = anthropic.Anthropic(api_key=api_key)
                print("✓ Claude API client initialized")
        
        if self.use_mock:
            print("ℹ Using mock compliance analysis (simulated violations)")
    
    def analyze_detection(self, 
                         image: np.ndarray, 
                         detection: DetectionResult) -> List[ViolationResult]:
        """
        Analyze a detected object for ADA compliance.
        
        Args:
            image: Full image (numpy array)
            detection: Detected object to analyze
            
        Returns:
            List of violations found (may be empty if compliant)
            
        This is the main method - it orchestrates the entire analysis process.
        """
        print(f"\nAnalyzing {detection.class_name}...")
        
        # Step 1: Crop the region of interest
        cropped = detection.get_crop(image)
        
        if cropped.size == 0:
            print("  ⚠ Invalid crop region, skipping")
            return []
        
        # Step 2: Get appropriate prompt for this object type
        prompt_text = prompts.get_prompt_for_object(detection.class_name)
        
        # Step 3: Send to Claude (real or mock)
        if self.use_mock:
            response = self._mock_analyze(detection.class_name)
        else:
            response = self._claude_analyze(cropped, prompt_text)
        
        # Step 4: Parse response into ViolationResult objects
        violations = self._parse_response(response)
        
        print(f"  Found {len(violations)} potential violation(s)")
        for v in violations:
            print(f"    - {v.type} ({v.severity})")
        
        return violations
    
    def _encode_image(self, image: np.ndarray) -> str:
        """
        Convert image to base64 string for API transmission.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Base64-encoded string
            
        Technical Concept - Base64 Encoding:
        Images are binary data (bytes). APIs expect text.
        Base64 converts binary → text so it can be sent in JSON.
        
        Example:
        Image bytes: [255, 216, 255, ...] (binary)
        Base64: "iVBORw0KGgoAAAANSUhEUgAA..." (text)
        """
        # Encode image as JPEG (compressed format)
        success, buffer = cv2.imencode('.jpg', image)
        
        if not success:
            raise ValueError("Failed to encode image")
        
        # Convert to base64 string
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return img_base64
    
    def _claude_analyze(self, image: np.ndarray, prompt: str) -> Dict:
        """
        Send image and prompt to Claude API for analysis.
        
        Args:
            image: Cropped image region
            prompt: ADA-specific analysis prompt
            
        Returns:
            Dictionary response from Claude
            
        Technical Concept - API Request:
        We're making an HTTP POST request to Claude's servers:
        1. Send: Image (base64) + Prompt (text)
        2. Claude analyzes the image
        3. Receive: JSON response with violations
        """
        # Encode image
        img_base64 = self._encode_image(image)
        
        try:
            # Make API call to Claude
            # This is the actual AI analysis happening!
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",  # Latest Claude model
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
            
            # Extract text response
            response_text = message.content[0].text
            
            # Parse JSON from response
            # Claude should return JSON, but we need to extract it
            response_json = self._extract_json(response_text)
            
            return response_json
            
        except Exception as e:
            print(f"  ⚠ API error: {e}")
            return {"violations": [], "overall_assessment": "Error during analysis", "notes": str(e)}
    
    def _extract_json(self, text: str) -> Dict:
        """
        Extract JSON from Claude's response.
        
        Args:
            text: Claude's full response (may include markdown, explanations)
            
        Returns:
            Parsed JSON dictionary
            
        Why needed?
        Claude might return:
        "Here's the analysis: ```json {...} ```"
        We need to extract just the {...} part and parse it.
        """
        # Try to parse as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Look for JSON within code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_text = text[start:end].strip()
        else:
            # Try to find JSON by looking for { }
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != 0:
                json_text = text[start:end]
            else:
                json_text = text
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"  ⚠ Failed to parse JSON: {e}")
            return {"violations": [], "overall_assessment": "Parse error", "notes": text[:200]}
    
    def _mock_analyze(self, object_name: str) -> Dict:
        """
        Simulate Claude's response for testing.
        
        Args:
            object_name: Type of object detected
            
        Returns:
            Mock JSON response
            
        Why mock responses?
        - Test the pipeline without API calls
        - Predictable results for debugging
        - No API costs during development
        """
        # Create different mock responses based on object type
        if object_name in ["door", "entrance"]:
            return {
                "violations": [
                    {
                        "type": "Door Width",
                        "severity": "Critical",
                        "ada_code": "404.2.3",
                        "description": "Door opening appears narrower than the required 32-inch clear width",
                        "recommendation": "Widen door opening or replace with a wider door unit",
                        "confidence": 0.7
                    }
                ],
                "overall_assessment": "Potential door width violation detected",
                "notes": "Mock analysis - precise measurement needed for verification"
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
                "overall_assessment": "Accessible parking signage appears to be missing",
                "notes": "Mock analysis - verify signage requirements"
            }
        
        elif object_name in ["chair", "couch", "bench", "potted_plant"]:
            return {
                "violations": [
                    {
                        "type": "Obstruction",
                        "severity": "Moderate",
                        "ada_code": "403.5.1",
                        "description": "Object may be obstructing the required 36-inch clear pathway width",
                        "recommendation": "Relocate object to maintain minimum 36-inch clear pathway",
                        "confidence": 0.6
                    }
                ],
                "overall_assessment": "Potential pathway obstruction",
                "notes": "Mock analysis - verify actual pathway clearance"
            }
        
        else:
            # No violations for other objects
            return {
                "violations": [],
                "overall_assessment": "No obvious violations detected in this view",
                "notes": "Mock analysis - limited analysis for this object type"
            }
    
    def _parse_response(self, response: Dict) -> List[ViolationResult]:
        """
        Convert Claude's JSON response into ViolationResult objects.
        
        Args:
            response: Dictionary from Claude (or mock)
            
        Returns:
            List of ViolationResult objects
        """
        violations = []
        
        # Get violations array from response
        violations_data = response.get("violations", [])
        
        for violation_dict in violations_data:
            try:
                violation = ViolationResult(violation_dict)
                violations.append(violation)
            except Exception as e:
                print(f"  ⚠ Error parsing violation: {e}")
        
        return violations
    
    def analyze_all_detections(self, 
                              image: np.ndarray, 
                              detections: List[DetectionResult]) -> Dict[str, List[ViolationResult]]:
        """
        Analyze all detected objects in an image.
        
        Args:
            image: Full image
            detections: List of all detected objects
            
        Returns:
            Dictionary mapping detection index to violations
            
        This processes multiple objects in one image, tracking which
        violations came from which detection.
        """
        results = {}
        
        print(f"\n{'='*60}")
        print(f"Analyzing {len(detections)} detected objects for ADA compliance")
        print('='*60)
        
        for i, detection in enumerate(detections):
            violations = self.analyze_detection(image, detection)
            results[f"detection_{i}"] = {
                "object": detection.class_name,
                "bbox": detection.bbox,
                "violations": [v.to_dict() for v in violations]
            }
        
        return results


# Demo/test code
if __name__ == "__main__":
    """
    Test the compliance analyzer with a detected object.
    """
    print("=" * 70)
    print("Compliance Analyzer - Demo Mode")
    print("=" * 70)
    
    from video_processor import process_image_file
    from object_detector import ObjectDetector
    
    # Load test image
    test_image_path = config.TEST_IMAGES_DIR / "realistic_store.jpg"
    
    if test_image_path.exists():
        print(f"\nLoading test image...")
        image = process_image_file(str(test_image_path))
        
        # Detect objects
        print("\nDetecting objects...")
        detector = ObjectDetector(use_mock=True)
        detections = detector.detect(image)
        print(f"Found {len(detections)} objects")
        
        # Analyze for compliance
        print("\nAnalyzing for ADA compliance...")
        analyzer = ComplianceAnalyzer(use_mock=True)
        
        all_results = analyzer.analyze_all_detections(image, detections)
        
        # Display results
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        
        for key, result in all_results.items():
            print(f"\n{result['object'].upper()} at {result['bbox']}")
            print(f"  Violations: {len(result['violations'])}")
            for v in result['violations']:
                print(f"    - [{v['severity']}] {v['type']}: {v['description'][:60]}...")
        
        # Save results to JSON
        output_file = config.OUTPUTS_DIR / "compliance_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n✓ Results saved to: {output_file}")
        
    else:
        print(f"Test image not found: {test_image_path}")
