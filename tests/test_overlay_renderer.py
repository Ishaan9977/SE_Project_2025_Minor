"""
Unit tests for AdvancedOverlayRenderer
"""

import unittest
import numpy as np
from utils.config_loader import OverlayConfig
from overlays.animation_engine import AnimationEngine
from overlays.advanced_overlay_renderer import AdvancedOverlayRenderer


class TestAdvancedOverlayRenderer(unittest.TestCase):
    """Test AdvancedOverlayRenderer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = OverlayConfig()
        self.animation_engine = AnimationEngine()
        self.renderer = AdvancedOverlayRenderer(self.config, self.animation_engine)
        
        # Create sample frame
        self.frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    def test_initialization(self):
        """Test renderer initialization"""
        self.assertIsNotNone(self.renderer.config)
        self.assertIsNotNone(self.renderer.animation_engine)
    
    def test_alpha_blend(self):
        """Test alpha blending"""
        fg = np.ones((100, 100, 3), dtype=np.uint8) * 255
        bg = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = self.renderer.alpha_blend(fg, bg, 0.5)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, fg.shape)
    
    def test_create_gradient_mask(self):
        """Test gradient mask creation"""
        mask = self.renderer.create_gradient_mask(100, 100, start_alpha=1.0, end_alpha=0.3)
        
        self.assertIsNotNone(mask)
        self.assertEqual(mask.shape, (100, 100))
        # Bottom should be more opaque (start_alpha=1.0) than top (end_alpha=0.3)
        self.assertGreater(mask[99, 0], mask[0, 0])
    
    def test_draw_lane_polygon_disabled(self):
        """Test lane polygon drawing when disabled"""
        config = OverlayConfig(show_lane_polygon=False)
        renderer = AdvancedOverlayRenderer(config)
        
        left_lane = np.array([100, 1080, 300, 540])
        right_lane = np.array([1820, 1080, 1620, 540])
        
        result = renderer.draw_lane_polygon(self.frame.copy(), left_lane, right_lane)
        
        # Should return unchanged frame
        self.assertTrue(np.array_equal(result, self.frame))
    
    def test_draw_lane_polygon_enabled(self):
        """Test lane polygon drawing when enabled"""
        left_lane = np.array([100, 1080, 300, 540])
        right_lane = np.array([1820, 1080, 1620, 540])
        
        result = self.renderer.draw_lane_polygon(self.frame.copy(), left_lane, right_lane)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_draw_distance_markers(self):
        """Test distance marker drawing"""
        detections = [
            {'bbox': [100, 100, 200, 300], 'class': 'car'},
            {'bbox': [300, 150, 400, 350], 'class': 'truck'}
        ]
        
        result = self.renderer.draw_distance_markers(self.frame.copy(), detections, [])
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_draw_warning_overlay(self):
        """Test warning overlay drawing"""
        result = self.renderer.draw_warning_overlay(
            self.frame.copy(), 'collision', 'WARNING: Vehicle Ahead', 'warning'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_draw_directional_arrow_left(self):
        """Test left directional arrow drawing"""
        result = self.renderer.draw_directional_arrow(
            self.frame.copy(), 'left', (960, 540)
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_draw_directional_arrow_right(self):
        """Test right directional arrow drawing"""
        result = self.renderer.draw_directional_arrow(
            self.frame.copy(), 'right', (960, 540)
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.frame.shape)
    
    def test_apply_fade_transition(self):
        """Test fade transition"""
        current = np.ones((100, 100, 3), dtype=np.uint8) * 255
        previous = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = self.renderer.apply_fade_transition(current, previous, 0.5)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, current.shape)
    
    def test_update_config(self):
        """Test configuration update"""
        new_config = OverlayConfig(show_bev=False)
        
        self.renderer.update_config(new_config)
        
        self.assertFalse(self.renderer.config.show_bev)
    
    def test_set_performance_mode(self):
        """Test performance mode setting"""
        self.renderer.set_performance_mode(True)
        
        self.assertTrue(self.renderer.performance_mode)
        
        self.renderer.set_performance_mode(False)
        
        self.assertFalse(self.renderer.performance_mode)


if __name__ == '__main__':
    unittest.main()
