// Global state
let currentSteeringAngle = 0;
let currentLaneOffset = 0;
let isProcessing = false;

// Update metrics every 1.5 seconds
setInterval(updateMetrics, 1500);

async function updateMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();
        
        if (data.status === 'success') {
            const metrics = data.metrics;
            document.getElementById('metric-fps').textContent = metrics.fps.toFixed(2);
            document.getElementById('metric-frames').textContent = metrics.total_frames;
            document.getElementById('metric-warnings').textContent = metrics.warnings || 0;
            document.getElementById('metric-critical').textContent = metrics.critical_alerts || 0;
        }
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
    
    try {
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
                
                // Show steering overlay
                document.getElementById('steering-overlay').style.display = 'flex';
            } else {
                isProcessing = false;
                mainStatus.className = 'status-badge idle';
                mainStatus.innerHTML = '<span class="status-dot"></span><span>Ready</span>';
                streamIndicator.style.color = '#f59e0b';
                streamStatus.textContent = 'Idle';
                
                // Hide steering overlay
                document.getElementById('steering-overlay').style.display = 'none';
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
                
                // Debug logging (remove in production)
                if (lkasActive || Math.abs(lkasAngle) > 0.1) {
                    console.log('LKAS:', {active: lkasActive, angle: lkasAngle, offset: laneOffset});
                }
                
                updateLKAS(lkasActive, lkasAngle, laneOffset);
                updateSteeringWheel(lkasAngle);
            }
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

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
            steeringAngle.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        } else if (Math.abs(clampedAngle) > 10) {
            steeringAngle.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
        } else {
            steeringAngle.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    }
}



async function startWebcam() {
    showToast('info', 'Starting Webcam', 'Initializing camera...');
    
    try {
        const response = await fetch('/api/video/start_webcam', { method: 'POST' });
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
            showToast('success', 'Video Uploaded', `${data.filename} - ${data.frames} frames @ ${data.resolution}`);
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
        
        // Reset steering
        currentSteeringAngle = 0;
        currentLaneOffset = 0;
        updateSteeringWheel(0);
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

function showVideoStream() {
    document.getElementById('video-placeholder').style.display = 'none';
    const videoStream = document.getElementById('video-stream');
    videoStream.src = '/video_feed?t=' + new Date().getTime();
    videoStream.style.display = 'block';
}

function hideVideoStream() {
    document.getElementById('video-placeholder').style.display = 'flex';
    document.getElementById('video-stream').style.display = 'none';
}

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

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'w' || e.key === 'W') {
        startWebcam();
    } else if (e.key === 's' || e.key === 'S') {
        stopVideo();
    }
});

// Initial update
updateMetrics();

// Add smooth transitions for steering wheel
setInterval(() => {
    if (isProcessing) {
        // Add subtle random movement to make it feel more alive
        const randomJitter = (Math.random() - 0.5) * 2;
        const targetAngle = currentSteeringAngle + randomJitter;
        updateSteeringWheel(targetAngle);
    }
}, 100);
