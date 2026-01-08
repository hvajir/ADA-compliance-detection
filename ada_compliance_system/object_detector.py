"""
Object Detector Module

This module handles object detection in images using YOLO-style detection.

IMPORTANT CONCEPT - Abstraction:
We're creating an "interface" (DetectionResult class and ObjectDetector class)
that defines HOW to use object detection, regardless of the specific model.
This means we can swap YOLO for another model later without changing other code.

Technical Terms:
- Bounding Box: Rectangle around a detected object [x, y, width, height]
- Confidence: How sure the model is (0.0 to 1.0, where 1.0 = 100% confident)
- Class: What type of object (door, car, person, etc.)
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
import config

@dataclass
class DetectionResult:
    """
    Data class to store information about a detected object.
    
    Why use @dataclass?
    - Automatically creates __init__, __repr__, etc.
    - Clean way to store structured data
    - Type hints make code more readable
    
    Attributes:
        class_id: Numeric ID of the object class
        class_name: Human-readable name (e.g., "car", "door")
        confidence: How confident the model is (0.0-1.0)
        bbox: Bounding box [x, y, width, height] in pixels
        center: Center point (x, y) of the bounding box
    """
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    center: Tuple[int, int]
    
    @property
    def x(self) -> int:
        """X coordinate of top-left corner"""
        return self.bbox[0]
    
    @property
    def y(self) -> int:
        """Y coordinate of top-left corner"""
        return self.bbox[1]
    
    @property
    def width(self) -> int:
        """Width of bounding box"""
        return self.bbox[2]
    
    @property
    def height(self) -> int:
        """Height of bounding box"""
        return self.bbox[3]
    
    def get_crop(self, image: np.ndarray) -> np.ndarray:
        """
        Extract the region of the image inside this bounding box.
        
        Args:
            image: Full image
            
        Returns:
            Cropped image containing just the detected object
            
        Why crop? We'll send these regions to Claude for detailed analysis.
        """
        x, y, w, h = self.bbox
        return image[y:y+h, x:x+w]


class ObjectDetector:
    """
    Handles object detection in images.
    
    Architecture Pattern: This class provides a consistent interface
    whether we're using real YOLO or a mock detector.
    """
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize the object detector.
        
        Args:
            use_mock: If True, use mock detection (for demo/testing)
                     If False, use real YOLO (requires ultralytics)
        
        Why have a mock mode?
        - Can develop/test without the full model
        - Faster for testing
        - Shows what the real output will look like
        """
        self.use_mock = use_mock
        self.confidence_threshold = config.YOLO_CONFIDENCE_THRESHOLD
        
        if not use_mock:
            try:
                from ultralytics import YOLO
                self.model = YOLO(config.YOLO_MODEL)
                print(f"✓ Loaded YOLO model: {config.YOLO_MODEL}")
            except ImportError:
                print("⚠ ultralytics not installed, falling back to mock mode")
                self.use_mock = True
        
        if self.use_mock:
            print("ℹ Using mock detector (simulated detections)")
    
    def detect(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Detect objects in an image.
        
        Args:
            image: Image as numpy array (from VideoProcessor)
            
        Returns:
            List of DetectionResult objects
            
        This is the main method - it analyzes the image and returns
        all detected objects with their locations and classifications.
        """
        if self.use_mock:
            return self._mock_detect(image)
        else:
            return self._yolo_detect(image)
    
    def _mock_detect(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Mock detection for testing/demo purposes.
        
        Simulates finding objects using simple computer vision techniques:
        - Edge detection to find rectangular shapes (doors, signs)
        - Color detection for specific features
        
        This is simplified but demonstrates the concept.
        """
        height, width = image.shape[:2]
        detections = []
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use Canny edge detection to find edges
        # Technical: Canny finds rapid changes in brightness (edges)
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours (continuous edges forming shapes)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze each contour to simulate object detection
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size - ignore tiny or huge detections
            area = w * h
            if area < 1000 or area > (width * height * 0.5):
                continue
            
            # Simulate classification based on aspect ratio and position
            aspect_ratio = w / h if h > 0 else 0
            
            # Heuristics (rules of thumb) to guess object type:
            if 0.3 < aspect_ratio < 0.7 and y > height * 0.3:
                # Tall and thin, lower in image = likely a door
                class_id = 0
                class_name = "door"
                confidence = 0.75
            elif aspect_ratio > 1.5 and w > width * 0.2:
                # Wide rectangle = possibly a vehicle
                class_id = 2
                class_name = "car"
                confidence = 0.65
            elif w < width * 0.3 and h < height * 0.3:
                # Small rectangle = possibly signage or obstacle
                class_id = 14
                class_name = "sign"
                confidence = 0.60
            else:
                # Unknown object
                class_id = 99
                class_name = "object"
                confidence = 0.50
            
            # Only keep high-confidence detections
            if confidence >= self.confidence_threshold:
                center = (x + w // 2, y + h // 2)
                detection = DetectionResult(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x, y, w, h),
                    center=center
                )
                detections.append(detection)
        
        print(f"  Mock detector found {len(detections)} objects")
        return detections
    
    def _yolo_detect(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Real YOLO detection (when ultralytics is available).
        
        YOLO (You Only Look Once) is a neural network that:
        1. Looks at the whole image once
        2. Predicts bounding boxes and classes simultaneously
        3. Very fast compared to older methods
        """
        results = self.model(image, verbose=False)
        detections = []
        
        # Parse YOLO results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extract detection info
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                # Filter by confidence
                if confidence < self.confidence_threshold:
                    continue
                
                # Convert to our format (x, y, width, height)
                x, y = int(x1), int(y1)
                w, h = int(x2 - x1), int(y2 - y1)
                center = (x + w // 2, y + h // 2)
                
                # Get class name from COCO dataset
                class_name = result.names[class_id]
                
                detection = DetectionResult(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x, y, w, h),
                    center=center
                )
                detections.append(detection)
        
        return detections
    
    def filter_relevant_objects(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """
        Filter detections to only keep ADA-relevant objects.
        
        Args:
            detections: All detected objects
            
        Returns:
            Filtered list of only relevant objects
            
        Why filter?
        - YOLO detects 80 different object types
        - We only care about ~15 for accessibility
        - Reduces noise and API costs (fewer objects to analyze)
        """
        relevant = []
        
        for detection in detections:
            # Check if this class is in our relevant classes list
            if detection.class_id in config.RELEVANT_CLASSES:
                relevant.append(detection)
                print(f"  ✓ Found relevant object: {detection.class_name} "
                      f"({detection.confidence:.2f} confidence)")
        
        return relevant


def visualize_detections(image: np.ndarray, 
                        detections: List[DetectionResult],
                        save_path: str = None) -> np.ndarray:
    """
    Draw bounding boxes on the image to visualize detections.
    
    Args:
        image: Original image
        detections: List of detected objects
        save_path: Optional path to save the annotated image
        
    Returns:
        Annotated image with bounding boxes
        
    Why visualize?
    - Helps debug detection issues
    - Shows users what was detected
    - Makes the demo more impressive!
    """
    # Make a copy so we don't modify the original
    annotated = image.copy()
    
    for detection in detections:
        x, y, w, h = detection.bbox
        
        # Choose color based on object type
        color = (0, 255, 0)  # Default green
        
        # Draw rectangle
        cv2.rectangle(annotated, (x, y), (x + w, y + h), 
                     color, config.BBOX_THICKNESS)
        
        # Create label text
        label = f"{detection.class_name}: {detection.confidence:.2f}"
        
        # Calculate text size for background
        (text_w, text_h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 
            config.FONT_SCALE, config.FONT_THICKNESS
        )
        
        # Draw label background (for readability)
        cv2.rectangle(annotated, (x, y - text_h - 10), 
                     (x + text_w, y), color, -1)
        
        # Draw label text
        cv2.putText(annotated, label, (x, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE,
                   (255, 255, 255), config.FONT_THICKNESS)
    
    if save_path:
        cv2.imwrite(save_path, annotated)
        print(f"✓ Saved annotated image to: {save_path}")
    
    return annotated


# Demo/test code
if __name__ == "__main__":
    """
    Test the object detector with our test image.
    """
    print("=" * 60)
    print("Object Detector - Demo Mode")
    print("=" * 60)
    
    # Load test image
    from video_processor import process_image_file
    test_image_path = config.TEST_IMAGES_DIR / "test_store_entrance.jpg"
    
    if test_image_path.exists():
        print(f"\nLoading test image: {test_image_path.name}")
        image = process_image_file(str(test_image_path))
        
        # Create detector
        print("\nInitializing detector...")
        detector = ObjectDetector(use_mock=True)
        
        # Detect objects
        print("\nRunning detection...")
        detections = detector.detect(image)
        
        print(f"\n✓ Detected {len(detections)} objects")
        for i, det in enumerate(detections, 1):
            print(f"  {i}. {det.class_name} at {det.bbox} "
                  f"(confidence: {det.confidence:.2f})")
        
        # Filter for relevant objects
        print("\nFiltering for ADA-relevant objects...")
        relevant = detector.filter_relevant_objects(detections)
        print(f"✓ Found {len(relevant)} relevant objects")
        
        # Visualize
        print("\nCreating visualization...")
        output_path = str(config.OUTPUTS_DIR / "detections_test.jpg")
        annotated = visualize_detections(image, detections, output_path)
        
        print("\n✓ Object detection test complete!")
    else:
        print(f"Test image not found: {test_image_path}")
        print("Run video_processor.py first to create test image")
