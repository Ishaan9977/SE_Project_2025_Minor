# Flask App Troubleshooting Guide

**Issue:** Black screen on video display

---

## Quick Fix Steps

### Step 1: Make Sure App is Running

```bash
python simple_app.py
```

You should see:
```
Simple ADAS Web Application - No WebSocket Required
Open your browser and navigate to: http://localhost:5000
```

### Step 2: Open Browser

Navigate to: **http://localhost:5000**

### Step 3: Start a Video Source

**The video feed will be black until you start a source!**

Click one of these buttons:
- **"Start Webcam"** - to use your webcam
- **"Upload Video"** - to upload a video file

### Step 4: Check for Success Message

You should see a green success message:
- "Webcam started successfully!" OR
- "Video uploaded and started: filename.mp4"

### Step 5: Video Should Appear

The black screen should be replaced with live video feed.

---

## Common Issues

### Issue 1: Black Screen (No Video Source)

**Symptom:** Black screen with no video

**Cause:** No video source has been started

**Solution:**
1. Click "Start Webcam" or "Upload Video"
2. Wait for success message
3. Video should appear

---

### Issue 2: Webcam Not Working

**Symptom:** Error message "Failed to open webcam"

**Possible Causes:**
- Webcam not connected
- Webcam in use by another app
- Permission denied

**Solutions:**

**A. Check if webcam is connected**
```bash
# Windows - check Device Manager
# Look for "Cameras" or "Imaging devices"
```

**B. Close other apps using webcam**
- Close Zoom, Skype, Teams, etc.
- Close other browser tabs with webcam access

**C. Check browser permissions**
- Browser may block webcam access
- Check browser settings for camera permissions

**D. Try different webcam index**
Edit `simple_app.py`, line ~170:
```python
# Change from:
video_capture = cv2.VideoCapture(0)

# To:
video_capture = cv2.VideoCapture(1)  # or 2, 3, etc.
```

---

### Issue 3: Video Upload Not Working

**Symptom:** Error message "Failed to open video file"

**Possible Causes:**
- Unsupported video format
- Corrupted video file
- File too large

**Solutions:**

**A. Check video format**
Supported formats: mp4, avi, mov, mkv, webm

**B. Try a different video**
Use `test_video.mp4` from the project

**C. Check file size**
Maximum: 500MB (configurable in `simple_app.py`)

**D. Convert video format**
```bash
# Using ffmpeg
ffmpeg -i input.mov -c:v libx264 output.mp4
```

---

### Issue 4: Video Feed Shows But No Processing

**Symptom:** Video shows but no ADAS overlays

**Cause:** ADAS system not initialized or error in processing

**Solution:**

**A. Check console logs**
Look at terminal where `simple_app.py` is running for errors

**B. Restart the app**
```bash
# Stop with Ctrl+C
# Start again
python simple_app.py
```

**C. Check ADAS initialization**
You should see in terminal:
```
Initializing Enhanced ADAS System...
Enhanced ADAS System initialized!
```

---

### Issue 5: Low FPS / Slow Processing

**Symptom:** Video is very slow or choppy

**Cause:** CPU processing is slow

**Solutions:**

**A. Reduce video resolution**
Edit `simple_app.py`, line ~173:
```python
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Lower resolution
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

**B. Use smaller video files**
Process shorter or lower resolution videos

**C. Expected performance**
- CPU: 7-10 FPS (normal)
- GPU: 25-30 FPS (if available)

---

### Issue 6: App Won't Start

**Symptom:** Error when running `python simple_app.py`

**Possible Errors:**

**A. "ModuleNotFoundError: No module named 'flask'"**
```bash
pip install flask
```

**B. "ModuleNotFoundError: No module named 'cv2'"**
```bash
pip install opencv-python
```

**C. "Port 5000 already in use"**
```bash
# Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in simple_app.py:
app.run(host='0.0.0.0', port=8080)
```

---

### Issue 7: Browser Shows "Cannot GET /"

**Symptom:** Browser shows error page

**Cause:** App not running or wrong URL

**Solution:**
1. Make sure app is running: `python simple_app.py`
2. Use correct URL: `http://localhost:5000`
3. Check terminal for errors

---

### Issue 8: Video Feed URL Shows Raw Data

**Symptom:** Browser downloads file or shows binary data

**Cause:** Accessing `/video_feed` directly

**Solution:**
- Don't access `/video_feed` directly
- Use the dashboard at `http://localhost:5000`
- The dashboard embeds the video feed correctly

---

## Testing Checklist

Use this checklist to verify everything is working:

- [ ] App starts without errors
- [ ] Browser opens to `http://localhost:5000`
- [ ] Dashboard loads with controls
- [ ] Placeholder shows "No Video Source"
- [ ] "Start Webcam" button works
- [ ] Webcam video appears with overlays
- [ ] "Stop" button stops video
- [ ] "Upload Video" button opens file dialog
- [ ] Video file uploads successfully
- [ ] Uploaded video plays with overlays
- [ ] Metrics update (FPS, frames, etc.)
- [ ] Status shows current source

---

## Quick Test Script

Run this to test if app is working:

```bash
python test_flask_app.py
```

This will check:
- App is running
- Endpoints are accessible
- ADAS is initialized

---

## Debug Mode

To see more detailed logs, edit `simple_app.py`:

```python
# Change from:
app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# To:
app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
```

**Warning:** Debug mode will reload app on code changes

---

## Browser Console

Check browser console for JavaScript errors:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors in red
4. Common errors:
   - Network errors (check if app is running)
   - CORS errors (shouldn't happen with this setup)
   - 404 errors (check file paths)

---

## Still Not Working?

### Collect Information

1. **Terminal output** - Copy error messages
2. **Browser console** - Copy JavaScript errors
3. **Python version** - Run `python --version`
4. **OpenCV version** - Run `python -c "import cv2; print(cv2.__version__)"`
5. **Flask version** - Run `python -c "import flask; print(flask.__version__)"`

### Try Minimal Test

Create `minimal_test.py`:
```python
import cv2
from flask import Flask, Response

app = Flask(__name__)

def generate():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return '<img src="/video">'

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(port=5001)
```

Run: `python minimal_test.py`
Open: `http://localhost:5001`

If this works, the issue is with ADAS processing.
If this doesn't work, the issue is with webcam/Flask setup.

---

## Contact Information

If you're still having issues, provide:
1. Error messages from terminal
2. Browser console errors
3. Python version
4. Operating system
5. What you've tried from this guide

---

**Last Updated:** November 16, 2025  
**App Version:** simple_app.py v1.0

