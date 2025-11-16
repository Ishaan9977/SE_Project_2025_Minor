"""
Lane Keeping Assistance System (LKAS)
Provides visual guidance to help driver stay in lane
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class LKAS:
    """Lane Keeping Assistance System"""
    
    def __init__(self, assist_threshold: float = 20.0):
        """
        Initialize LKAS
        
        Args:
            assist_threshold: Pixel threshold for activating assistance
        """
        self.assist_threshold = assist_threshold
        self.steering_angle = 0.0  # Calculated steering angle
        self.assist_active = False
    
    def calculate_steering_angle(self, lane_center: Optional[float], 
                                vehicle_offset: Optional[float],
                                frame_width: int) -> float:
        """
        Calculate steering angle recommendation
        
        Args:
            lane_center: X coordinate of lane center
            vehicle_offset: Offset of vehicle from lane center
            frame_width: Width of the frame
            
        Returns:
            Steering angle in degrees (negative = left, positive = right)
        """
        if lane_center is None or vehicle_offset is None:
            self.assist_active = False
            return 0.0
        
        # Activate assistance if offset exceeds threshold
        if abs(vehicle_offset) > self.assist_threshold:
            self.assist_active = True
            # Calculate steering angle (proportional to offset)
            # Normalize offset to frame width and convert to angle
            normalized_offset = vehicle_offset / (frame_width / 2)
            self.steering_angle = normalized_offset * 30.0  # Max 30 degrees
        else:
            self.assist_active = False
            self.steering_angle = 0.0
        
        return self.steering_angle
    
    def draw_assistance(self, frame: np.ndarray, lane_center: Optional[float],
                      vehicle_offset: Optional[float]) -> np.ndarray:
        """
        Draw LKAS guidance on the frame
        
        Args:
            frame: Input frame
            lane_center: X coordinate of lane center
            vehicle_offset: Offset of vehicle from lane center
            
        Returns:
            Frame with assistance guidance drawn
        """
        height, width = frame.shape[:2]
        vehicle_center_x = width / 2
        
        # Draw lane keeping zone
        if lane_center is not None:
            # Draw green zone (safe area)
            zone_width = 40
            cv2.rectangle(frame, 
                         (int(lane_center - zone_width), height - 100),
                         (int(lane_center + zone_width), height),
                         (0, 255, 0), -1)
            cv2.rectangle(frame, 
                         (int(lane_center - zone_width), height - 100),
                         (int(lane_center + zone_width), height),
                         (0, 255, 0), 3)
        
        # Draw steering guidance
        if self.assist_active:
            # Draw steering wheel indicator
            wheel_center = (width - 100, 100)
            wheel_radius = 40
            
            # Draw wheel circle
            cv2.circle(frame, wheel_center, wheel_radius, (255, 255, 255), 3)
            cv2.circle(frame, wheel_center, 5, (255, 255, 255), -1)
            
            # Draw steering indicator
            angle_rad = np.radians(self.steering_angle)
            end_x = int(wheel_center[0] + wheel_radius * 0.7 * np.sin(angle_rad))
            end_y = int(wheel_center[1] - wheel_radius * 0.7 * np.cos(angle_rad))
            
            # Color based on direction
            if self.steering_angle < 0:
                color = (0, 255, 255)  # Yellow for left
            else:
                color = (255, 0, 255)  # Magenta for right
            
            cv2.line(frame, wheel_center, (end_x, end_y), color, 4)
            
            # Draw steering text
            if self.steering_angle < 0:
                steer_text = f"Steer Left: {abs(self.steering_angle):.1f}°"
            else:
                steer_text = f"Steer Right: {self.steering_angle:.1f}°"
            
            text_size = cv2.getTextSize(steer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = wheel_center[0] - text_size[0] // 2
            text_y = wheel_center[1] + wheel_radius + 30
            cv2.putText(frame, steer_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw center line between vehicle and lane
        if lane_center is not None and vehicle_offset is not None:
            if abs(vehicle_offset) > self.assist_threshold:
                # Draw correction line
                line_color = (0, 255, 255) if vehicle_offset > 0 else (255, 0, 255)
                cv2.line(frame, 
                        (int(vehicle_center_x), height - 50),
                        (int(lane_center), height - 50),
                        line_color, 3)
                cv2.arrowedLine(frame,
                               (int(vehicle_center_x), height - 50),
                               (int(lane_center), height - 50),
                               line_color, 3, tipLength=0.3)
        
        # Draw status text
        status_text = "LKAS: ACTIVE" if self.assist_active else "LKAS: STANDBY"
        status_color = (0, 255, 0) if self.assist_active else (128, 128, 128)
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        return frame

