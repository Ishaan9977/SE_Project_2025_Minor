"""
Hybrid Lane Detector with DL and CV Fallback
Automatically falls back to CV detection when DL confidence is low
"""

import logging
import time
from typing import Optional, Tuple
import numpy as np

from .dl_lane_detector import DLLaneDetector
from .lane_detection_result import LaneDetectionResult
from lane_detector import LaneDetector

logger = logging.getLogger(__name__)


class HybridLaneDetector:
    """
    Hybrid lane detector that uses DL model with CV fallback
    """
    
    def __init__(self, dl_detector: Optional[DLLaneDetector], 
                 conf_threshold: float = 0.6,
                 max_consecutive_failures: int = 5):
        """
        Initialize Hybrid Lane Detector
        
        Args:
            dl_detector: Deep learning lane detector (can be None)
            conf_threshold: Confidence threshold for using DL results
            max_consecutive_failures: Max consecutive DL failures before disabling
        """
        self.dl_detector = dl_detector
        self.cv_detector = LaneDetector()  # Traditional CV detector
        self.conf_threshold = conf_threshold
        self.max_consecutive_failures = max_consecutive_failures
        
        self.consecutive_failures = 0
        self.dl_enabled = dl_detector is not None and dl_detector.is_model_loaded()
        self.fallback_count = 0
        self.dl_success_count = 0
        self.cv_fallback_count = 0
        
        logger.info(f"Hybrid Lane Detector initialized")
        logger.info(f"DL enabled: {self.dl_enabled}, Confidence threshold: {self.conf_threshold}")
    
    def detect_lanes(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], np.ndarray]:
        """
        Detect lanes with automatic fallback
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (left_lane, right_lane, processed_frame)
        """
        left_lane = None
        right_lane = None
        used_dl = False
        
        # Try DL detection first if enabled
        if self.dl_enabled and self.consecutive_failures < self.max_consecutive_failures:
            try:
                result = self.dl_detector.detect_lanes(frame)
                
                # Check if DL detection was successful and confident
                if result.success and result.confidence >= self.conf_threshold:
                    # Use DL results
                    left_lane, right_lane = self._convert_dl_result_to_lines(result, frame.shape)
                    
                    if left_lane is not None or right_lane is not None:
                        used_dl = True
                        self.consecutive_failures = 0
                        self.dl_success_count += 1
                        logger.debug(f"DL detection successful (confidence: {result.confidence:.2f})")
                    else:
                        logger.debug("DL detection returned no valid lanes")
                        self.consecutive_failures += 1
                else:
                    logger.debug(f"DL confidence too low: {result.confidence:.2f} < {self.conf_threshold}")
                    self.consecutive_failures += 1
            
            except Exception as e:
                logger.warning(f"DL detection error: {e}")
                self.consecutive_failures += 1
        
        # Fallback to CV if DL failed or not used
        if not used_dl:
            try:
                left_lane, right_lane, _ = self.cv_detector.detect_lanes(frame)
                self.cv_fallback_count += 1
                logger.debug("Using CV fallback detection")
            except Exception as e:
                logger.error(f"CV detection error: {e}")
        
        # Check if DL should be disabled
        if self.consecutive_failures >= self.max_consecutive_failures and self.dl_enabled:
            logger.warning(f"DL detector disabled after {self.consecutive_failures} consecutive failures")
            self.dl_enabled = False
        
        return left_lane, right_lane, frame
    
    def _convert_dl_result_to_lines(self, result: LaneDetectionResult, 
                                    frame_shape: Tuple[int, int, int]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Convert DL detection result to line format compatible with existing system
        
        Args:
            result: LaneDetectionResult from DL detector
            frame_shape: Frame shape (height, width, channels)
            
        Returns:
            Tuple of (left_lane, right_lane) in [x1, y1, x2, y2] format
        """
        height, width = frame_shape[:2]
        
        left_lane = None
        right_lane = None
        
        # Convert left lane
        if result.left_lane is not None:
            left_lane = self._points_to_line(result.left_lane, height)
        
        # Convert right lane
        if result.right_lane is not None:
            right_lane = self._points_to_line(result.right_lane, height)
        
        return left_lane, right_lane
    
    def _points_to_line(self, points: np.ndarray, frame_height: int) -> Optional[np.ndarray]:
        """
        Convert lane points to line format [x1, y1, x2, y2]
        
        Args:
            points: Lane points (Nx2 or polynomial coefficients)
            frame_height: Frame height
            
        Returns:
            Line coordinates or None
        """
        if points is None:
            return None
        
        try:
            # Check if points are polynomial coefficients
            if points.ndim == 1 and len(points) <= 3:
                # Polynomial coefficients
                y1 = frame_height
                y2 = int(frame_height * 0.6)
                
                x1 = int(np.polyval(points, y1))
                x2 = int(np.polyval(points, y2))
                
                return np.array([x1, y1, x2, y2])
            
            # Check if already in line format
            elif points.ndim == 1 and len(points) == 4:
                return points
            
            # Points array - fit polynomial
            elif points.ndim == 2 and points.shape[1] == 2:
                # Fit polynomial to points
                if len(points) < 2:
                    return None
                
                x = points[:, 0]
                y = points[:, 1]
                
                # Fit 2nd degree polynomial
                try:
                    coeffs = np.polyfit(y, x, 2)
                except:
                    # Fallback to linear
                    coeffs = np.polyfit(y, x, 1)
                
                y1 = frame_height
                y2 = int(frame_height * 0.6)
                
                x1 = int(np.polyval(coeffs, y1))
                x2 = int(np.polyval(coeffs, y2))
                
                return np.array([x1, y1, x2, y2])
        
        except Exception as e:
            logger.warning(f"Error converting points to line: {e}")
        
        return None
    
    def get_statistics(self) -> dict:
        """Get detection statistics"""
        total = self.dl_success_count + self.cv_fallback_count
        
        return {
            'dl_success_count': self.dl_success_count,
            'cv_fallback_count': self.cv_fallback_count,
            'total_detections': total,
            'dl_success_rate': self.dl_success_count / total if total > 0 else 0.0,
            'consecutive_failures': self.consecutive_failures,
            'dl_enabled': self.dl_enabled
        }
    
    def reset_statistics(self):
        """Reset detection statistics"""
        self.dl_success_count = 0
        self.cv_fallback_count = 0
        self.consecutive_failures = 0
    
    def enable_dl(self):
        """Re-enable DL detection"""
        if self.dl_detector is not None and self.dl_detector.is_model_loaded():
            self.dl_enabled = True
            self.consecutive_failures = 0
            logger.info("DL detection re-enabled")
    
    def disable_dl(self):
        """Disable DL detection"""
        self.dl_enabled = False
        logger.info("DL detection disabled")
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold"""
        if 0.0 <= threshold <= 1.0:
            self.conf_threshold = threshold
            logger.info(f"Confidence threshold updated to {threshold}")
        else:
            logger.warning(f"Invalid confidence threshold: {threshold}")
