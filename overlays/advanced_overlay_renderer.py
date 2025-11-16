"""
Advanced Overlay Renderer
Professional-grade visual overlays with animations and effects
"""

import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional

from utils.config_loader import OverlayConfig
from .animation_engine import AnimationEngine

logger = logging.getLogger(__name__)


class AdvancedOverlayRenderer:
    """
    Advanced overlay renderer with animations and professional effects
    """
    
    def __init__(self, config: OverlayConfig, animation_engine: Optional[AnimationEngine] = None):
        """
        Initialize Advanced Overlay Renderer
        
        Args:
            config: Overlay configuration
            animation_engine: Animation engine instance (creates new if None)
        """
        self.config = config
        self.animation_engine = animation_engine or AnimationEngine()
        
        # Performance tracking
        self.frame_time = 0.0
        self.performance_mode = False
        
        # Previous frame for transitions
        self.previous_frame = None
        
        logger.info("Advanced Overlay Renderer initialized")
    
    def alpha_blend(self, foreground: np.ndarray, background: np.ndarray, 
                   alpha: float) -> np.ndarray:
        """
        Alpha blend two images
        
        Args:
            foreground: Foreground image
            background: Background image
            alpha: Alpha value (0.0 to 1.0)
            
        Returns:
            Blended image
        """
        alpha = np.clip(alpha, 0.0, 1.0)
        return cv2.addWeighted(foreground, alpha, background, 1.0 - alpha, 0)
    
    def create_gradient_mask(self, height: int, width: int, 
                            start_alpha: float = 1.0, end_alpha: float = 0.3) -> np.ndarray:
        """
        Create vertical gradient mask (opaque at bottom, transparent at top)
        
        Args:
            height: Mask height
            width: Mask width
            start_alpha: Alpha at bottom
            end_alpha: Alpha at top
            
        Returns:
            Gradient mask (height x width)
        """
        gradient = np.linspace(end_alpha, start_alpha, height)
        mask = np.tile(gradient[:, np.newaxis], (1, width))
        return mask
    
    def draw_lane_polygon(self, frame: np.ndarray, left_lane: Optional[np.ndarray], 
                         right_lane: Optional[np.ndarray]) -> np.ndarray:
        """
        Draw semi-transparent polygon between lane lines
        
        Args:
            frame: Input frame
            left_lane: Left lane line [x1, y1, x2, y2] or points
            right_lane: Right lane line [x1, y1, x2, y2] or points
            
        Returns:
            Frame with lane polygon drawn
        """
        if not self.config.show_lane_polygon:
            return frame
        
        if left_lane is None or right_lane is None:
            return frame
        
        height, width = frame.shape[:2]
        
        try:
            # Convert lanes to points if needed
            left_points = self._lane_to_points(left_lane, height)
            right_points = self._lane_to_points(right_lane, height)
            
            if left_points is None or right_points is None:
                return frame
            
            # Create polygon points (left bottom to top, right top to bottom)
            polygon_points = np.vstack([left_points, right_points[::-1]])
            polygon_points = polygon_points.astype(np.int32)
            
            # Create overlay
            overlay = frame.copy()
            
            # Draw filled polygon
            cv2.fillPoly(overlay, [polygon_points], self.config.lane_polygon_color)
            
            # Apply gradient if enabled
            if self.config.gradient_enabled:
                # Create gradient mask
                mask = self.create_gradient_mask(height, width, 
                                                start_alpha=self.config.lane_polygon_alpha,
                                                end_alpha=self.config.lane_polygon_alpha * 0.3)
                
                # Apply mask to overlay
                for c in range(3):
                    overlay[:, :, c] = overlay[:, :, c] * mask + frame[:, :, c] * (1 - mask)
                
                frame = overlay.astype(np.uint8)
            else:
                # Simple alpha blend
                frame = self.alpha_blend(overlay, frame, self.config.lane_polygon_alpha)
            
        except Exception as e:
            logger.warning(f"Error drawing lane polygon: {e}")
        
        return frame
    
    def _lane_to_points(self, lane: np.ndarray, frame_height: int, 
                       num_points: int = 50) -> Optional[np.ndarray]:
        """
        Convert lane representation to array of points
        
        Args:
            lane: Lane in various formats
            frame_height: Frame height
            num_points: Number of points to generate
            
        Returns:
            Array of points (Nx2) or None
        """
        if lane is None:
            return None
        
        try:
            # Check format
            if lane.ndim == 1:
                if len(lane) == 4:
                    # Line format [x1, y1, x2, y2]
                    x1, y1, x2, y2 = lane
                    y_values = np.linspace(y1, y2, num_points)
                    x_values = np.linspace(x1, x2, num_points)
                    return np.column_stack((x_values, y_values))
                
                elif len(lane) <= 3:
                    # Polynomial coefficients
                    y_values = np.linspace(frame_height, frame_height * 0.6, num_points)
                    x_values = np.polyval(lane, y_values)
                    return np.column_stack((x_values, y_values))
            
            elif lane.ndim == 2 and lane.shape[1] == 2:
                # Already points
                return lane
        
        except Exception as e:
            logger.warning(f"Error converting lane to points: {e}")
        
        return None
    
    def draw_distance_markers(self, frame: np.ndarray, detections: List[Dict],
                             distance_estimations: List[Any]) -> np.ndarray:
        """
        Draw distance markers on detected objects
        
        Args:
            frame: Input frame
            detections: List of detections
            distance_estimations: List of distance estimations
            
        Returns:
            Frame with distance markers
        """
        if not self.config.show_distance_markers:
            return frame
        
        height, width = frame.shape[:2]
        
        # Draw distance intervals (horizontal lines)
        if self.config.distance_intervals:
            for i, interval in enumerate(self.config.distance_intervals):
                # Calculate y position (perspective scaling)
                y = int(height - (interval / max(self.config.distance_intervals)) * height * 0.7)
                
                # Draw line
                color = (100, 100, 100)
                cv2.line(frame, (int(width * 0.2), y), (int(width * 0.8), y), color, 1)
                
                # Draw label
                label = f"{interval}m"
                cv2.putText(frame, label, (int(width * 0.82), y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame
    
    def draw_warning_overlay(self, frame: np.ndarray, warning_type: str,
                            message: str, severity: str) -> np.ndarray:
        """
        Draw warning overlay with animation
        
        Args:
            frame: Input frame
            warning_type: Type of warning
            message: Warning message
            severity: Severity level ('info', 'warning', 'critical')
            
        Returns:
            Frame with warning overlay
        """
        if not self.config.show_animations:
            return self._draw_static_warning(frame, message, severity)
        
        height, width = frame.shape[:2]
        
        # Get or create animation
        anim_name = f"warning_{warning_type}"
        if not self.animation_engine.is_animation_active(anim_name):
            self.animation_engine.register_animation(
                anim_name, 
                self.config.warning_fade_duration,
                easing="ease_in_out"
            )
            self.animation_engine.start_animation(anim_name)
        
        # Get animation value
        fade_value = self.animation_engine.get_animation_value(anim_name)
        
        # Draw warning with fade
        return self._draw_static_warning(frame, message, severity, alpha=fade_value)
    
    def _draw_static_warning(self, frame: np.ndarray, message: str, 
                            severity: str, alpha: float = 1.0) -> np.ndarray:
        """Draw static warning without animation"""
        height, width = frame.shape[:2]
        
        # Color based on severity
        if severity == 'critical':
            color = (0, 0, 255)  # Red
        elif severity == 'warning':
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 255, 255)  # Yellow
        
        # Draw banner
        banner_height = 60
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, banner_height), color, -1)
        
        # Apply alpha
        frame = self.alpha_blend(overlay, frame, alpha * 0.3)
        
        # Draw text
        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = banner_height // 2 + text_size[1] // 2
        
        cv2.putText(frame, message, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        return frame
    
    def draw_directional_arrow(self, frame: np.ndarray, direction: str,
                              position: Tuple[int, int]) -> np.ndarray:
        """
        Draw animated directional arrow
        
        Args:
            frame: Input frame
            direction: Direction ('left' or 'right')
            position: Arrow position (x, y)
            
        Returns:
            Frame with arrow drawn
        """
        if not self.config.show_animations:
            return self._draw_static_arrow(frame, direction, position)
        
        # Get or create animation
        anim_name = f"arrow_{direction}"
        if not self.animation_engine.is_animation_active(anim_name):
            self.animation_engine.register_animation(
                anim_name,
                1.0,  # 1 second cycle
                easing="ease_in_out",
                loop=True
            )
            self.animation_engine.start_animation(anim_name)
        
        # Get animation value for pulsing
        pulse_value = self.animation_engine.get_animation_value(anim_name)
        
        # Draw arrow with animation
        return self._draw_static_arrow(frame, direction, position, pulse_value)
    
    def _draw_static_arrow(self, frame: np.ndarray, direction: str,
                          position: Tuple[int, int], pulse: float = 0.5) -> np.ndarray:
        """Draw static arrow"""
        x, y = position
        
        # Arrow size based on pulse
        base_size = 50
        size = int(base_size * (0.8 + 0.4 * pulse))
        
        # Color based on direction
        color = (0, 165, 255)  # Orange
        
        # Create arrow points
        if direction == 'left':
            points = np.array([
                [x, y],
                [x + size, y - size // 2],
                [x + size, y - size // 4],
                [x + size * 2, y - size // 4],
                [x + size * 2, y + size // 4],
                [x + size, y + size // 4],
                [x + size, y + size // 2]
            ], np.int32)
        else:  # right
            points = np.array([
                [x, y],
                [x - size, y - size // 2],
                [x - size, y - size // 4],
                [x - size * 2, y - size // 4],
                [x - size * 2, y + size // 4],
                [x - size, y + size // 4],
                [x - size, y + size // 2]
            ], np.int32)
        
        # Draw arrow
        cv2.fillPoly(frame, [points], color)
        cv2.polylines(frame, [points], True, (255, 255, 255), 2)
        
        return frame
    
    def apply_fade_transition(self, current_frame: np.ndarray,
                             previous_frame: Optional[np.ndarray],
                             alpha: float) -> np.ndarray:
        """
        Apply fade transition between frames
        
        Args:
            current_frame: Current frame
            previous_frame: Previous frame
            alpha: Fade alpha (0.0 = previous, 1.0 = current)
            
        Returns:
            Blended frame
        """
        if previous_frame is None or previous_frame.shape != current_frame.shape:
            return current_frame
        
        return self.alpha_blend(current_frame, previous_frame, alpha)
    
    def update_config(self, config: OverlayConfig):
        """Update overlay configuration"""
        self.config = config
        logger.info("Overlay configuration updated")
    
    def set_performance_mode(self, enabled: bool):
        """Enable/disable performance mode (reduces effects)"""
        self.performance_mode = enabled
        logger.info(f"Performance mode: {'enabled' if enabled else 'disabled'}")
