"""
ADAS Main Application
Integrates LDWS, LKAS, and FCWS using YOLOv8
"""

import cv2
import argparse
import sys
from object_detector import ObjectDetector
from lane_detector import LaneDetector
from fcws import FCWS
from ldws import LDWS
from lkas import LKAS


class ADASSystem:
    """Main ADAS system integrating all components"""
    
    def __init__(self, yolo_model: str = 'yolov8n.pt', conf_threshold: float = 0.5):
        """
        Initialize ADAS system
        
        Args:
            yolo_model: Path to YOLOv8 model
            conf_threshold: Confidence threshold for object detection
        """
        print("Initializing ADAS System...")
        print("Loading YOLOv8 model...")
        self.object_detector = ObjectDetector(yolo_model, conf_threshold)
        self.lane_detector = LaneDetector()
        self.fcws = FCWS(warning_distance=150.0, critical_distance=80.0)
        self.ldws = LDWS(departure_threshold=30.0)
        self.lkas = LKAS(assist_threshold=20.0)
        print("ADAS System initialized successfully!")
    
    def process_frame(self, frame):
        """
        Process a single frame through all ADAS modules
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Processed frame with all ADAS overlays
        """
        # Object detection (for FCWS)
        detections = self.object_detector.detect(frame)
        
        # Lane detection (for LDWS and LKAS)
        left_lane, right_lane, lane_frame = self.lane_detector.detect_lanes(frame)
        
        # Calculate lane center and vehicle offset
        height, width = frame.shape[:2]
        lane_center, vehicle_offset = self.lane_detector.calculate_lane_center(
            left_lane, right_lane, width, height
        )
        
        # FCWS processing
        fcws_state, risky_detections = self.fcws.check_collision_risk(detections, frame)
        frame = self.fcws.draw_warning(frame, risky_detections)
        
        # LDWS processing
        ldws_state = self.ldws.check_lane_departure(lane_center, vehicle_offset, width)
        frame = self.ldws.draw_warning(frame, lane_center, vehicle_offset)
        
        # LKAS processing
        steering_angle = self.lkas.calculate_steering_angle(lane_center, vehicle_offset, width)
        frame = self.lkas.draw_assistance(frame, lane_center, vehicle_offset)
        
        # Draw object detections
        frame = self.object_detector.draw_detections(frame, detections)
        
        # Draw lane lines
        if left_lane is not None:
            cv2.line(frame, (left_lane[0], left_lane[1]), 
                    (left_lane[2], left_lane[3]), (0, 255, 0), 3)
        if right_lane is not None:
            cv2.line(frame, (right_lane[0], right_lane[1]), 
                    (right_lane[2], right_lane[3]), (0, 255, 0), 3)
        
        # Draw status panel
        frame = self._draw_status_panel(frame, fcws_state, ldws_state, len(detections))
        
        return frame
    
    def _draw_status_panel(self, frame, fcws_state, ldws_state, num_detections):
        """
        Draw status panel with system information
        
        Args:
            frame: Input frame
            fcws_state: FCWS warning state
            ldws_state: LDWS warning state
            num_detections: Number of detected objects
            
        Returns:
            Frame with status panel
        """
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
        lkas_color = (0, 255, 0) if self.lkas.assist_active else (128, 128, 128)
        lkas_status = "ACTIVE" if self.lkas.assist_active else "STANDBY"
        cv2.putText(frame, f"LKAS: {lkas_status}", (20, y_offset + line_height * 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, lkas_color, 2)
        
        # Detection count
        cv2.putText(frame, f"Objects: {num_detections}", (20, y_offset + line_height * 3), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def process_video(self, input_source, output_path=None, display=True):
        """
        Process video file or webcam stream
        
        Args:
            input_source: Path to video file or 0 for webcam
            output_path: Optional path to save output video
            display: Whether to display video in real-time
        """
        # Open video source
        if isinstance(input_source, str):
            cap = cv2.VideoCapture(input_source)
        else:
            cap = cv2.VideoCapture(input_source)
        
        if not cap.isOpened():
            print(f"Error: Could not open video source {input_source}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video properties: {width}x{height} @ {fps} FPS")
        
        # Setup video writer if output path is provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Write frame if output is specified
                if writer:
                    writer.write(processed_frame)
                
                # Display frame
                if display:
                    cv2.imshow('ADAS System', processed_frame)
                    
                    # Press 'q' to quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Processed {frame_count} frames...")
        
        except KeyboardInterrupt:
            print("\nProcessing interrupted by user")
        
        finally:
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            print(f"Processing complete. Total frames: {frame_count}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ADAS System with YOLOv8')
    parser.add_argument('--input', type=str, default='0',
                       help='Input video file path or 0 for webcam (default: 0)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video file path (optional)')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='YOLOv8 model path (default: yolov8n.pt)')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold (default: 0.5)')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable video display')
    
    args = parser.parse_args()
    
    # Convert input to int if it's '0' for webcam
    input_source = int(args.input) if args.input == '0' else args.input
    
    # Initialize ADAS system
    adas = ADASSystem(yolo_model=args.model, conf_threshold=args.conf)
    
    # Process video
    adas.process_video(input_source, args.output, display=not args.no_display)


if __name__ == '__main__':
    main()

