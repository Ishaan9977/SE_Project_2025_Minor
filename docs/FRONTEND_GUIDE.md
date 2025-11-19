# Frontend Components - Complete Guide

## 9. FRONTEND COMPONENTS

### 9.1 templates/dashboard.html - Main UI

**Purpose**: User interface for ADAS dashboard

**Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta tags, title, CSS links -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='dashboard.css') }}">
</head>
<body>
    <!-- Animated Background -->
    <div class="bg-animation">
        <!-- Floating particles -->
    </div>
    
    <div class="dashboard-container">
        <!-- Header -->
        <div class="header">
            <div class="header-left">
                <h1><i class="fas fa-car"></i> ADAS Enhanced Dashboard</h1>
                <p>Advanced Driver Assistance System - Real-time Monitoring</p>
            </div>
            <div class="header-right">
                <div class="status-badge idle" id="main-status">
                    <span class="status-dot"></span>
                    <span>Ready</span>
                </div>
            </div>
        </div>
        
        <!-- Main Grid -->
        <div class="main-grid">
            <!-- Video Section -->
            <div class="video-section">
                <!-- Video Status Bar -->
                <div class="video-status-bar">
                    <i class="fas fa-circle" id="stream-indicator"></i>
                    <span id="stream-status">Idle</span>
                </div>
                
                <!-- Video Container -->
                <div class="video-container">
                    <!-- Placeholder -->
                    <div class="video-placeholder" id="video-placeholder">
                        <i class="fas fa-video"></i>
                        <h3>No Active Stream</h3>
                        <p>Start webcam or upload a video to begin processing</p>
                    </div>
                    
                    <!-- Video Stream -->
                    <img id="video-stream" class="video-stream" 
                         src="/video_feed" style="display: none;">
                    
                    <!-- Steering Wheel Overlay (Top-Right) -->
                    <div class="steering-overlay-top" id="steering-overlay" 
                         style="display: none;">
                        <img src="{{ url_for('static', filename='assets/steering_wheel.png') }}" 
                             class="steering-wheel" id="steering-wheel">
                        <div class="steering-angle" id="steering-angle">0°</div>
                    </div>
                    
                    <!-- Directional Indicators -->
                    <div class="direction-indicators" id="direction-indicators" 
                         style="display: none;">
                        <div class="direction-arrow left-arrow" id="left-arrow">
                            <i class="fas fa-arrow-left"></i>
                            <span>Turn Left</span>
                        </div>
                        <div class="direction-arrow right-arrow" id="right-arrow">
                            <i class="fas fa-arrow-right"></i>
                            <span>Turn Right</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Control Panel -->
            <div class="control-panel">
                <!-- Video Controls Card -->
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-video"></i>
                        Video Controls
                    </div>
                    <button class="btn-custom btn-primary-custom" 
                            onclick="startWebcam()">
                        <i class="fas fa-camera"></i>
                        <span>Start Webcam</span>
                    </button>
                    <button class="btn-custom btn-success-custom" 
                            onclick="document.getElementById('videoUpload').click()">
                        <i class="fas fa-upload"></i>
                        <span>Upload Video</span>
                    </button>
                    <input type="file" id="videoUpload" accept="video/*" 
                           style="display: none;" onchange="uploadVideo(this)">
                    <button class="btn-custom btn-danger-custom" 
                            onclick="stopVideo()">
                        <i class="fas fa-stop"></i>
                        <span>Stop Stream</span>
                    </button>
                </div>
                
                <!-- Performance Metrics Card -->
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-chart-line"></i>
                        Performance Metrics
                    </div>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-tachometer-alt"></i></div>
                            <div class="metric-label">FPS</div>
                            <div class="metric-value" id="metric-fps">0.00</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-film"></i></div>
                            <div class="metric-label">Frames</div>
                            <div class="metric-value" id="metric-frames">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>
                            <div class="metric-label">Warnings</div>
                            <div class="metric-value" id="metric-warnings">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-bell"></i></div>
                            <div class="metric-label">Critical</div>
                            <div class="metric-value" id="metric-critical">0</div>
                        </div>
                    </div>
                </div>
                
                <!-- LKAS Card -->
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-compass"></i>
                        Lane Keeping Assistance
                    </div>
                    <div class="lkas-display">
                        <div class="lkas-wheel-container">
                            <img src="{{ url_for('static', filename='assets/steering_wheel.png') }}" 
                                 class="lkas-wheel" id="lkas-wheel">
                            <div class="lkas-status" id="lkas-status">INACTIVE</div>
                        </div>
                        <div class="lkas-info">
                            <div class="lkas-info-item">
                                <span class="lkas-label">Steering Angle:</span>
                                <span class="lkas-value" id="lkas-angle-value">0°</span>
                            </div>
                            <div class="lkas-info-item">
                                <span class="lkas-label">Lane Offset:</span>
                                <span class="lkas-value" id="lkas-offset-value">0 px</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- System Status Card -->
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-shield-alt"></i>
                        System Status
                    </div>
                    <div class="status-grid">
                        <div class="status-item">
                            <span class="status-label">
                                <i class="fas fa-car-crash"></i> FCWS
                            </span>
                            <span class="status-value status-inactive" 
                                  id="status-fcws">INACTIVE</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">
                                <i class="fas fa-road"></i> LDWS
                            </span>
                            <span class="status-value status-inactive" 
                                  id="status-ldws">INACTIVE</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">
                                <i class="fas fa-steering-wheel"></i> LKAS
                            </span>
                            <span class="status-value status-inactive" 
                                  id="status-lkas">INACTIVE</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Toast Container -->
    <div class="toast-container" id="toast-container"></div>
    
    <!-- JavaScript -->
    <script src="{{ url_for('static', filename='dashboard.js') }}"></script>
