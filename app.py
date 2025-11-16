"""
Flask Web Application for ADAS System
Provides web interface for real-time ADAS processing
"""

import cv2
import os
import threading
import time
from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
from main import ADASSystem

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['SECRET_KEY'] = 'adas-secret-key-change-in-production'

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Global variables for video streaming
adas_system = None
video_capture = None
current_video_path = None
processing_active = False
frame_lock = threading.Lock()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_adas():
    """Initialize ADAS system"""
    global adas_system
    if adas_system is None:
        print("Initializing ADAS System...")
        adas_system = ADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
        print("ADAS System initialized!")
    return adas_system

def get_video_capture(source):
    """Get video capture object"""
    global video_capture, current_video_path
    
    if video_capture is not None:
        video_capture.release()
    
    if isinstance(source, str):
        video_capture = cv2.VideoCapture(source)
        current_video_path = source
    else:
        video_capture = cv2.VideoCapture(source)
        current_video_path = None
    
    return video_capture

def generate_frames():
    """Generate video frames with ADAS processing"""
    global video_capture, processing_active, adas_system
    
    if adas_system is None:
        adas_system = init_adas()
    
    while processing_active:
        with frame_lock:
            if video_capture is None or not video_capture.isOpened():
                break
            
            ret, frame = video_capture.read()
            if not ret:
                # If video file ended, restart it
                if current_video_path:
                    video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = video_capture.read()
                    if not ret:
                        break
                else:
                    break
            
            # Process frame through ADAS
            processed_frame = adas_system.process_frame(frame)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Small delay to control frame rate
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_webcam', methods=['POST'])
def start_webcam():
    """Start webcam streaming"""
    global video_capture, processing_active
    
    try:
        get_video_capture(0)
        processing_active = True
        return jsonify({'status': 'success', 'message': 'Webcam started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/start_video', methods=['POST'])
def start_video():
    """Start video file streaming"""
    global video_capture, processing_active
    
    try:
        if 'video' not in request.files:
            return jsonify({'status': 'error', 'message': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create uploads directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            get_video_capture(filepath)
            processing_active = True
            
            return jsonify({'status': 'success', 'message': 'Video started', 'filename': filename})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop():
    """Stop video streaming"""
    global video_capture, processing_active
    
    try:
        processing_active = False
        if video_capture is not None:
            video_capture.release()
            video_capture = None
        return jsonify({'status': 'success', 'message': 'Streaming stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get current system status"""
    global processing_active, video_capture, adas_system
    
    status_info = {
        'processing': processing_active,
        'video_loaded': video_capture is not None and video_capture.isOpened() if video_capture else False,
        'adas_initialized': adas_system is not None
    }
    
    if adas_system:
        status_info.update({
            'fcws_state': adas_system.fcws.warning_state,
            'ldws_state': adas_system.ldws.warning_state,
            'lkas_active': adas_system.lkas.assist_active
        })
    
    return jsonify(status_info)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update ADAS settings"""
    global adas_system
    
    try:
        data = request.get_json()
        
        if adas_system is None:
            adas_system = init_adas()
        
        # Update confidence threshold if provided
        if 'conf_threshold' in data:
            conf = float(data['conf_threshold'])
            adas_system.object_detector.conf_threshold = conf
        
        # Update FCWS thresholds if provided
        if 'fcws_warning_distance' in data:
            adas_system.fcws.warning_distance = float(data['fcws_warning_distance'])
        if 'fcws_critical_distance' in data:
            adas_system.fcws.critical_distance = float(data['fcws_critical_distance'])
        
        # Update LDWS threshold if provided
        if 'ldws_threshold' in data:
            adas_system.ldws.departure_threshold = float(data['ldws_threshold'])
        
        # Update LKAS threshold if provided
        if 'lkas_threshold' in data:
            adas_system.lkas.assist_threshold = float(data['lkas_threshold'])
        
        return jsonify({'status': 'success', 'message': 'Settings updated'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize ADAS system
    init_adas()
    
    print("Starting Flask ADAS Application...")
    print("Open your browser and navigate to: http://localhost:5000")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

