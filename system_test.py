"""
Comprehensive System and Module Test for DL-Enhanced ADAS
Tests all core components without web interface dependencies
"""

import sys
import time
import cv2
import numpy as np
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test Results Tracking
class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        logger.info(f"✓ PASS: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        logger.error(f"✗ FAIL: {test_name} - {error}")
    
    def summary(self):
        total = self.passed + self.failed
        logger.info("\n" + "="*70)
        logger.info(f"TEST SUMMARY: {self.passed}/{total} passed")
        logger.info("="*70)
        if self.errors:
            logger.error("\nFailed Tests:")
            for test_name, error in self.errors:
                logger.error(f"  - {test_name}: {error}")
        return self.failed == 0

results = TestResults()


# ============================================================================
# MODULE TESTS
# ============================================================================

def test_config_loader():
    """Test configuration loading and management"""
    logger.info("\n[TEST] Config Loader Module")
    try:
        from utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        assert config.config is not None, "Config not loaded"
        assert 'overlays' in config.config, "Missing overlays config"
        assert 'distance_estimator' in config.config, "Missing distance estimator config"
        
        results.add_pass("Config Loader - Initialization")
        
        # Test config retrieval
        overlay_config = config.get_overlay_config()
        assert overlay_config is not None, "Failed to get overlay config"
        results.add_pass("Config Loader - Get Overlay Config")
        
        # Test config update
        config.update_from_dict({'test_key': 'test_value'})
        assert config.config.get('test_key') == 'test_value', "Config update failed"
        results.add_pass("Config Loader - Update Config")
        
    except Exception as e:
        results.add_fail("Config Loader Module", str(e))


def test_model_manager():
    """Test model manager and hardware detection"""
    logger.info("\n[TEST] Model Manager Module")
    try:
        from utils.model_manager import ModelManager
        
        manager = ModelManager()
        assert manager is not None, "Model manager not initialized"
        results.add_pass("Model Manager - Initialization")
        
        # Test hardware detection
        device_info = manager.get_device_info()
        assert device_info is not None, "Failed to get device info"
        assert 'device' in device_info, "Missing device info"
        logger.info(f"  Device: {device_info['device']}")
        results.add_pass("Model Manager - Hardware Detection")
        
    except Exception as e:
        results.add_fail("Model Manager Module", str(e))


def test_distance_estimator():
    """Test distance estimation module"""
    logger.info("\n[TEST] Distance Estimator Module")
    try:
        from utils.distance_estimator import DistanceEstimator
        
        estimator = DistanceEstimator()
        assert estimator is not None, "Distance estimator not initialized"
        results.add_pass("Distance Estimator - Initialization")
        
        # Test with sample points
        test_points = np.array([[100, 200], [150, 250], [200, 300]])
        distances = estimator.estimate_distances(test_points)
        assert distances is not None, "Failed to estimate distances"
        assert len(distances) == len(test_points), "Distance count mismatch"
        results.add_pass("Distance Estimator - Distance Calculation")
        
    except Exception as e:
        results.add_fail("Distance Estimator Module", str(e))


def test_lane_detection():
    """Test lane detection modules"""
    logger.info("\n[TEST] Lane Detection Modules")
    try:
        from dl_models.hybrid_lane_detector import HybridLaneDetector
        
        detector = HybridLaneDetector()
        assert detector is not None, "Hybrid lane detector not initialized"
        results.add_pass("Lane Detection - Hybrid Detector Initialization")
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[200:300, 200:400] = [0, 255, 0]  # Green rectangle
        
        # Test detection
        lanes = detector.detect(test_frame)
        assert lanes is not None, "Lane detection returned None"
        results.add_pass("Lane Detection - Detection on Test Frame")
        
    except Exception as e:
        results.add_fail("Lane Detection Module", str(e))


def test_overlay_renderer():
    """Test overlay rendering system"""
    logger.info("\n[TEST] Overlay Renderer Module")
    try:
        from overlays.advanced_overlay_renderer import AdvancedOverlayRenderer
        from utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        overlay_config = config.get_overlay_config()
        
        renderer = AdvancedOverlayRenderer(overlay_config)
        assert renderer is not None, "Overlay renderer not initialized"
        results.add_pass("Overlay Renderer - Initialization")
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test rendering
        rendered = renderer.render(test_frame, {})
        assert rendered is not None, "Rendering returned None"
        assert rendered.shape == test_frame.shape, "Output shape mismatch"
        results.add_pass("Overlay Renderer - Frame Rendering")
        
    except Exception as e:
        results.add_fail("Overlay Renderer Module", str(e))


def test_animation_engine():
    """Test animation engine"""
    logger.info("\n[TEST] Animation Engine Module")
    try:
        from overlays.animation_engine import AnimationEngine
        
        engine = AnimationEngine()
        assert engine is not None, "Animation engine not initialized"
        results.add_pass("Animation Engine - Initialization")
        
        # Test easing functions
        easing_functions = ['linear', 'ease_in', 'ease_out', 'ease_in_out', 'bounce', 'elastic']
        for easing in easing_functions:
            value = engine.ease(0.5, easing)
            assert 0 <= value <= 1, f"Invalid easing value for {easing}"
        results.add_pass("Animation Engine - Easing Functions")
        
    except Exception as e:
        results.add_fail("Animation Engine Module", str(e))


def test_bev_transformer():
    """Test bird's eye view transformer"""
    logger.info("\n[TEST] BEV Transformer Module")
    try:
        from transforms.bev_transformer import BEVTransformer
        
        transformer = BEVTransformer()
        assert transformer is not None, "BEV transformer not initialized"
        results.add_pass("BEV Transformer - Initialization")
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test transformation
        bev_frame = transformer.transform(test_frame)
        assert bev_frame is not None, "BEV transformation returned None"
        results.add_pass("BEV Transformer - Frame Transformation")
        
    except Exception as e:
        results.add_fail("BEV Transformer Module", str(e))


# ============================================================================
# SYSTEM INTEGRATION TESTS
# ============================================================================

def test_enhanced_adas_initialization():
    """Test Enhanced ADAS system initialization"""
    logger.info("\n[TEST] Enhanced ADAS System Integration")
    try:
        from enhanced_adas_system import EnhancedADASSystem
        
        logger.info("  Initializing Enhanced ADAS System...")
        adas = EnhancedADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
        assert adas is not None, "ADAS system not initialized"
        results.add_pass("Enhanced ADAS - System Initialization")
        
        return adas
    except Exception as e:
        results.add_fail("Enhanced ADAS - System Initialization", str(e))
        return None


def test_frame_processing(adas):
    """Test frame processing pipeline"""
    logger.info("\n[TEST] Frame Processing Pipeline")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[100:300, 150:500] = [100, 150, 200]  # Add some content
        
        logger.info("  Processing test frame...")
        start_time = time.time()
        processed_frame = adas.process_frame(test_frame)
        process_time = time.time() - start_time
        
        assert processed_frame is not None, "Processing returned None"
        assert processed_frame.shape == test_frame.shape, "Output shape mismatch"
        assert process_time < 1.0, f"Processing too slow: {process_time:.2f}s"
        
        logger.info(f"  Processing time: {process_time*1000:.2f}ms")
        results.add_pass("Frame Processing - Single Frame")
        
    except Exception as e:
        results.add_fail("Frame Processing Pipeline", str(e))


def test_system_status(adas):
    """Test system status reporting"""
    logger.info("\n[TEST] System Status Reporting")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        status = adas.get_system_status()
        assert status is not None, "Status is None"
        assert 'lane_detection' in status, "Missing lane detection status"
        assert 'fcws' in status, "Missing FCWS status"
        assert 'ldws' in status, "Missing LDWS status"
        
        logger.info(f"  Lane Detection: {status['lane_detection']}")
        logger.info(f"  FCWS: {status['fcws']}")
        logger.info(f"  LDWS: {status['ldws']}")
        
        results.add_pass("System Status - Status Retrieval")
        
    except Exception as e:
        results.add_fail("System Status Reporting", str(e))


def test_performance_metrics(adas):
    """Test performance metrics collection"""
    logger.info("\n[TEST] Performance Metrics")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        metrics = adas.get_performance_metrics()
        assert metrics is not None, "Metrics is None"
        assert 'fps' in metrics, "Missing FPS metric"
        assert 'total_frames' in metrics, "Missing frame count"
        assert 'errors' in metrics, "Missing error count"
        
        logger.info(f"  FPS: {metrics['fps']:.2f}")
        logger.info(f"  Total Frames: {metrics['total_frames']}")
        logger.info(f"  Errors: {metrics['errors']}")
        
        results.add_pass("Performance Metrics - Metrics Collection")
        
    except Exception as e:
        results.add_fail("Performance Metrics", str(e))


def test_batch_processing(adas):
    """Test batch frame processing"""
    logger.info("\n[TEST] Batch Frame Processing")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        num_frames = 10
        logger.info(f"  Processing {num_frames} frames...")
        
        start_time = time.time()
        for i in range(num_frames):
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            processed = adas.process_frame(test_frame)
            assert processed is not None, f"Frame {i} processing failed"
        
        total_time = time.time() - start_time
        avg_time = total_time / num_frames
        fps = num_frames / total_time
        
        logger.info(f"  Total time: {total_time:.2f}s")
        logger.info(f"  Average per frame: {avg_time*1000:.2f}ms")
        logger.info(f"  Throughput: {fps:.2f} FPS")
        
        results.add_pass("Batch Processing - Multiple Frames")
        
    except Exception as e:
        results.add_fail("Batch Frame Processing", str(e))


def test_video_file_processing():
    """Test processing video file if available"""
    logger.info("\n[TEST] Video File Processing")
    try:
        from enhanced_adas_system import EnhancedADASSystem
        
        # Check for test video
        video_path = Path('test_video.mp4')
        if not video_path.exists():
            logger.warning("  Test video not found, skipping")
            return
        
        logger.info(f"  Loading video: {video_path}")
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.warning("  Failed to open video")
            return
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        logger.info(f"  Video: {frame_count} frames @ {fps:.1f} FPS")
        
        adas = EnhancedADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
        
        processed_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed = adas.process_frame(frame)
            processed_count += 1
            
            if processed_count % 50 == 0:
                logger.info(f"  Processed {processed_count}/{frame_count} frames")
        
        total_time = time.time() - start_time
        avg_fps = processed_count / total_time
        
        cap.release()
        
        logger.info(f"  Processing complete: {processed_count} frames in {total_time:.2f}s")
        logger.info(f"  Average FPS: {avg_fps:.2f}")
        
        results.add_pass("Video File Processing - Complete Video")
        
    except Exception as e:
        results.add_fail("Video File Processing", str(e))


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "="*70)
    logger.info("DL-ENHANCED ADAS SYSTEM - COMPREHENSIVE TEST SUITE")
    logger.info("="*70)
    
    # Module Tests
    logger.info("\n[PHASE 1] MODULE TESTS")
    logger.info("-" * 70)
    test_config_loader()
    test_model_manager()
    test_distance_estimator()
    test_lane_detection()
    test_overlay_renderer()
    test_animation_engine()
    test_bev_transformer()
    
    # System Integration Tests
    logger.info("\n[PHASE 2] SYSTEM INTEGRATION TESTS")
    logger.info("-" * 70)
    adas = test_enhanced_adas_initialization()
    test_frame_processing(adas)
    test_system_status(adas)
    test_performance_metrics(adas)
    test_batch_processing(adas)
    # Skip video file processing for now - focus on core modules
    # test_video_file_processing()
    
    # Summary
    success = results.summary()
    
    return 0 if success else 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
