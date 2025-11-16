"""
Configuration Loader for ADAS Enhanced System
Handles loading, validation, and management of configuration files
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OverlayConfig:
    """Configuration for overlay rendering"""
    show_lane_polygon: bool = True
    show_distance_markers: bool = True
    show_bev: bool = True
    show_animations: bool = True
    lane_polygon_alpha: float = 0.3
    lane_polygon_color: Tuple[int, int, int] = (0, 255, 0)
    warning_fade_duration: float = 0.3
    animation_speed: float = 1.0
    bev_position: str = 'bottom-right'
    bev_size: Tuple[int, int] = (300, 400)
    bev_alpha: float = 0.8
    distance_intervals: list = field(default_factory=lambda: [10, 20, 30, 40, 50])
    show_confidence: bool = True
    gradient_enabled: bool = True


class ConfigLoader:
    """Loads and manages ADAS system configuration"""
    
    DEFAULT_CONFIG_PATH = "config/adas_config.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to configuration file (uses default if None)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        self.overlay_config: Optional[OverlayConfig] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                self.config = self._get_default_config()
            
            # Validate configuration
            self._validate_config()
            
            # Create overlay config
            self._create_overlay_config()
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            self.config = self._get_default_config()
            self._create_overlay_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'models': {
                'lane_detection': {
                    'enabled': True,
                    'model_path': 'models/ultra_fast_lane.onnx',
                    'model_type': 'onnx',
                    'confidence_threshold': 0.6,
                    'device': 'auto'
                },
                'object_detection': {
                    'model_path': 'yolov8n.pt',
                    'confidence_threshold': 0.5
                }
            },
            'overlays': {
                'lane_polygon': {
                    'enabled': True,
                    'color': [0, 255, 0],
                    'alpha': 0.3,
                    'gradient_enabled': True
                },
                'distance_markers': {
                    'enabled': True,
                    'intervals': [10, 20, 30, 40, 50],
                    'show_confidence': True
                },
                'bev': {
                    'enabled': True,
                    'position': 'bottom-right',
                    'size': [300, 400],
                    'alpha': 0.8
                },
                'animations': {
                    'enabled': True,
                    'speed': 1.0,
                    'fade_duration': 0.3
                }
            },
            'camera': {
                'calibration_file': None,
                'resolution': [1920, 1080],
                'fps': 30
            },
            'performance': {
                'target_fps': 15,
                'max_latency_ms': 100,
                'enable_frame_skip': True,
                'enable_performance_mode': False
            },
            'fallback': {
                'enable_cv_fallback': True,
                'cv_confidence_threshold': 0.6,
                'max_consecutive_dl_failures': 5
            },
            'fcws': {
                'warning_distance': 150.0,
                'critical_distance': 80.0
            },
            'ldws': {
                'departure_threshold': 30.0
            },
            'lkas': {
                'assist_threshold': 20.0
            }
        }
    
    def _validate_config(self) -> None:
        """Validate configuration values"""
        # Validate confidence thresholds
        if 'models' in self.config:
            if 'lane_detection' in self.config['models']:
                conf = self.config['models']['lane_detection'].get('confidence_threshold', 0.6)
                if not 0.0 <= conf <= 1.0:
                    logger.warning(f"Invalid lane detection confidence threshold: {conf}, using 0.6")
                    self.config['models']['lane_detection']['confidence_threshold'] = 0.6
            
            if 'object_detection' in self.config['models']:
                conf = self.config['models']['object_detection'].get('confidence_threshold', 0.5)
                if not 0.0 <= conf <= 1.0:
                    logger.warning(f"Invalid object detection confidence threshold: {conf}, using 0.5")
                    self.config['models']['object_detection']['confidence_threshold'] = 0.5
        
        # Validate overlay alpha values
        if 'overlays' in self.config:
            if 'lane_polygon' in self.config['overlays']:
                alpha = self.config['overlays']['lane_polygon'].get('alpha', 0.3)
                if not 0.0 <= alpha <= 1.0:
                    logger.warning(f"Invalid lane polygon alpha: {alpha}, using 0.3")
                    self.config['overlays']['lane_polygon']['alpha'] = 0.3
            
            if 'bev' in self.config['overlays']:
                alpha = self.config['overlays']['bev'].get('alpha', 0.8)
                if not 0.0 <= alpha <= 1.0:
                    logger.warning(f"Invalid BEV alpha: {alpha}, using 0.8")
                    self.config['overlays']['bev']['alpha'] = 0.8
        
        # Validate performance settings
        if 'performance' in self.config:
            target_fps = self.config['performance'].get('target_fps', 15)
            if target_fps <= 0:
                logger.warning(f"Invalid target FPS: {target_fps}, using 15")
                self.config['performance']['target_fps'] = 15
    
    def _create_overlay_config(self) -> None:
        """Create OverlayConfig dataclass from configuration"""
        overlays = self.config.get('overlays', {})
        
        lane_poly = overlays.get('lane_polygon', {})
        dist_markers = overlays.get('distance_markers', {})
        bev = overlays.get('bev', {})
        animations = overlays.get('animations', {})
        
        self.overlay_config = OverlayConfig(
            show_lane_polygon=lane_poly.get('enabled', True),
            show_distance_markers=dist_markers.get('enabled', True),
            show_bev=bev.get('enabled', True),
            show_animations=animations.get('enabled', True),
            lane_polygon_alpha=lane_poly.get('alpha', 0.3),
            lane_polygon_color=tuple(lane_poly.get('color', [0, 255, 0])),
            warning_fade_duration=animations.get('fade_duration', 0.3),
            animation_speed=animations.get('speed', 1.0),
            bev_position=bev.get('position', 'bottom-right'),
            bev_size=tuple(bev.get('size', [300, 400])),
            bev_alpha=bev.get('alpha', 0.8),
            distance_intervals=dist_markers.get('intervals', [10, 20, 30, 40, 50]),
            show_confidence=dist_markers.get('show_confidence', True),
            gradient_enabled=lane_poly.get('gradient_enabled', True)
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'models.lane_detection.enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'models.lane_detection.enabled')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Recreate overlay config if overlay settings changed
        if keys[0] == 'overlays':
            self._create_overlay_config()
        
        logger.info(f"Configuration updated: {key} = {value}")
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            path: Path to save configuration (uses loaded path if None)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self.config_path
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
        logger.info("Configuration reloaded")
    
    def get_overlay_config(self) -> OverlayConfig:
        """Get overlay configuration dataclass"""
        return self.overlay_config
    
    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values from dictionary
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        for key, value in updates.items():
            self.set(key, value)
