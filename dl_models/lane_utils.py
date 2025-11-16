"""
Utility functions for lane processing
Includes polynomial fitting, curvature calculation, and lane analysis
"""

import numpy as np
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


def fit_lane_polynomial(lane_points: np.ndarray, degree: int = 2) -> Optional[np.ndarray]:
    """
    Fit polynomial to lane points
    
    Args:
        lane_points: Array of lane points (Nx2) where each row is [x, y]
        degree: Polynomial degree (default: 2 for quadratic)
        
    Returns:
        Polynomial coefficients [a, b, c, ...] or None if fitting fails
    """
    if lane_points is None or len(lane_points) < degree + 1:
        return None
    
    try:
        # Extract x and y coordinates
        if lane_points.ndim == 2 and lane_points.shape[1] == 2:
            x = lane_points[:, 0]
            y = lane_points[:, 1]
        else:
            logger.warning(f"Invalid lane points shape: {lane_points.shape}")
            return None
        
        # Remove invalid points (NaN, inf)
        valid_mask = np.isfinite(x) & np.isfinite(y)
        x = x[valid_mask]
        y = y[valid_mask]
        
        if len(x) < degree + 1:
            return None
        
        # Fit polynomial (x as function of y)
        # This is more stable for near-vertical lanes
        coeffs = np.polyfit(y, x, degree)
        
        return coeffs
    
    except Exception as e:
        logger.warning(f"Error fitting polynomial: {e}")
        return None


def calculate_curvature(poly_coeffs: np.ndarray, y_eval: float) -> float:
    """
    Calculate lane curvature from polynomial coefficients
    
    Args:
        poly_coeffs: Polynomial coefficients [a, b, c, ...] for x = f(y)
        y_eval: Y position to evaluate curvature
        
    Returns:
        Curvature radius in pixels (larger = straighter)
    """
    if poly_coeffs is None or len(poly_coeffs) < 3:
        return float('inf')
    
    try:
        # For polynomial x = a*y^2 + b*y + c
        # First derivative: dx/dy = 2*a*y + b
        # Second derivative: d2x/dy2 = 2*a
        # Curvature: ((1 + (dx/dy)^2)^(3/2)) / |d2x/dy2|
        
        a = poly_coeffs[0]
        b = poly_coeffs[1]
        
        dx_dy = 2 * a * y_eval + b
        d2x_dy2 = 2 * a
        
        if abs(d2x_dy2) < 1e-6:
            return float('inf')
        
        curvature = ((1 + dx_dy**2)**1.5) / abs(d2x_dy2)
        
        return curvature
    
    except Exception as e:
        logger.warning(f"Error calculating curvature: {e}")
        return float('inf')


def calculate_curvature_meters(poly_coeffs: np.ndarray, y_eval: float,
                               ym_per_pix: float = 30/720, 
                               xm_per_pix: float = 3.7/700) -> float:
    """
    Calculate lane curvature in meters
    
    Args:
        poly_coeffs: Polynomial coefficients in pixel space
        y_eval: Y position to evaluate curvature (pixels)
        ym_per_pix: Meters per pixel in y dimension
        xm_per_pix: Meters per pixel in x dimension
        
    Returns:
        Curvature radius in meters
    """
    if poly_coeffs is None or len(poly_coeffs) < 3:
        return float('inf')
    
    try:
        # Convert polynomial to world space
        # If x = a*y^2 + b*y + c in pixel space
        # Then x_m = a_m*y_m^2 + b_m*y_m + c_m in world space
        # where a_m = a * xm_per_pix / (ym_per_pix^2)
        #       b_m = b * xm_per_pix / ym_per_pix
        #       c_m = c * xm_per_pix
        
        a = poly_coeffs[0] * xm_per_pix / (ym_per_pix**2)
        b = poly_coeffs[1] * xm_per_pix / ym_per_pix
        
        y_eval_m = y_eval * ym_per_pix
        
        dx_dy = 2 * a * y_eval_m + b
        d2x_dy2 = 2 * a
        
        if abs(d2x_dy2) < 1e-6:
            return float('inf')
        
        curvature = ((1 + dx_dy**2)**1.5) / abs(d2x_dy2)
        
        return curvature
    
    except Exception as e:
        logger.warning(f"Error calculating curvature in meters: {e}")
        return float('inf')


