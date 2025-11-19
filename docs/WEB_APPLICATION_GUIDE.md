# Web Application - Complete Guide

## 7. WEB APPLICATION

### 7.1 app.py - Flask Server

**Purpose**: Web server providing HTTP API and video streaming

**Architecture**:
```
Browser (Client)
    ↓ HTTP Requests
Flask Server (app.py)
    ↓ Process Frames
EnhancedADASSystem
    ↓ MJPEG Stream
Browser (Client)
```

**Key Code**:
```python
from flask import Flask, render_template, Response, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import threading
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['SECRET_KEY'] = 'adas-enhanced-secret-key'

# Global variables
enhanced_adas = None
video_capture = None
current_video_path = None
processing_active = False
frame_lock = threading.Lock()

# Processing statistics
processing_stats = {
    'total_frames': 0,
    'processed_frames': 0,
    'start_time': None,
    'current_fps': 0.0,
    'errors': 0,
    'last_error': None,
    'source': 'idle',
    'detections': 0,
    'warnings': 0,
    'critical_alerts': 0
}
```

**Initialization**:
```python
def init_enhanced_adas():
    """Initialize Enhanced ADAS System"""
    global enhanced_adas, config_loader
    if enhanced_adas is None:
        logger.info("Initializing Enhanced ADAS System...")
        config_loader = ConfigLoader()
        enhanced_adas = EnhancedADASSystem(
            yolo_model='yolov8n.pt',
            conf_threshold=0.5
        )
        logger.info("Enhanced ADAS System initialized!")
    return enhanced_adas
```

**Frame Generation (MJPEG Streaming)**:
```python
def generate_frames():
    """
    Generate video frames with ADAS processing
    
    Yields MJPEG frames for streaming to browser
    """
    global video_capture, processing_active, enhanced_adas, processing_stats
    
    if enhanced_adas is None:
        enhanced_adas = init_enhanced_adas()
    
    processing_stats['start_time'] = time.time()
    processing_stats['processed_frames'] = 0
    
    while processing_active:
        try:
            with frame_lock:
                if video_capture is None or not video_capture.isOpened():
                    time.sleep(0.1)
                    continue
                
                # Read frame
                ret, frame = video_capture.read()
                if not ret:
                    if current_video_path:
                        # Loop video
                        video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = video_capture.read()
                        if not ret:
                            time.sleep(0.1)
                            continue
                    else:
                        # Webcam - wait for next frame
                        time.sleep(0.033)
                        continue
                
                # Process frame with ADAS
                try:
                    processed_frame = enhanced_adas.process_frame(frame)
                    
                    # Update statistics from system status
                    system_status = enhanced_adas.get_system_status()
                    if system_status.get('fcws', {}).get('warning_state') == 'WARNING':
                        processing_stats['warnings'] += 1
                    elif system_status.get('fcws', {}).get('warning_state') == 'CRITICAL':
                        processing_stats['critical_alerts'] += 1
                    
                except Exception as e:
                    logger.warning(f"ADAS processing error: {e}")
                    processed_frame = frame
                
                # Update statistics
                processing_stats['processed_frames'] += 1
                elapsed = time.time() - processing_stats['start_time']
                if elapsed > 0:
                    processing_stats['current_fps'] = (
                        processing_stats['processed_frames'] / elapsed
                    )
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame, 
                                          [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       frame_bytes + b'\r\n')
        
        except Exception as e:
            logger.error(f"Error in frame generation: {e}")
            processing_stats['errors'] += 1
            processing_stats['last_error'] = str(e)
            time.sleep(0.1)
            continue
        
        time.sleep(0.033)  # ~30 FPS
```

**Routes - Main Pages**:
```python
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route - MJPEG stream"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets (images, etc.)"""
    try:
        logger.info(f"Serving asset: {filename}")
        return send_from_directory('assets', filename)
    except Exception as e:
        logger.error(f"Error serving asset {filename}: {e}")
        return jsonify({'error': str(e)}), 404
```

