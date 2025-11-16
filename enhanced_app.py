"""
Enhanced Flask Web Application for ADAS System - Phase 5 (Modern Edition)
Real-time streaming with WebSocket support, interactive controls, and modern UI
"""

import cv2
import os
import threading
import time
import json
import logging
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from enhanced_adas_system import EnhancedADASSystem
from utils.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['SECRET_KEY'] = 'adas-enhanced-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Global state management
class ADASState:
    def __init__(self):
        self.video_capture = None
        self.current_video_path = None
        self.processing_active = False
        self.frame_lock = threading.Lock()
        self.enhanced_adas = None
        self.config_loader = None
        self.stats = {
            'total_frames': 0,
            'processed_frames': 0,
            'start_time': None,
            'current_fps': 0.0,
            'errors': 0,
            'last_error': None,
            'avg_frame_time': 0.0,
            'source': 'idle'
        }
        self.connected_clients = set()

state = ADASState()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_enhanced_adas():
    """Initialize Enhanced ADAS System"""
    if state.enhanced_adas is None:
        logger.info("Initializing Enhanced ADAS System...")
        state.config_loader = ConfigLoader()
        state.enhanced_adas = EnhancedADASSystem(yolo_model='yolov8n.pt', conf_threshold=0.5)
        logger.info("Enhanced ADAS System initialized!")
    return state.enhanced_adas


def broadcast_stats():
    """Broadcast stats to all connected clients"""
    socketio.emit('stats_update', {
        'fps': round(state.stats['current_fps'], 2),
        'frames': state.stats['processed_frames'],
        'errors': state.stats['errors'],
        'source': state.stats['source'],
        'avg_time': round(state.stats['avg_frame_time'], 2)
    }, broadcast=True)


def generate_frames():
    """Generate video frames with ADAS processing"""
    if state.enhanced_adas is None:
        init_enhanced_adas()
    
    state.stats['start_time'] = time.time()
    state.stats['processed_frames'] = 0
    frame_times = []
    
    while state.processing_active:
        frame_bytes = None
        frame_start = time.time()
        
        try:
            with state.frame_lock:
                if state.video_capture is None or not state.video_capture.isOpened():
                    time.sleep(0.1)
                    continue
                
                ret, frame = state.video_capture.read()
                if not ret:
                    if state.current_video_path:
                        state.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = state.video_capture.read()
                        if not ret:
                            time.sleep(0.1)
                            continue
                    else:
                        time.sleep(0.033)
                        continue
                
                # Process frame with enhanced ADAS
                try:
                    processed_frame = state.enhanced_adas.process_frame(frame)
                except Exception as e:
                    logger.warning(f"ADAS processing error: {e}")
                    processed_frame = frame
                
                # Update statistics
                state.stats['processed_frames'] += 1
                elapsed = time.time() - state.stats['start_time']
                if elapsed > 0:
                    state.stats['current_fps'] = state.stats['processed_frames'] / elapsed
                
                # Track frame time
                frame_time = time.time() - frame_start
                frame_times.append(frame_time)
                if len(frame_times) > 30:
                    frame_times.pop(0)
                state.stats['avg_frame_time'] = sum(frame_times) / len(frame_times) * 1000
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
        
        except Exception as e:
            logger.error(f"Frame generation error: {e}")
            state.stats['errors'] += 1
            state.stats['last_error'] = str(e)
            time.sleep(0.1)
            continue
        
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033)


# ============================================================================
# ROUTES - Main Pages
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('enhanced_dashboard.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    state.connected_clients.add(request.sid)
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'data': 'Connected to ADAS System'})
    broadcast_stats()


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    state.connected_clients.discard(request.sid)
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('request_stats')
def handle_stats_request():
    """Send current stats to requesting client"""
    emit('stats_update', {
        'fps': round(state.stats['current_fps'], 2),
        'frames': state.stats['processed_frames'],
        'errors': state.stats['errors'],
        'source': state.stats['source'],
        'avg_time': round(state.stats['avg_frame_time'], 2)
    })


@socketio.on('start_webcam')
def handle_start_webcam():
    """Start webcam streaming via WebSocket"""
    try:
        logger.info("Starting webcam...")
        state.processing_active = False
        time.sleep(0.2)
        
        with state.frame_lock:
            if state.video_capture is not None:
                state.video_capture.release()
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                emit('error', {'message': 'Failed to open webcam'})
                return
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            ret, test_frame = cap.read()
            if not ret:
                cap.release()
                emit('error', {'message': 'Failed to read from webcam'})
                return
            
            state.video_capture = cap
            state.current_video_path = None
        
        state.stats['start_time'] = time.time()
        state.stats['processed_frames'] = 0
        state.stats['source'] = 'webcam'
        state.processing_active = True
        
        emit('status_update', {'status': 'Webcam Active', 'source': 'webcam'}, broadcast=True)
        logger.info("Webcam started successfully")
    
    except Exception as e:
        logger.error(f"Webcam error: {e}")
        emit('error', {'message': f'Webcam error: {str(e)}'})


