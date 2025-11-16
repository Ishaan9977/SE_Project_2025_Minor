"""
Unit tests for DistanceEstimator
"""

import unittest
import numpy as np
from utils.distance_estimator import DistanceEstimator, DistanceEstimation


class TestDistanceEstimator(unittest.TestCase):
    """Test DistanceEstimator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.estimator = DistanceEstimator()
    
    def test_initialization(self):
        """Test distance estimator initialization"""
        self.assertFalse(self.estimator.has_calibration)
        self.assertIsNotNone(self.estimator.object_heights)
        self.assertIn('car', self.estimator.object_heights)
    
    def test_uncalibrated_distance_estimation(self):
        """Test uncalibrated distance estimation"""
        bbox = [100, 100, 200, 300]  # [x1, y1, x2, y2]
        frame_height = 1080
        
        result = self.estimator.estimate_distance(bbox, frame_height, 'car')
        
        self.assertIsInstance(result, DistanceEstimation)
        self.assertIsNone(result.distance_meters)
        self.assertGreater(result.distance_pixels, 0)
        self.assertGreater(result.confidence, 0)
        self.assertFalse(result.has_calibration)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        bbox = [100, 100, 200, 300]
        
        conf = self.estimator.calculate_confidence(bbox, 0.9, calibrated=False)
        
        self.assertGreater(conf, 0)
        self.assertLessEqual(conf, 1.0)
    
    def test_confidence_interval_calculation(self):
        """Test confidence interval calculation"""
        distance = 50.0
        confidence = 0.8
        
        min_dist, max_dist = self.estimator._calculate_confidence_interval(
            distance, confidence, calibrated=False
        )
        
        self.assertLess(min_dist, distance)
        self.assertGreater(max_dist, distance)
    
    def test_batch_distance_estimation(self):
        """Test batch distance estimation"""
        detections = [
            {'bbox': [100, 100, 200, 300], 'class': 'car', 'confidence': 0.9},
            {'bbox': [300, 150, 400, 350], 'class': 'truck', 'confidence': 0.85},
            {'bbox': [500, 200, 600, 400], 'class': 'person', 'confidence': 0.8}
        ]
        
        results = self.estimator.estimate_distances_batch(detections, 1080)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, DistanceEstimation)
    
    def test_default_object_heights(self):
        """Test default object heights"""
        heights = self.estimator.object_heights
        
        self.assertEqual(heights['car'], 1.5)
        self.assertEqual(heights['truck'], 3.0)
        self.assertEqual(heights['person'], 1.7)
    
    def test_calibration_info_retrieval(self):
        """Test getting calibration information"""
        info = self.estimator.get_calibration_info()
        
        self.assertFalse(info['has_calibration'])
        self.assertIsNone(info['calibration_file'])
        self.assertIsNotNone(info['object_heights'])


if __name__ == '__main__':
    unittest.main()
