"""
ONNX Lane Detector Implementation
Supports ONNX format lane detection models
"""

import cv2
import numpy as np
import time
import logging
from typing import Dict, Any, Optional, Tuple

from .dl_lane_detector import DLLaneDetector
from .lane_detection_result import LaneDetectionResult

logger = logging.getLogger(__name__)


class ONNXLaneDetector(DLLaneDetector):
    """ONNX-based lane detector"""
    
    def __init__(self, model_path: str, device: str = 'cpu', 
                 conf_threshold: float = 0.6, input_size: Tuple[int, int] = (288, 800)):
        """
        Initialize ONNX Lane Detector
        
        Args:
            model_path: Path to ONNX model file
            device: Inference device ('cuda', 'cpu')
            conf_threshold: Confidence threshold
            input_size: Model input size (height, width)
        """
        super().__init__(model_path, 'onnx', device, conf_threshold, input_size)
        self.session = None
        self.input_name = None
        self.output_names = None
        
        # Try to load model
        if not self.load_model():
            logger.warning("Failed to load ONNX model during initialization")
    
    def load_model(self) -> bool:
        """Load ONNX model"""
        try:
            import onnxruntime as ort
            
            # Select execution providers
            providers = []
            if self.device == 'cuda':
                if 'CUDAExecutionProvider' in ort.get_available_providers():
                    providers.append('CUDAExecutionProvider')
                else:
                    logger.warning("CUDA requested but not available, using CPU")
            
            providers.append('CPUExecutionProvider')
            
            # Create inference session
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            
            # Get input/output info
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]
            
            input_shape = self.session.get_inputs()[0].shape
            
            self.is_loaded = True
            
            logger.info(f"ONNX model loaded successfully")
            logger.info(f"Input: {self.input_name}, Shape: {input_shape}")
            logger.info(f"Outputs: {self.output_names}")
            logger.info(f"Providers: {self.session.get_providers()}")
            
            return True
        
        except ImportError:
            logger.error("onnxruntime not installed. Install with: pip install onnxruntime")
            return False
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")
            return False
    
    def detect_lanes(self, frame: np.ndarray) -> LaneDetectionResult:
        """
        Detect lanes using ONNX model
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            LaneDetectionResult
        """
        if not self.is_loaded:
            return LaneDetectionResult(
                left_lane=None,
                right_lane=None,
                confidence=0.0,
                success=False,
                model_used='dl'
            )
        
        start_time = time.time()
        
        try:
            # Preprocess frame
            input_tensor = self.preprocess_frame(frame)
            
            # Run inference
            outputs = self.session.run(self.output_names, {self.input_name: input_tensor})
            
            # Postprocess output
            original_shape = (frame.shape[0], frame.shape[1])
            processed = self.postprocess_output(outputs, original_shape)
            
            processing_time = time.time() - start_time
            
            # Create result
            result = LaneDetectionResult(
                left_lane=processed.get('left_lane'),
                right_lane=processed.get('right_lane'),
                confidence=processed.get('confidence', 0.0),
                lane_type=processed.get('lane_type', 'unknown'),
                success=processed.get('success', False),
                processing_time=processing_time,
                model_used='dl'
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error during lane detection: {e}")
            return LaneDetectionResult(
                left_lane=None,
                right_lane=None,
                confidence=0.0,
                success=False,
                processing_time=time.time() - start_time,
                model_used='dl'
            )
    
    def postprocess_output(self, model_output: Any, original_shape: Tuple[int, int]) -> Dict[str, Any]:
        """
        Postprocess ONNX model output
        
        This is a generic implementation that handles common lane detection output formats.
        Override this method for specific model architectures.
        
        Args:
            model_output: Raw output from ONNX model
            original_shape: Original frame shape (height, width)
            
        Returns:
            Dictionary with processed lane information
        """
        try:
            # Handle different output formats
            if isinstance(model_output, (list, tuple)):
                # Multiple outputs - assume first is lane predictions
                output = model_output[0]
            else:
                output = model_output
            
            # Convert to numpy if needed
            if not isinstance(output, np.ndarray):
                output = np.array(output)
            
            # Generic postprocessing for lane detection
            # This assumes output shape is (batch, num_lanes, num_points, 2) or similar
            
            result = {
                'left_lane': None,
                'right_lane': None,
                'confidence': 0.0,
                'lane_type': 'unknown',
                'success': False
            }
            
            # Try to extract lane information
            if output.ndim >= 2:
                # Squeeze batch dimension if present
                if output.shape[0] == 1:
                    output = output[0]
                
                # Attempt to parse lanes
                # This is a simplified version - real implementation depends on model architecture
                if output.ndim == 3:  # (num_lanes, num_points, 2)
                    if output.shape[0] >= 2:
                        left_lane_points = output[0]
                        right_lane_points = output[1]
                        
                        # Filter valid points (non-zero or within bounds)
                        left_valid = left_lane_points[np.any(left_lane_points != 0, axis=1)]
                        right_valid = right_lane_points[np.any(right_lane_points != 0, axis=1)]
                        
                        if len(left_valid) > 0:
                            # Scale to original size
                            scaled_left = self.scale_lanes_to_original(
                                {'left': left_valid}, original_shape
                            )
                            result['left_lane'] = scaled_left.get('left')
                        
                        if len(right_valid) > 0:
                            scaled_right = self.scale_lanes_to_original(
                                {'right': right_valid}, original_shape
                            )
                            result['right_lane'] = scaled_right.get('right')
                        
                        # Calculate confidence (simplified)
                        if result['left_lane'] is not None or result['right_lane'] is not None:
                            result['confidence'] = 0.8  # Placeholder
                            result['success'] = True
            
            return result
        
        except Exception as e:
            logger.error(f"Error in postprocessing: {e}")
            return {
                'left_lane': None,
                'right_lane': None,
                'confidence': 0.0,
                'lane_type': 'unknown',
                'success': False
            }
    
    def convert_points_to_line(self, points: np.ndarray, frame_height: int) -> Optional[np.ndarray]:
        """
        Convert lane points to line format [x1, y1, x2, y2]
        
        Args:
            points: Lane points (Nx2)
            frame_height: Frame height
            
        Returns:
            Line coordinates or None
        """
        if points is None or len(points) < 2:
            return None
        
        try:
            # Fit polynomial
            poly_coeffs = self.get_lane_polynomials(points, degree=2)
            
            if poly_coeffs is None:
                # Fallback to linear fit
                poly_coeffs = self.get_lane_polynomials(points, degree=1)
            
            if poly_coeffs is not None:
                # Evaluate at top and bottom of frame
                y1 = frame_height
                y2 = int(frame_height * 0.6)
                
                x1 = int(np.polyval(poly_coeffs, y1))
                x2 = int(np.polyval(poly_coeffs, y2))
                
                return np.array([x1, y1, x2, y2])
        
        except Exception as e:
            logger.warning(f"Error converting points to line: {e}")
        
        return None
