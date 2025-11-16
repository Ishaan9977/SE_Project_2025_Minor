"""
Bird's Eye View (BEV) Transformer
Creates top-down perspective view of lane detection
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class BirdEyeViewTransformer:
    """
    Transforms camera view to bird's eye view (top-down perspective)
    """
    
    def __init__(self, src_points: Optional[np.ndarray] = None,
                 dst_points: Optional[np.ndarray] = None,
                 output_size: Tuple[int, int] = (300, 400)):
        """
        Initialize BEV Transformer
        
        Args:
            src_points: Source points in original image (4x2 array)
            dst_points: Destination points in BEV (4x2 array)
            output_size: BEV output size (width, height)
        """
        self.output_size = output_size
        self.src_points = src_points
        self.dst_points = dst_points
        
        # Transformation matrices
        self.M = None  # Forward transform
        self.M_inv = None  # Inverse transform
        
        # Calculate transform if points provided
        if src_points is not None and dst_points is not None:
            self.calculate_transform_matrix()
        
        logger.info(f"BEV Transformer initialized (output size: {output_size})")
    
    def set_default_points(self, frame_width: int, frame_height: int):
        """
        Set default transformation points based on frame size
        
        Args:
            frame_width: Frame width
            frame_height: Frame height
        """
        # Source points (trapezoid in original image)
        # These define the region of interest for lane detection
        self.src_points = np.float32([
            [frame_width * 0.2, frame_height],           # Bottom left
            [frame_width * 0.45, frame_height * 0.6],    # Top left
            [frame_width * 0.55, frame_height * 0.6],    # Top right
            [frame_width * 0.8, frame_height]            # Bottom right
        ])
        
        # Destination points (rectangle in BEV)
        bev_width, bev_height = self.output_size
        self.dst_points = np.float32([
            [bev_width * 0.2, bev_height],               # Bottom left
            [bev_width * 0.2, 0],                        # Top left
            [bev_width * 0.8, 0],                        # Top right
            [bev_width * 0.8, bev_height]                # Bottom right
        ])
        
        self.calculate_transform_matrix()
        logger.info("Default transformation points set")
    
    def calculate_transform_matrix(self) -> np.ndarray:
        """
        Calculate perspective transformation matrix
        
        Returns:
            Transformation matrix
        """
        if self.src_points is None or self.dst_points is None:
            logger.error("Source or destination points not set")
            return None
        
        try:
            # Calculate forward transform
            self.M = cv2.getPerspectiveTransform(self.src_points, self.dst_points)
            
            # Calculate inverse transform
            self.M_inv = cv2.getPerspectiveTransform(self.dst_points, self.src_points)
            
            logger.debug("Transformation matrices calculated")
            return self.M
        
        except Exception as e:
            logger.error(f"Error calculating transformation matrix: {e}")
            return None
    
    def transform_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Transform frame to bird's eye view
        
        Args:
            frame: Input frame
            
        Returns:
            BEV frame or None if transform fails
        """
        if self.M is None:
            # Try to set default points
            height, width = frame.shape[:2]
            self.set_default_points(width, height)
            
            if self.M is None:
                logger.error("Transformation matrix not available")
                return None
        
        try:
            # Apply perspective warp
            bev_frame = cv2.warpPerspective(
                frame,
                self.M,
                self.output_size,
                flags=cv2.INTER_LINEAR
            )
            
            return bev_frame
        
        except Exception as e:
            logger.error(f"Error transforming frame: {e}")
            return None
    
    def transform_lanes(self, left_lane: Optional[np.ndarray],
                       right_lane: Optional[np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Transform lane coordinates to BEV space
        
        Args:
            left_lane: Left lane points or line
            right_lane: Right lane points or line
            
        Returns:
            Tuple of (transformed_left, transformed_right)
        """
        if self.M is None:
            return None, None
        
        left_transformed = self._transform_lane(left_lane)
        right_transformed = self._transform_lane(right_lane)
        
        return left_transformed, right_transformed
    
    def _transform_lane(self, lane: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """Transform single lane to BEV coordinates"""
        if lane is None or self.M is None:
            return None
        
        try:
            # Convert to points if needed
            if lane.ndim == 1 and len(lane) == 4:
                # Line format [x1, y1, x2, y2]
                points = np.array([[lane[0], lane[1]], [lane[2], lane[3]]], dtype=np.float32)
            elif lane.ndim == 2 and lane.shape[1] == 2:
                # Already points
                points = lane.astype(np.float32)
            else:
                return None
            
            # Transform points
            points_reshaped = points.reshape(-1, 1, 2)
            transformed = cv2.perspectiveTransform(points_reshaped, self.M)
            transformed = transformed.reshape(-1, 2)
            
            return transformed
        
        except Exception as e:
            logger.warning(f"Error transforming lane: {e}")
            return None
    
    def draw_bev_overlay(self, bev_frame: np.ndarray,
                        left_lane: Optional[np.ndarray] = None,
                        right_lane: Optional[np.ndarray] = None,
                        vehicle_pos: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Draw overlay on BEV frame (lanes, vehicle indicator, etc.)
        
        Args:
            bev_frame: BEV frame
            left_lane: Left lane in BEV coordinates
            right_lane: Right lane in BEV coordinates
            vehicle_pos: Vehicle position (default: bottom center)
            
        Returns:
            BEV frame with overlay
        """
        height, width = bev_frame.shape[:2]
        
        # Default vehicle position (bottom center)
        if vehicle_pos is None:
            vehicle_pos = (width // 2, height - 20)
        
        # Draw lanes
        if left_lane is not None:
            self._draw_lane_on_bev(bev_frame, left_lane, (0, 255, 0))
        
        if right_lane is not None:
            self._draw_lane_on_bev(bev_frame, right_lane, (0, 255, 0))
        
        # Draw drivable area if both lanes present
        if left_lane is not None and right_lane is not None:
            self._draw_drivable_area(bev_frame, left_lane, right_lane)
        
        # Draw vehicle indicator
        self._draw_vehicle_indicator(bev_frame, vehicle_pos)
        
        # Draw grid
        self._draw_grid(bev_frame)
        
        return bev_frame
    
    def _draw_lane_on_bev(self, bev_frame: np.ndarray, lane: np.ndarray, color: Tuple[int, int, int]):
        """Draw lane on BEV frame"""
        try:
            if lane.ndim == 2 and lane.shape[1] == 2:
                # Points array
                points = lane.astype(np.int32)
                cv2.polylines(bev_frame, [points], False, color, 3)
            elif lane.ndim == 1 and len(lane) == 4:
                # Line format
                x1, y1, x2, y2 = lane.astype(int)
                cv2.line(bev_frame, (x1, y1), (x2, y2), color, 3)
        except Exception as e:
            logger.warning(f"Error drawing lane on BEV: {e}")
    
    def _draw_drivable_area(self, bev_frame: np.ndarray,
                           left_lane: np.ndarray, right_lane: np.ndarray):
        """Draw semi-transparent drivable area between lanes"""
        try:
            # Convert lanes to points
            left_points = left_lane if left_lane.ndim == 2 else np.array([[left_lane[0], left_lane[1]], [left_lane[2], left_lane[3]]])
            right_points = right_lane if right_lane.ndim == 2 else np.array([[right_lane[0], right_lane[1]], [right_lane[2], right_lane[3]]])
            
            # Create polygon
            polygon = np.vstack([left_points, right_points[::-1]]).astype(np.int32)
            
            # Draw filled polygon with transparency
            overlay = bev_frame.copy()
            cv2.fillPoly(overlay, [polygon], (0, 255, 0))
            cv2.addWeighted(overlay, 0.2, bev_frame, 0.8, 0, bev_frame)
        
        except Exception as e:
            logger.warning(f"Error drawing drivable area: {e}")
    
    def _draw_vehicle_indicator(self, bev_frame: np.ndarray, position: Tuple[int, int]):
        """Draw vehicle indicator at fixed position"""
        x, y = position
        
        # Draw vehicle as rectangle
        vehicle_width = 30
        vehicle_height = 50
        
        top_left = (x - vehicle_width // 2, y - vehicle_height)
        bottom_right = (x + vehicle_width // 2, y)
        
        # Draw filled rectangle
        cv2.rectangle(bev_frame, top_left, bottom_right, (255, 0, 0), -1)
        cv2.rectangle(bev_frame, top_left, bottom_right, (255, 255, 255), 2)
        
        # Draw direction indicator (triangle)
        triangle = np.array([
            [x, y - vehicle_height - 10],
            [x - 10, y - vehicle_height],
            [x + 10, y - vehicle_height]
        ], np.int32)
        cv2.fillPoly(bev_frame, [triangle], (255, 0, 0))
    
    def _draw_grid(self, bev_frame: np.ndarray):
        """Draw reference grid on BEV"""
        height, width = bev_frame.shape[:2]
        
        # Draw horizontal lines (distance markers)
        for i in range(1, 5):
            y = int(height * i / 5)
            cv2.line(bev_frame, (0, y), (width, y), (100, 100, 100), 1)
        
        # Draw center line
        cv2.line(bev_frame, (width // 2, 0), (width // 2, height), (150, 150, 150), 1)
    
    def create_pip_overlay(self, main_frame: np.ndarray, bev_frame: np.ndarray,
                          position: str = 'bottom-right', size: Optional[Tuple[int, int]] = None,
                          alpha: float = 0.8) -> np.ndarray:
        """
        Create picture-in-picture overlay of BEV on main frame
        
        Args:
            main_frame: Main frame
            bev_frame: BEV frame
            position: Position ('bottom-right', 'bottom-left', 'top-right', 'top-left')
            size: PIP size (uses BEV size if None)
            alpha: Transparency
            
        Returns:
            Main frame with PIP overlay
        """
        if bev_frame is None:
            return main_frame
        
        main_height, main_width = main_frame.shape[:2]
        
        # Resize BEV if size specified
        if size is not None:
            bev_frame = cv2.resize(bev_frame, size)
        
        bev_height, bev_width = bev_frame.shape[:2]
        
        # Calculate position
        margin = 20
        if position == 'bottom-right':
            x = main_width - bev_width - margin
            y = main_height - bev_height - margin
        elif position == 'bottom-left':
            x = margin
            y = main_height - bev_height - margin
        elif position == 'top-right':
            x = main_width - bev_width - margin
            y = margin
        elif position == 'top-left':
            x = margin
            y = margin
        else:
            x = main_width - bev_width - margin
            y = main_height - bev_height - margin
        
        # Ensure within bounds
        x = max(0, min(x, main_width - bev_width))
        y = max(0, min(y, main_height - bev_height))
        
        # Create border
        border_thickness = 3
        cv2.rectangle(main_frame,
                     (x - border_thickness, y - border_thickness),
                     (x + bev_width + border_thickness, y + bev_height + border_thickness),
                     (255, 255, 255), border_thickness)
        
        # Blend BEV onto main frame
        roi = main_frame[y:y+bev_height, x:x+bev_width]
        blended = cv2.addWeighted(bev_frame, alpha, roi, 1.0 - alpha, 0)
        main_frame[y:y+bev_height, x:x+bev_width] = blended
        
        return main_frame
    
    def get_transform_info(self) -> dict:
        """Get transformation information"""
        return {
            'output_size': self.output_size,
            'has_transform': self.M is not None,
            'src_points': self.src_points.tolist() if self.src_points is not None else None,
            'dst_points': self.dst_points.tolist() if self.dst_points is not None else None
        }


# Alias for backward compatibility
BEVTransformer = BirdEyeViewTransformer
