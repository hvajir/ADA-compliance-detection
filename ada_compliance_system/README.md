# ADA Compliance Detection System

AI-powered accessibility auditing for retail spaces using computer vision and large language models.

## 📋 Overview

This system automatically detects and analyzes ADA (Americans with Disabilities Act) compliance violations in retail spaces using:
- **YOLOv8** for object detection (Deep Learning Component)
- **Claude API** for compliance analysis (Proof of Concept)
- Automated visual reporting

## 🎯 Competition Demo - Quick Start

### For Your MIT Competition Demo:

1. **Install dependencies:**
   ```bash
   pip install opencv-python pillow numpy matplotlib python-dotenv ultralytics
   ```

2. **⚠️ CRITICAL: Switch to Real YOLO**
   
   Open `demo.py` and change:
   ```python
   run_demo(
       image_path,
       use_real_yolo=True,    # ⚠️ Change this to True!
       use_real_claude=False   # Keep False unless you have API key
   )
   ```

3. **Run the demo:**
   ```bash
   python3 demo.py test_images/your_image.jpg
   ```

## 📁 Project Structure

```
ada_compliance_system/
├── config.py                 # Configuration and settings
├── video_processor.py        # Video/image loading
├── object_detector.py        # YOLOv8 object detection
├── compliance_analyzer.py    # ADA compliance analysis
├── prompts.py               # ADA-specific prompts
├── visualizer.py            # Enhanced visualization
├── demo.py                  # Main demo script ⭐
├── test_images/             # Input images
└── outputs/                 # Generated reports
```

## 🚀 Usage

### Basic Usage:
```bash
python3 demo.py path/to/image.jpg
```

### What It Does:
1. Loads the image
2. Detects accessibility features (doors, parking, pathways)
3. Analyzes each feature for ADA violations
4. Generates annotated images
5. Saves JSON report with findings

### Output Files:
- `<image>_report.jpg` - Annotated image with violations
- `<image>_comparison.jpg` - Side-by-side before/after
- `<image>_report.json` - Detailed analysis data

## 🔧 System Architecture

```
Input Image
    ↓
Video Processor (Part 2)
    ↓
YOLOv8 Object Detection (Part 3) ← DEEP LEARNING
    ↓
Filter ADA-Relevant Objects
    ↓
Compliance Analyzer (Part 4)
    ↓
Visual Report Generator (Part 5)
    ↓
Output: Annotated Images + JSON Report
```

## 🎓 For Your Presentation

### Key Points to Emphasize:

1. **Deep Learning Component:**
   - YOLOv8 is a convolutional neural network
   - 225+ layers, trained on 1.2M images
   - Transfer learning approach

2. **Novel Application:**
   - First AI system for automated ADA compliance
   - Addresses real business problem ($20K-75K per lawsuit)
   - Social impact (accessibility for disabled persons)

3. **System Design:**
   - Modular architecture
   - Separation of concerns
   - Scalable to multiple locations

### Addressing the Claude API:

**If judges ask about deep learning:**
> "YOLOv8 object detection is our primary deep learning component. The compliance analysis currently uses Claude API to demonstrate feasibility. In production, this would be replaced with custom classification models trained on ADA violation data. The challenge is obtaining labeled training data - there's no public dataset of ADA violations."

## 🔄 Switching from Mock to Real Models

### Object Detection (YOLO):

In any script, change:
```python
# Mock (for testing):
detector = ObjectDetector(use_mock=True)

# Real (for competition):
detector = ObjectDetector(use_mock=False)
```

### Claude API:

1. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

2. In scripts, change:
   ```python
   # Mock:
   analyzer = ComplianceAnalyzer(use_mock=True)
   
   # Real:
   analyzer = ComplianceAnalyzer(use_mock=False)
   ```

## 📊 ADA Violations Detected

The system checks for:

1. **Parking:**
   - Missing signage (Critical)
   - Inadequate dimensions (Critical)
   - Missing access aisle (Critical)

2. **Entrances:**
   - Door width < 32" (Critical)
   - Threshold > 0.5" (Moderate)
   - Inaccessible hardware (Moderate)

3. **Pathways:**
   - Width < 36" (Critical)
   - Obstructions (Moderate)
   - Surface hazards (Minor)

4. **Ramps:**
   - Slope > 1:12 (Critical)
   - Missing handrails (Critical)
   - No edge protection (Moderate)

5. **Signage:**
   - Missing braille (Moderate)
   - Improper height (Minor)
   - Poor contrast (Minor)

## 🧪 Testing

Run individual modules:
```bash
# Test config
python3 config.py

# Test video processor
python3 video_processor.py

# Test object detector
python3 object_detector.py

# Test compliance analyzer
python3 compliance_analyzer.py

# Test visualizer
python3 visualizer.py

# Full pipeline test
python3 full_pipeline_demo.py
```

## 📝 Known Limitations

1. **Measurement Accuracy:**
   - Cannot measure exact dimensions without depth data
   - Flags potential violations for expert verification

2. **Visual-Only Detection:**
   - Cannot detect non-visual issues (door force, grab bar capacity)
   - Limited to ~40-60% of total ADA requirements

3. **Mock Classifier:**
   - Compliance analysis currently uses Claude API (placeholder)
   - Production would need custom-trained models

## 🔮 Future Enhancements

### Phase 2:
- Fine-tune YOLO on accessibility-specific dataset
- Integrate LiDAR for precise measurements
- Guided filming workflow

### Phase 3:
- Real-time security camera integration
- Multi-location dashboard
- Remediation tracking
- Mobile app

## 📚 Dependencies

```
opencv-python>=4.8.0      # Computer vision
ultralytics>=8.0.0        # YOLOv8
anthropic>=0.18.0         # Claude API (optional)
pillow>=10.0.0           # Image processing
numpy>=1.24.0            # Numerical computing
matplotlib>=3.7.0        # Visualization
python-dotenv>=1.0.0     # Environment variables
```

## 🎯 Competition Checklist

- [ ] Install ultralytics: `pip install ultralytics`
- [ ] Change `use_real_yolo=True` in demo.py
- [ ] Test on 3-5 different retail images
- [ ] Prepare presentation slides
- [ ] Practice 3-minute pitch
- [ ] Have backup screenshots ready
- [ ] Know how to explain YOLO architecture
- [ ] Be ready to discuss limitations honestly

## 🏆 Presentation Tips

1. **Start with problem:** ADA lawsuits cost $20K-75K
2. **Show live demo:** Run demo.py on test image
3. **Explain YOLO:** Show it detects objects in real-time
4. **Show results:** Display annotated image
5. **Discuss impact:** Make accessibility auditing affordable
6. **Address limitations:** Need custom models, more data
7. **Future vision:** Continuous monitoring, mobile app

## 📧 Support

For issues or questions during development, review:
- Technical spec document
- Individual module docstrings
- Test scripts in each module

## 🎓 MIT 6.S191 - Introduction to Deep Learning

**Team:** [Your Name]  
**Date:** January 2026  
**Project:** AI-Powered ADA Compliance Detection  
**Competition:** Project Proposal Pitch

---

**Good luck with your presentation! 🚀**
