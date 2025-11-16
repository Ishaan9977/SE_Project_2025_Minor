"""
Lane Detection Module for ADAS
Detects lane markings using computer vision techniques
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional


class LaneDetector:
    """Lane detection using traditional CV methods (can be replaced with deep learning)"""
    
    def __init__(self):
        """Initialize lane detector"""
        pass
    
    def detect_lanes(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], np.ndarray]:
        """
        Detect left and right lane lines
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            Tuple of (left_lane_points, right_lane_points, processed_frame)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Create region of interest (lower half of image)
        height, width = edges.shape
        mask = np.zeros_like(edges)
        roi_vertices = np.array([[
            (width * 0.1, height),
            (width * 0.45, height * 0.6),
            (width * 0.55, height * 0.6),
            (width * 0.9, height)
        ]], dtype=np.int32)
        cv2.fillPoly(mask, roi_vertices, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # Apply Hough Transform to detect lines
        lines = cv2.HoughLinesP(masked_edges, rho=1, theta=np.pi/180, 
                                threshold=50, minLineLength=50, maxLineGap=100)
        
        left_lane, right_lane = self._separate_lanes(lines, width, height)
        
        # Draw lanes on frame
        processed_frame = frame.copy()
        if left_lane is not None:
            cv2.line(processed_frame, (left_lane[0], left_lane[1]), 
                    (left_lane[2], left_lane[3]), (0, 255, 0), 3)
        if right_lane is not None:
            cv2.line(processed_frame, (right_lane[0], right_lane[1]), 
                    (right_lane[2], right_lane[3]), (0, 255, 0), 3)
        
        return left_lane, right_lane, processed_frame
    
    def _separate_lanes(self, lines: Optional[np.ndarray], width: int, height: int) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Separate detected lines into left and right lanes
        
        Args:
            lines: Detected lines from Hough Transform
            width: Frame width
            height: Frame height
            
        Returns:
            Tuple of (left_lane, right_lane)
        """
        if lines is None:
            return None, None
        
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate slope
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            
            # Filter by slope (lanes should have significant slope)
            if abs(slope) < 0.3:
                continue
            
            # Separate left and right lanes
            if slope < 0:  # Left lane (negative slope)
                left_lines.append(line[0])
            else:  # Right lane (positive slope)
                right_lines.append(line[0])
        
        # Average left lane
        left_lane = None
        if left_lines:
            left_lane = self._average_lines(left_lines, height)
        
        # Average right lane
        right_lane = None
        if right_lines:
            right_lane = self._average_lines(right_lines, height)
        
        return left_lane, right_lane
    
    def _average_lines(self, lines: List, height: int) -> np.ndarray:
        """
        Average multiple lines into a single line
        
        Args:
            lines: List of line coordinates
            height: Frame height
            
        Returns:
            Averaged line coordinates
        """
        if not lines:
            return None
        
        # Calculate average slope and intercept
        slopes = []
        intercepts = []
        
        for x1, y1, x2, y2 in lines:
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            slopes.append(slope)
            intercepts.append(intercept)
        
        if not slopes:
            return None
        
        avg_slope = np.mean(slopes)
        avg_intercept = np.mean(intercepts)
        
        # Calculate line endpoints
        y1 = height
        y2 = int(height * 0.6)
        x1 = int((y1 - avg_intercept) / avg_slope)
        x2 = int((y2 - avg_intercept) / avg_slope)
        
        return np.array([x1, y1, x2, y2])
    
    def calculate_lane_center(self, left_lane: Optional[np.ndarray], 
                             right_lane: Optional[np.ndarray], 
                             width: int, height: int) -> Tuple[Optional[float], Optional[np.ndarray]]:
        """
        Calculate the center of the lane and vehicle position
        
        Args:
            left_lane: Left lane line coordinates
            right_lane: Right lane line coordinates
            width: Frame width
            height: Frame height
            
        Returns:
            Tuple of (lane_center_x, vehicle_position_offset)
        """
        if left_lane is None or right_lane is None:
            return None, None
        
        # Calculate lane center at bottom of frame
        left_x = left_lane[0]
        right_x = right_lane[0]
        lane_center_x = (left_x + right_x) / 2
        
        # Vehicle center (assuming camera is centered)
        vehicle_center_x = width / 2
        
        # Calculate offset
        offset = vehicle_center_x - lane_center_x
        
        return lane_center_x, offset

