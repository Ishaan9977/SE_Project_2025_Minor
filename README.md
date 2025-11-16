# ADAS System - LDWS, LKAS, FCWS with YOLOv8

An Advanced Driver Assistance System (ADAS) implementation featuring:
- **LDWS** (Lane Departure Warning System)
- **LKAS** (Lane Keeping Assistance System)
- **FCWS** (Forward Collision Warning System)

Built using **YOLOv8** for object detection and traditional computer vision for lane detection.

## Features

### Forward Collision Warning System (FCWS)
- Detects vehicles and obstacles ahead using YOLOv8
- Calculates distance to objects
- Provides visual warnings (WARNING/CRITICAL) when collision risk is detected
- Highlights risky objects in the forward path

### Lane Departure Warning System (LDWS)
- Detects lane markings using computer vision
- Monitors vehicle position relative to lane center
- Warns when vehicle is departing from the lane (left/right)
- Visual indicators show lane center and vehicle position

### Lane Keeping Assistance System (LKAS)
- Provides steering guidance to help stay in lane
- Visual steering wheel indicator
- Shows recommended steering angle
- Activates when vehicle drifts from lane center

## Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-capable GPU (optional, for faster inference)

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. YOLOv8 model will be automatically downloaded on first run (yolov8n.pt)

## Usage

### Basic Usage (Webcam)
```bash
python main.py
```

### Process Video File
```bash
python main.py --input path/to/video.mp4
```

### Save Output Video
```bash
python main.py --input path/to/video.mp4 --output output.mp4
```

### Use Different YOLOv8 Model
```bash
python main.py --model yolov8s.pt  # or yolov8m.pt, yolov8l.pt, yolov8x.pt
```

### Adjust Confidence Threshold
```bash
python main.py --conf 0.6  # Higher threshold = fewer but more confident detections
```

### Process Without Display (for headless systems)
```bash
python main.py --input video.mp4 --output output.mp4 --no-display
```

## Web Application (Flask)

The project includes a Flask web application for accessing the ADAS system through a browser interface.

### Start Flask Web Server
```bash
python app.py
```

Then open your browser and navigate to: `http://localhost:5000`

### Web Interface Features

- **Real-time Video Streaming**: View processed video feed in your browser
- **Webcam Support**: Start webcam feed directly from the interface
- **Video Upload**: Upload and process video files through the web interface
- **Live Status Updates**: Real-time display of FCWS, LDWS, and LKAS status
- **Adjustable Settings**: Modify detection thresholds and warning distances via sliders
- **Responsive Design**: Works on desktop and mobile devices

### Web Interface Controls

- **Start Webcam**: Begin processing webcam feed
- **Upload Video**: Select and process a video file
- **Stop**: Stop current video processing
- **Settings Panel**: Adjust various ADAS parameters in real-time

The web interface automatically updates system status every second and allows you to adjust settings without restarting the application.

## Command Line Arguments

- `--input`: Input video file path or `0` for webcam (default: `0`)
- `--output`: Output video file path (optional)
- `--model`: YOLOv8 model path (default: `yolov8n.pt`)
- `--conf`: Confidence threshold for object detection (default: `0.5`)
- `--no-display`: Disable video display window

## Project Structure

```
ADAS_Project/
├── app.py                  # Flask web application
├── main.py                 # Command-line application entry point
├── object_detector.py      # YOLOv8 object detection module
├── lane_detector.py        # Lane detection module
├── fcws.py                 # Forward Collision Warning System
├── ldws.py                 # Lane Departure Warning System
├── lkas.py                 # Lane Keeping Assistance System
├── example_usage.py        # Example usage scripts
├── templates/              # Flask HTML templates
│   └── index.html          # Web interface
├── static/                 # Static web files
│   ├── style.css           # Web interface styles
│   └── script.js           # Web interface JavaScript
├── uploads/                # Uploaded video files (created automatically)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## How It Works

### Object Detection (FCWS)
- Uses YOLOv8 to detect vehicles, pedestrians, and other obstacles
- Filters detections in the forward path (center region)
- Estimates distance based on bounding box size and position
- Provides warnings when objects are too close

### Lane Detection (LDWS/LKAS)
- Uses Canny edge detection and Hough Transform to detect lane markings
- Separates left and right lane lines
- Calculates lane center and vehicle offset
- Monitors for lane departures and provides steering guidance

### System Integration
- All modules process frames in real-time
- Visual overlays show warnings, lane lines, and guidance
- Status panel displays current system states

## Performance

- **YOLOv8n**: Fastest, suitable for real-time on CPU
- **YOLOv8s/m/l/x**: More accurate but slower, better with GPU

For real-time performance, use `yolov8n.pt` with a GPU or a powerful CPU.

## Customization

### Adjust Warning Thresholds

Edit the initialization in `main.py`:
```python
self.fcws = FCWS(warning_distance=150.0, critical_distance=80.0)
self.ldws = LDWS(departure_threshold=30.0)
self.lkas = LKAS(assist_threshold=20.0)
```

### Improve Lane Detection

For better lane detection, consider:
- Using a deep learning-based lane detection model (e.g., Ultra-Fast-Lane-Detection)
- Camera calibration for better distance estimation
- Perspective transformation for bird's-eye view

## Limitations

- Lane detection uses traditional CV methods - may struggle with poor lighting or unclear lane markings
- Distance estimation is simplified - real systems use camera calibration and sensor fusion
- Designed for forward-facing camera views
- Performance depends on hardware (CPU/GPU)

## Future Improvements

- [ ] Integrate deep learning-based lane detection
- [ ] Add camera calibration for accurate distance measurement
- [ ] Implement sensor fusion (combine with IMU, GPS)
- [ ] Add more sophisticated collision prediction algorithms
- [ ] Support for multiple camera views
- [ ] Real-time performance optimization

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- YOLOv8 by Ultralytics
- OpenCV for computer vision utilities
- Inspired by various ADAS implementations in the research community

