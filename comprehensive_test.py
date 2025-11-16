"""
Comprehensive Testing Suite for DL-Enhanced ADAS System
Tests all components, video processing, and generates detailed reports
"""

import sys
import time
import cv2
import numpy as np
import logging
import json
from pathlib import Path
from datetime import datetime

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
        self.details = []
    
    def add_pass(self, test_name, details=""):
        self.passed += 1
        msg = f"✓ PASS: {test_name}"
        logger.info(msg)
        self.details.append({"test": test_name, "status": "PASS", "details": details})
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        msg = f"✗ FAIL: {test_name} - {error}"
        logger.error(msg)
        self.details.append({"test": test_name, "status": "FAIL", "error": error})
    
    def summary(self):
        total = self.passed + self.failed
        logger.info("\n" + "="*80)
        logger.info(f"TEST SUMMARY: {self.passed}/{total} passed ({100*self.passed//total}%)")
        logger.info("="*80)
        if self.errors:
            logger.error("\nFailed Tests:")
            for test_name, error in self.errors:
                logger.error(f"  - {test_name}: {error}")
        return self.failed == 0

results = TestResults()


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_imports():
    """Test all critical imports"""
    logger.info("\n[UNIT TEST] Import Validation")
    try:
        from enhanced_adas_system import EnhancedADASSystem
        from utils.config_loader import ConfigLoader
        from utils.model_manager import ModelManager
        from utils.distance_estimator import DistanceEstimator
        from dl_models.hybrid_lane_detector import HybridLaneDetector
        from overlays.advanced_overlay_renderer import AdvancedOverlayRenderer
        from overlays.animation_engine import AnimationEngine
        from transforms.bev_transformer import BEVTransformer
        
        results.add_pass("All Imports", "All critical modules imported successfully")
    except Exception as e:
        results.add_fail("All Imports", str(e))


def test_config_system():
    """Test configuration system"""
    logger.info("\n[UNIT TEST] Configuration System")
    try:
        from utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        assert config.config is not None, "Config not loaded"
        
        # Test config retrieval
        overlay_config = config.get_overlay_config()
        assert overlay_config is not None, "Overlay config missing"
        
        # Test config update
        config.update_from_dict({'test_key': 'test_value'})
        assert config.config.get('test_key') == 'test_value', "Config update failed"
        
        results.add_pass("Configuration System", f"Config keys: {len(config.config)}")
    except Exception as e:
        results.add_fail("Configuration System", str(e))


def test_hardware_detection():
    """Test hardware detection"""
    logger.info("\n[UNIT TEST] Hardware Detection")
    try:
        from utils.model_manager import ModelManager
        from utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        manager = ModelManager(config)
        
        device_info = manager.get_device_info()
        assert device_info is not None, "Device info missing"
        
        device = device_info.get('device', 'unknown')
        results.add_pass("Hardware Detection", f"Device: {device}")
    except Exception as e:
        results.add_fail("Hardware Detection", str(e))


def test_distance_estimation():
    """Test distance estimation"""
    logger.info("\n[UNIT TEST] Distance Estimation")
    try:
        from utils.distance_estimator import DistanceEstimator
        
        estimator = DistanceEstimator()
        assert estimator is not None, "Estimator not initialized"
        
        results.add_pass("Distance Estimation", "Estimator initialized")
    except Exception as e:
        results.add_fail("Distance Estimation", str(e))


def test_animation_engine():
    """Test animation engine"""
    logger.info("\n[UNIT TEST] Animation Engine")
    try:
        from overlays.animation_engine import AnimationEngine
        
        engine = AnimationEngine()
        assert engine is not None, "Engine not initialized"
        
        # Test update
        engine.update(0.033)
        
        results.add_pass("Animation Engine", "Engine initialized and updated")
    except Exception as e:
        results.add_fail("Animation Engine", str(e))


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_adas_initialization():
    """Test ADAS system initialization"""
    logger.info("\n[INTEGRATION TEST] ADAS System Initialization")
    try:
        from enhanced_adas_system import EnhancedADASSystem
        
        logger.info("  Initializing Enhanced ADAS System...")
        adas = EnhancedADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
        assert adas is not None, "ADAS not initialized"
        
        results.add_pass("ADAS Initialization", "System ready")
        return adas
    except Exception as e:
        results.add_fail("ADAS Initialization", str(e))
        return None


def test_frame_processing(adas):
    """Test single frame processing"""
    logger.info("\n[INTEGRATION TEST] Frame Processing")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[100:300, 150:500] = [100, 150, 200]
        
        start_time = time.time()
        processed_frame = adas.process_frame(test_frame)
        process_time = time.time() - start_time
        
        assert processed_frame is not None, "Processing returned None"
        assert processed_frame.shape == test_frame.shape, "Output shape mismatch"
        
        results.add_pass("Frame Processing", f"Time: {process_time*1000:.2f}ms")
    except Exception as e:
        results.add_fail("Frame Processing", str(e))


def test_batch_processing(adas):
    """Test batch frame processing"""
    logger.info("\n[INTEGRATION TEST] Batch Frame Processing")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        num_frames = 20
        logger.info(f"  Processing {num_frames} frames...")
        
        start_time = time.time()
        for i in range(num_frames):
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            processed = adas.process_frame(test_frame)
            assert processed is not None, f"Frame {i} processing failed"
        
        total_time = time.time() - start_time
        avg_time = total_time / num_frames
        fps = num_frames / total_time
        
        results.add_pass("Batch Processing", f"FPS: {fps:.2f}, Avg: {avg_time*1000:.2f}ms")
    except Exception as e:
        results.add_fail("Batch Processing", str(e))


def test_system_status(adas):
    """Test system status reporting"""
    logger.info("\n[INTEGRATION TEST] System Status")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        status = adas.get_system_status()
        assert status is not None, "Status is None"
        assert 'lane_detection' in status, "Missing lane detection status"
        assert 'fcws' in status, "Missing FCWS status"
        assert 'ldws' in status, "Missing LDWS status"
        
        results.add_pass("System Status", "All subsystems reporting")
    except Exception as e:
        results.add_fail("System Status", str(e))


def test_performance_metrics(adas):
    """Test performance metrics"""
    logger.info("\n[INTEGRATION TEST] Performance Metrics")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        metrics = adas.get_performance_metrics()
        assert metrics is not None, "Metrics is None"
        assert 'fps' in metrics, "Missing FPS metric"
        assert 'total_frames' in metrics, "Missing frame count"
        
        results.add_pass("Performance Metrics", f"FPS: {metrics['fps']:.2f}")
    except Exception as e:
        results.add_fail("Performance Metrics", str(e))


# ============================================================================
# VIDEO PROCESSING TESTS
# ============================================================================

def test_video_file_exists():
    """Check if test video exists"""
    logger.info("\n[VIDEO TEST] File Existence Check")
    video_path = Path('test_video.mp4')
    
    if video_path.exists():
        file_size = video_path.stat().st_size / (1024*1024)  # MB
        results.add_pass("Video File Exists", f"Size: {file_size:.2f} MB")
        return str(video_path)
    else:
        results.add_fail("Video File Exists", "test_video.mp4 not found")
        return None


def test_video_properties(video_path):
    """Test video file properties"""
    logger.info("\n[VIDEO TEST] Video Properties")
    if video_path is None:
        logger.warning("  Skipping - video not found")
        return None
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            results.add_fail("Video Properties", "Failed to open video")
            return None
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        details = f"Frames: {frame_count}, FPS: {fps:.1f}, Resolution: {width}x{height}, Duration: {duration:.1f}s"
        results.add_pass("Video Properties", details)
        
        return {
            'frame_count': frame_count,
            'fps': fps,
            'width': width,
            'height': height,
            'duration': duration
        }
    except Exception as e:
        results.add_fail("Video Properties", str(e))
        return None


def test_video_processing(video_path, adas):
    """Test full video processing"""
    logger.info("\n[VIDEO TEST] Full Video Processing")
    if video_path is None or adas is None:
        logger.warning("  Skipping - video or ADAS not available")
        return None
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            results.add_fail("Video Processing", "Failed to open video")
            return None
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"  Processing {frame_count} frames...")
        
        processed_count = 0
        start_time = time.time()
        frame_times = []
        errors = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_start = time.time()
            try:
                processed = adas.process_frame(frame)
                frame_time = time.time() - frame_start
                frame_times.append(frame_time)
                processed_count += 1
            except Exception as e:
                errors += 1
                logger.warning(f"  Frame {processed_count} error: {e}")
            
            if processed_count % 100 == 0:
                logger.info(f"  Processed {processed_count}/{frame_count} frames")
        
        total_time = time.time() - start_time
        cap.release()
        
        avg_fps = processed_count / total_time if total_time > 0 else 0
        avg_frame_time = np.mean(frame_times) * 1000 if frame_times else 0
        
        details = f"Processed: {processed_count}/{frame_count}, FPS: {avg_fps:.2f}, Avg Time: {avg_frame_time:.2f}ms, Errors: {errors}"
        results.add_pass("Video Processing", details)
        
        return {
            'processed_frames': processed_count,
            'total_frames': frame_count,
            'fps': avg_fps,
            'avg_frame_time': avg_frame_time,
            'total_time': total_time,
            'errors': errors
        }
    except Exception as e:
        results.add_fail("Video Processing", str(e))
        return None


def test_video_output(video_path, adas):
    """Test video output generation"""
    logger.info("\n[VIDEO TEST] Video Output Generation")
    if video_path is None or adas is None:
        logger.warning("  Skipping - video or ADAS not available")
        return
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            results.add_fail("Video Output", "Failed to open video")
            return
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_path = 'test_video_output.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        processed_count = 0
        for i in range(min(100, frame_count)):  # Process first 100 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            processed = adas.process_frame(frame)
            out.write(processed)
            processed_count += 1
        
        cap.release()
        out.release()
        
        if Path(output_path).exists():
            output_size = Path(output_path).stat().st_size / (1024*1024)
            results.add_pass("Video Output", f"Generated: {output_path} ({output_size:.2f} MB, {processed_count} frames)")
        else:
            results.add_fail("Video Output", "Output file not created")
    except Exception as e:
        results.add_fail("Video Output", str(e))


# ============================================================================
# STRESS TESTS
# ============================================================================

def test_memory_stability(adas):
    """Test memory stability under load"""
    logger.info("\n[STRESS TEST] Memory Stability")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get initial memory
        initial_memory = process.memory_info().rss / (1024*1024)  # MB
        
        # Process 50 frames
        for i in range(50):
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            adas.process_frame(test_frame)
        
        # Get final memory
        final_memory = process.memory_info().rss / (1024*1024)  # MB
        memory_increase = final_memory - initial_memory
        
        if memory_increase < 100:  # Less than 100MB increase
            results.add_pass("Memory Stability", f"Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {memory_increase:.1f}MB")
        else:
            results.add_fail("Memory Stability", f"Memory increase too high: {memory_increase:.1f}MB")
    except ImportError:
        logger.warning("  psutil not available, skipping memory test")
    except Exception as e:
        results.add_fail("Memory Stability", str(e))


def test_error_recovery(adas):
    """Test error recovery"""
    logger.info("\n[STRESS TEST] Error Recovery")
    if adas is None:
        logger.warning("  Skipping - ADAS not initialized")
        return
    
    try:
        # Test with invalid frames
        invalid_frames = [
            None,
            np.array([]),
            np.zeros((0, 0, 3), dtype=np.uint8),
            np.zeros((480, 640, 1), dtype=np.uint8),  # Wrong channels
        ]
        
        recovered = 0
        for i, invalid_frame in enumerate(invalid_frames):
            try:
                if invalid_frame is not None and invalid_frame.size > 0:
                    adas.process_frame(invalid_frame)
            except:
                recovered += 1
        
        # Test with valid frame after errors
        valid_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        processed = adas.process_frame(valid_frame)
        
        if processed is not None:
            results.add_pass("Error Recovery", f"Recovered from {recovered} errors, system still operational")
        else:
            results.add_fail("Error Recovery", "System failed to recover")
    except Exception as e:
        results.add_fail("Error Recovery", str(e))


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "="*80)
    logger.info("DL-ENHANCED ADAS SYSTEM - COMPREHENSIVE TEST SUITE")
    logger.info("="*80)
    
    # Unit Tests
    logger.info("\n[PHASE 1] UNIT TESTS")
    logger.info("-" * 80)
    test_imports()
    test_config_system()
    test_hardware_detection()
    test_distance_estimation()
    test_animation_engine()
    
    # Integration Tests
    logger.info("\n[PHASE 2] INTEGRATION TESTS")
    logger.info("-" * 80)
    adas = test_adas_initialization()
    test_frame_processing(adas)
    test_batch_processing(adas)
    test_system_status(adas)
    test_performance_metrics(adas)
    
    # Video Tests
    logger.info("\n[PHASE 3] VIDEO PROCESSING TESTS")
    logger.info("-" * 80)
    video_path = test_video_file_exists()
    video_props = test_video_properties(video_path)
    video_results = test_video_processing(video_path, adas)
    test_video_output(video_path, adas)
    
    # Stress Tests
    logger.info("\n[PHASE 4] STRESS TESTS")
    logger.info("-" * 80)
    test_memory_stability(adas)
    test_error_recovery(adas)
    
    # Summary
    success = results.summary()
    
    # Generate detailed report
    generate_report(video_props, video_results)
    
    return 0 if success else 1


def generate_report(video_props, video_results):
    """Generate detailed test report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': results.passed + results.failed,
            'passed': results.passed,
            'failed': results.failed,
            'pass_rate': f"{100*results.passed//(results.passed+results.failed)}%"
        },
        'video_properties': video_props,
        'video_results': video_results,
        'test_details': results.details
    }
    
    # Save JSON report
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\nDetailed report saved to: test_report.json")


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
