"""
Enhanced Distance Estimator
Provides accurate distance estimation with camera calibration support
"""

import json
import os
import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DistanceEstimation:
    """Result from distance estimation"""
    distance_meters: Optional[float]
    distance_pixels: float
    confidence: float
    has_calibration: bool
    confidence_interval: Tuple[float, float]  # (min, max)
    method: str = 'uncalibrated'  # 'calibrated' or 'uncalibrated'


class DistanceEstimator:
    """
    Enhanced distance estimator with camera calibration support
    """
    
    # Default object heights in meters
    DEFAULT_OBJECT_HEIGHTS = {
        'car': 1.5,
        'truck': 3.0,
        'bus': 3.2,
        'motorcycle': 1.2,
        'bicycle': 1.7,
        'person': 1.7
    }
    
    def __init__(self, calibration_file: Optional[str] = None):
        """
        Initialize Distance Estimator
        
        Args:
            calibration_file: Path to camera calibration JSON file
        """
        self.calibration_file = calibration_file
        self.has_calibration = False
        
        # Calibration parameters
        self.camera_matrix = None
        self.dist_coeffs = None
        self.image_size = None
        self.object_heights = self.DEFAULT_OBJECT_HEIGHTS.copy()
        
        # Focal length (will be extracted from camera matrix)
        self.focal_length = None
        
        # Load calibration if provided
        if calibration_file:
            self.load_calibration(calibration_file)
        
        logger.info(f"Distance Estimator initialized (calibrated: {self.has_calibration})")
    
    def load_calibration(self, calibration_file: str) -> bool:
        """
        Load camera calibration from JSON file
        
        Args:
            calibration_file: Path to calibration file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(calibration_file):
            logger.warning(f"Calibration file not found: {calibration_file}")
            return False
        
        try:
            with open(calibration_file, 'r') as f:
                calib_data = json.load(f)
            
            # Load camera matrix
            if 'camera_matrix' in calib_data:
                self.camera_matrix = np.array(calib_data['camera_matrix'])
                # Extract focal length (average of fx and fy)
                fx = self.camera_matrix[0, 0]
                fy = self.camera_matrix[1, 1]
                self.focal_length = (fx + fy) / 2.0
            
            # Load distortion coefficients
            if 'dist_coeffs' in calib_data:
                self.dist_coeffs = np.array(calib_data['dist_coeffs'])
            
            # Load image size
            if 'image_size' in calib_data:
                self.image_size = tuple(calib_data['image_size'])
            
            # Load object heights
            if 'object_heights' in calib_data:
                self.object_heights.update(calib_data['object_heights'])
            
            self.has_calibration = True
            self.calibration_file = calibration_file
            
            logger.info(f"Calibration loaded from {calibration_file}")
            logger.info(f"Focal length: {self.focal_length:.2f}")
            logger.info(f"Image size: {self.image_size}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")
            return False
    
    def estimate_distance(self, bbox: List[int], frame_height: int, 
                         object_class: str, detection_conf: float = 1.0) -> DistanceEstimation:
        """
        Estimate distance to detected object
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            frame_height: Frame height in pixels
            object_class: Object class name
            detection_conf: Detection confidence score
            
        Returns:
            DistanceEstimation result
        """
        x1, y1, x2, y2 = bbox
        bbox_height = y2 - y1
        bbox_width = x2 - x1
        
        # Calculate pixel-based distance
        distance_pixels = self._calculate_pixel_distance(bbox, frame_height)
        
        # Try calibrated estimation first
        if self.has_calibration and self.focal_length is not None:
            distance_meters = self.pixel_to_meters(bbox_height, object_class)
            
            if distance_meters is not None:
                confidence = self.calculate_confidence(bbox, detection_conf, calibrated=True)
                confidence_interval = self._calculate_confidence_interval(
                    distance_meters, confidence, calibrated=True
                )
                
                return DistanceEstimation(
                    distance_meters=distance_meters,
                    distance_pixels=distance_pixels,
                    confidence=confidence,
                    has_calibration=True,
                    confidence_interval=confidence_interval,
                    method='calibrated'
                )
        
        # Fallback to uncalibrated estimation
        distance_normalized = self._normalize_distance(distance_pixels, frame_height)
        confidence = self.calculate_confidence(bbox, detection_conf, calibrated=False)
        confidence_interval = self._calculate_confidence_interval(
            distance_normalized, confidence, calibrated=False
        )
        
        return DistanceEstimation(
            distance_meters=None,
            distance_pixels=distance_pixels,
            confidence=confidence,
            has_calibration=False,
            confidence_interval=confidence_interval,
            method='uncalibrated'
        )
    
    def pixel_to_meters(self, bbox_height: int, object_class: str) -> Optional[float]:
        """
        Convert pixel height to distance in meters using pinhole camera model
        
        Args:
            bbox_height: Bounding box height in pixels
            object_class: Object class name
            
        Returns:
            Distance in meters or None if conversion fails
        """
        if not self.has_calibration or self.focal_length is None:
            return None
        
        # Get real-world object height
        real_height = self.object_heights.get(object_class)
        if real_height is None:
            logger.debug(f"Unknown object class: {object_class}, using default")
            real_height = 1.5  # Default height
        
        if bbox_height <= 0:
            return None
        
        try:
            # Pinhole camera model: distance = (focal_length * real_height) / pixel_height
            distance = (self.focal_length * real_height) / bbox_height
            
            # Sanity check (0.5m to 200m)
            if 0.5 <= distance <= 200.0:
                return distance
            else:
                logger.debug(f"Distance out of range: {distance:.2f}m")
                return None
        
        except Exception as e:
            logger.warning(f"Error converting pixels to meters: {e}")
            return None
    
    def _calculate_pixel_distance(self, bbox: List[int], frame_height: int) -> float:
        """
        Calculate distance based on bounding box size and position (pixel-based)
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            frame_height: Frame height
            
        Returns:
            Distance in pixels (larger = farther)
        """
        x1, y1, x2, y2 = bbox
        bbox_height = y2 - y1
        bbox_width = x2 - x1
        bbox_area = bbox_width * bbox_height
        
        # Bottom center of bounding box (closest point)
        bottom_y = y2
        
        # Normalize by frame size
        normalized_area = bbox_area / (frame_height * frame_height)
        normalized_y = bottom_y / frame_height
        
        # Distance estimation: larger area and lower position = closer
        # Inverse relationship
        distance = frame_height * (1.0 - normalized_area * 2) * (1.0 - normalized_y * 0.5)
        
        # Ensure minimum distance
        distance = max(distance, 10.0)
        
        return distance
    
    def _normalize_distance(self, distance_pixels: float, frame_height: int) -> float:
        """
        Normalize pixel distance to a 0-100 scale
        
        Args:
            distance_pixels: Distance in pixels
            frame_height: Frame height
            
        Returns:
            Normalized distance (0-100)
        """
        # Map pixel distance to 0-100 scale
        max_distance = frame_height * 2
        normalized = (distance_pixels / max_distance) * 100
        
        return min(normalized, 100.0)
    
    def calculate_confidence(self, bbox: List[int], detection_conf: float, 
                           calibrated: bool = False) -> float:
        """
        Calculate confidence score for distance estimation
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            detection_conf: Detection confidence
            calibrated: Whether using calibrated estimation
            
        Returns:
            Confidence score (0-1)
        """
        x1, y1, x2, y2 = bbox
        bbox_height = y2 - y1
        bbox_width = x2 - x1
        
        # Base confidence from detection
        confidence = detection_conf
        
        # Adjust based on bbox size (larger = more confident)
        size_factor = min(bbox_height * bbox_width / 10000, 1.0)
        confidence *= (0.7 + 0.3 * size_factor)
        
        # Adjust based on aspect ratio (reasonable aspect ratio = more confident)
        aspect_ratio = bbox_width / max(bbox_height, 1)
        if 0.3 <= aspect_ratio <= 3.0:
            confidence *= 1.0
        else:
            confidence *= 0.8
        
        # Calibrated estimation is more confident
        if calibrated:
            confidence *= 1.2
        else:
            confidence *= 0.7
        
        return min(confidence, 1.0)
    
    def _calculate_confidence_interval(self, distance: float, confidence: float, 
                                      calibrated: bool = False) -> Tuple[float, float]:
        """
        Calculate confidence interval for distance estimation
        
        Args:
            distance: Estimated distance
            confidence: Confidence score
            calibrated: Whether using calibrated estimation
            
        Returns:
            Tuple of (min_distance, max_distance)
        """
        if calibrated:
            # Calibrated: ±10-20% based on confidence
            error_margin = (1.0 - confidence) * 0.2 + 0.1
        else:
            # Uncalibrated: ±20-40% based on confidence
            error_margin = (1.0 - confidence) * 0.4 + 0.2
        
        min_distance = distance * (1.0 - error_margin)
        max_distance = distance * (1.0 + error_margin)
        
        return (min_distance, max_distance)
    
    def estimate_distances_batch(self, detections: List[Dict[str, Any]], 
                                frame_height: int) -> List[DistanceEstimation]:
        """
        Estimate distances for multiple detections
        
        Args:
            detections: List of detection dictionaries
            frame_height: Frame height
            
        Returns:
            List of DistanceEstimation results
        """
        results = []
        
        for det in detections:
            bbox = det.get('bbox', [0, 0, 0, 0])
            object_class = det.get('class', 'unknown')
            confidence = det.get('confidence', 1.0)
            
            estimation = self.estimate_distance(bbox, frame_height, object_class, confidence)
            results.append(estimation)
        
        return results
    
    def get_calibration_info(self) -> Dict[str, Any]:
        """Get calibration information"""
        return {
            'has_calibration': self.has_calibration,
            'calibration_file': self.calibration_file,
            'focal_length': self.focal_length,
            'image_size': self.image_size,
            'object_heights': self.object_heights
        }
