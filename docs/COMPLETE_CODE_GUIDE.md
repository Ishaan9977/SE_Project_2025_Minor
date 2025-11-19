# Complete ADAS Project Code Guide

## Table of Contents
1. [Core System Files](#1-core-system-files)
2. [Detection Components](#2-detection-components)
3. [Warning Systems](#3-warning-systems)
4. [Deep Learning Models](#4-deep-learning-models)
5. [Rendering Components](#5-rendering-components)
6. [Utility Components](#6-utility-components)
7. [Web Application](#7-web-application)
8. [Configuration Files](#8-configuration-files)
9. [Frontend Components](#9-frontend-components)

---

## 1. CORE SYSTEM FILES

### 1.1 main.py - Base ADAS System

**Purpose**: Basic ADAS system with traditional computer vision lane detection

**Key Components**:
```python
class ADASSystem:
    """Base ADAS system integrating all components"""
    
    def __init__(self, yolo_model='yolov8n.pt', conf_threshold=0.5):
        # Initialize object detector
        self.object_detector = ObjectDetector(yolo_model, conf_threshold)
        
        # Initialize lane detector (traditional CV)
        self.lane_detector = LaneDetector()
        
        # Initialize warning systems
        self.fcws = FCWS(warning_distance=150.0, critical_distance=80.0)
        self.ldws = LDWS(departure_threshold=30.0)
        self.lkas = LKAS(assist_threshold=20.0)
```

**Main Processing Method**:
```python
def process_frame(self, frame: np.ndarray) -> np.ndarray:
    """
    Process single frame through ADAS pipeline
    
    Steps:
    1. Detect objects (vehicles, pedestrians)
    2. Detect lane markings
    3. Calculate lane center and vehicle offset
    4. Check collision risk (FCWS)
    5. Check lane departure (LDWS)
    6. Calculate steering assistance (LKAS)
    7. Draw all overlays
    """
    height, width = frame.shape[:2]
    
    # 1. Object Detection
    detections = self.object_detector.detect(frame)
    
    # 2. Lane Detection
    left_lane, right_lane = self.lane_detector.detect_lanes(frame)
    
    # 3. Calculate lane metrics
    lane_center, vehicle_offset = self.lane_detector.calculate_lane_center(
        left_lane, right_lane, width, height
    )
    
    # 4. FCWS - Check collision risk
    fcws_state, risky_detections = self.fcws.check_collision_risk(
        detections, height
    )
    
    # 5. LDWS - Check lane departure
    ldws_state = self.ldws.check_lane_departure(
        lane_center, vehicle_offset, width
    )
    
    # 6. LKAS - Calculate steering angle
    steering_angle = self.lkas.calculate_steering_angle(
        lane_center, vehicle_offset, width
    )
    
    # 7. Draw overlays
    frame = self.lane_detector.draw_lanes(frame, left_lane, right_lane)
    frame = self.fcws.draw_warning(frame, risky_detections)
    frame = self.ldws.draw_warning(frame, lane_center, vehicle_offset)
    frame = self.lkas.draw_assistance(frame, lane_center, vehicle_offset)
    frame = self.object_detector.draw_detections(frame, detections)
    
    return frame
```

**Usage**:
```python
# Webcam processing
def run_webcam(self):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = self.process_frame(frame)
        cv2.imshow('ADAS', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

---

### 1.2 enhanced_adas_system.py - Enhanced ADAS System

**Purpose**: Advanced ADAS with deep learning, enhanced features, and performance optimization

**Key Enhancements**:
- Deep learning lane detection with CV fallback
- Advanced distance estimation
- Enhanced overlays with animations
- Bird's eye view transformation
- Performance monitoring and adaptation
- Error handling and recovery

**Class Structure**:
```python
class EnhancedADASSystem(ADASSystem):
    """Enhanced ADAS with DL and advanced features"""
    
    def __init__(self, config_path=None, yolo_model='yolov8n.pt', 
                 conf_threshold=0.5):
        # Initialize base system
        super().__init__(yolo_model, conf_threshold)
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        
        # Initialize advanced components
        self.model_manager = ModelManager(self.config)
        self.dl_lane_detector = self._init_dl_lane_detector()
        self.hybrid_lane_detector = HybridLaneDetector(
            self.dl_lane_detector,
            conf_threshold=0.6,
            max_consecutive_failures=5
        )
        
        # Enhanced warning systems
        self.distance_estimator = DistanceEstimator(
            self.config.get('camera.calibration_file')
        )
        self.enhanced_fcws = EnhancedFCWS(
            warning_distance=30.0,
            critical_distance=15.0,
            distance_estimator=self.distance_estimator
        )
        
        # Rendering components
        self.animation_engine = AnimationEngine()
        self.overlay_renderer = AdvancedOverlayRenderer(
            self.config_loader.get_overlay_config(),
            self.animation_engine
        )
        self.bev_transformer = BirdEyeViewTransformer(
            output_size=(300, 400)
        )
        
        # Performance tracking
        self.performance_stats = {
            'total_frames': 0,
            'total_time': 0.0,
            'frame_times': [],
            'detection_times': [],
            'overlay_times': [],
            'errors': 0
        }
        
        # Error handling
        self.error_handler = ErrorHandler(max_consecutive_errors=5)
        
        # Current state
        self.current_vehicle_offset = 0
```

**Enhanced Processing Pipeline**:
```python
def process_frame(self, frame: np.ndarray) -> np.ndarray:
    """
    Enhanced frame processing with DL and advanced features
    
    Pipeline:
    1. Object Detection (YOLOv8)
    2. Lane Detection (DL + CV Fallback)
    3. Calculate Lane Metrics
    4. Enhanced FCWS with Distance Estimation
    5. LDWS Check
    6. LKAS Calculation
    7. Advanced Overlay Rendering
    8. Bird's Eye View Transformation
    9. Status Panel Drawing
    10. Performance Monitoring
    """
    frame_start = time.time()
    height, width = frame.shape[:2]
    
    try:
        # 1. Object Detection
        detection_start = time.time()
        detections = self.object_detector.detect(frame)
        self.performance_stats['detection_times'].append(
            time.time() - detection_start
        )
        
        # 2. Hybrid Lane Detection (DL + CV Fallback)
        lane_result = self.hybrid_lane_detector.detect_lanes(frame)
        left_lane = lane_result.left_lane
        right_lane = lane_result.right_lane
        
        # 3. Calculate Lane Metrics
        lane_center, vehicle_offset = self.lane_detector.calculate_lane_center(
            left_lane, right_lane, width, height
        )
        
        # Store for status reporting
        self.current_vehicle_offset = vehicle_offset if vehicle_offset else 0
        
        # 4. Enhanced FCWS with Distance Estimation
        fcws_state, risky_detections = self.enhanced_fcws.check_collision_risk(
            detections, height
        )
        
        # 5. LDWS Check
        ldws_state = self.ldws.check_lane_departure(
            lane_center, vehicle_offset, width
        )
        
        # 6. LKAS Calculation
        steering_angle = self.lkas.calculate_steering_angle(
            lane_center, vehicle_offset, width
        )
        
        # 7. Advanced Overlay Rendering
        overlay_start = time.time()
        
        # Draw lane polygon
        if self.config.get('overlays.lane_polygon.enabled', True):
            frame = self.overlay_renderer.draw_lane_polygon(
                frame, left_lane, right_lane,
                color=(0, 255, 0),
                alpha=0.3
            )
        
        # Draw distance markers
        if self.config.get('overlays.distance_markers.enabled', True):
            distances = [
                self.distance_estimator.estimate_distance(
                    det['bbox'], height, det['class']
                )
                for det in risky_detections
            ]
            frame = self.overlay_renderer.draw_distance_markers(
                frame, risky_detections, distances
            )
        
        # Draw warnings
        frame = self.fcws.draw_warning(frame, risky_detections)
        frame = self.ldws.draw_warning(frame, lane_center, vehicle_offset)
        frame = self.lkas.draw_assistance(frame, lane_center, vehicle_offset)
        
        # Draw detections
        frame = self.object_detector.draw_detections(frame, detections)
        
        self.performance_stats['overlay_times'].append(
            time.time() - overlay_start
        )
        
        # 8. Bird's Eye View Transformation
        if self.config.get('overlays.bev.enabled', True):
            try:
                self.bev_transformer.set_default_points(width, height)
                bev_frame = self.bev_transformer.transform_frame(frame)
                
                if bev_frame is not None:
                    left_bev, right_bev = self.bev_transformer.transform_lanes(
                        left_lane, right_lane
                    )
                    bev_frame = self.bev_transformer.draw_bev_overlay(
                        bev_frame, left_bev, right_bev
                    )
                    
                    frame = self.bev_transformer.create_pip_overlay(
                        frame, bev_frame,
                        position='bottom-right',
                        size=(300, 400),
                        alpha=0.8
                    )
            except Exception as e:
                logger.debug(f"BEV rendering error: {e}")
        
        # 9. Draw Status Panel
        frame = self._draw_enhanced_status_panel(
            frame, fcws_state, ldws_state, len(detections),
            self.hybrid_lane_detector.dl_enabled
        )
        
        # 10. Update Performance Stats
        frame_time = time.time() - frame_start
        self.performance_stats['total_frames'] += 1
        self.performance_stats['total_time'] += frame_time
        self.performance_stats['frame_times'].append(frame_time)
        
        # Check performance and adapt
        self._check_performance_and_adapt()
        
        return frame
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        self.performance_stats['errors'] += 1
        self.error_handler.handle_processing_error(
            e, self.performance_stats['total_frames']
        )
        return frame
```

**System Status Method**:
```python
def get_system_status(self) -> Dict[str, Any]:
    """Get complete system status for web interface"""
    return {
        'fcws': {
            'warning_state': self.fcws.warning_state,
            'statistics': self.enhanced_fcws.get_statistics()
        },
        'ldws': {
            'state': self.ldws.warning_state,
            'lane_offset': self.current_vehicle_offset
        },
        'lkas': {
            'active': self.lkas.assist_active,
            'steering_angle': self.lkas.steering_angle
        },
        'lane_detection': {
            'dl_enabled': self.hybrid_lane_detector.dl_enabled,
            'stats': self.hybrid_lane_detector.get_statistics()
        },
        'distance_estimation': self.distance_estimator.get_calibration_info(),
        'performance': self.get_performance_metrics(),
        'config': {
            'overlays_enabled': self.config.get('overlays.lane_polygon.enabled'),
            'bev_enabled': self.config.get('overlays.bev.enabled'),
            'animations_enabled': self.config.get('overlays.animations.enabled')
        }
    }
```

**Performance Monitoring**:
```python
def _check_performance_and_adapt(self):
    """Monitor performance and adapt settings"""
    if len(self.performance_stats['frame_times']) < 10:
        return
    
    # Calculate average frame time
    recent_times = self.performance_stats['frame_times'][-10:]
    avg_time = sum(recent_times) / len(recent_times)
    
    # If processing too slow (< 15 FPS)
    if avg_time > 0.067:  # 67ms = ~15 FPS
        logger.warning(f"Performance degraded: {1/avg_time:.1f} FPS")
        
        # Disable non-critical features
        if self.config.get('overlays.bev.enabled'):
            self.config['overlays.bev.enabled'] = False
            logger.info("Disabled BEV to improve performance")
        
        if self.config.get('overlays.animations.enabled'):
            self.config['overlays.animations.enabled'] = False
            logger.info("Disabled animations to improve performance")
```

---


## 2. DETECTION COMPONENTS

### 2.1 object_detector.py - YOLOv8 Object Detection

**Purpose**: Detect vehicles, pedestrians, and obstacles using YOLOv8

**Key Code**:
```python
from ultralytics import YOLO
import cv2
import numpy as np

class ObjectDetector:
    """YOLOv8-based object detection"""
    
    def __init__(self, model_path='yolov8n.pt', conf_threshold=0.5):
        """
        Initialize object detector
        
        Args:
            model_path: Path to YOLOv8 model (.pt file)
            conf_threshold: Confidence threshold (0-1)
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # COCO class names relevant for ADAS
        self.target_classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'bus', 
            'truck', 'traffic light', 'stop sign'
        ]
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame
        
        Returns:
            List of detections with format:
            {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class': str,
                'class_id': int
            }
        """
        # Run inference
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extract box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                # Filter by target classes
                if class_name in self.target_classes:
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence,
                        'class': class_name,
                        'class_id': class_id
                    })
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, 
                       detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det['class']
            
            # Color based on class
            if class_name in ['car', 'truck', 'bus']:
                color = (0, 255, 0)  # Green for vehicles
            elif class_name == 'person':
                color = (0, 0, 255)  # Red for pedestrians
            else:
                color = (255, 0, 0)  # Blue for others
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(frame, (x1, y1 - label_h - 10), 
                         (x1 + label_w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
```

---

### 2.2 lane_detector.py - Traditional CV Lane Detection

**Purpose**: Detect lane markings using traditional computer vision

**Algorithm**:
1. Convert to grayscale
2. Apply Gaussian blur
3. Canny edge detection
4. Region of interest masking
5. Hough line transform
6. Separate left/right lanes
7. Fit polynomial curves

**Key Code**:
```python
class LaneDetector:
    """Traditional CV-based lane detection"""
    
    def __init__(self):
        self.roi_vertices = None
        self.canny_low = 50
        self.canny_high = 150
    
    def detect_lanes(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect lane markings
        
        Returns:
            (left_lane, right_lane): Arrays of (x, y) points
        """
        # 1. Preprocessing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 2. Edge detection
        edges = cv2.Canny(blur, self.canny_low, self.canny_high)
        
        # 3. Region of interest
        height, width = frame.shape[:2]
        roi_vertices = np.array([[
            (width * 0.1, height),
            (width * 0.4, height * 0.6),
            (width * 0.6, height * 0.6),
            (width * 0.9, height)
        ]], dtype=np.int32)
        
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, roi_vertices, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # 4. Hough line detection
        lines = cv2.HoughLinesP(
            masked_edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=50,
            maxLineGap=150
        )
        
        if lines is None:
            return None, None
        
        # 5. Separate left and right lanes
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate slope
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            
            # Filter by slope
            if slope < -0.5:  # Left lane (negative slope)
                left_lines.append(line[0])
            elif slope > 0.5:  # Right lane (positive slope)
                right_lines.append(line[0])
        
        # 6. Fit polynomial curves
        left_lane = self._fit_lane_line(left_lines, height)
        right_lane = self._fit_lane_line(right_lines, height)
        
        return left_lane, right_lane
    
    def _fit_lane_line(self, lines: List, height: int) -> np.ndarray:
        """Fit polynomial to lane points"""
        if not lines:
            return None
        
        # Extract all points
        points = []
        for line in lines:
            x1, y1, x2, y2 = line
            points.extend([(x1, y1), (x2, y2)])
        
        if len(points) < 2:
            return None
        
        # Fit 2nd degree polynomial
        points = np.array(points)
        x = points[:, 0]
        y = points[:, 1]
        
        coeffs = np.polyfit(y, x, 2)
        
        # Generate points along the curve
        y_points = np.linspace(height * 0.6, height, 100)
        x_points = np.polyval(coeffs, y_points)
        
        lane_points = np.column_stack((x_points, y_points)).astype(np.int32)
        
        return lane_points
    
    def calculate_lane_center(self, left_lane: np.ndarray, 
                             right_lane: np.ndarray,
                             width: int, height: int) -> Tuple[float, float]:
        """
        Calculate lane center and vehicle offset
        
        Returns:
            (lane_center_x, vehicle_offset)
        """
        if left_lane is None or right_lane is None:
            return None, None
        
        # Get bottom points of lanes
        left_bottom = left_lane[-1][0]
        right_bottom = right_lane[-1][0]
        
        # Calculate lane center
        lane_center = (left_bottom + right_bottom) / 2
        
        # Vehicle is assumed to be at frame center
        vehicle_center = width / 2
        
        # Calculate offset (positive = right of center)
        offset = vehicle_center - lane_center
        
        return lane_center, offset
    
    def draw_lanes(self, frame: np.ndarray, 
                   left_lane: np.ndarray, 
                   right_lane: np.ndarray) -> np.ndarray:
        """Draw detected lanes on frame"""
        overlay = frame.copy()
        
        if left_lane is not None:
            cv2.polylines(overlay, [left_lane], False, (0, 255, 0), 5)
        
        if right_lane is not None:
            cv2.polylines(overlay, [right_lane], False, (0, 255, 0), 5)
        
        # Draw lane polygon
        if left_lane is not None and right_lane is not None:
            # Create polygon between lanes
            polygon = np.vstack((left_lane, right_lane[::-1]))
            cv2.fillPoly(overlay, [polygon], (0, 255, 0))
            
            # Blend with original
            frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        return frame
```

---

### 2.3 hybrid_lane_detector.py - DL + CV Hybrid

**Purpose**: Combine deep learning and CV with intelligent fallback

**Key Code**:
```python
class HybridLaneDetector:
    """Hybrid lane detector with DL and CV fallback"""
    
    def __init__(self, dl_detector: ONNXLaneDetector,
                 conf_threshold: float = 0.6,
                 max_consecutive_failures: int = 5):
        """
        Initialize hybrid detector
        
        Args:
            dl_detector: Deep learning detector (ONNX)
            conf_threshold: Confidence threshold for DL
            max_consecutive_failures: Max failures before fallback
        """
        self.dl_detector = dl_detector
        self.cv_detector = LaneDetector()
        self.conf_threshold = conf_threshold
        self.max_consecutive_failures = max_consecutive_failures
        
        # State tracking
        self.consecutive_failures = 0
        self.dl_enabled = True
        
        # Statistics
        self.statistics = {
            'total_detections': 0,
            'dl_detections': 0,
            'cv_detections': 0,
            'dl_failures': 0
        }
    
    def detect_lanes(self, frame: np.ndarray) -> LaneDetectionResult:
        """
        Detect lanes with DL, fallback to CV if needed
        
        Returns:
            LaneDetectionResult with lanes and metadata
        """
        self.statistics['total_detections'] += 1
        
        # Try DL detection first
        if self.dl_enabled and self.dl_detector is not None:
            try:
                result = self.dl_detector.detect_lanes(frame)
                
                # Check confidence
                if result.success and result.confidence >= self.conf_threshold:
                    # DL detection successful
                    self.consecutive_failures = 0
                    self.statistics['dl_detections'] += 1
                    result.model_used = 'dl'
                    return result
                else:
                    # Low confidence, try CV
                    self.consecutive_failures += 1
                    self.statistics['dl_failures'] += 1
                    
            except Exception as e:
                logger.warning(f"DL detection error: {e}")
                self.consecutive_failures += 1
                self.statistics['dl_failures'] += 1
        
        # Check if should disable DL
        if self.consecutive_failures >= self.max_consecutive_failures:
            logger.warning("Disabling DL detector due to consecutive failures")
            self.dl_enabled = False
        
        # Fallback to CV detection
        left_lane, right_lane = self.cv_detector.detect_lanes(frame)
        
        self.statistics['cv_detections'] += 1
        
        return LaneDetectionResult(
            left_lane=left_lane,
            right_lane=right_lane,
            confidence=0.5,  # CV doesn't provide confidence
            lane_type='unknown',
            success=(left_lane is not None and right_lane is not None),
            processing_time=0.0,
            model_used='cv'
        )
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        return {
            **self.statistics,
            'dl_success_rate': (
                self.statistics['dl_detections'] / 
                max(1, self.statistics['total_detections'])
            ),
            'cv_usage_rate': (
                self.statistics['cv_detections'] / 
                max(1, self.statistics['total_detections'])
            )
        }
```

---

