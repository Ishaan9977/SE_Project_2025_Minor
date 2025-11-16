"""
Data classes for lane detection results
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class LaneDetectionResult:
    """Result from lane detection model"""
    left_lane: Optional[np.ndarray]  # Polynomial coefficients or point array
    right_lane: Optional[np.ndarray]
    confidence: float
    lane_type: str = 'unknown'  # 'solid', 'dashed', 'double', 'unknown'
    success: bool = False
    processing_time: float = 0.0
    model_used: str = 'unknown'  # 'dl' or 'cv'
    
    def __post_init__(self):
        """Validate data after initialization"""
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
