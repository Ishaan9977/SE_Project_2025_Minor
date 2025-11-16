"""
YOLOv8 Object Detection Module for ADAS
Detects vehicles, pedestrians, and other obstacles
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict


class ObjectDetector:
    """YOLOv8-based object detector for ADAS applications"""
    
    def __init__(self, model_path: str = 'yolov8n.pt', conf_threshold: float = 0.5):
        """
        Initialize the object detector
        
        Args:
            model_path: Path to YOLOv8 model weights
            conf_threshold: Confidence threshold for detections
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        # COCO classes relevant for ADAS (vehicles, pedestrians, etc.)
        self.relevant_classes = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle',
            5: 'bus', 7: 'truck'
        }
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in the frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detected objects with bounding boxes and confidence scores
        """
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                if cls_id in self.relevant_classes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    
                    detections.append({
                        'class': self.relevant_classes[cls_id],
                        'class_id': cls_id,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence,
                        'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                        'area': int((x2 - x1) * (y2 - y1))
                    })
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes on the frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with drawn bounding boxes
        """
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Color based on class
            if class_name in ['car', 'truck', 'bus']:
                color = (0, 0, 255)  # Red for vehicles
            elif class_name == 'person':
                color = (0, 255, 0)  # Green for pedestrians
            else:
                color = (255, 0, 0)  # Blue for others
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame

