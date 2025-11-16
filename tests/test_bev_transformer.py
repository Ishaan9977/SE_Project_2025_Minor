"""
Unit tests for BirdEyeViewTransformer
"""

import unittest
import numpy as np
import cv2
from transforms.bev_transformer import BirdEyeViewTransformer


class TestBirdEyeViewTransformer(unittest.TestCase):
    """Test BirdEyeViewTransformer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.transformer = BirdEyeViewTransformer(output_size=(300, 400))
        
        # Create sample frame
        self.frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.frame_height, self.frame_width = self.frame.shape[:2]
    
    def test_initialization(self):
        """Test transformer initialization"""
        self.assertEqual(self.transformer.output_size, (300, 400))
        self.assertIsNone(self.transformer.M)
    
    def test_set_default_points(self):
        """Test setting default transformation points"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        self.assertIsNotNone(self.transformer.src_points)
        self.assertIsNotNone(self.transformer.dst_points)
        self.assertIsNotNone(self.transformer.M)
    
    def test_calculate_transform_matrix(self):
        """Test transformation matrix calculation"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        M = self.transformer.calculate_transform_matrix()
        
        self.assertIsNotNone(M)
        self.assertEqual(M.shape, (3, 3))
    
    def test_transform_frame(self):
        """Test frame transformation"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        bev_frame = self.transformer.transform_frame(self.frame)
        
        self.assertIsNotNone(bev_frame)
        self.assertEqual(bev_frame.shape[:2], (400, 300))
    
    def test_transform_lanes(self):
        """Test lane transformation"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        # Create sample lanes
        left_lane = np.array([100, 1080, 300, 540])
        right_lane = np.array([1820, 1080, 1620, 540])
        
        left_transformed, right_transformed = self.transformer.transform_lanes(
            left_lane, right_lane
        )
        
        self.assertIsNotNone(left_transformed)
        self.assertIsNotNone(right_transformed)
    
    def test_draw_bev_overlay(self):
        """Test drawing BEV overlay"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        bev_frame = self.transformer.transform_frame(self.frame)
        
        # Create sample lanes in BEV space
        left_lane = np.array([[60, 400], [60, 200], [60, 0]])
        right_lane = np.array([[240, 400], [240, 200], [240, 0]])
        
        result = self.transformer.draw_bev_overlay(bev_frame, left_lane, right_lane)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, bev_frame.shape)
    
    def test_create_pip_overlay_bottom_right(self):
        """Test PIP overlay creation (bottom-right)"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        bev_frame = self.transformer.transform_frame(self.frame)
        
        result = self.transformer.create_pip_overlay(
            self.frame, bev_frame, position='bottom-right'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_create_pip_overlay_bottom_left(self):
        """Test PIP overlay creation (bottom-left)"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        bev_frame = self.transformer.transform_frame(self.frame)
        
        result = self.transformer.create_pip_overlay(
            self.frame, bev_frame, position='bottom-left'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_create_pip_overlay_top_right(self):
        """Test PIP overlay creation (top-right)"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        bev_frame = self.transformer.transform_frame(self.frame)
        
        result = self.transformer.create_pip_overlay(
            self.frame, bev_frame, position='top-right'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_create_pip_overlay_with_size(self):
        """Test PIP overlay with custom size"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        bev_frame = self.transformer.transform_frame(self.frame)
        
        result = self.transformer.create_pip_overlay(
            self.frame, bev_frame, size=(200, 250)
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_get_transform_info(self):
        """Test getting transformation information"""
        self.transformer.set_default_points(self.frame_width, self.frame_height)
        
        info = self.transformer.get_transform_info()
        
        self.assertEqual(info['output_size'], (300, 400))
        self.assertTrue(info['has_transform'])
        self.assertIsNotNone(info['src_points'])
        self.assertIsNotNone(info['dst_points'])


if __name__ == '__main__':
    unittest.main()