**Routes - Video Control**:
```python
@app.route('/api/video/start_webcam', methods=['POST'])
def start_webcam():
    """Start webcam streaming"""
    global video_capture, processing_active, current_video_path
    
    try:
        logger.info("Starting webcam...")
        
        # Stop any existing stream
        processing_active = False
        time.sleep(0.2)
        
        with frame_lock:
            if video_capture is not None:
                video_capture.release()
            
            # Try to open webcam
            video_capture = cv2.VideoCapture(0)
            
            if not video_capture.isOpened():
                logger.error("Failed to open webcam")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to open webcam'
                }), 500
            
            # Set webcam properties
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            video_capture.set(cv2.CAP_PROP_FPS, 30)
            
            # Verify we can read a frame
            ret, test_frame = video_capture.read()
            if not ret:
                video_capture.release()
                video_capture = None
                logger.error("Failed to read from webcam")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to read from webcam'
                }), 500
            
            current_video_path = None
        
        # Reset statistics
        processing_stats['start_time'] = time.time()
        processing_stats['processed_frames'] = 0
        processing_stats['warnings'] = 0
        processing_stats['critical_alerts'] = 0
        processing_stats['source'] = 'webcam'
        processing_active = True
        
        logger.info("Webcam started successfully")
        return jsonify({
            'status': 'success',
            'message': 'Webcam started successfully'
        })
    
    except Exception as e:
        logger.error(f"Webcam error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Webcam error: {str(e)}'
        }), 500

@app.route('/api/video/upload', methods=['POST'])
def upload_video():
    """Upload and process video file"""
    global video_capture, processing_active, current_video_path
    
    try:
        logger.info("Video upload request received")
        
        if 'video' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No video file provided'
            }), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            # Stop any existing stream
            processing_active = False
            time.sleep(0.2)
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logger.info(f"Saving video to: {filepath}")
            file.save(filepath)
            
            # Verify file was saved
            if not os.path.exists(filepath):
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to save video file'
                }), 500
            
            with frame_lock:
                if video_capture is not None:
                    video_capture.release()
                
                # Try to open the video
                video_capture = cv2.VideoCapture(filepath)
                if not video_capture.isOpened():
                    return jsonify({
                        'status': 'error',
                        'message': 'Failed to open video file'
                    }), 500
                
                # Get video properties
                frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = video_capture.get(cv2.CAP_PROP_FPS)
                width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                current_video_path = filepath
            
            # Reset statistics
            processing_stats['start_time'] = time.time()
            processing_stats['processed_frames'] = 0
            processing_stats['warnings'] = 0
            processing_stats['critical_alerts'] = 0
            processing_stats['source'] = f'video: {filename}'
            processing_active = True
            
            logger.info(f"Video started: {filename}")
            
            return jsonify({
                'status': 'success',
                'message': 'Video started successfully',
                'filename': filename,
                'frames': frame_count,
                'fps': fps,
                'resolution': f'{width}x{height}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid file type. Supported: MP4, AVI, MOV, MKV, WEBM'
            }), 400
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Upload error: {str(e)}'
        }), 500

@app.route('/api/video/stop', methods=['POST'])
def stop_video():
    """Stop video streaming"""
    global video_capture, processing_active, current_video_path
    
    try:
        logger.info("Stopping video stream...")
        processing_active = False
        time.sleep(0.1)
        
        with frame_lock:
            if video_capture is not None:
                video_capture.release()
                video_capture = None
        
        current_video_path = None
        processing_stats['source'] = 'idle'
        logger.info("Video stream stopped")
        return jsonify({
            'status': 'success',
            'message': 'Streaming stopped'
        })
    except Exception as e:
        logger.error(f"Error stopping video: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

**Routes - Status and Metrics**:
```python
@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    global processing_active, video_capture, enhanced_adas, processing_stats
    
    try:
        status_info = {
            'processing': processing_active,
            'video_loaded': (
                video_capture is not None and 
                video_capture.isOpened() if video_capture else False
            ),
            'adas_initialized': enhanced_adas is not None,
            'processing_stats': processing_stats
        }
        
        if enhanced_adas:
            system_status = enhanced_adas.get_system_status()
            status_info['system'] = system_status
        
        return jsonify({'status': 'success', 'data': status_info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    global enhanced_adas, processing_stats
    
    try:
        metrics = {
            'fps': processing_stats['current_fps'],
            'total_frames': processing_stats['processed_frames'],
            'errors': processing_stats['errors'],
            'warnings': processing_stats['warnings'],
            'critical_alerts': processing_stats['critical_alerts'],
            'source': processing_stats['source']
        }
        
        if enhanced_adas is not None:
            perf_metrics = enhanced_adas.get_performance_metrics()
            metrics.update(perf_metrics)
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

**Main Entry Point**:
```python
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize Enhanced ADAS system
    init_enhanced_adas()
    
    logger.info("="*70)
    logger.info("Enhanced ADAS Web Application")
    logger.info("="*70)
    logger.info("Open your browser and navigate to: http://localhost:5000")
    logger.info("="*70)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
```

---

### 7.2 Key Concepts

**MJPEG Streaming**:
- Multipart JPEG stream
- Each frame is a separate JPEG image
- Boundary marker separates frames
- Browser displays as continuous video

**Threading**:
- `frame_lock` prevents race conditions
- Multiple threads access `video_capture`
- Ensures thread-safe frame reading

**Global State**:
- `processing_active`: Controls frame generation loop
- `video_capture`: OpenCV VideoCapture object
- `enhanced_adas`: ADAS system instance
- `processing_stats`: Performance metrics

**Error Handling**:
- Try-except blocks around critical operations
- Graceful degradation on errors
- Logging for debugging
- User-friendly error messages

---

