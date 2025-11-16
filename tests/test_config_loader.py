"""
Unit tests for ConfigLoader
"""

import unittest
import os
import json
import tempfile
from utils.config_loader import ConfigLoader, OverlayConfig


class TestConfigLoader(unittest.TestCase):
    """Test ConfigLoader functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yaml')
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_default_config_creation(self):
        """Test creating config with defaults"""
        loader = ConfigLoader(self.config_file)
        
        self.assertIsNotNone(loader.config)
        self.assertIn('models', loader.config)
        self.assertIn('overlays', loader.config)
        self.assertIn('performance', loader.config)
    
    def test_get_config_value(self):
        """Test getting config values with dot notation"""
        loader = ConfigLoader(self.config_file)
        
        # Test existing values
        self.assertTrue(loader.get('models.lane_detection.enabled'))
        self.assertEqual(loader.get('performance.target_fps'), 15)
        
        # Test non-existing value with default
        self.assertIsNone(loader.get('non.existing.key'))
        self.assertEqual(loader.get('non.existing.key', 'default'), 'default')
    
    def test_set_config_value(self):
        """Test setting config values"""
        loader = ConfigLoader(self.config_file)
        
        # Set value
        loader.set('models.lane_detection.confidence_threshold', 0.7)
        
        # Verify it was set
        self.assertEqual(loader.get('models.lane_detection.confidence_threshold'), 0.7)
    
    def test_overlay_config_creation(self):
        """Test OverlayConfig dataclass creation"""
        loader = ConfigLoader(self.config_file)
        overlay_config = loader.get_overlay_config()
        
        self.assertIsInstance(overlay_config, OverlayConfig)
        self.assertTrue(overlay_config.show_lane_polygon)
        self.assertTrue(overlay_config.show_bev)
        self.assertEqual(overlay_config.lane_polygon_alpha, 0.3)
    
    def test_config_validation(self):
        """Test config validation"""
        loader = ConfigLoader(self.config_file)
        
        # Invalid confidence threshold should be corrected
        loader.set('models.lane_detection.confidence_threshold', 1.5)
        # Validation happens on load, not on set, so we need to reload
        loader._validate_config()
        # After validation, should be clamped
        self.assertLessEqual(loader.get('models.lane_detection.confidence_threshold'), 1.0)
    
    def test_config_save_and_load(self):
        """Test saving and loading config"""
        loader = ConfigLoader(self.config_file)
        
        # Modify config
        loader.set('performance.target_fps', 20)
        
        # Save
        success = loader.save()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load in new instance
        loader2 = ConfigLoader(self.config_file)
        self.assertEqual(loader2.get('performance.target_fps'), 20)
    
    def test_update_from_dict(self):
        """Test batch update from dictionary"""
        loader = ConfigLoader(self.config_file)
        
        updates = {
            'performance.target_fps': 25,
            'performance.max_latency_ms': 80,
            'overlays.lane_polygon.alpha': 0.5
        }
        
        loader.update_from_dict(updates)
        
        self.assertEqual(loader.get('performance.target_fps'), 25)
        self.assertEqual(loader.get('performance.max_latency_ms'), 80)
        self.assertEqual(loader.get('overlays.lane_polygon.alpha'), 0.5)


if __name__ == '__main__':
    unittest.main()
