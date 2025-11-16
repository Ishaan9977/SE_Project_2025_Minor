// ADAS Web Application JavaScript

let statusUpdateInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateStatusDisplay();
    startStatusUpdates();
});

function initializeEventListeners() {
    // Start webcam button
    document.getElementById('start-webcam').addEventListener('click', startWebcam);
    
    // Stop button
    document.getElementById('stop-btn').addEventListener('click', stopStreaming);
    
    // Video upload
    document.getElementById('video-upload').addEventListener('change', handleVideoUpload);
    
    // Apply settings button
    document.getElementById('apply-settings').addEventListener('click', applySettings);
    
    // Range input value displays
    setupRangeInputs();
}

function setupRangeInputs() {
    // Confidence threshold
    const confSlider = document.getElementById('conf-threshold');
    const confValue = document.getElementById('conf-value');
    confSlider.addEventListener('input', (e) => {
        confValue.textContent = parseFloat(e.target.value).toFixed(1);
    });
    
    // FCWS warning distance
    const fcwsWarning = document.getElementById('fcws-warning');
    const fcwsWarningValue = document.getElementById('fcws-warning-value');
    fcwsWarning.addEventListener('input', (e) => {
        fcwsWarningValue.textContent = e.target.value;
    });
    
    // FCWS critical distance
    const fcwsCritical = document.getElementById('fcws-critical');
    const fcwsCriticalValue = document.getElementById('fcws-critical-value');
    fcwsCritical.addEventListener('input', (e) => {
        fcwsCriticalValue.textContent = e.target.value;
    });
    
    // LDWS threshold
    const ldwsThreshold = document.getElementById('ldws-threshold');
    const ldwsThresholdValue = document.getElementById('ldws-threshold-value');
    ldwsThreshold.addEventListener('input', (e) => {
        ldwsThresholdValue.textContent = e.target.value;
    });
    
    // LKAS threshold
    const lkasThreshold = document.getElementById('lkas-threshold');
    const lkasThresholdValue = document.getElementById('lkas-threshold-value');
    lkasThreshold.addEventListener('input', (e) => {
        lkasThresholdValue.textContent = e.target.value;
    });
}

async function startWebcam() {
    try {
        const response = await fetch('/start_webcam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showVideoStream();
            showNotification('Webcam started successfully', 'success');
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('Error starting webcam: ' + error.message, 'error');
    }
}

async function handleVideoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        showNotification('Uploading video...', 'info');
        
        const response = await fetch('/start_video', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showVideoStream();
            showNotification('Video loaded successfully', 'success');
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('Error uploading video: ' + error.message, 'error');
    }
    
    // Reset file input
    event.target.value = '';
}

async function stopStreaming() {
    try {
        const response = await fetch('/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            hideVideoStream();
            showNotification('Streaming stopped', 'info');
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('Error stopping stream: ' + error.message, 'error');
    }
}

function showVideoStream() {
    const videoStream = document.getElementById('video-stream');
    const placeholder = document.getElementById('video-placeholder');
    
    videoStream.classList.add('active');
    placeholder.classList.add('hidden');
    
    // Force reload of video stream
    const src = videoStream.src;
    videoStream.src = '';
    setTimeout(() => {
        videoStream.src = src + '?t=' + new Date().getTime();
    }, 100);
}

function hideVideoStream() {
    const videoStream = document.getElementById('video-stream');
    const placeholder = document.getElementById('video-placeholder');
    
    videoStream.classList.remove('active');
    placeholder.classList.remove('hidden');
}

async function updateStatusDisplay() {
    try {
        const response = await fetch('/status');
        const status = await response.json();
        
        // Update processing status
        const processingStatus = document.getElementById('processing-status');
        if (status.processing) {
            processingStatus.textContent = 'Active';
            processingStatus.className = 'status-value active';
        } else {
            processingStatus.textContent = 'Inactive';
            processingStatus.className = 'status-value';
        }
        
        // Update FCWS status
        const fcwsStatus = document.getElementById('fcws-status');
        if (status.fcws_state) {
            fcwsStatus.textContent = status.fcws_state;
            if (status.fcws_state === 'SAFE') {
                fcwsStatus.className = 'status-value safe';
            } else if (status.fcws_state === 'WARNING') {
                fcwsStatus.className = 'status-value warning';
            } else if (status.fcws_state === 'CRITICAL') {
                fcwsStatus.className = 'status-value critical';
            }
        } else {
            fcwsStatus.textContent = '-';
            fcwsStatus.className = 'status-value';
        }
        
        // Update LDWS status
        const ldwsStatus = document.getElementById('ldws-status');
        if (status.ldws_state) {
            ldwsStatus.textContent = status.ldws_state;
            if (status.ldws_state === 'SAFE') {
                ldwsStatus.className = 'status-value safe';
            } else {
                ldwsStatus.className = 'status-value warning';
            }
        } else {
            ldwsStatus.textContent = '-';
            ldwsStatus.className = 'status-value';
        }
        
        // Update LKAS status
        const lkasStatus = document.getElementById('lkas-status');
        if (status.lkas_active !== undefined) {
            lkasStatus.textContent = status.lkas_active ? 'Active' : 'Standby';
            lkasStatus.className = status.lkas_active ? 'status-value active' : 'status-value';
        } else {
            lkasStatus.textContent = '-';
            lkasStatus.className = 'status-value';
        }
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

function startStatusUpdates() {
    // Update status every second
    statusUpdateInterval = setInterval(updateStatusDisplay, 1000);
}

function stopStatusUpdates() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
        statusUpdateInterval = null;
    }
}

async function applySettings() {
    const settings = {
        conf_threshold: parseFloat(document.getElementById('conf-threshold').value),
        fcws_warning_distance: parseFloat(document.getElementById('fcws-warning').value),
        fcws_critical_distance: parseFloat(document.getElementById('fcws-critical').value),
        ldws_threshold: parseFloat(document.getElementById('ldws-threshold').value),
        lkas_threshold: parseFloat(document.getElementById('lkas-threshold').value)
    };
    
    try {
        const response = await fetch('/update_settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Settings applied successfully', 'success');
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('Error applying settings: ' + error.message, 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    `;
    
    // Set background color based on type
    if (type === 'success') {
        notification.style.background = '#4CAF50';
    } else if (type === 'error') {
        notification.style.background = '#f44336';
    } else {
        notification.style.background = '#2196F3';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

