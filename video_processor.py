"""
Video Processor Module

This module handles extracting key frames from video files for analysis.
Videos contain thousands of frames, but we only need a few representative frames.

Technical concepts:
- Videos are sequences of images (frames) shown rapidly
- We extract frames at intervals rather than analyzing every single frame
- This saves computation time and API costs
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import config

class VideoProcessor:
    """
    Handles video file processing and frame extraction.
    
    Why use a class?
    - Groups related functionality together (cohesion)
    - Can maintain state (like video properties)
    - Makes code reusable and testable
    """
    
    def __init__(self, video_path: str):
        """
        Initialize the video processor.
        
        Args:
            video_path: Path to the video file
            
        Technical note: __init__ is a "constructor" - runs when you create
        a new VideoProcessor object. It sets up the initial state.
        """
        self.video_path = Path(video_path)
        
        # Verify file exists
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Open video file using OpenCV
        self.video = cv2.VideoCapture(str(video_path))
        
        if not self.video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        self.fps = self.video.get(cv2.CAP_PROP_FPS)  # Frames per second
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0
        
        print(f"Video loaded: {self.video_path.name}")
        print(f"  Duration: {self.duration:.2f} seconds")
        print(f"  FPS: {self.fps:.2f}")
        print(f"  Total frames: {self.frame_count}")
    
    def extract_frames(self, num_frames: int = None) -> List[np.ndarray]:
        """
        Extract evenly spaced frames from the video.
        
        Args:
            num_frames: Number of frames to extract (default from config)
            
        Returns:
            List of frame images as numpy arrays
            
        How it works:
        1. Calculate which frame numbers to extract (evenly spaced)
        2. Jump to each frame position in the video
        3. Read the frame and store it
        4. Return all extracted frames
        
        Why numpy arrays? Images in OpenCV are represented as multi-dimensional
        arrays of pixel values. Each pixel has RGB values (Red, Green, Blue).
        """
        if num_frames is None:
            num_frames = config.FRAMES_TO_EXTRACT
        
        # Calculate frame indices to extract (evenly spaced)
        # Example: 100 frame video, extract 5 frames = frames 0, 25, 50, 75, 100
        frame_indices = np.linspace(0, self.frame_count - 1, num_frames, dtype=int)
        
        extracted_frames = []
        
        print(f"\nExtracting {num_frames} frames...")
        
        for idx, frame_num in enumerate(frame_indices):
            # Set video position to specific frame
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            
            # Read the frame
            success, frame = self.video.read()
            
            if success:
                extracted_frames.append(frame)
                timestamp = frame_num / self.fps
                print(f"  ✓ Frame {idx + 1}/{num_frames} at {timestamp:.2f}s")
            else:
                print(f"  ✗ Failed to read frame {frame_num}")
        
        return extracted_frames
    
    def save_frames(self, frames: List[np.ndarray], output_dir: str = None) -> List[Path]:
        """
        Save extracted frames as image files.
        
        Args:
            frames: List of frame images
            output_dir: Directory to save frames (default: outputs/)
            
        Returns:
            List of paths to saved frame files
            
        Technical note: We save frames so we can visualize them and
        use them later without re-processing the video.
        """
        if output_dir is None:
            output_dir = config.OUTPUTS_DIR
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        saved_paths = []
        video_name = self.video_path.stem  # Filename without extension
        
        print(f"\nSaving frames to {output_dir}/...")
        
        for idx, frame in enumerate(frames):
            # Create filename: video_name_frame_001.jpg
            filename = f"{video_name}_frame_{idx + 1:03d}.jpg"
            output_path = output_dir / filename
            
            # Save frame as JPEG
            # cv2.imwrite encodes the numpy array as an image file
            cv2.imwrite(str(output_path), frame)
            saved_paths.append(output_path)
            
            print(f"  ✓ Saved: {filename}")
        
        return saved_paths
    
    def process_image(self, image_path: str) -> np.ndarray:
        """
        Load a single image file (not a video).
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array
            
        Why this method? Our system should work with both videos AND images.
        This is called "flexible input handling".
        """
        img_path = Path(image_path)
        
        if not img_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read image file
        image = cv2.imread(str(img_path))
        
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        print(f"Image loaded: {img_path.name}")
        print(f"  Size: {image.shape[1]}x{image.shape[0]} pixels")
        
        return image
    
    def __del__(self):
        """
        Destructor - cleanup when object is destroyed.
        
        Technical note: Always release video resources to avoid memory leaks.
        This is called "resource management".
        """
        if hasattr(self, 'video'):
            self.video.release()


def process_video_file(video_path: str, num_frames: int = None) -> Tuple[List[np.ndarray], List[Path]]:
    """
    Convenience function to process a video file in one step.
    
    Args:
        video_path: Path to video file
        num_frames: Number of frames to extract
        
    Returns:
        Tuple of (frame_list, saved_paths)
        
    Why a standalone function? Sometimes you want simple, one-line usage
    without creating a VideoProcessor object explicitly.
    """
    processor = VideoProcessor(video_path)
    frames = processor.extract_frames(num_frames)
    saved_paths = processor.save_frames(frames)
    return frames, saved_paths


def process_image_file(image_path: str) -> np.ndarray:
    """
    Convenience function to load a single image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image as numpy array
    """
    processor = VideoProcessor.__new__(VideoProcessor)  # Create without __init__
    return processor.process_image(image_path)


# Demo/test code - runs when you execute this file directly
if __name__ == "__main__":
    """
    This block only runs if you execute: python3 video_processor.py
    It won't run if you import this module in another file.
    
    This is useful for testing individual modules.
    """
    print("=" * 60)
    print("Video Processor - Demo Mode")
    print("=" * 60)
    
    # Check if there are any video files in test_images
    import os
    test_files = list(config.TEST_IMAGES_DIR.glob("*.mp4")) + \
                 list(config.TEST_IMAGES_DIR.glob("*.mov")) + \
                 list(config.TEST_IMAGES_DIR.glob("*.avi"))
    
    if test_files:
        print(f"\nFound {len(test_files)} video file(s) in test_images/")
        test_video = test_files[0]
        print(f"Processing: {test_video.name}\n")
        
        frames, paths = process_video_file(str(test_video))
        
        print(f"\n✓ Successfully extracted {len(frames)} frames")
        print(f"✓ Frames saved to: {config.OUTPUTS_DIR}/")
    else:
        print("\nNo video files found in test_images/")
        print("Add a .mp4, .mov, or .avi file to test_images/ and run again")
        print("\nYou can also test with a single image:")
        
        # Check for image files
        image_files = list(config.TEST_IMAGES_DIR.glob("*.jpg")) + \
                     list(config.TEST_IMAGES_DIR.glob("*.png"))
        
        if image_files:
            test_image = image_files[0]
            print(f"\nProcessing image: {test_image.name}")
            img = process_image_file(str(test_image))
            print(f"✓ Image loaded successfully: {img.shape}")
        else:
            print("No image files (.jpg, .png) found either")
            print("Add some test media to test_images/ directory")