</body>
</html>
```

---

### 9.2 static/dashboard.js - Interactive Logic

**Purpose**: Handle user interactions and update UI

**Key Functions**:

**1. Update Metrics (Polling)**:
```javascript
// Update metrics every 1.5 seconds
setInterval(updateMetrics, 1500);

async function updateMetrics() {
    try {
        // Fetch metrics from API
        const response = await fetch('/api/metrics');
        const data = await response.json();
        
        if (data.status === 'success') {
            const metrics = data.metrics;
            
            // Update metric displays
            document.getElementById('metric-fps').textContent = 
                metrics.fps.toFixed(2);
            document.getElementById('metric-frames').textContent = 
                metrics.total_frames;
            document.getElementById('metric-warnings').textContent = 
                metrics.warnings || 0;
            document.getElementById('metric-critical').textContent = 
                metrics.critical_alerts || 0;
        }
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
    
    try {
        // Fetch system status
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'success') {
            const statusData = data.data;
            const source = statusData.processing_stats.source;
            
            // Update main status badge
            const mainStatus = document.getElementById('main-status');
            const streamIndicator = document.getElementById('stream-indicator');
            const streamStatus = document.getElementById('stream-status');
            
            if (statusData.processing) {
                isProcessing = true;
                mainStatus.className = 'status-badge active';
                mainStatus.innerHTML = '<span class="status-dot"></span><span>Active</span>';
                streamIndicator.style.color = '#10b981';
                streamStatus.textContent = source;
                
                // Show steering overlay and direction indicators
                document.getElementById('steering-overlay').style.display = 'flex';
                document.getElementById('direction-indicators').style.display = 'block';
            } else {
                isProcessing = false;
                mainStatus.className = 'status-badge idle';
                mainStatus.innerHTML = '<span class="status-dot"></span><span>Ready</span>';
                streamIndicator.style.color = '#f59e0b';
                streamStatus.textContent = 'Idle';
                
                // Hide overlays
                document.getElementById('steering-overlay').style.display = 'none';
                document.getElementById('direction-indicators').style.display = 'none';
            }
            
            // Update system status
            if (statusData.system) {
                // FCWS status
                const fcwsState = statusData.system.fcws?.warning_state || 'SAFE';
                updateSystemStatus('fcws', fcwsState);
                
                // LDWS status
                const ldwsState = statusData.system.ldws?.state || 'SAFE';
                updateSystemStatus('ldws', ldwsState);
                
                // LKAS with steering angle
                const lkasActive = statusData.system.lkas?.active || false;
                const lkasAngle = statusData.system.lkas?.steering_angle || 0;
                const laneOffset = statusData.system.ldws?.lane_offset || 0;
                
                // Debug logging
                if (lkasActive || Math.abs(lkasAngle) > 0.1) {
                    console.log('LKAS:', {
                        active: lkasActive, 
                        angle: lkasAngle, 
                        offset: laneOffset
                    });
                }
                
                updateLKAS(lkasActive, lkasAngle, laneOffset);
                updateSteeringWheel(lkasAngle);
                updateDirectionalIndicators(ldwsState, laneOffset);
            }
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}
```

**2. Update System Status**:
```javascript
function updateSystemStatus(system, state) {
    const element = document.getElementById(`status-${system}`);
    if (!element) return;
    
    element.textContent = state;
    element.className = 'status-value';
    
    if (state === 'SAFE' || state === 'INACTIVE') {
        element.classList.add('status-inactive');
    } else if (state === 'WARNING' || state === 'ACTIVE') {
        element.classList.add('status-warning');
    } else if (state === 'CRITICAL') {
        element.classList.add('status-critical');
    } else {
        element.classList.add('status-inactive');
    }
}
```

**3. Update LKAS Display**:
```javascript
function updateLKAS(active, angle, offset) {
    const lkasStatus = document.getElementById('lkas-status');
    const lkasWheel = document.getElementById('lkas-wheel');
    const lkasAngleValue = document.getElementById('lkas-angle-value');
    const lkasOffsetValue = document.getElementById('lkas-offset-value');
    
    if (active) {
        lkasStatus.textContent = 'ACTIVE';
        lkasStatus.classList.add('active');
        updateSystemStatus('lkas', 'ACTIVE');
    } else {
        lkasStatus.textContent = 'INACTIVE';
        lkasStatus.classList.remove('active');
        updateSystemStatus('lkas', 'INACTIVE');
    }
    
    // Update steering wheel rotation
    lkasWheel.style.transform = `rotate(${angle}deg)`;
    
    // Update values
    lkasAngleValue.textContent = `${angle.toFixed(1)}°`;
    lkasOffsetValue.textContent = `${offset.toFixed(0)} px`;
    
    currentSteeringAngle = angle;
    currentLaneOffset = offset;
}
```

**4. Update Steering Wheel**:
```javascript
function updateSteeringWheel(angle) {
    const steeringWheel = document.getElementById('steering-wheel');
    const steeringAngle = document.getElementById('steering-angle');
    
    if (steeringWheel && steeringAngle) {
        // Clamp angle to reasonable range (-45 to +45 degrees)
        const clampedAngle = Math.max(-45, Math.min(45, angle));
        
        steeringWheel.style.transform = `rotate(${clampedAngle}deg)`;
        steeringAngle.textContent = `${clampedAngle.toFixed(1)}°`;
        
        // Add color coding based on angle
        if (Math.abs(clampedAngle) > 20) {
            steeringAngle.style.background = 
                'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        } else if (Math.abs(clampedAngle) > 10) {
            steeringAngle.style.background = 
                'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
        } else {
            steeringAngle.style.background = 
                'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    }
}
```

**5. Update Directional Indicators**:
```javascript
function updateDirectionalIndicators(ldwsState, offset) {
    const leftArrow = document.getElementById('left-arrow');
    const rightArrow = document.getElementById('right-arrow');
    
    // Reset all arrows
    leftArrow.classList.remove('active');
    rightArrow.classList.remove('active');
    
    if (!isProcessing) return;
    
    // Show appropriate arrow based on LDWS state and offset
    if (ldwsState === 'LEFT_WARNING' || (ldwsState === 'WARNING' && offset > 20)) {
        // Drifting right, show left arrow (correction needed)
        leftArrow.classList.add('active');
    } else if (ldwsState === 'RIGHT_WARNING' || (ldwsState === 'WARNING' && offset < -20)) {
        // Drifting left, show right arrow (correction needed)
        rightArrow.classList.add('active');
    }
    // If SAFE, no arrows shown
}
```

**6. Video Control Functions**:
```javascript
async function startWebcam() {
    showToast('info', 'Starting Webcam', 'Initializing camera...');
    
    try {
        const response = await fetch('/api/video/start_webcam', { 
            method: 'POST' 
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('success', 'Webcam Started', 'Camera is now active');
            showVideoStream();
        } else {
            showToast('error', 'Webcam Error', data.message);
        }
    } catch (error) {
        showToast('error', 'Network Error', error.message);
    }
}

async function uploadVideo(input) {
    const file = input.files[0];
    if (!file) return;
    
    showToast('info', 'Uploading Video', `Processing ${file.name}...`);
    
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        const response = await fetch('/api/video/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('success', 'Video Uploaded', 
                     `${data.filename} - ${data.frames} frames @ ${data.resolution}`);
            showVideoStream();
        } else {
            showToast('error', 'Upload Error', data.message);
        }
    } catch (error) {
        showToast('error', 'Network Error', error.message);
    }
    
    input.value = '';
}

async function stopVideo() {
    try {
        const response = await fetch('/api/video/stop', { method: 'POST' });
        const data = await response.json();
        showToast('success', 'Stream Stopped', data.message);
        hideVideoStream();
        
        // Reset steering and indicators
        currentSteeringAngle = 0;
        currentLaneOffset = 0;
        updateSteeringWheel(0);
        updateDirectionalIndicators('INACTIVE', 0);
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}
```

**7. Toast Notifications**:
```javascript
function showToast(type, title, message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast-custom';
    
    const icons = {
        success: '<i class="fas fa-check-circle toast-icon" style="color: #10b981;"></i>',
        error: '<i class="fas fa-times-circle toast-icon" style="color: #ef4444;"></i>',
        warning: '<i class="fas fa-exclamation-triangle toast-icon" style="color: #f59e0b;"></i>',
        info: '<i class="fas fa-info-circle toast-icon" style="color: #3b82f6;"></i>'
    };
    
    toast.innerHTML = `
        ${icons[type] || icons.info}
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.4s ease-out reverse';
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}
```

**8. Keyboard Shortcuts**:
```javascript
// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'w' || e.key === 'W') {
        startWebcam();
    } else if (e.key === 's' || e.key === 'S') {
        stopVideo();
    }
});
```

---

### 9.3 static/dashboard.css - Styling

**Key Styles**:

**1. Background**:
```css
body {
    background: url('assets/background.jpg') center center / cover no-repeat fixed;
    min-height: 100vh;
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow-x: hidden;
    position: relative;
}

body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.15);
    z-index: 0;
}
```

**2. Steering Wheel (Top-Right)**:
```css
.steering-overlay-top {
    position: absolute;
    top: 15px;
    right: 15px;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    z-index: 10;
    animation: slideInFromTop 0.5s ease-out;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.5);
}

.steering-wheel {
    width: 120px;
    height: 120px;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    filter: drop-shadow(0 5px 20px rgba(255, 255, 255, 0.4));
}

.steering-angle {
    color: white;
    font-weight: 700;
    font-size: 20px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 8px 16px;
    border-radius: 20px;
    min-width: 60px;
    text-align: center;
}
```

**3. Directional Arrows**:
```css
.direction-arrow {
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(10px);
    padding: 20px 30px;
    border-radius: 15px;
    opacity: 0;
    transition: opacity 0.3s ease, transform 0.3s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.direction-arrow i {
    font-size: 48px;
    color: #fff;
}

.direction-arrow span {
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.left-arrow.active {
    opacity: 1;
    animation: pulseLeft 1.5s ease-in-out infinite;
}

.right-arrow.active {
    opacity: 1;
    animation: pulseRight 1.5s ease-in-out infinite;
}

@keyframes pulseLeft {
    0%, 100% { 
        transform: translateX(0) scale(1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    50% { 
        transform: translateX(-10px) scale(1.05);
        box-shadow: 0 15px 40px rgba(255, 193, 7, 0.6);
    }
}
```

---

## Summary

The frontend consists of:
1. **HTML** - Structure and layout
2. **CSS** - Styling and animations
3. **JavaScript** - Interactivity and API communication

Key features:
- Real-time metric updates (polling every 1.5s)
- Animated steering wheel (rotates with LKAS angle)
- Directional arrows (show when lane departure detected)
- Toast notifications (user feedback)
- Responsive design (works on all devices)
- Keyboard shortcuts (W = webcam, S = stop)

All components work together to create a professional, interactive ADAS dashboard!
