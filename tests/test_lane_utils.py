"""
Unit tests for lane_utils
"""

import unittest
import numpy as np
from dl_models import lane_utils


class TestLaneUtils(unittest.TestCase):
    """Test lane utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create sample lane points
        self.lane_points = np.array([
            [100, 1080],
            [150, 900],
            [200, 720],
            [250, 540],
            [300, 360]
        ], dtype=np.float32)
    
    def test_fit_lane_polynomial(self):
        """Test polynomial fitting"""
        coeffs = lane_utils.fit_lane_polynomial(self.lane_points, degree=2)
        
        self.assertIsNotNone(coeffs)
        self.assertEqual(len(coeffs), 3)  # Quadratic has 3 coefficients
    
    def test_fit_lane_polynomial_linear(self):
        """Test linear polynomial fitting"""
        coeffs = lane_utils.fit_lane_polynomial(self.lane_points, degree=1)
        
        self.assertIsNotNone(coeffs)
        self.assertEqual(len(coeffs), 2)  # Linear has 2 coefficients
    
    def test_calculate_curvature(self):
        """Test curvature calculation"""
        coeffs = np.array([0.001, 0.5, 100])  # Quadratic coefficients
        
        curvature = lane_utils.calculate_curvature(coeffs, 540)
        
        self.assertGreater(curvature, 0)
        self.assertNotEqual(curvature, float('inf'))
    
    def test_evaluate_polynomial(self):
        """Test polynomial evaluation"""
        coeffs = np.array([0.001, 0.5, 100])
        y_values = np.array([100, 200, 300])
        
        x_values = lane_utils.evaluate_polynomial(coeffs, y_values)
        
        self.assertIsNotNone(x_values)
        self.assertEqual(len(x_values), 3)
    
    def test_generate_lane_points(self):
        """Test lane point generation"""
        coeffs = np.array([0.001, 0.5, 100])
        
        points = lane_utils.generate_lane_points(coeffs, 1080, 540, num_points=50)
        
        self.assertIsNotNone(points)
        self.assertEqual(points.shape[0], 50)
        self.assertEqual(points.shape[1], 2)
    
    def test_calculate_lane_width(self):
        """Test lane width calculation"""
        left_poly = np.array([0.001, 0.5, 100])
        right_poly = np.array([0.001, 0.5, 200])
        
        width = lane_utils.calculate_lane_width(left_poly, right_poly, 540)
        
        self.assertIsNotNone(width)
        self.assertGreater(width, 0)
    
    def test_smooth_lane_polynomial(self):
        """Test polynomial smoothing"""
        poly_history = [
            np.array([0.001, 0.5, 100]),
            np.array([0.0011, 0.51, 101]),
            np.array([0.0009, 0.49, 99])
        ]
        
        smoothed = lane_utils.smooth_lane_polynomial(poly_history, window_size=3)
        
        self.assertIsNotNone(smoothed)
        self.assertEqual(len(smoothed), 3)
    
    def test_validate_lane_polynomial(self):
        """Test polynomial validation"""
        # Use a polynomial that produces reasonable x values
        valid_poly = np.array([0.0001, 0.5, 960])
        
        is_valid = lane_utils.validate_lane_polynomial(valid_poly, 1920, 1080)
        
        self.assertTrue(is_valid)
    
    def test_convert_line_to_polynomial(self):
        """Test line to polynomial conversion"""
        line = np.array([100, 1080, 300, 540])
        
        coeffs = lane_utils.convert_line_to_polynomial(line)
        
        self.assertIsNotNone(coeffs)
        self.assertEqual(len(coeffs), 2)  # Linear


if __name__ == '__main__':
    unittest.main()
