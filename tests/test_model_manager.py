"""
Unit tests for ModelManager
"""

import unittest
from utils.model_manager import ModelManager


class TestModelManager(unittest.TestCase):
    """Test ModelManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'models': {
                'lane_detection': {
                    'enabled': True,
                    'model_path': 'models/test.onnx',
                    'model_type': 'onnx',
                    'confidence_threshold': 0.6,
                    'device': 'auto'
                }
            }
        }
    
    def test_hardware_detection(self):
        """Test hardware detection"""
        manager = ModelManager(self.config)
        
        hardware = manager.detect_hardware()
        
        # Should always have CPU
        self.assertTrue(hardware['cpu'])
        
        # Check for expected keys
        self.assertIn('cuda', hardware)
        self.assertIn('mps', hardware)
        self.assertIn('openvino', hardware)
    
    def test_device_selection(self):
        """Test device selection"""
        manager = ModelManager(self.config)
        
        device = manager.get_device()
        
        # Should be one of the valid devices
        self.assertIn(device, ['cuda', 'mps', 'openvino', 'cpu'])
    
    def test_hardware_info_retrieval(self):
        """Test getting hardware information"""
        manager = ModelManager(self.config)
        
        info = manager.get_hardware_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('cpu', info)
        self.assertTrue(info['cpu'])
    
    def test_model_registration(self):
        """Test model registration"""
        manager = ModelManager(self.config)
        
        # Create mock model
        mock_model = {'type': 'onnx', 'session': None}
        
        manager.register_model('test_model', mock_model)
        
        # Verify registration
        self.assertIn('test_model', manager.loaded_models)
        self.assertEqual(manager.loaded_models['test_model'], mock_model)
    
    def test_model_info_retrieval(self):
        """Test getting model information"""
        manager = ModelManager(self.config)
        
        # Create mock model with mock session
        class MockSession:
            def get_providers(self):
                return ['CPUExecutionProvider']
        
        mock_model = {'type': 'onnx', 'session': MockSession()}
        manager.register_model('test_model', mock_model)
        
        info = manager.get_model_info('test_model')
        
        self.assertEqual(info['name'], 'test_model')
        self.assertEqual(info['type'], 'onnx')
        self.assertEqual(info['device'], manager.get_device())
    
    def test_nonexistent_model_info(self):
        """Test getting info for non-existent model"""
        manager = ModelManager(self.config)
        
        info = manager.get_model_info('nonexistent')
        
        self.assertIn('error', info)


if __name__ == '__main__':
    unittest.main()
