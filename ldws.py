"""
Lane Departure Warning System (LDWS)
Warns driver when vehicle is about to depart from the lane
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class LDWS:
    """Lane Departure Warning System"""
    
    def __init__(self, departure_threshold: float = 30.0):
        """
        Initialize LDWS
        
        Args:
            departure_threshold: Pixel threshold for lane departure warning
        """
        self.departure_threshold = departure_threshold
        self.warning_state = "SAFE"  # SAFE, LEFT_WARNING, RIGHT_WARNING
        self.departure_count = 0  # Count consecutive departure frames
    
    def check_lane_departure(self, lane_center: Optional[float], 
                            vehicle_offset: Optional[float],
                            frame_width: int) -> str:
        """
        Check if vehicle is departing from the lane
        
        Args:
            lane_center: X coordinate of lane center
            vehicle_offset: Offset of vehicle from lane center
            frame_width: Width of the frame
            
        Returns:
            Warning state string
        """
        if lane_center is None or vehicle_offset is None:
            self.warning_state = "SAFE"
            self.departure_count = 0
            return self.warning_state
        
        # Check for left departure
        if vehicle_offset > self.departure_threshold:
            self.warning_state = "LEFT_WARNING"
            self.departure_count += 1
        # Check for right departure
        elif vehicle_offset < -self.departure_threshold:
            self.warning_state = "RIGHT_WARNING"
            self.departure_count += 1
        else:
            self.warning_state = "SAFE"
            self.departure_count = 0
        
        return self.warning_state
    
    def draw_warning(self, frame: np.ndarray, lane_center: Optional[float],
                    vehicle_offset: Optional[float]) -> np.ndarray:
        """
        Draw LDWS warnings on the frame
        
        Args:
            frame: Input frame
            lane_center: X coordinate of lane center
            vehicle_offset: Offset of vehicle from lane center
            
        Returns:
            Frame with warnings drawn
        """
        height, width = frame.shape[:2]
        
        # Draw lane center indicator
        if lane_center is not None:
            cv2.line(frame, (int(lane_center), height - 50), 
                    (int(lane_center), height), (255, 0, 255), 3)
            cv2.circle(frame, (int(lane_center), height - 25), 10, (255, 0, 255), -1)
        
        # Draw vehicle center indicator
        vehicle_center_x = width / 2
        cv2.line(frame, (int(vehicle_center_x), height - 50), 
                (int(vehicle_center_x), height), (0, 255, 255), 3)
        cv2.circle(frame, (int(vehicle_center_x), height - 25), 10, (0, 255, 255), -1)
        
        # Draw warning based on state
        if self.warning_state == "LEFT_WARNING":
            # Left departure warning
            text = "WARNING: Departing Left Lane"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = 100
            
            # Draw warning box
            cv2.rectangle(frame, (text_x - 10, text_y - 40), 
                         (text_x + text_size[0] + 10, text_y + 10), (0, 165, 255), -1)
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            
            # Draw left arrow
            arrow_points = np.array([
                [50, height // 2],
                [100, height // 2 - 30],
                [100, height // 2 - 10],
                [150, height // 2 - 10],
                [150, height // 2 + 10],
                [100, height // 2 + 10],
                [100, height // 2 + 30]
            ], np.int32)
            cv2.fillPoly(frame, [arrow_points], (0, 165, 255))
            
        elif self.warning_state == "RIGHT_WARNING":
            # Right departure warning
            text = "WARNING: Departing Right Lane"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = 100
            
            # Draw warning box
            cv2.rectangle(frame, (text_x - 10, text_y - 40), 
                         (text_x + text_size[0] + 10, text_y + 10), (0, 165, 255), -1)
            cv2.putText(frame, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            
            # Draw right arrow
            arrow_points = np.array([
                [width - 50, height // 2],
                [width - 100, height // 2 - 30],
                [width - 100, height // 2 - 10],
                [width - 150, height // 2 - 10],
                [width - 150, height // 2 + 10],
                [width - 100, height // 2 + 10],
                [width - 100, height // 2 + 30]
            ], np.int32)
            cv2.fillPoly(frame, [arrow_points], (0, 165, 255))
        
        # Draw offset information
        if vehicle_offset is not None:
            offset_text = f"Offset: {vehicle_offset:.1f}px"
            cv2.putText(frame, offset_text, (10, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame

