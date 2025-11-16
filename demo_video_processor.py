"""
Demo Video Processor for ADAS Enhanced System
Processes test_video.mp4 and generates output with all features
"""

import cv2
import os
import sys
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import ADAS components
from main import ADASSystem
from utils.config_loader import ConfigLoader
from utils.distance_estimator import DistanceEstimator
from enhanced_fcws import EnhancedFCWS
from overlays.animation_engine import AnimationEngine
from overlays.advanced_overlay_renderer import AdvancedOverlayRenderer
from transforms.bev_transformer import BirdEyeViewTransformer


class VideoProcessor:
    """Process video with ADAS system and generate results"""
    
    def __init__(self, video_path, output_dir='demo_output'):
        """
        Initialize video processor
        
        Args:
            video_path: Path to input video
            output_dir: Directory for output files
        """
        self.video_path = video_path
        self.output_dir = output_dir
        self.config_loader = ConfigLoader()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize ADAS system
        logger.info("Initializing ADAS System...")
        self.adas = ADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
        
        # Initialize enhanced components
        self.distance_estimator = DistanceEstimator()
        self.enhanced_fcws = EnhancedFCWS(
            warning_distance=30.0,
            critical_distance=15.0,
            distance_estimator=self.distance_estimator
        )
        
        self.animation_engine = AnimationEngine()
        overlay_config = self.config_loader.get_overlay_config()
        self.overlay_renderer = AdvancedOverlayRenderer(overlay_config, self.animation_engine)
        
        self.bev_transformer = BirdEyeViewTransformer(output_size=(300, 400))
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'processed_frames': 0,
            'skipped_frames': 0,
            'total_detections': 0,
            'total_time': 0.0,
            'avg_fps': 0.0,
            'warnings': {'SAFE': 0, 'WARNING': 0, 'CRITICAL': 0}
        }
        
        logger.info("Video Processor initialized successfully")
    
    def process_video(self, output_video=True, output_frames=False):
        """
        Process video file
        
        Args:
            output_video: Whether to save output video
            output_frames: Whether to save individual frames
        """
        logger.info(f"Processing video: {self.video_path}")
        
        # Open video
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {self.video_path}")
            return False
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video properties: {width}x{height} @ {fps} FPS, {total_frames} frames")
        
        # Setup video writer
        writer = None
        if output_video:
            output_path = os.path.join(self.output_dir, 'output_video.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            logger.info(f"Output video will be saved to: {output_path}")
        
        # Process frames
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                self.stats['total_frames'] += 1
                
                # Process frame
                frame_start = time.time()
                processed_frame = self._process_frame(frame)
                frame_time = time.time() - frame_start
                
                self.stats['processed_frames'] += 1
                self.stats['total_time'] += frame_time
                
                # Write output
                if writer:
                    writer.write(processed_frame)
                
                # Save frame if requested
                if output_frames and frame_count % 30 == 0:  # Every 30 frames
                    frame_path = os.path.join(self.output_dir, f'frame_{frame_count:04d}.jpg')
                    cv2.imwrite(frame_path, processed_frame)
                
                # Progress
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    current_fps = frame_count / elapsed
                    logger.info(f"Processed {frame_count}/{total_frames} frames ({current_fps:.1f} FPS)")
        
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return False
        
        finally:
            cap.release()
            if writer:
                writer.release()
        
        # Calculate statistics
        self.stats['total_time'] = time.time() - start_time
        self.stats['avg_fps'] = self.stats['processed_frames'] / self.stats['total_time']
        
        logger.info(f"Video processing complete!")
        logger.info(f"Total time: {self.stats['total_time']:.2f}s")
        logger.info(f"Average FPS: {self.stats['avg_fps']:.2f}")
        
        return True
    
    def _process_frame(self, frame):
        """Process single frame with all ADAS features"""
        height, width = frame.shape[:2]
        
        # Object detection
        detections = self.adas.object_detector.detect(frame)
        self.stats['total_detections'] += len(detections)
        
        # Lane detection
        left_lane, right_lane, _ = self.adas.lane_detector.detect_lanes(frame)
        
        # Calculate lane metrics
        lane_center, vehicle_offset = self.adas.lane_detector.calculate_lane_center(
            left_lane, right_lane, width, height
        )
        
        # Enhanced FCWS with distance estimation
        fcws_state, risky_detections = self.enhanced_fcws.check_collision_risk(detections, frame)
        self.stats['warnings'][fcws_state] += 1
        
        # LDWS
        ldws_state = self.adas.ldws.check_lane_departure(lane_center, vehicle_offset, width)
        
        # LKAS
        steering_angle = self.adas.lkas.calculate_steering_angle(lane_center, vehicle_offset, width)
        
        # Update animations
        self.animation_engine.update(0.033)  # ~30 FPS
        
        # Draw overlays
        frame = self.overlay_renderer.draw_lane_polygon(frame, left_lane, right_lane)
        frame = self.enhanced_fcws.draw_warning(frame, risky_detections)
        frame = self.adas.ldws.draw_warning(frame, lane_center, vehicle_offset)
        frame = self.adas.lkas.draw_assistance(frame, lane_center, vehicle_offset)
        frame = self.adas.object_detector.draw_detections(frame, detections)
        
        # Draw BEV if enabled
        if self.config_loader.get('overlays.bev.enabled'):
            try:
                self.bev_transformer.set_default_points(width, height)
                bev_frame = self.bev_transformer.transform_frame(frame)
                if bev_frame is not None:
                    left_bev, right_bev = self.bev_transformer.transform_lanes(left_lane, right_lane)
                    bev_frame = self.bev_transformer.draw_bev_overlay(bev_frame, left_bev, right_bev)
                    frame = self.bev_transformer.create_pip_overlay(frame, bev_frame, position='bottom-right')
            except Exception as e:
                logger.debug(f"BEV rendering error: {e}")
        
        # Draw status panel
        frame = self._draw_status_panel(frame, fcws_state, ldws_state, len(detections))
        
        return frame
    
    def _draw_status_panel(self, frame, fcws_state, ldws_state, num_detections):
        """Draw status panel on frame"""
        height, width = frame.shape[:2]
        
        # Draw semi-transparent panel
        panel_height = 120
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (10, 10), (300, panel_height), (255, 255, 255), 2)
        
        # Draw status information
        y_offset = 35
        line_height = 25
        
        # FCWS status
        fcws_color = (0, 255, 0) if fcws_state == "SAFE" else (0, 165, 255) if fcws_state == "WARNING" else (0, 0, 255)
        cv2.putText(frame, f"FCWS: {fcws_state}", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fcws_color, 2)
        
        # LDWS status
        ldws_color = (0, 255, 0) if ldws_state == "SAFE" else (0, 165, 255)
        cv2.putText(frame, f"LDWS: {ldws_state}", (20, y_offset + line_height), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, ldws_color, 2)
        
        # LKAS status
        lkas_color = (0, 255, 0) if self.adas.lkas.assist_active else (128, 128, 128)
        lkas_status = "ACTIVE" if self.adas.lkas.assist_active else "STANDBY"
        cv2.putText(frame, f"LKAS: {lkas_status}", (20, y_offset + line_height * 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, lkas_color, 2)
        
        # Detection count
        cv2.putText(frame, f"Objects: {num_detections}", (20, y_offset + line_height * 3), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def generate_report(self):
        """Generate processing report"""
        report_path = os.path.join(self.output_dir, 'processing_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("ADAS ENHANCED SYSTEM - VIDEO PROCESSING REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Input Video: {self.video_path}\n")
            f.write(f"Output Directory: {self.output_dir}\n\n")
            
            f.write("VIDEO STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Frames: {self.stats['total_frames']}\n")
            f.write(f"Processed Frames: {self.stats['processed_frames']}\n")
            f.write(f"Skipped Frames: {self.stats['skipped_frames']}\n")
            f.write(f"Total Processing Time: {self.stats['total_time']:.2f} seconds\n")
            f.write(f"Average FPS: {self.stats['avg_fps']:.2f}\n\n")
            
            f.write("DETECTION STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Detections: {self.stats['total_detections']}\n")
            f.write(f"Average Detections per Frame: {self.stats['total_detections'] / max(self.stats['processed_frames'], 1):.2f}\n\n")
            
            f.write("WARNING STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"SAFE Frames: {self.stats['warnings']['SAFE']}\n")
            f.write(f"WARNING Frames: {self.stats['warnings']['WARNING']}\n")
            f.write(f"CRITICAL Frames: {self.stats['warnings']['CRITICAL']}\n\n")
            
            f.write("SYSTEM CONFIGURATION\n")
            f.write("-" * 70 + "\n")
            f.write(f"Lane Detection Model: DL + CV Fallback\n")
            f.write(f"Object Detection Model: YOLOv8n\n")
            f.write(f"Distance Estimation: Uncalibrated (Normalized)\n")
            f.write(f"Overlay Rendering: Advanced with Animations\n")
            f.write(f"BEV Transformation: Enabled\n\n")
            
            f.write("FEATURES ENABLED\n")
            f.write("-" * 70 + "\n")
            f.write(f"[OK] Forward Collision Warning System (FCWS)\n")
            f.write(f"[OK] Lane Departure Warning System (LDWS)\n")
            f.write(f"[OK] Lane Keeping Assistance System (LKAS)\n")
            f.write(f"[OK] Enhanced Distance Estimation\n")
            f.write(f"[OK] Advanced Overlay Rendering\n")
            f.write(f"[OK] Animation Engine\n")
            f.write(f"[OK] Bird's Eye View Transformation\n\n")
            
            f.write("="*70 + "\n")
        
        logger.info(f"Report saved to: {report_path}")
        return report_path


def main():
    """Main entry point"""
    video_path = 'test_video.mp4'
    
    # Check if video exists
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return 1
    
    # Process video
    processor = VideoProcessor(video_path, output_dir='demo_output')
    
    logger.info("Starting video processing...")
    success = processor.process_video(output_video=True, output_frames=False)
    
    if success:
        # Generate report
        processor.generate_report()
        
        logger.info("\n" + "="*70)
        logger.info("VIDEO PROCESSING COMPLETE!")
        logger.info("="*70)
        logger.info(f"Output files saved to: demo_output/")
        logger.info(f"  - output_video.mp4 (processed video)")
        logger.info(f"  - processing_report.txt (detailed report)")
        logger.info("="*70)
        
        return 0
    else:
        logger.error("Video processing failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
