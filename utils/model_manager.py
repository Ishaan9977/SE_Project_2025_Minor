"""
Model Manager for ADAS Enhanced System
Handles loading and management of multiple detection models with hardware detection
"""

import os
import logging
import time
import numpy as np
from typing import Dict, Any, Optional, Tuple
import torch

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and benchmarking of detection models"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Model Manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.hardware_info = self.detect_hardware()
        self.device = self.select_inference_device()
        self.loaded_models = {}
        
        logger.info(f"Model Manager initialized with device: {self.device}")
        logger.info(f"Hardware capabilities: {self.hardware_info}")
    
    def detect_hardware(self) -> Dict[str, bool]:
        """
        Detect available hardware acceleration
        
        Returns:
            Dictionary with hardware availability flags
        """
        hardware = {
            'cuda': False,
            'cuda_version': None,
            'mps': False,  # Apple Metal Performance Shaders
            'openvino': False,
            'cpu': True
        }
        
        # Check for CUDA (NVIDIA GPU)
        try:
            if torch.cuda.is_available():
                hardware['cuda'] = True
                hardware['cuda_version'] = torch.version.cuda
                hardware['cuda_device_count'] = torch.cuda.device_count()
                hardware['cuda_device_name'] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
                logger.info(f"CUDA available: {hardware['cuda_device_name']} (CUDA {hardware['cuda_version']})")
            else:
                logger.info("CUDA not available")
        except Exception as e:
            logger.warning(f"Error checking CUDA availability: {e}")
        
        # Check for Apple Metal (MPS)
        try:
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                hardware['mps'] = True
                logger.info("Apple Metal (MPS) available")
            else:
                logger.info("Apple Metal (MPS) not available")
        except Exception as e:
            logger.warning(f"Error checking MPS availability: {e}")
        
        # Check for OpenVINO
        try:
            import openvino
            hardware['openvino'] = True
            hardware['openvino_version'] = openvino.__version__
            logger.info(f"OpenVINO available: version {hardware['openvino_version']}")
        except ImportError:
            logger.info("OpenVINO not available")
        except Exception as e:
            logger.warning(f"Error checking OpenVINO availability: {e}")
        
        return hardware
    
    def select_inference_device(self) -> str:
        """
        Select optimal inference device based on hardware availability
        
        Returns:
            Device string ('cuda', 'mps', 'cpu', etc.)
        """
        # Check config for device preference
        device_config = self.config.get('models', {}).get('lane_detection', {}).get('device', 'auto')
        
        if device_config != 'auto':
            # User specified a device
            if device_config == 'cuda' and self.hardware_info['cuda']:
                return 'cuda'
            elif device_config == 'mps' and self.hardware_info['mps']:
                return 'mps'
            elif device_config == 'openvino' and self.hardware_info['openvino']:
                return 'openvino'
            elif device_config == 'cpu':
                return 'cpu'
            else:
                logger.warning(f"Requested device '{device_config}' not available, falling back to auto-selection")
        
        # Auto-select device with priority: CUDA > MPS > OpenVINO > CPU
        if self.hardware_info['cuda']:
            return 'cuda'
        elif self.hardware_info['mps']:
            return 'mps'
        elif self.hardware_info['openvino']:
            return 'openvino'
        else:
            return 'cpu'
    
    def load_lane_model(self, model_path: str, model_type: str) -> Optional[Any]:
        """
        Load lane detection model
        
        Args:
            model_path: Path to model file
            model_type: Type of model ('onnx', 'pytorch', 'tensorflow')
            
        Returns:
            Loaded model or None if loading fails
        """
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return None
        
        try:
            if model_type.lower() == 'onnx':
                return self._load_onnx_model(model_path)
            elif model_type.lower() == 'pytorch':
                return self._load_pytorch_model(model_path)
            elif model_type.lower() == 'tensorflow':
                return self._load_tensorflow_model(model_path)
            else:
                logger.error(f"Unsupported model type: {model_type}")
                return None
        
        except Exception as e:
            logger.error(f"Error loading model {model_path}: {e}")
            return None
    
    def _load_onnx_model(self, model_path: str) -> Optional[Any]:
        """Load ONNX model"""
        try:
            import onnxruntime as ort
            
            # Select execution provider based on device
            providers = []
            if self.device == 'cuda' and 'CUDAExecutionProvider' in ort.get_available_providers():
                providers.append('CUDAExecutionProvider')
            providers.append('CPUExecutionProvider')
            
            session = ort.InferenceSession(model_path, providers=providers)
            
            # Get model info
            input_name = session.get_inputs()[0].name
            input_shape = session.get_inputs()[0].shape
            output_names = [output.name for output in session.get_outputs()]
            
            logger.info(f"ONNX model loaded: {model_path}")
            logger.info(f"Input: {input_name}, Shape: {input_shape}")
            logger.info(f"Outputs: {output_names}")
            logger.info(f"Execution providers: {session.get_providers()}")
            
            return {
                'session': session,
                'type': 'onnx',
                'input_name': input_name,
                'input_shape': input_shape,
                'output_names': output_names
            }
        
        except ImportError:
            logger.error("onnxruntime not installed. Install with: pip install onnxruntime")
            return None
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")
            return None
    
    def _load_pytorch_model(self, model_path: str) -> Optional[Any]:
        """Load PyTorch model"""
        try:
            model = torch.load(model_path, map_location=self.device)
            
            if isinstance(model, dict) and 'model' in model:
                model = model['model']
            
            model.eval()
            
            if self.device == 'cuda':
                model = model.cuda()
            elif self.device == 'mps':
                model = model.to('mps')
            
            logger.info(f"PyTorch model loaded: {model_path}")
            logger.info(f"Device: {self.device}")
            
            return {
                'model': model,
                'type': 'pytorch',
                'device': self.device
            }
        
        except Exception as e:
            logger.error(f"Error loading PyTorch model: {e}")
            return None
    
    def _load_tensorflow_model(self, model_path: str) -> Optional[Any]:
        """Load TensorFlow model"""
        try:
            import tensorflow as tf
            
            model = tf.keras.models.load_model(model_path)
            
            logger.info(f"TensorFlow model loaded: {model_path}")
            logger.info(f"Input shape: {model.input_shape}")
            logger.info(f"Output shape: {model.output_shape}")
            
            return {
                'model': model,
                'type': 'tensorflow'
            }
        
        except ImportError:
            logger.error("TensorFlow not installed. Install with: pip install tensorflow")
            return None
        except Exception as e:
            logger.error(f"Error loading TensorFlow model: {e}")
            return None
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a loaded model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        if model_name not in self.loaded_models:
            return {'error': 'Model not loaded'}
        
        model_data = self.loaded_models[model_name]
        
        info = {
            'name': model_name,
            'type': model_data.get('type', 'unknown'),
            'device': self.device
        }
        
        if model_data['type'] == 'onnx':
            info['input_shape'] = model_data.get('input_shape')
            info['output_names'] = model_data.get('output_names')
            info['providers'] = model_data['session'].get_providers()
        
        return info
    
    def benchmark_model(self, model: Any, num_frames: int = 100, 
                       input_shape: Tuple[int, ...] = (1, 3, 288, 800)) -> Dict[str, float]:
        """
        Benchmark model inference performance
        
        Args:
            model: Model to benchmark
            num_frames: Number of frames to test
            input_shape: Input tensor shape
            
        Returns:
            Dictionary with performance metrics
        """
        if model is None:
            return {'error': 'Model is None'}
        
        model_type = model.get('type', 'unknown')
        
        try:
            # Generate dummy input
            if model_type == 'onnx':
                dummy_input = np.random.randn(*input_shape).astype(np.float32)
            elif model_type == 'pytorch':
                if self.device == 'cuda':
                    dummy_input = torch.randn(*input_shape).cuda()
                elif self.device == 'mps':
                    dummy_input = torch.randn(*input_shape).to('mps')
                else:
                    dummy_input = torch.randn(*input_shape)
            elif model_type == 'tensorflow':
                import tensorflow as tf
                dummy_input = tf.random.normal(input_shape)
            else:
                return {'error': f'Unsupported model type: {model_type}'}
            
            # Warmup
            logger.info("Warming up model...")
            for _ in range(10):
                if model_type == 'onnx':
                    model['session'].run(None, {model['input_name']: dummy_input})
                elif model_type == 'pytorch':
                    with torch.no_grad():
                        _ = model['model'](dummy_input)
                elif model_type == 'tensorflow':
                    _ = model['model'](dummy_input, training=False)
            
            # Benchmark
            logger.info(f"Benchmarking model with {num_frames} frames...")
            start_time = time.time()
            
            for _ in range(num_frames):
                if model_type == 'onnx':
                    model['session'].run(None, {model['input_name']: dummy_input})
                elif model_type == 'pytorch':
                    with torch.no_grad():
                        _ = model['model'](dummy_input)
                elif model_type == 'tensorflow':
                    _ = model['model'](dummy_input, training=False)
            
            total_time = time.time() - start_time
            avg_time = (total_time / num_frames) * 1000  # Convert to ms
            fps = num_frames / total_time
            
            metrics = {
                'total_time_sec': round(total_time, 3),
                'avg_inference_ms': round(avg_time, 2),
                'fps': round(fps, 2),
                'num_frames': num_frames,
                'device': self.device,
                'model_type': model_type
            }
            
            logger.info(f"Benchmark results: {avg_time:.2f}ms per frame, {fps:.2f} FPS")
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error during benchmarking: {e}")
            return {'error': str(e)}
    
    def register_model(self, name: str, model: Any) -> None:
        """
        Register a loaded model
        
        Args:
            name: Model name
            model: Loaded model
        """
        self.loaded_models[name] = model
        logger.info(f"Model registered: {name}")
    
    def get_device(self) -> str:
        """Get current inference device"""
        return self.device
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        return self.hardware_info
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information
        
        Returns:
            Dictionary with device and hardware information
        """
        return {
            'device': self.device,
            'hardware': self.hardware_info
        }
