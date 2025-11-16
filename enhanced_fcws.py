"""
Enhanced Forward Collision Warning System (FCWS)
Uses DistanceEstimator for accurate distance measurements
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Any

from utils.distance_estimator import DistanceEstimator, DistanceEstimation

logger = logging.getLogger(__name__)


class EnhancedFCWS:
    """Enhanced Forward Collision Warning System with calibrated distance estimation"""
    
    def __init__(self, warning_distance: float = 30.0, critical_distance: float = 15.0,
                 distance_estimator: Optional[DistanceEstimator] = None):
        """
        Initialize Enhanced FCWS
        
        Args:
            warning_distance: Distance threshold for warning (meters if calibrated, else normalized)
            critical_distance: Distance threshold for critical warning (meters if calibrated, else normalized)
            distance_estimator: DistanceEstimator instance (creates new if None)
        """
        self.warning_distance = warning_distance
        self.critical_distance = critical_distance
        self.warning_state = "SAFE"  # SAFE, WARNING, CRITICAL
        
        # Use provided distance estimator or create new one
        self.distance_estimator = distance_estimator or DistanceEstimator()
        
        # Track if using calibrated distances
        self.using_calibrated = self.distance_estimator.has_calibration
        
        logger.info(f"Enhanced FCWS initialized (calibrated: {self.using_calibrated})")
        logger.info(f"Warning distance: {warning_distance}, Critical distance: {critical_distance}")
    
    def check_collision_risk(self, detections: List[Dict], frame: np.ndarray) -> Tuple[str, List[Dict]]:
        """
        Check for collision risk with detected objects using enhanced distance estimation
        
        Args:
            detections: List of detected objects
            frame: Current frame
            
        Returns:
            Tuple of (warning_state, risky_detections)
        """
        height, width = frame.shape[:2]
        risky_detections = []
        
        # Filter detections in the forward path (center region)
        forward_zone_left = width * 0.2
        forward_zone_right = width * 0.8
        
        for det in detections:
            center_x = det['center'][0]
            
            # Check if object is in forward path
            if forward_zone_left < center_x < forward_zone_right:
                # Check if object is a vehicle (higher priority)
                if det['class'] in ['car', 'truck', 'bus', 'motorcycle', 'person']:
                    # Estimate distance using enhanced estimator
                    bbox = det['bbox']
                    object_class = det['class']
                    detection_conf = det.get('confidence', 1.0)
                    
                    distance_est = self.distance_estimator.estimate_distance(
                        bbox, height, object_class, detection_conf
                    )
                    
                    # Store distance estimation
                    det['distance_estimation'] = distance_est
                    det['distance'] = distance_est.distance_meters if distance_est.distance_meters else distance_est.distance_pixels
                    det['distance_confidence'] = distance_est.confidence
                    
                    risky_detections.append(det)
        
        # Sort by distance (closest first)
        risky_detections.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Determine warning state based on closest object
        if not risky_detections:
            self.warning_state = "SAFE"
        else:
            closest = risky_detections[0]
            distance_est = closest['distance_estimation']
            
            # Use appropriate distance value
            if distance_est.has_calibration and distance_est.distance_meters:
                distance = distance_est.distance_meters
            else:
                # Use normalized distance for uncalibrated
                distance = self.distance_estimator._normalize_distance(
                    distance_est.distance_pixels, height
                )
            
            # Determine warning level
            if distance < self.critical_distance:
                self.warning_state = "CRITICAL"
            elif distance < self.warning_distance:
                self.warning_state = "WARNING"
            else:
                self.warning_state = "SAFE"
        
        return self.warning_state, risky_detections
    
    def draw_warning(self, frame: np.ndarray, risky_detections: List[Dict]) -> np.ndarray:
        """
        Draw enhanced FCWS warnings with distance information
        
        Args:
            frame: Input frame
            risky_detections: List of risky detections
            
        Returns:
            Frame with warnings drawn
        """
        height, width = frame.shape[:2]
        
        # Draw warning overlay
        if self.warning_state == "CRITICAL":
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Critical warning text
            text = "CRITICAL: BRAKE NOW!"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            text_x = (width - text_size[0]) // 2
            text_y = height // 2
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            
        elif self.warning_state == "WARNING":
            # Warning text
            text = "WARNING: Vehicle Ahead"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = 50
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
        
        # Draw distance information for top 3 closest objects
        for i, det in enumerate(risky_detections[:3]):
            x1, y1, x2, y2 = det['bbox']
            distance_est = det.get('distance_estimation')
            
            if distance_est:
                # Format distance text
                if distance_est.has_calibration and distance_est.distance_meters:
                    dist_text = f"{det['class']}: {distance_est.distance_meters:.1f}m"
                    conf_text = f"±{(distance_est.confidence_interval[1] - distance_est.distance_meters):.1f}m"
                else:
                    dist_text = f"{det['class']}: {distance_est.distance_pixels:.0f}px"
                    conf_text = f"conf: {distance_est.confidence:.2f}"
                
                # Color based on distance
                if i == 0:  # Closest object
                    if self.warning_state == "CRITICAL":
                        color = (0, 0, 255)  # Red
                    elif self.warning_state == "WARNING":
                        color = (0, 165, 255)  # Orange
                    else:
                        color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 255, 255)  # Yellow for others
                
                # Draw distance text with background
                text_size = cv2.getTextSize(dist_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                bg_x1 = x1
                bg_y1 = y1 - text_size[1] - 25
                bg_x2 = x1 + text_size[0] + 10
                bg_y2 = y1 - 5
                
                # Draw background rectangle
                cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
                cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2)
                
                # Draw distance text
                cv2.putText(frame, dist_text, (x1 + 5, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Draw confidence/interval text (smaller)
                cv2.putText(frame, conf_text, (x1 + 5, y1 - 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                # Highlight bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw confidence indicator (small bar)
                conf_bar_width = int(distance_est.confidence * 50)
                cv2.rectangle(frame, (x1, y2 + 5), (x1 + conf_bar_width, y2 + 10), color, -1)
        
        return frame
    
    def set_distance_thresholds(self, warning_distance: float, critical_distance: float):
        """
        Update distance thresholds
        
        Args:
            warning_distance: New warning distance threshold
            critical_distance: New critical distance threshold
        """
        self.warning_distance = warning_distance
        self.critical_distance = critical_distance
        logger.info(f"Distance thresholds updated: warning={warning_distance}, critical={critical_distance}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get FCWS statistics"""
        return {
            'warning_state': self.warning_state,
            'using_calibrated': self.using_calibrated,
            'warning_distance': self.warning_distance,
            'critical_distance': self.critical_distance,
            'calibration_info': self.distance_estimator.get_calibration_info()
        }
