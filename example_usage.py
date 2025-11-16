"""
Example usage of ADAS System
Demonstrates how to use individual modules or the complete system
"""

import cv2
from main import ADASSystem

def example_webcam():
    """Example: Process webcam feed"""
    print("Starting webcam ADAS system...")
    adas = ADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
    adas.process_video(0, display=True)

def example_video_file():
    """Example: Process video file"""
    print("Processing video file...")
    adas = ADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
    adas.process_video('input_video.mp4', output_path='output_video.mp4', display=True)

def example_single_frame():
    """Example: Process a single frame"""
    print("Processing single frame...")
    adas = ADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
    
    # Load image
    frame = cv2.imread('test_image.jpg')
    if frame is None:
        print("Error: Could not load test_image.jpg")
        return
    
    # Process frame
    processed_frame = adas.process_frame(frame)
    
    # Display result
    cv2.imshow('Processed Frame', processed_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Save result
    cv2.imwrite('output_image.jpg', processed_frame)
    print("Saved output_image.jpg")

if __name__ == '__main__':
    # Uncomment the example you want to run:
    
    # example_webcam()
    # example_video_file()
    example_single_frame()

