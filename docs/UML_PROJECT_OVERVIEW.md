# Complete ADAS Project Overview for UML Diagrams

## Project Summary

**Project Name**: Advanced Driver Assistance System (ADAS) with Deep Learning Enhancement  
**Type**: Real-time Video Processing System with Web Interface  
**Architecture**: Client-Server (Flask Backend + HTML/CSS/JS Frontend)  
**Primary Language**: Python (Backend), JavaScript (Frontend)  
**Key Technologies**: YOLOv8, OpenCV, Flask, Deep Learning (ONNX)

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │   Dashboard  │  │   Controls   │          │
│  │   (Client)   │  │   (HTML/CSS) │  │ (JavaScript) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                      WEB SERVER LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Flask Application (app.py)                   │   │
│  │  ├─ Routes (/, /video_feed, /api/*)                      │   │
│  │  ├─ Video Streaming (MJPEG)                              │   │
│  │  └─ API Endpoints (status, metrics, config)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    ADAS PROCESSING LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         EnhancedADASSystem (Main Orchestrator)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────┬───────────┴───────────┬──────────────┐       │
│  │              │                       │              │       │
│  ▼              ▼                       ▼              ▼       │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│ │ Object │  │  Lane  │  │  FCWS  │  │  LDWS  │  │  LKAS  │   │
│ │Detector│  │Detector│  │        │  │        │  │        │   │
│ └────────┘  └────────┘  └────────┘  └────────┘  └────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     SUPPORT SERVICES LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Config     │  │   Distance   │  │   Overlay    │          │
│  │   Loader     │  │  Estimator   │  │   Renderer   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. DETAILED CLASS STRUCTURE

### 2.1 Core ADAS Classes

#### Class: ADASSystem (main.py)
**Purpose**: Base ADAS system with traditional CV lane detection  
**Attributes**:
- `yolo_model: str` - Path to YOLO model
- `conf_threshold: float` - Detection confidence threshold
- `object_detector: ObjectDetector` - YOLOv8 detector instance
- `lane_detector: LaneDetector` - CV lane detector instance
- `fcws: FCWS` - Forward collision warning system
- `ldws: LDWS` - Lane departure warning system
- `lkas: LKAS` - Lane keeping assistance system

**Methods**:
- `__init__(yolo_model, conf_threshold)` - Initialize system
- `process_frame(frame: np.ndarray) -> np.ndarray` - Process single frame
- `run_webcam()` - Run with webcam input
- `run_video(video_path)` - Run with video file

**Relationships**:
- Aggregates: ObjectDetector, LaneDetector, FCWS, LDWS, LKAS
- Inherits: None
- Used by: Flask app, EnhancedADASSystem

---

#### Class: EnhancedADASSystem (enhanced_adas_system.py)
**Purpose**: Enhanced ADAS with DL lane detection and advanced features  
**Attributes**:
- All attributes from ADASSystem (inherited)
- `config_loader: ConfigLoader` - Configuration manager
- `config: Dict` - System configuration
- `model_manager: ModelManager` - ML model manager
- `dl_lane_detector: ONNXLaneDetector` - DL lane detector
- `hybrid_lane_detector: HybridLaneDetector` - DL+CV hybrid
- `distance_estimator: DistanceEstimator` - Distance calculation
- `enhanced_fcws: EnhancedFCWS` - Enhanced collision warning
- `animation_engine: AnimationEngine` - UI animations
- `overlay_renderer: AdvancedOverlayRenderer` - Advanced overlays
- `bev_transformer: BirdEyeViewTransformer` - Bird's eye view
- `performance_stats: Dict` - Performance metrics
- `error_handler: ErrorHandler` - Error management
- `current_vehicle_offset: float` - Current lane offset

**Methods**:
- `__init__(config_path, yolo_model, conf_threshold)` - Initialize
- `process_frame(frame) -> np.ndarray` - Enhanced frame processing
- `get_system_status() -> Dict` - Get complete system status
- `get_performance_metrics() -> Dict` - Get performance data
- `update_config(config: Dict)` - Update configuration
- `_init_dl_lane_detector() -> ONNXLaneDetector` - Initialize DL detector
- `_draw_enhanced_status_panel(frame, ...) -> np.ndarray` - Draw status
- `_check_performance_and_adapt()` - Adaptive performance

**Relationships**:
- Inherits: ADASSystem
- Aggregates: All support classes
- Used by: Flask app (app.py)

---


### 2.2 Detection Classes

#### Class: ObjectDetector (object_detector.py)
**Purpose**: YOLOv8-based object detection  
**Attributes**:
- `model: YOLO` - YOLOv8 model instance
- `conf_threshold: float` - Confidence threshold
- `device: str` - Computation device (cpu/cuda)

**Methods**:
- `__init__(model_path, conf_threshold)` - Initialize detector
- `detect(frame: np.ndarray) -> List[Dict]` - Detect objects
- `draw_detections(frame, detections) -> np.ndarray` - Draw boxes
- `filter_detections(detections, classes) -> List[Dict]` - Filter by class

**Relationships**:
- Used by: ADASSystem, EnhancedADASSystem
- Depends on: ultralytics.YOLO

---

#### Class: LaneDetector (lane_detector.py)
**Purpose**: Traditional CV-based lane detection  
**Attributes**:
- `roi_vertices: np.ndarray` - Region of interest vertices
- `canny_low: int` - Canny edge low threshold
- `canny_high: int` - Canny edge high threshold

**Methods**:
- `__init__()` - Initialize detector
- `detect_lanes(frame) -> Tuple[np.ndarray, np.ndarray]` - Detect lanes
- `calculate_lane_center(left, right, width, height) -> Tuple` - Calculate center
- `_preprocess_frame(frame) -> np.ndarray` - Preprocessing
- `_detect_edges(frame) -> np.ndarray` - Edge detection
- `_apply_roi(edges) -> np.ndarray` - Apply ROI mask
- `_detect_lines(edges) -> List` - Hough line detection
- `_separate_lanes(lines) -> Tuple` - Separate left/right
- `_fit_lane_line(points) -> np.ndarray` - Fit polynomial

**Relationships**:
- Used by: ADASSystem
- Depends on: OpenCV (cv2)

---

#### Class: HybridLaneDetector (hybrid_lane_detector.py)
**Purpose**: Combines DL and CV lane detection with fallback  
**Attributes**:
- `dl_detector: ONNXLaneDetector` - DL detector
- `cv_detector: LaneDetector` - CV detector
- `conf_threshold: float` - Confidence threshold
- `max_consecutive_failures: int` - Max failures before fallback
- `consecutive_failures: int` - Current failure count
- `dl_enabled: bool` - DL detector status
- `statistics: Dict` - Detection statistics

**Methods**:
- `__init__(dl_detector, conf_threshold, max_failures)` - Initialize
- `detect_lanes(frame) -> LaneDetectionResult` - Detect with fallback
- `get_statistics() -> Dict` - Get detection stats
- `reset_statistics()` - Reset counters

**Relationships**:
- Aggregates: ONNXLaneDetector, LaneDetector
- Used by: EnhancedADASSystem

---

#### Class: ONNXLaneDetector (onnx_lane_detector.py)
**Purpose**: ONNX-based deep learning lane detection  
**Attributes**:
- `model_path: str` - Path to ONNX model
- `session: ort.InferenceSession` - ONNX runtime session
- `input_size: Tuple[int, int]` - Model input size
- `conf_threshold: float` - Confidence threshold

**Methods**:
- `__init__(model_path, conf_threshold)` - Initialize
- `detect_lanes(frame) -> LaneDetectionResult` - Detect lanes
- `preprocess(frame) -> np.ndarray` - Preprocess frame
- `postprocess(output) -> LaneDetectionResult` - Process output
- `is_available() -> bool` - Check if model loaded

**Relationships**:
- Used by: HybridLaneDetector
- Depends on: onnxruntime

---

### 2.3 Warning System Classes

#### Class: FCWS (fcws.py)
**Purpose**: Forward Collision Warning System  
**Attributes**:
- `warning_distance: float` - Warning threshold (pixels)
- `critical_distance: float` - Critical threshold (pixels)
- `warning_state: str` - Current state (SAFE/WARNING/CRITICAL)

**Methods**:
- `__init__(warning_distance, critical_distance)` - Initialize
- `check_collision_risk(detections, frame_height) -> Tuple` - Check risk
- `calculate_distance(detection, frame_height) -> float` - Calculate distance
- `draw_warning(frame, risky_detections) -> np.ndarray` - Draw warnings

**Relationships**:
- Used by: ADASSystem, EnhancedADASSystem
- Enhanced by: EnhancedFCWS

---

#### Class: EnhancedFCWS (enhanced_fcws.py)
**Purpose**: Enhanced FCWS with distance estimation  
**Attributes**:
- All attributes from FCWS (inherited)
- `distance_estimator: DistanceEstimator` - Distance calculator
- `statistics: Dict` - Warning statistics

**Methods**:
- All methods from FCWS (inherited)
- `get_statistics() -> Dict` - Get warning stats
- `reset_statistics()` - Reset counters

**Relationships**:
- Inherits: FCWS
- Aggregates: DistanceEstimator
- Used by: EnhancedADASSystem

---

#### Class: LDWS (ldws.py)
**Purpose**: Lane Departure Warning System  
**Attributes**:
- `departure_threshold: float` - Departure threshold (pixels)
- `warning_state: str` - State (SAFE/LEFT_WARNING/RIGHT_WARNING)
- `departure_count: int` - Consecutive departure frames

**Methods**:
- `__init__(departure_threshold)` - Initialize
- `check_lane_departure(lane_center, offset, width) -> str` - Check departure
- `draw_warning(frame, lane_center, offset) -> np.ndarray` - Draw warning

**Relationships**:
- Used by: ADASSystem, EnhancedADASSystem

---

#### Class: LKAS (lkas.py)
**Purpose**: Lane Keeping Assistance System  
**Attributes**:
- `assist_threshold: float` - Assistance threshold (pixels)
- `steering_angle: float` - Calculated steering angle (degrees)
- `assist_active: bool` - Assistance status

**Methods**:
- `__init__(assist_threshold)` - Initialize
- `calculate_steering_angle(lane_center, offset, width) -> float` - Calculate angle
- `draw_assistance(frame, lane_center, offset) -> np.ndarray` - Draw guidance

**Relationships**:
- Used by: ADASSystem, EnhancedADASSystem

---

### 2.4 Support Classes

#### Class: DistanceEstimator (distance_estimator.py)
**Purpose**: Estimate real-world distances from pixel measurements  
**Attributes**:
- `calibration_data: Dict` - Camera calibration parameters
- `has_calibration: bool` - Calibration status

**Methods**:
- `__init__(calibration_file)` - Initialize
- `load_calibration(file_path) -> bool` - Load calibration
- `estimate_distance(bbox, frame_height, object_class) -> Dict` - Estimate
- `pixel_to_meters(pixel_distance, bbox_height) -> float` - Convert units
- `calculate_confidence(bbox, detection_conf) -> float` - Calculate confidence
- `get_calibration_info() -> Dict` - Get calibration status

**Relationships**:
- Used by: EnhancedFCWS
- Depends on: Camera calibration data

---

#### Class: AdvancedOverlayRenderer (advanced_overlay.py)
**Purpose**: Render advanced visual overlays with animations  
**Attributes**:
- `config: Dict` - Overlay configuration
- `animation_engine: AnimationEngine` - Animation controller

**Methods**:
- `__init__(config, animation_engine)` - Initialize
- `draw_lane_polygon(frame, left, right, color, alpha) -> np.ndarray` - Draw polygon
- `draw_distance_markers(frame, detections, distances) -> np.ndarray` - Draw markers
- `draw_warning_overlay(frame, warning_type, message, severity) -> np.ndarray` - Draw warning
- `draw_directional_arrow(frame, direction, position, phase) -> np.ndarray` - Draw arrow
- `apply_fade_transition(current, previous, alpha) -> np.ndarray` - Apply fade

**Relationships**:
- Aggregates: AnimationEngine
- Used by: EnhancedADASSystem

---

#### Class: AnimationEngine (animation_engine.py)
**Purpose**: Manage UI animations and transitions  
**Attributes**:
- `animations: Dict[str, Animation]` - Active animations
- `start_time: float` - Engine start time

**Methods**:
- `__init__()` - Initialize engine
- `register_animation(name, duration, easing) -> None` - Register animation
- `update(delta_time) -> None` - Update all animations
- `get_animation_value(name) -> float` - Get current value
- `apply_easing(t, easing_type) -> float` - Apply easing function

**Relationships**:
- Used by: AdvancedOverlayRenderer
- Manages: Animation objects

---

#### Class: BirdEyeViewTransformer (bev_transform.py)
**Purpose**: Transform perspective to bird's eye view  
**Attributes**:
- `src_points: np.ndarray` - Source trapezoid points
- `dst_points: np.ndarray` - Destination rectangle points
- `output_size: Tuple[int, int]` - BEV output size
- `transform_matrix: np.ndarray` - Transformation matrix

**Methods**:
- `__init__(output_size)` - Initialize
- `set_default_points(width, height)` - Set default points
- `calculate_transform_matrix() -> np.ndarray` - Calculate matrix
- `transform_frame(frame) -> np.ndarray` - Transform frame
- `transform_lanes(left, right) -> Tuple` - Transform lane coordinates
- `draw_bev_overlay(bev_frame, left, right) -> np.ndarray` - Draw on BEV
- `create_pip_overlay(main, bev, position, size, alpha) -> np.ndarray` - Create PIP

**Relationships**:
- Used by: EnhancedADASSystem
- Depends on: OpenCV perspective transform

---

#### Class: ConfigLoader (config_loader.py)
**Purpose**: Load and manage system configuration  
**Attributes**:
- `config_path: str` - Path to config file
- `config: Dict` - Configuration dictionary

**Methods**:
- `__init__(config_path)` - Initialize
- `load() -> Dict` - Load configuration
- `save() -> None` - Save configuration
- `get(key, default) -> Any` - Get config value
- `update_from_dict(updates: Dict) -> None` - Update config
- `get_overlay_config() -> Dict` - Get overlay settings

**Relationships**:
- Used by: EnhancedADASSystem
- Manages: YAML configuration files

---

#### Class: ModelManager (model_manager.py)
**Purpose**: Manage ML model loading and selection  
**Attributes**:
- `config: Dict` - Model configuration
- `available_devices: Dict[str, bool]` - Available hardware

**Methods**:
- `__init__(config)` - Initialize
- `load_lane_model(path, type) -> Optional[Any]` - Load lane model
- `detect_hardware() -> Dict[str, bool]` - Detect available hardware
- `select_inference_device() -> str` - Select best device
- `get_model_info(name) -> Dict` - Get model information
- `benchmark_model(model, num_frames) -> Dict` - Benchmark performance

**Relationships**:
- Used by: EnhancedADASSystem
- Manages: Model loading and hardware detection

---

#### Class: ErrorHandler (error_handler.py)
**Purpose**: Handle errors and implement recovery strategies  
**Attributes**:
- `max_consecutive_errors: int` - Max errors before safe mode
- `consecutive_errors: int` - Current error count
- `error_log: List[Dict]` - Error history

**Methods**:
- `__init__(max_consecutive_errors)` - Initialize
- `handle_model_error(error, model_name) -> bool` - Handle model error
- `handle_processing_error(error, frame_num) -> np.ndarray` - Handle processing error
- `should_enter_safe_mode() -> bool` - Check if safe mode needed
- `reset_error_counters() -> None` - Reset counters

**Relationships**:
- Used by: EnhancedADASSystem, HybridLaneDetector

---


### 2.5 Web Application Classes

#### Class: Flask Application (app.py)
**Purpose**: Web server and API endpoints  
**Attributes**:
- `app: Flask` - Flask application instance
- `enhanced_adas: EnhancedADASSystem` - ADAS system instance
- `video_capture: cv2.VideoCapture` - Video capture object
- `current_video_path: str` - Current video file path
- `processing_active: bool` - Processing status flag
- `frame_lock: threading.Lock` - Thread synchronization
- `config_loader: ConfigLoader` - Configuration loader
- `processing_stats: Dict` - Processing statistics

**Methods**:
- `init_enhanced_adas() -> EnhancedADASSystem` - Initialize ADAS
- `generate_frames() -> Generator` - Generate video frames
- `index() -> str` - Main dashboard route
- `video_feed() -> Response` - Video streaming route
- `serve_assets(filename) -> Response` - Serve static assets
- `start_webcam() -> Response` - Start webcam endpoint
- `upload_video() -> Response` - Upload video endpoint
- `stop_video() -> Response` - Stop video endpoint
- `get_status() -> Response` - Get system status endpoint
- `get_metrics() -> Response` - Get metrics endpoint
- `get_config() -> Response` - Get configuration endpoint
- `update_config() -> Response` - Update configuration endpoint

**Relationships**:
- Aggregates: EnhancedADASSystem, ConfigLoader
- Serves: HTML templates, static files
- Provides: REST API, video streaming

---

## 3. DATA STRUCTURES AND MODELS

### 3.1 Data Classes

#### LaneDetectionResult (lane_detection_result.py)
```python
@dataclass
class LaneDetectionResult:
    left_lane: Optional[np.ndarray]      # Left lane points/coefficients
    right_lane: Optional[np.ndarray]     # Right lane points/coefficients
    confidence: float                     # Detection confidence (0-1)
    lane_type: str                        # 'solid', 'dashed', 'double', 'unknown'
    success: bool                         # Detection success flag
    processing_time: float                # Processing time in seconds
    model_used: str                       # 'dl' or 'cv'
```

#### DistanceEstimation
```python
@dataclass
class DistanceEstimation:
    distance_meters: Optional[float]     # Distance in meters
    distance_pixels: float               # Distance in pixels
    confidence: float                    # Estimation confidence
    has_calibration: bool                # Calibration available
    confidence_interval: Tuple[float, float]  # (min, max) range
```

#### OverlayConfig
```python
@dataclass
class OverlayConfig:
    show_lane_polygon: bool = True
    show_distance_markers: bool = True
    show_bev: bool = True
    show_animations: bool = True
    lane_polygon_alpha: float = 0.3
    warning_fade_duration: float = 0.3
    animation_speed: float = 1.0
    bev_position: str = 'bottom-right'
    bev_size: Tuple[int, int] = (300, 400)
```

---

## 4. SYSTEM INTERACTIONS AND WORKFLOWS

### 4.1 Main Processing Flow

```
User Action (Start Webcam/Upload Video)
    ↓
Flask Route Handler (start_webcam/upload_video)
    ↓
Initialize video_capture
    ↓
Set processing_active = True
    ↓
generate_frames() starts
    ↓
Loop: While processing_active
    ├─ Read frame from video_capture
    ├─ Pass frame to enhanced_adas.process_frame()
    │   ├─ 1. Object Detection (YOLOv8)
    │   ├─ 2. Lane Detection (DL + CV Fallback)
    │   ├─ 3. Calculate Lane Metrics
    │   ├─ 4. FCWS Check
    │   ├─ 5. LDWS Check
    │   ├─ 6. LKAS Calculate
    │   ├─ 7. Distance Estimation
    │   ├─ 8. Render Overlays
    │   ├─ 9. BEV Transformation
    │   └─ 10. Draw Status Panel
    ├─ Encode frame as JPEG
    ├─ Yield frame to client
    └─ Update statistics
    ↓
Client receives MJPEG stream
    ↓
Display in browser
```

### 4.2 Lane Detection Flow

```
Frame Input
    ↓
HybridLaneDetector.detect_lanes()
    ↓
Try: DL Lane Detection
    ├─ ONNXLaneDetector.detect_lanes()
    │   ├─ Preprocess frame
    │   ├─ ONNX inference
    │   ├─ Postprocess output
    │   └─ Return LaneDetectionResult
    ├─ Check confidence
    ├─ If confidence >= threshold
    │   └─ Return DL result
    └─ If confidence < threshold or error
        ↓
        Fallback: CV Lane Detection
            ├─ LaneDetector.detect_lanes()
            │   ├─ Grayscale conversion
            │   ├─ Gaussian blur
            │   ├─ Canny edge detection
            │   ├─ ROI masking
            │   ├─ Hough line detection
            │   ├─ Separate left/right lanes
            │   └─ Fit polynomial
            └─ Return CV result
```

### 4.3 Collision Warning Flow

```
Object Detections + Frame
    ↓
EnhancedFCWS.check_collision_risk()
    ↓
Filter detections in forward path
    ↓
For each detection:
    ├─ Calculate distance (pixels)
    ├─ DistanceEstimator.estimate_distance()
    │   ├─ If calibration available
    │   │   └─ Convert to meters
    │   └─ Else
    │       └─ Use normalized distance
    └─ Store distance
    ↓
Sort by distance (closest first)
    ↓
Determine warning state:
    ├─ If closest < critical_distance
    │   └─ State = CRITICAL
    ├─ Else if closest < warning_distance
    │   └─ State = WARNING
    └─ Else
        └─ State = SAFE
    ↓
Update statistics
    ↓
Return (state, risky_detections)
```

### 4.4 Configuration Update Flow

```
User changes setting in UI
    ↓
JavaScript sends POST to /api/config/update
    ↓
Flask route handler
    ↓
ConfigLoader.update_from_dict(changes)
    ↓
ConfigLoader.save() to YAML file
    ↓
Apply changes to ADAS system:
    ├─ Update object_detector.conf_threshold
    ├─ Update fcws.warning_distance
    ├─ Update ldws.departure_threshold
    └─ Update lkas.assist_threshold
    ↓
Return success response
    ↓
UI updates to reflect changes
```

---

## 5. STATE MACHINES

### 5.1 FCWS State Machine

**States**:
- SAFE: No collision risk
- WARNING: Potential collision risk
- CRITICAL: Immediate collision risk

**Transitions**:
```
SAFE ──[vehicle detected & distance < warning_distance]──> WARNING
WARNING ──[distance < critical_distance]──> CRITICAL
WARNING ──[distance >= warning_distance]──> SAFE
CRITICAL ──[distance >= critical_distance]──> WARNING
CRITICAL ──[no vehicle detected]──> SAFE
```

**Actions**:
- On enter WARNING: Display yellow warning, log event
- On enter CRITICAL: Display red alert, sound alarm (if enabled)
- On enter SAFE: Clear warnings

### 5.2 LDWS State Machine

**States**:
- SAFE: Vehicle centered in lane
- LEFT_WARNING: Departing left
- RIGHT_WARNING: Departing right

**Transitions**:
```
SAFE ──[offset > departure_threshold]──> LEFT_WARNING
SAFE ──[offset < -departure_threshold]──> RIGHT_WARNING
LEFT_WARNING ──[offset <= departure_threshold]──> SAFE
RIGHT_WARNING ──[offset >= -departure_threshold]──> SAFE
```

**Actions**:
- On enter LEFT_WARNING: Show left arrow, increment counter
- On enter RIGHT_WARNING: Show right arrow, increment counter
- On enter SAFE: Clear arrows, reset counter

### 5.3 LKAS State Machine

**States**:
- INACTIVE: No lane detected or offset < threshold
- ACTIVE: Providing steering assistance

**Transitions**:
```
INACTIVE ──[lane detected & |offset| > assist_threshold]──> ACTIVE
ACTIVE ──[no lane detected OR |offset| <= assist_threshold]──> INACTIVE
```

**Actions**:
- On enter ACTIVE: Calculate steering angle, show guidance
- On enter INACTIVE: Reset steering angle to 0

### 5.4 Video Processing State Machine

**States**:
- IDLE: No video source
- INITIALIZING: Loading video source
- PROCESSING: Actively processing frames
- PAUSED: Processing paused
- ERROR: Error occurred
- STOPPED: User stopped processing

**Transitions**:
```
IDLE ──[start_webcam/upload_video]──> INITIALIZING
INITIALIZING ──[success]──> PROCESSING
INITIALIZING ──[failure]──> ERROR
PROCESSING ──[stop_video]──> STOPPED
PROCESSING ──[error]──> ERROR
ERROR ──[retry]──> INITIALIZING
STOPPED ──[start again]──> INITIALIZING
```

---

## 6. SEQUENCE DIAGRAMS SCENARIOS

### 6.1 Scenario: User Starts Webcam

**Actors**: User, Browser, Flask App, ADAS System, Webcam

**Sequence**:
1. User clicks "Start Webcam" button
2. Browser sends POST to /api/video/start_webcam
3. Flask stops any existing stream
4. Flask initializes cv2.VideoCapture(0)
5. Flask verifies webcam opened successfully
6. Flask sets processing_active = True
7. Flask starts generate_frames() thread
8. generate_frames() reads frame from webcam
9. generate_frames() calls enhanced_adas.process_frame()
10. ADAS processes frame (detection, warnings, overlays)
11. generate_frames() encodes frame as JPEG
12. generate_frames() yields frame
13. Browser receives frame via /video_feed
14. Browser displays frame in <img> element
15. Repeat steps 8-14 while processing_active

### 6.2 Scenario: Lane Departure Detected

**Actors**: ADAS System, Lane Detector, LDWS, Overlay Renderer

**Sequence**:
1. Frame enters process_frame()
2. HybridLaneDetector detects lanes
3. LaneDetector calculates lane_center and vehicle_offset
4. LDWS.check_lane_departure(lane_center, offset, width)
5. LDWS detects offset > departure_threshold
6. LDWS sets warning_state = "LEFT_WARNING"
7. LDWS increments departure_count
8. AdvancedOverlayRenderer draws left arrow
9. AnimationEngine animates arrow sliding
10. Frame returned with warning overlay
11. User sees visual warning

### 6.3 Scenario: Configuration Update

**Actors**: User, Browser, Flask App, ConfigLoader, ADAS System

**Sequence**:
1. User adjusts slider in settings panel
2. JavaScript captures change event
3. JavaScript sends POST to /api/config/update with new value
4. Flask receives request
5. Flask calls config_loader.update_from_dict(changes)
6. ConfigLoader updates internal config dictionary
7. ConfigLoader saves to YAML file
8. Flask applies changes to ADAS components
9. Flask returns success response
10. Browser updates UI to confirm change
11. ADAS uses new settings on next frame

---


## 7. USE CASES

### 7.1 Primary Use Cases

#### UC1: Start Real-Time Webcam Processing
**Actor**: Driver/User  
**Preconditions**: Webcam connected, system initialized  
**Main Flow**:
1. User opens dashboard in browser
2. User clicks "Start Webcam" button
3. System initializes webcam
4. System starts processing frames
5. System displays processed video with overlays
6. System continuously monitors for hazards

**Postconditions**: Video stream active, warnings operational  
**Alternative Flows**:
- 3a. Webcam not available → Display error message
- 4a. Processing fails → Enter safe mode with basic features

#### UC2: Upload and Process Video File
**Actor**: User  
**Preconditions**: System initialized  
**Main Flow**:
1. User clicks "Upload Video" button
2. User selects video file from file system
3. System validates file format
4. System loads video file
5. System processes video frame by frame
6. System displays processed video with overlays

**Postconditions**: Video processed, statistics available  
**Alternative Flows**:
- 3a. Invalid format → Display error, request valid file
- 4a. File too large → Display warning, process anyway
- 5a. Processing error → Skip frame, continue with next

#### UC3: Receive Forward Collision Warning
**Actor**: System (automated), Driver (receives warning)  
**Preconditions**: Video processing active, vehicle detected  
**Main Flow**:
1. System detects vehicle in forward path
2. System calculates distance to vehicle
3. System determines distance < warning_threshold
4. System changes FCWS state to WARNING
5. System displays yellow warning overlay
6. System updates status panel
7. Driver sees warning and takes action

**Postconditions**: Warning displayed, event logged  
**Alternative Flows**:
- 3a. Distance < critical_threshold → Display CRITICAL warning (red)
- 7a. Driver doesn't respond → Warning persists

#### UC4: Receive Lane Departure Warning
**Actor**: System (automated), Driver (receives warning)  
**Preconditions**: Video processing active, lanes detected  
**Main Flow**:
1. System detects lane markings
2. System calculates vehicle position
3. System determines vehicle offset > threshold
4. System changes LDWS state to LEFT_WARNING/RIGHT_WARNING
5. System displays directional arrow
6. System updates status panel
7. Driver sees warning and corrects steering

**Postconditions**: Warning displayed, event logged  
**Alternative Flows**:
- 3a. Offset within threshold → No warning, display SAFE
- 7a. Driver doesn't correct → Warning persists, counter increments

#### UC5: Receive Lane Keeping Assistance
**Actor**: System (automated), Driver (receives guidance)  
**Preconditions**: Video processing active, lanes detected  
**Main Flow**:
1. System detects lane markings
2. System calculates vehicle offset
3. System determines offset > assist_threshold
4. System calculates steering angle
5. System activates LKAS
6. System displays steering wheel with angle
7. System shows recommended steering direction
8. Driver follows guidance

**Postconditions**: Guidance displayed, steering angle shown  
**Alternative Flows**:
- 3a. Offset < threshold → LKAS remains inactive
- 8a. Driver ignores guidance → Guidance persists

#### UC6: Adjust System Configuration
**Actor**: User  
**Preconditions**: System running  
**Main Flow**:
1. User opens settings panel
2. User adjusts slider/input for setting
3. System validates new value
4. System updates configuration
5. System saves configuration to file
6. System applies changes immediately
7. System confirms update to user

**Postconditions**: Configuration updated, changes active  
**Alternative Flows**:
- 3a. Invalid value → Display error, revert to previous
- 6a. Apply fails → Display error, keep old settings

#### UC7: View System Performance Metrics
**Actor**: User  
**Preconditions**: System running  
**Main Flow**:
1. User views performance panel
2. System displays current FPS
3. System displays frame count
4. System displays warning/critical counts
5. System updates metrics every 1.5 seconds

**Postconditions**: User informed of system performance  
**Alternative Flows**:
- 5a. Performance degraded → Display warning indicator

#### UC8: Stop Video Processing
**Actor**: User  
**Preconditions**: Video processing active  
**Main Flow**:
1. User clicks "Stop" button
2. System sets processing_active = False
3. System releases video capture
4. System stops frame generation
5. System resets statistics
6. System displays idle state

**Postconditions**: Processing stopped, resources released  
**Alternative Flows**: None

---

### 7.2 Secondary Use Cases

#### UC9: System Enters Safe Mode
**Actor**: System (automated)  
**Preconditions**: Multiple consecutive errors  
**Main Flow**:
1. System detects consecutive_errors > threshold
2. System disables DL models
3. System switches to CV-only detection
4. System disables advanced overlays
5. System displays safe mode indicator
6. System logs safe mode entry

**Postconditions**: System in safe mode, basic features active

#### UC10: Export Processing Report
**Actor**: User  
**Preconditions**: Video processed  
**Main Flow**:
1. User requests report
2. System compiles statistics
3. System generates report file
4. System saves report to disk
5. System notifies user of completion

**Postconditions**: Report saved, available for review

---

## 8. COMPONENT INTERACTIONS

### 8.1 Component Diagram Elements

**Components**:
1. **Web UI Component**
   - Interfaces: HTTP, WebSocket
   - Provides: User interface, video display
   - Requires: Flask API

2. **Flask Server Component**
   - Interfaces: HTTP REST API, MJPEG streaming
   - Provides: API endpoints, video streaming
   - Requires: ADAS Processing

3. **ADAS Processing Component**
   - Interfaces: Frame processing API
   - Provides: Detection, warnings, overlays
   - Requires: Detection models, configuration

4. **Object Detection Component**
   - Interfaces: Detection API
   - Provides: Object bounding boxes
   - Requires: YOLOv8 model

5. **Lane Detection Component**
   - Interfaces: Lane detection API
   - Provides: Lane coordinates
   - Requires: DL model or CV algorithms

6. **Warning Systems Component**
   - Interfaces: Warning API
   - Provides: FCWS, LDWS, LKAS
   - Requires: Detection results

7. **Overlay Rendering Component**
   - Interfaces: Rendering API
   - Provides: Visual overlays
   - Requires: Detection results, animations

8. **Configuration Component**
   - Interfaces: Config API
   - Provides: System settings
   - Requires: YAML files

### 8.2 Deployment Architecture

**Nodes**:
1. **Client Machine** (Browser)
   - Runs: HTML/CSS/JavaScript
   - Connects to: Flask Server

2. **Server Machine** (Python)
   - Runs: Flask, ADAS System
   - Processes: Video frames
   - Stores: Configuration, models

3. **GPU (Optional)**
   - Accelerates: DL inference
   - Used by: YOLOv8, ONNX models

**Network**:
- HTTP/HTTPS for API calls
- MJPEG over HTTP for video streaming
- WebSocket for real-time updates (optional)

---

## 9. ACTIVITY DIAGRAMS SCENARIOS

### 9.1 Frame Processing Activity

```
[Start] → Read Frame
    ↓
[Decision: Frame Valid?]
    ├─ No → [Log Error] → [Return Previous Frame] → [End]
    └─ Yes ↓
        Detect Objects (Parallel)
        Detect Lanes (Parallel)
        ↓
        [Join: Both Complete]
        ↓
        Calculate Lane Metrics
        ↓
        Check FCWS
        Check LDWS (Parallel)
        Check LKAS (Parallel)
        ↓
        [Join: All Checks Complete]
        ↓
        Estimate Distances
        ↓
        Render Overlays
        ↓
        [Decision: BEV Enabled?]
        ├─ Yes → Transform to BEV → Add PIP
        └─ No ↓
            Draw Status Panel
            ↓
            Update Statistics
            ↓
            [Return Processed Frame] → [End]
```

### 9.2 Configuration Update Activity

```
[Start] → Receive Config Update Request
    ↓
[Decision: Valid Format?]
    ├─ No → [Return Error] → [End]
    └─ Yes ↓
        Parse Changes
        ↓
        [Decision: Valid Values?]
        ├─ No → [Return Validation Error] → [End]
        └─ Yes ↓
            Update Config Dictionary
            ↓
            [Fork]
            ├─ Save to YAML File
            └─ Apply to ADAS Components
            ↓
            [Join: Both Complete]
            ↓
            [Decision: Save Successful?]
            ├─ No → [Rollback Changes] → [Return Error] → [End]
            └─ Yes ↓
                Log Update
                ↓
                [Return Success] → [End]
```

### 9.3 Error Handling Activity

```
[Start] → Error Occurs
    ↓
[Decision: Error Type?]
    ├─ Model Error → [Increment Model Error Counter]
    │   ↓
    │   [Decision: Counter > Threshold?]
    │   ├─ Yes → [Disable DL Model] → [Enable CV Fallback]
    │   └─ No → [Log Error] → [Continue]
    │
    ├─ Processing Error → [Increment Processing Error Counter]
    │   ↓
    │   [Decision: Counter > Threshold?]
    │   ├─ Yes → [Enter Safe Mode] → [Disable Advanced Features]
    │   └─ No → [Skip Frame] → [Continue]
    │
    └─ Critical Error → [Stop Processing] → [Display Error] → [End]
```

---

## 10. TIMING AND PERFORMANCE

### 10.1 Performance Requirements

| Operation | Target Time | Max Time | Frequency |
|-----------|-------------|----------|-----------|
| Frame Processing | 50-80ms | 100ms | 15-30 FPS |
| Object Detection | 15-25ms | 30ms | Per frame |
| Lane Detection (DL) | 20-30ms | 40ms | Per frame |
| Lane Detection (CV) | 10-20ms | 30ms | Per frame |
| Overlay Rendering | 10-15ms | 20ms | Per frame |
| BEV Transform | 5-10ms | 15ms | Per frame |
| API Response | <100ms | 200ms | On request |
| Config Update | <50ms | 100ms | On change |

### 10.2 Timing Constraints

**Real-time Constraints**:
- Video must maintain ≥15 FPS for smooth playback
- Warnings must appear within 100ms of detection
- User interactions must respond within 200ms

**Soft Constraints**:
- Configuration updates should apply within 1 second
- Statistics should update every 1-2 seconds
- Error recovery should complete within 5 seconds

---

## 11. PACKAGE STRUCTURE

```
ADAS_Project/
├── main.py                          # Base ADAS system
├── enhanced_adas_system.py          # Enhanced ADAS system
├── app.py                           # Flask web application
│
├── detection/                       # Detection package
│   ├── __init__.py
│   ├── object_detector.py          # YOLOv8 detector
│   ├── lane_detector.py            # CV lane detector
│   └── hybrid_lane_detector.py     # Hybrid detector
│
├── dl_models/                       # Deep learning package
│   ├── __init__.py
│   ├── onnx_lane_detector.py       # ONNX detector
│   ├── lane_detection_result.py    # Result data class
│   └── lane_utils.py               # Utility functions
│
├── warning_systems/                 # Warning systems package
│   ├── __init__.py
│   ├── fcws.py                     # Forward collision warning
│   ├── enhanced_fcws.py            # Enhanced FCWS
│   ├── ldws.py                     # Lane departure warning
│   └── lkas.py                     # Lane keeping assistance
│
├── rendering/                       # Rendering package
│   ├── __init__.py
│   ├── advanced_overlay.py         # Advanced overlays
│   ├── animation_engine.py         # Animation engine
│   └── bev_transform.py            # Bird's eye view
│
├── utils/                           # Utilities package
│   ├── __init__.py
│   ├── config_loader.py            # Configuration loader
│   ├── distance_estimator.py       # Distance estimation
│   ├── model_manager.py            # Model management
│   └── error_handler.py            # Error handling
│
├── templates/                       # Flask templates
│   ├── dashboard.html              # Main dashboard
│   └── test_assets.html            # Asset test page
│
├── static/                          # Static files
│   ├── dashboard.css               # Dashboard styles
│   ├── dashboard.js                # Dashboard scripts
│   └── assets/                     # Images
│       ├── steering_wheel.png
│       ├── left.png
│       ├── right.png
│       ├── up.png
│       └── background.jpg
│
├── config/                          # Configuration files
│   ├── adas_config.yaml            # System config
│   └── sample_calibration.json     # Camera calibration
│
├── models/                          # ML models
│   ├── yolov8n.pt                  # YOLOv8 model
│   └── lane_detection.onnx         # Lane detection model
│
├── demo_output/                     # Demo outputs
│   ├── output_video.mp4
│   ├── processing_report.txt
│   └── sample_outputs/
│
├── docs/                            # Documentation
│   ├── requirements.md
│   ├── design.md
│   ├── tasks.md
│   └── UML_PROJECT_OVERVIEW.md
│
└── tests/                           # Test suite
    ├── test_flask_app.py
    ├── system_test.py
    └── comprehensive_test.py
```

---

## 12. EXTERNAL INTERFACES

### 12.1 User Interface

**Dashboard Interface**:
- Video display area with overlays
- Control buttons (Start Webcam, Upload Video, Stop)
- Performance metrics panel
- System status indicators
- LKAS guidance display
- Settings panel

**Elements**:
- Steering wheel indicator (rotates with angle)
- Directional arrows (left, right, up)
- Status badges (SAFE, WARNING, CRITICAL)
- FPS counter
- Frame counter
- Warning/Critical event counters

### 12.2 API Interface

**REST Endpoints**:
```
GET  /                          # Main dashboard
GET  /video_feed                # MJPEG video stream
GET  /assets/<filename>         # Static assets
POST /api/video/start_webcam    # Start webcam
POST /api/video/upload          # Upload video
POST /api/video/stop            # Stop processing
GET  /api/status                # Get system status
GET  /api/metrics               # Get performance metrics
GET  /api/config                # Get configuration
POST /api/config/update         # Update configuration
GET  /api/debug/assets          # Debug asset info
```

**Response Formats**:
```json
// Status Response
{
    "status": "success",
    "data": {
        "processing": true,
        "video_loaded": true,
        "adas_initialized": true,
        "system": {
            "fcws": {"warning_state": "SAFE"},
            "ldws": {"state": "SAFE", "lane_offset": 0},
            "lkas": {"active": true, "steering_angle": 15.3}
        }
    }
}

// Metrics Response
{
    "status": "success",
    "metrics": {
        "fps": 8.19,
        "total_frames": 825,
        "warnings": 103,
        "critical_alerts": 14
    }
}
```

### 12.3 Hardware Interfaces

**Camera Interface**:
- OpenCV VideoCapture
- Supports: Webcam (index 0), video files
- Formats: MP4, AVI, MOV, MKV, WEBM

**GPU Interface** (Optional):
- CUDA for NVIDIA GPUs
- OpenVINO for Intel hardware
- MPS for Apple Silicon

### 12.4 File System Interfaces

**Configuration Files**:
- YAML format for system config
- JSON format for camera calibration

**Model Files**:
- PyTorch (.pt) for YOLOv8
- ONNX (.onnx) for lane detection

**Output Files**:
- MP4 video files
- TXT processing reports
- JPG sample frames

---

