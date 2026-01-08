"""
Configuration file for ADA Compliance Detection System

This file stores all configuration settings including API keys,
file paths, and detection parameters.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
TEST_IMAGES_DIR = PROJECT_ROOT / "test_images"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Create directories if they don't exist
TEST_IMAGES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# API Configuration
# NOTE: In production, use environment variables or .env file for security
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# YOLOv8 Configuration
YOLO_MODEL = "yolov8n.pt"  # 'n' = nano (fastest, smallest)
YOLO_CONFIDENCE_THRESHOLD = 0.5  # Only keep detections with >50% confidence

# Video Processing Configuration
FRAMES_TO_EXTRACT = 5  # Number of frames to extract from videos
VIDEO_SKIP_SECONDS = 2  # Extract one frame every N seconds

# Object Detection - Classes we care about for ADA compliance
# These are COCO dataset class IDs that YOLOv8 is trained on
RELEVANT_CLASSES = {
    0: "person",           # For pathway analysis
    2: "car",              # For parking analysis
    7: "truck",            # For parking analysis
    13: "stop_sign",       # For signage analysis
    14: "parking_meter",   # For parking analysis
    56: "chair",           # Potential obstruction
    57: "couch",           # Potential obstruction
    58: "potted_plant",    # Potential obstruction
    60: "dining_table",    # Potential obstruction
    61: "toilet",          # Restroom features
    62: "tv",              # Potential obstruction
    64: "mouse",           # Potential obstruction (display items)
    73: "book",            # Potential obstruction
}

# Violation severity levels
SEVERITY_CRITICAL = "Critical"
SEVERITY_MODERATE = "Moderate"
SEVERITY_MINOR = "Minor"

# Color codes for visualization (BGR format for OpenCV)
COLOR_CRITICAL = (0, 0, 255)      # Red
COLOR_MODERATE = (0, 165, 255)    # Orange
COLOR_MINOR = (0, 255, 255)       # Yellow
COLOR_COMPLIANT = (0, 255, 0)     # Green

# Visualization settings
BBOX_THICKNESS = 2
FONT_SCALE = 0.6
FONT_THICKNESS = 2

print("✓ Configuration loaded successfully")
