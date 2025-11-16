"""
Forward Collision Warning System (FCWS)
Warns driver of potential collisions with vehicles ahead
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple


class FCWS:
    """Forward Collision Warning System"""
    
    def __init__(self, warning_distance: float = 100.0, critical_distance: float = 50.0):
        """
        Initialize FCWS
        
        Args:
            warning_distance: Distance threshold for warning (pixels)
            critical_distance: Distance threshold for critical warning (pixels)
        """
        self.warning_distance = warning_distance
        self.critical_distance = critical_distance
        self.warning_state = "SAFE"  # SAFE, WARNING, CRITICAL
    
    def calculate_distance(self, detection: Dict, frame_height: int) -> float:
        """
        Estimate distance to detected object based on bounding box size and position
        
        Args:
            detection: Detection dictionary with bbox and class info
            frame_height: Height of the frame
            
        Returns:
            Estimated distance (pixels)
        """
        x1, y1, x2, y2 = detection['bbox']
        bbox_height = y2 - y1
        bbox_width = x2 - x1
        bbox_area = bbox_width * bbox_height
        
        # Bottom center of bounding box (closest point to vehicle)
        bottom_y = y2
        center_x = (x1 + x2) / 2
        
        # Distance estimation based on:
        # 1. Bounding box size (larger = closer)
        # 2. Vertical position (lower = closer)
        # 3. Class type (different sizes for different vehicles)
        
        # Normalize by frame size
        normalized_area = bbox_area / (frame_height * frame_height)
        normalized_y = bottom_y / frame_height
        
        # Inverse relationship: larger area and lower position = closer
        # This is a simplified model - in real systems, you'd use camera calibration
        distance = frame_height * (1.0 - normalized_area * 2) * (1.0 - normalized_y * 0.5)
        
        # Ensure minimum distance
        distance = max(distance, 10.0)
        
        return distance
    
    def check_collision_risk(self, detections: List[Dict], frame: np.ndarray) -> Tuple[str, List[Dict]]:
        """
        Check for collision risk with detected objects
        
        Args:
            detections: List of detected objects
            frame: Current frame
            
        Returns:
            Tuple of (warning_state, risky_detections)
        """
        height, width = frame.shape[:2]
        risky_detections = []
        
        # Filter detections in the forward path (center region)
        forward_zone_width = width * 0.6
        forward_zone_left = width * 0.2
        forward_zone_right = width * 0.8
        
        for det in detections:
            center_x = det['center'][0]
            
            # Check if object is in forward path
            if forward_zone_left < center_x < forward_zone_right:
                distance = self.calculate_distance(det, height)
                
                # Check if object is a vehicle (higher priority)
                if det['class'] in ['car', 'truck', 'bus', 'motorcycle']:
                    det['distance'] = distance
                    risky_detections.append(det)
        
        # Sort by distance (closest first)
        risky_detections.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Determine warning state
        if not risky_detections:
            self.warning_state = "SAFE"
        else:
            closest_distance = risky_detections[0].get('distance', float('inf'))
            if closest_distance < self.critical_distance:
                self.warning_state = "CRITICAL"
            elif closest_distance < self.warning_distance:
                self.warning_state = "WARNING"
            else:
                self.warning_state = "SAFE"
        
        return self.warning_state, risky_detections
    
    def draw_warning(self, frame: np.ndarray, risky_detections: List[Dict]) -> np.ndarray:
        """
        Draw FCWS warnings on the frame
        
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
        
        # Draw distance information for risky detections
        for det in risky_detections[:3]:  # Show top 3 closest
            x1, y1, x2, y2 = det['bbox']
            distance = det.get('distance', 0)
            
            # Draw distance text
            dist_text = f"{det['class']}: {distance:.1f}px"
            cv2.putText(frame, dist_text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Highlight bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
        
        return frame