@socketio.on('upload_video')
def handle_upload_video(data):
    """Handle video upload via WebSocket"""
    try:
        if 'filename' not in data or 'data' not in data:
            emit('error', {'message': 'Invalid upload data'})
            return
        
        logger.info(f"Video upload request: {data['filename']}")
        
        state.processing_active = False
        time.sleep(0.2)
        
        os.makedirs(state.config_loader.config.get('upload_folder', 'uploads'), exist_ok=True)
        filename = secure_filename(data['filename'])
        filepath = os.path.join('uploads', filename)
        
        # Save file from base64 data
        import base64
        video_data = base64.b64decode(data['data'].split(',')[1])
        with open(filepath, 'wb') as f:
            f.write(video_data)
        
        # Verify and open video
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            emit('error', {'message': 'Failed to open video file'})
            return
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        with state.frame_lock:
            if state.video_capture is not None:
                state.video_capture.release()
            state.video_capture = cv2.VideoCapture(filepath)
            state.current_video_path = filepath
        
        state.stats['start_time'] = time.time()
        state.stats['processed_frames'] = 0
        state.stats['source'] = f'video: {filename}'
        state.processing_active = True
        
        emit('status_update', {
            'status': 'Video Playing',
            'source': filename,
            'frames': frame_count,
            'fps': fps
        }, broadcast=True)
        logger.info(f"Video started: {filename}")
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        emit('error', {'message': f'Upload error: {str(e)}'})


@socketio.on('stop_stream')
def handle_stop_stream():
    """Stop video streaming"""
    try:
        logger.info("Stopping stream...")
        state.processing_active = False
        time.sleep(0.1)
        
        with state.frame_lock:
            if state.video_capture is not None:
                state.video_capture.release()
                state.video_capture = None
        
        state.current_video_path = None
        state.stats['source'] = 'idle'
        
        emit('status_update', {'status': 'Stopped', 'source': 'idle'}, broadcast=True)
        logger.info("Stream stopped")
    
    except Exception as e:
        logger.error(f"Stop error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('update_config')
def handle_update_config(data):
    """Update system configuration"""
    try:
        if state.config_loader is None:
            state.config_loader = ConfigLoader()
        
        state.config_loader.update_from_dict(data)
        state.config_loader.save()
        
        if state.enhanced_adas is not None:
            overlay_config = state.config_loader.get_overlay_config()
            state.enhanced_adas.overlay_renderer.update_config(overlay_config)
        
        emit('config_updated', {'updated_keys': list(data.keys())}, broadcast=True)
        logger.info(f"Config updated: {list(data.keys())}")
    
    except Exception as e:
        logger.error(f"Config update error: {e}")
        emit('error', {'message': f'Config error: {str(e)}'})


# ============================================================================
# REST API ENDPOINTS (Fallback)
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    try:
        status_info = {
            'processing': state.processing_active,
            'video_loaded': state.video_capture is not None and state.video_capture.isOpened() if state.video_capture else False,
            'adas_initialized': state.enhanced_adas is not None,
            'stats': state.stats,
            'connected_clients': len(state.connected_clients)
        }
        
        if state.enhanced_adas:
            system_status = state.enhanced_adas.get_system_status()
            status_info['system'] = system_status
        
        return jsonify({'status': 'success', 'data': status_info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    try:
        if state.enhanced_adas is None:
            return jsonify({'status': 'error', 'message': 'ADAS not initialized'}), 500
        
        metrics = state.enhanced_adas.get_performance_metrics()
        return jsonify({'status': 'success', 'metrics': metrics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def get_health():
    """Get system health status"""
    try:
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'errors': state.stats['errors'],
            'last_error': state.stats['last_error']
        }
        
        if state.stats['errors'] > 10:
            health['status'] = 'degraded'
        
        if state.enhanced_adas:
            metrics = state.enhanced_adas.get_performance_metrics()
            if metrics.get('fps', 0) < 5:
                health['status'] = 'degraded'
        
        return jsonify({'status': 'success', 'health': health})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        info = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-phase5-modern',
            'components': {
                'adas_initialized': state.enhanced_adas is not None,
                'config_loaded': state.config_loader is not None,
                'websocket_enabled': True
            }
        }
        
        if state.enhanced_adas:
            info['adas_status'] = state.enhanced_adas.get_system_status()
        
        return jsonify({'status': 'success', 'info': info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# ============================================================================
# Initialization
# ============================================================================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    
    # Initialize Enhanced ADAS system
    init_enhanced_adas()
    
    logger.info("="*70)
    logger.info("Enhanced ADAS Web Application - Phase 5 (Modern Edition)")
    logger.info("="*70)
    logger.info("Open your browser and navigate to: http://localhost:5000")
    logger.info("WebSocket support enabled for real-time updates")
    logger.info("="*70)
    
    # Run Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
