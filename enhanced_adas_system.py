"""
Enhanced ADAS System - Complete Integration
Integrates all components: DL detection, distance estimation, overlays, BEV, animations
"""

import cv2
import numpy as np
import time
import logging
from typing import Dict, Any, List, Tuple, Optional

from main import ADASSystem
from utils.config_loader import ConfigLoader
from utils.model_manager import ModelManager
from utils.distance_estimator import DistanceEstimator
from dl_models.hybrid_lane_detector import HybridLaneDetector
from dl_models.onnx_lane_detector import ONNXLaneDetector
from enhanced_fcws import EnhancedFCWS
from overlays.animation_engine import AnimationEngine
from overlays.advanced_overlay_renderer import AdvancedOverlayRenderer
from transforms.bev_transformer import BirdEyeViewTransformer

logger = logging.getLogger(__name__)


class EnhancedADASSystem(ADASSystem):
    """
    Enhanced ADAS System with all Phase 1-3 features integrated
    """
    
    def __init__(self, config_path: Optional[str] = None, yolo_model: str = 'yolov8n.pt',
                 conf_threshold: float = 0.5):
        """
        Initialize Enhanced ADAS System
        
        Args:
            config_path: Path to configuration file
            yolo_model: YOLOv8 model path
            conf_threshold: Object detection confidence threshold
        """
        # Initialize base ADAS system
        super().__init__(yolo_model=yolo_model, conf_threshold=conf_threshold)
        
        logger.info("Initializing Enhanced ADAS System...")
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        
        # Initialize Model Manager
        logger.info("Initializing Model Manager...")
        self.model_manager = ModelManager(self.config)
        
        # Initialize DL Lane Detection
        logger.info("Initializing DL Lane Detection...")
        self.dl_lane_detector = self._init_dl_lane_detector()
        
        # Initialize Hybrid Lane Detector
        logger.info("Initializing Hybrid Lane Detector...")
        self.hybrid_lane_detector = HybridLaneDetector(
            self.dl_lane_detector,
            conf_threshold=self.config.get('fallback.cv_confidence_threshold', 0.6),
            max_consecutive_failures=self.config.get('fallback.max_consecutive_dl_failures', 5)
        )
        
        # Initialize Distance Estimator
        logger.info("Initializing Distance Estimator...")
        calibration_file = self.config.get('camera.calibration_file')
        self.distance_estimator = DistanceEstimator(calibration_file)
        
        # Initialize Enhanced FCWS
        logger.info("Initializing Enhanced FCWS...")
        self.enhanced_fcws = EnhancedFCWS(
            warning_distance=self.config.get('fcws.warning_distance', 30.0),
            critical_distance=self.config.get('fcws.critical_distance', 15.0),
            distance_estimator=self.distance_estimator
        )
        
        # Initialize Animation Engine
        logger.info("Initializing Animation Engine...")
        self.animation_engine = AnimationEngine()
        
        # Initialize Advanced Overlay Renderer
        logger.info("Initializing Advanced Overlay Renderer...")
        overlay_config = self.config_loader.get_overlay_config()
        self.overlay_renderer = AdvancedOverlayRenderer(overlay_config, self.animation_engine)
        
        # Initialize BEV Transformer
        logger.info("Initializing BEV Transformer...")
        bev_size = tuple(self.config.get('overlays.bev.size', [300, 400]))
        self.bev_transformer = BirdEyeViewTransformer(output_size=bev_size)
        
        # Current state tracking
        self.current_vehicle_offset = 0
        
        # Performance tracking
        self.performance_stats = {
            'total_frames': 0,
            'total_time': 0.0,
            'frame_times': [],
            'detection_times': [],
            'overlay_times': [],
            'errors': 0
        }
        
        # Error tracking
        self.error_handler = ErrorHandler(
            max_consecutive_errors=self.config.get('fallback.max_consecutive_dl_failures', 5)
        )
        
        logger.info("Enhanced ADAS System initialized successfully!")
    
    def _init_dl_lane_detector(self) -> Optional[ONNXLaneDetector]:
        """Initialize DL lane detector"""
        try:
            model_config = self.config.get('models.lane_detection', {})
            
            if not model_config.get('enabled', True):
                logger.info("DL lane detection disabled in config")
                return None
            
            model_path = model_config.get('model_path')
            model_type = model_config.get('model_type', 'onnx')
            device = self.model_manager.get_device()
            conf_threshold = model_config.get('confidence_threshold', 0.6)
            
            if model_type.lower() == 'onnx':
                detector = ONNXLaneDetector(
                    model_path=model_path,
                    device=device,
                    conf_threshold=conf_threshold
                )
                
                if detector.is_model_loaded():
                    logger.info(f"DL Lane Detector loaded successfully (device: {device})")
                    return detector
                else:
                    logger.warning("Failed to load DL lane detector, will use CV fallback")
                    return None
            else:
                logger.warning(f"Unsupported model type: {model_type}")
                return None
        
        except Exception as e:
            logger.error(f"Error initializing DL lane detector: {e}")
            return None
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame with all enhanced features
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Processed frame with all overlays
        """
        frame_start = time.time()
        height, width = frame.shape[:2]
        
        try:
            # 1. Object Detection
            det_start = time.time()
            detections = self.object_detector.detect(frame)
            det_time = time.time() - det_start
            self.performance_stats['detection_times'].append(det_time)
            
            # 2. Lane Detection (Hybrid DL+CV)
            left_lane, right_lane, _ = self.hybrid_lane_detector.detect_lanes(frame)
            
            # 3. Calculate lane metrics
            lane_center, vehicle_offset = self.lane_detector.calculate_lane_center(
                left_lane, right_lane, width, height
            )
            
            # Store for status reporting
            self.current_vehicle_offset = vehicle_offset if vehicle_offset is not None else 0
            
            # 4. Enhanced FCWS with distance estimation
            fcws_state, risky_detections = self.enhanced_fcws.check_collision_risk(detections, frame)
            
            # 5. LDWS
            ldws_state = self.ldws.check_lane_departure(lane_center, vehicle_offset, width)
            
            # 6. LKAS
            steering_angle = self.lkas.calculate_steering_angle(lane_center, vehicle_offset, width)
            
            # 7. Update animations
            self.animation_engine.update(0.033)  # ~30 FPS
            
            # 8. Render overlays
            overlay_start = time.time()
            
            # Lane polygon
            frame = self.overlay_renderer.draw_lane_polygon(frame, left_lane, right_lane)
            
            # Distance markers
            frame = self.overlay_renderer.draw_distance_markers(frame, detections, [])
            
            # Enhanced FCWS warnings
            frame = self.enhanced_fcws.draw_warning(frame, risky_detections)
            
            # LDWS warnings
            frame = self.ldws.draw_warning(frame, lane_center, vehicle_offset)
            
            # LKAS assistance
            frame = self.lkas.draw_assistance(frame, lane_center, vehicle_offset)
            
            # Object detections
            frame = self.object_detector.draw_detections(frame, detections)
            
            # 9. BEV Transformation
            if self.config.get('overlays.bev.enabled', True):
                try:
                    self.bev_transformer.set_default_points(width, height)
                    bev_frame = self.bev_transformer.transform_frame(frame)
                    
                    if bev_frame is not None:
                        left_bev, right_bev = self.bev_transformer.transform_lanes(left_lane, right_lane)
                        bev_frame = self.bev_transformer.draw_bev_overlay(bev_frame, left_bev, right_bev)
                        
                        bev_position = self.config.get('overlays.bev.position', 'bottom-right')
                        bev_size = tuple(self.config.get('overlays.bev.size', [300, 400]))
                        bev_alpha = self.config.get('overlays.bev.alpha', 0.8)
                        
                        frame = self.bev_transformer.create_pip_overlay(
                            frame, bev_frame, position=bev_position, size=bev_size, alpha=bev_alpha
                        )
                except Exception as e:
                    logger.debug(f"BEV rendering error: {e}")
            
            overlay_time = time.time() - overlay_start
            self.performance_stats['overlay_times'].append(overlay_time)
            
            # 10. Draw status panel
            frame = self._draw_enhanced_status_panel(
                frame, fcws_state, ldws_state, len(detections),
                self.hybrid_lane_detector.dl_enabled
            )
            
            # Update performance stats
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
            self.error_handler.handle_processing_error(e, self.performance_stats['total_frames'])
            
            # Return original frame on error
            return frame
    
    def _draw_enhanced_status_panel(self, frame: np.ndarray, fcws_state: str,
                                   ldws_state: str, num_detections: int,
                                   dl_enabled: bool) -> np.ndarray:
        """Draw enhanced status panel with additional information"""
        height, width = frame.shape[:2]
        
        # Draw semi-transparent panel
        panel_height = 150
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (10, 10), (400, panel_height), (255, 255, 255), 2)
        
        # Draw status information
        y_offset = 35
        line_height = 25
        
        # FCWS status
        fcws_color = (0, 255, 0) if fcws_state == "SAFE" else (0, 165, 255) if fcws_state == "WARNING" else (0, 0, 255)
        cv2.putText(frame, f"FCWS: {fcws_state}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fcws_color, 2)
        
        # LDWS status
        ldws_color = (0, 255, 0) if ldws_state == "SAFE" else (0, 165, 255)
        cv2.putText(frame, f"LDWS: {ldws_state}", (20, y_offset + line_height),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, ldws_color, 2)
        
        # LKAS status
        lkas_color = (0, 255, 0) if self.lkas.assist_active else (128, 128, 128)
        lkas_status = "ACTIVE" if self.lkas.assist_active else "STANDBY"
        cv2.putText(frame, f"LKAS: {lkas_status}", (20, y_offset + line_height * 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, lkas_color, 2)
        
        # Detection count
        cv2.putText(frame, f"Objects: {num_detections}", (20, y_offset + line_height * 3),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Lane detection mode
        lane_mode = "DL" if dl_enabled else "CV"
        lane_color = (0, 255, 0) if dl_enabled else (0, 165, 255)
        cv2.putText(frame, f"Lane: {lane_mode}", (20, y_offset + line_height * 4),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, lane_color, 2)
        
        # FPS
        if len(self.performance_stats['frame_times']) > 0:
            avg_frame_time = np.mean(self.performance_stats['frame_times'][-30:])
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            cv2.putText(frame, f"FPS: {fps:.1f}", (220, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame
    
    def _check_performance_and_adapt(self):
        """Check performance and adapt settings if needed"""
        if len(self.performance_stats['frame_times']) < 30:
            return
        
        # Calculate average frame time
        avg_frame_time = np.mean(self.performance_stats['frame_times'][-30:])
        max_latency = self.config.get('performance.max_latency_ms', 100) / 1000.0
        
        # Check if performance is degrading
        if avg_frame_time > max_latency:
            logger.warning(f"Performance degradation detected: {avg_frame_time*1000:.1f}ms > {max_latency*1000:.1f}ms")
            
            # Disable non-critical overlays
            if self.config.get('overlays.bev.enabled', True):
                logger.info("Disabling BEV overlay for performance")
                self.config['overlays.bev.enabled'] = False
            
            if self.config.get('overlays.animations.enabled', True):
                logger.info("Disabling animations for performance")
                self.config['overlays.animations.enabled'] = False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if self.performance_stats['total_frames'] == 0:
            return {}
        
        avg_frame_time = self.performance_stats['total_time'] / self.performance_stats['total_frames']
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        return {
            'total_frames': self.performance_stats['total_frames'],
            'total_time': self.performance_stats['total_time'],
            'avg_frame_time_ms': avg_frame_time * 1000,
            'fps': fps,
            'avg_detection_time_ms': np.mean(self.performance_stats['detection_times']) * 1000 if self.performance_stats['detection_times'] else 0,
            'avg_overlay_time_ms': np.mean(self.performance_stats['overlay_times']) * 1000 if self.performance_stats['overlay_times'] else 0,
            'errors': self.performance_stats['errors'],
            'dl_lane_enabled': self.hybrid_lane_detector.dl_enabled
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
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
                'overlays_enabled': self.config.get('overlays.lane_polygon.enabled', True),
                'bev_enabled': self.config.get('overlays.bev.enabled', True),
                'animations_enabled': self.config.get('overlays.animations.enabled', True)
            }
        }


class ErrorHandler:
    """Error handling and recovery"""
    
    def __init__(self, max_consecutive_errors: int = 10):
        """Initialize error handler"""
        self.max_consecutive_errors = max_consecutive_errors
        self.consecutive_errors = 0
        self.error_log = []
    
    def handle_processing_error(self, error: Exception, frame_num: int):
        """Handle processing error"""
        self.consecutive_errors += 1
        self.error_log.append({
            'frame': frame_num,
            'error': str(error),
            'timestamp': time.time()
        })
        
        if self.consecutive_errors >= self.max_consecutive_errors:
            logger.error(f"Too many consecutive errors ({self.consecutive_errors}), entering safe mode")
    
    def reset(self):
        """Reset error counters"""
        self.consecutive_errors = 0