def evaluate_polynomial(poly_coeffs: np.ndarray, y_values: np.ndarray) -> Optional[np.ndarray]:
    """
    Evaluate polynomial at given y values
    
    Args:
        poly_coeffs: Polynomial coefficients
        y_values: Y values to evaluate at
        
    Returns:
        Corresponding x values or None
    """
    if poly_coeffs is None:
        return None
    
    try:
        x_values = np.polyval(poly_coeffs, y_values)
        return x_values
    except Exception as e:
        logger.warning(f"Error evaluating polynomial: {e}")
        return None


def generate_lane_points(poly_coeffs: np.ndarray, y_start: int, y_end: int, 
                        num_points: int = 50) -> Optional[np.ndarray]:
    """
    Generate lane points from polynomial coefficients
    
    Args:
        poly_coeffs: Polynomial coefficients
        y_start: Starting y coordinate
        y_end: Ending y coordinate
        num_points: Number of points to generate
        
    Returns:
        Array of points (Nx2) or None
    """
    if poly_coeffs is None:
        return None
    
    try:
        y_values = np.linspace(y_start, y_end, num_points)
        x_values = np.polyval(poly_coeffs, y_values)
        
        points = np.column_stack((x_values, y_values))
        
        return points
    except Exception as e:
        logger.warning(f"Error generating lane points: {e}")
        return None


def calculate_lane_width(left_poly: np.ndarray, right_poly: np.ndarray, 
                        y_eval: float) -> Optional[float]:
    """
    Calculate lane width at given y position
    
    Args:
        left_poly: Left lane polynomial coefficients
        right_poly: Right lane polynomial coefficients
        y_eval: Y position to evaluate
        
    Returns:
        Lane width in pixels or None
    """
    if left_poly is None or right_poly is None:
        return None
    
    try:
        left_x = np.polyval(left_poly, y_eval)
        right_x = np.polyval(right_poly, y_eval)
        
        width = abs(right_x - left_x)
        
        return width
    except Exception as e:
        logger.warning(f"Error calculating lane width: {e}")
        return None


def smooth_lane_polynomial(poly_history: List[np.ndarray], 
                          window_size: int = 5) -> Optional[np.ndarray]:
    """
    Smooth lane polynomial using moving average
    
    Args:
        poly_history: List of polynomial coefficients from recent frames
        window_size: Number of frames to average
        
    Returns:
        Smoothed polynomial coefficients or None
    """
    if not poly_history or len(poly_history) == 0:
        return None
    
    try:
        # Take last window_size polynomials
        recent = poly_history[-window_size:]
        
        # Filter out None values
        valid = [p for p in recent if p is not None]
        
        if len(valid) == 0:
            return None
        
        # Average coefficients
        smoothed = np.mean(valid, axis=0)
        
        return smoothed
    except Exception as e:
        logger.warning(f"Error smoothing polynomial: {e}")
        return None


def validate_lane_polynomial(poly_coeffs: np.ndarray, frame_width: int, 
                            frame_height: int) -> bool:
    """
    Validate that polynomial represents a reasonable lane
    
    Args:
        poly_coeffs: Polynomial coefficients
        frame_width: Frame width
        frame_height: Frame height
        
    Returns:
        True if valid, False otherwise
    """
    if poly_coeffs is None:
        return False
    
    try:
        # Check if polynomial produces reasonable x values
        y_bottom = frame_height
        y_top = frame_height * 0.6
        
        x_bottom = np.polyval(poly_coeffs, y_bottom)
        x_top = np.polyval(poly_coeffs, y_top)
        
        # Check if x values are within frame bounds (with margin)
        margin = frame_width * 0.2
        if x_bottom < -margin or x_bottom > frame_width + margin:
            return False
        if x_top < -margin or x_top > frame_width + margin:
            return False
        
        # Check if curvature is reasonable (not too sharp)
        curvature = calculate_curvature(poly_coeffs, frame_height * 0.8)
        min_curvature = 50  # pixels
        
        if curvature < min_curvature:
            return False
        
        return True
    
    except Exception as e:
        logger.warning(f"Error validating polynomial: {e}")
        return False


def convert_line_to_polynomial(line: np.ndarray) -> Optional[np.ndarray]:
    """
    Convert line format [x1, y1, x2, y2] to polynomial coefficients
    
    Args:
        line: Line in format [x1, y1, x2, y2]
        
    Returns:
        Polynomial coefficients (linear) or None
    """
    if line is None or len(line) != 4:
        return None
    
    try:
        x1, y1, x2, y2 = line
        
        # Fit linear polynomial
        y_points = np.array([y1, y2])
        x_points = np.array([x1, x2])
        
        coeffs = np.polyfit(y_points, x_points, 1)
        
        return coeffs
    except Exception as e:
        logger.warning(f"Error converting line to polynomial: {e}")
        return None
