"""
Deep Learning Lane Detector Base Class
Provides interface for DL-based lane detection with preprocessing and postprocessing
"""

import cv2
import numpy as np
import time
import logging
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

from .lane_detection_result import LaneDetectionResult

logger = logging.getLogger(__name__)


class DLLaneDetector(ABC):
    """Base class for deep learning lane detectors"""
    
    def __init__(self, model_path: str, model_type: str, device: str, 
                 conf_threshold: float = 0.6, input_size: Tuple[int, int] = (288, 800)):
        """
        Initialize DL Lane Detector
        
        Args:
            model_path: Path to model file
            model_type: Type of model ('onnx', 'pytorch', 'tensorflow')
            device: Inference device ('cuda', 'cpu', 'mps', etc.)
            conf_threshold: Confidence threshold for detections
            input_size: Model input size (height, width)
        """
        self.model_path = model_path
        self.model_type = model_type
        self.device = device
        self.conf_threshold = conf_threshold
        self.input_size = input_size
        self.model = None
        self.is_loaded = False
        
        logger.info(f"Initializing DL Lane Detector: {model_type} on {device}")
    
    @abstractmethod
    def load_model(self) -> bool:
        """
        Load the model
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for model input
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Preprocessed tensor/array ready for model
        """
        # Resize to model input size
        resized = cv2.resize(frame, (self.input_size[1], self.input_size[0]))
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        
        # Transpose to CHW format (channels first)
        transposed = np.transpose(normalized, (2, 0, 1))
        
        # Add batch dimension
        batched = np.expand_dims(transposed, axis=0)
        
        return batched
    
    @abstractmethod
    def detect_lanes(self, frame: np.ndarray) -> LaneDetectionResult:
        """
        Detect lanes in frame
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            LaneDetectionResult with detection information
        """
        pass
    
    @abstractmethod
    def postprocess_output(self, model_output: Any, original_shape: Tuple[int, int]) -> Dict[str, Any]:
        """
        Postprocess model output to standardized format
        
        Args:
            model_output: Raw output from model
            original_shape: Original frame shape (height, width)
            
        Returns:
            Dictionary with processed lane information
        """
        pass
    
    def get_lane_polynomials(self, lane_points: np.ndarray, degree: int = 2) -> Optional[np.ndarray]:
        """
        Fit polynomial to lane points
        
        Args:
            lane_points: Array of lane points (Nx2)
            degree: Polynomial degree
            
        Returns:
            Polynomial coefficients or None if fitting fails
        """
        if lane_points is None or len(lane_points) < degree + 1:
            return None
        
        try:
            # Extract x and y coordinates
            if lane_points.ndim == 2 and lane_points.shape[1] == 2:
                x = lane_points[:, 0]
                y = lane_points[:, 1]
            else:
                return None
            
            # Fit polynomial (y as function of x)
            coeffs = np.polyfit(y, x, degree)
            
            return coeffs
        
        except Exception as e:
            logger.warning(f"Error fitting polynomial: {e}")
            return None
    
    def calculate_lane_curvature(self, poly_coeffs: np.ndarray, y_eval: float) -> float:
        """
        Calculate lane curvature from polynomial coefficients
        
        Args:
            poly_coeffs: Polynomial coefficients
            y_eval: Y position to evaluate curvature
            
        Returns:
            Curvature radius in pixels
        """
        if poly_coeffs is None or len(poly_coeffs) < 3:
            return float('inf')
        
        try:
            # For polynomial x = a*y^2 + b*y + c
            # Curvature = ((1 + (dx/dy)^2)^(3/2)) / |d2x/dy2|
            a, b = poly_coeffs[0], poly_coeffs[1]
            
            dx_dy = 2 * a * y_eval + b
            d2x_dy2 = 2 * a
            
            curvature = ((1 + dx_dy**2)**1.5) / abs(d2x_dy2)
            
            return curvature
        
        except Exception as e:
            logger.warning(f"Error calculating curvature: {e}")
            return float('inf')
    
    def scale_lanes_to_original(self, lanes: Dict[str, Any], 
                                original_shape: Tuple[int, int]) -> Dict[str, Any]:
        """
        Scale lane coordinates from model input size to original frame size
        
        Args:
            lanes: Dictionary with lane information
            original_shape: Original frame shape (height, width)
            
        Returns:
            Scaled lane information
        """
        scale_x = original_shape[1] / self.input_size[1]
        scale_y = original_shape[0] / self.input_size[0]
        
        scaled_lanes = {}
        
        for key, value in lanes.items():
            if value is not None and isinstance(value, np.ndarray):
                if value.ndim == 2 and value.shape[1] == 2:
                    # Scale point coordinates
                    scaled_value = value.copy()
                    scaled_value[:, 0] *= scale_x
                    scaled_value[:, 1] *= scale_y
                    scaled_lanes[key] = scaled_value
                elif value.ndim == 1 and len(value) == 4:
                    # Scale line coordinates [x1, y1, x2, y2]
                    scaled_value = value.copy()
                    scaled_value[0] *= scale_x
                    scaled_value[1] *= scale_y
                    scaled_value[2] *= scale_x
                    scaled_value[3] *= scale_y
                    scaled_lanes[key] = scaled_value
                else:
                    scaled_lanes[key] = value
            else:
                scaled_lanes[key] = value
        
        return scaled_lanes
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_path': self.model_path,
            'model_type': self.model_type,
            'device': self.device,
            'conf_threshold': self.conf_threshold,
            'input_size': self.input_size,
            'is_loaded': self.is_loaded
        }
