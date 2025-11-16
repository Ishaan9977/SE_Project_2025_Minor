# Troubleshooting Guide - Phase 5 Web Interface

## Common Issues and Solutions

### Issue 1: Webcam Not Working

**Symptoms:**
- "Failed to open webcam" error
- Webcam button doesn't start streaming

**Solutions:**

1. **Check Camera Availability**
   - Ensure your camera is connected and not in use by another application
   - Close other applications using the camera (Zoom, Skype, etc.)
   - Try restarting your computer

2. **Check Camera Permissions**
   - Windows: Settings → Privacy & Security → Camera → Allow apps to access camera
   - Ensure Python/Flask has camera permissions

3. **Test Camera with OpenCV**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   if cap.isOpened():
       print("Camera works!")
       cap.release()
   else:
       print("Camera not available")
   ```

4. **Try Different Camera Index**
   - If you have multiple cameras, try index 1, 2, etc.
   - Edit enhanced_app.py and change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

---

### Issue 2: Video Upload Not Working

**Symptoms:**
- Upload button doesn't respond
- "Failed to save video file" error
- "Failed to open video file" error

**Solutions:**

1. **Check File Format**
   - Supported formats: MP4, AVI, MOV, MKV, WebM
   - Ensure file extension is correct
   - Try converting video to MP4 format

2. **Check File Size**
   - Maximum file size: 500MB
   - If file is larger, split it or compress it

3. **Check Uploads Folder**
   - Ensure `uploads/` directory exists and is writable
   - Check permissions: `ls -la uploads/`
   - If missing, create it: `mkdir uploads`

4. **Verify Video File**
   ```python
   import cv2
   cap = cv2.VideoCapture('path/to/video.mp4')
   if cap.isOpened():
       print("Video works!")
       cap.release()
   else:
       print("Video file is corrupted or unsupported")
   ```

5. **Check Browser Console**
   - Open browser DevTools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab to see API response

---

### Issue 3: Video Stream Not Displaying

**Symptoms:**
- Black screen in video area
- Video feed not updating

**Solutions:**

1. **Check if Processing is Active**
   - Look at status badge - should show "Webcam Active" or "Video Playing"
   - Check browser console for errors

2. **Restart the Application**
   ```bash
   # Stop the app (Ctrl+C)
   # Then restart
   python enhanced_app.py
   ```

3. **Check Flask Logs**
   - Look at terminal output for error messages
   - Check for "Error processing frame" messages

4. **Clear Browser Cache**
   - Press Ctrl+Shift+Delete
   - Clear cache and cookies
   - Refresh page

---

### Issue 4: Configuration Changes Not Applying

**Symptoms:**
- Toggling overlays doesn't change video
- Slider changes don't take effect

**Solutions:**

1. **Check Browser Console**
   - Open DevTools (F12)
   - Look for API errors in Console tab
   - Check Network tab for failed requests

2. **Verify API Endpoint**
   - Test manually: `curl http://localhost:5000/api/config`
   - Should return current configuration

3. **Restart Application**
   - Stop Flask app (Ctrl+C)
   - Restart: `python enhanced_app.py`

---

### Issue 5: Performance Issues (Low FPS)

**Symptoms:**
- FPS counter shows < 5 FPS
- Video is choppy or laggy

**Solutions:**

1. **Check System Resources**
   - Open Task Manager (Ctrl+Shift+Esc)
   - Check CPU and GPU usage
   - Close unnecessary applications

2. **Reduce Video Resolution**
   - Resize video before uploading
   - Use lower resolution webcam if available

3. **Disable Non-Critical Overlays**
   - Toggle off BEV (Bird's Eye View)
   - Disable animations
   - Disable distance markers

4. **Use Smaller YOLO Model**
   - Current: yolov8n (nano)
   - Already using smallest model
   - Consider reducing video resolution

---

### Issue 6: ADAS Processing Errors

**Symptoms:**
- "ADAS processing error" in logs
- Video shows but no overlays

**Solutions:**

1. **Check ADAS System Initialization**
   - Look for initialization errors in terminal
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **Verify Model Files**
   - YOLOv8 model should auto-download
   - Check if `yolov8n.pt` exists in current directory
   - If missing, it will download on first run

3. **Check Configuration File**
   - Ensure `config/adas_config.yaml` exists
   - Verify configuration is valid YAML

4. **Restart with Fresh Initialization**
   ```bash
   # Stop app
   # Delete any cached models
   # Restart
   python enhanced_app.py
   ```

---

### Issue 7: Port Already in Use

**Symptoms:**
- "Address already in use" error
- Cannot start Flask app

**Solutions:**

1. **Find Process Using Port 5000**
   ```bash
   # Windows
   netstat -ano | findstr :5000
   
   # Get the PID and kill it
   taskkill /PID <PID> /F
   ```

2. **Use Different Port**
   - Edit enhanced_app.py
   - Change `app.run(port=5000)` to `app.run(port=5001)`

3. **Wait and Retry**
   - Sometimes port takes time to release
   - Wait 30 seconds and try again

---

### Issue 8: Browser Connection Issues

**Symptoms:**
- "Cannot connect to localhost:5000"
- Connection refused error

**Solutions:**

1. **Verify Flask is Running**
   - Check terminal for "Running on http://0.0.0.0:5000"
   - If not running, start it: `python enhanced_app.py`

2. **Try Different URL**
   - Instead of localhost: `http://127.0.0.1:5000`
   - Or use machine IP: `http://<your-ip>:5000`

3. **Check Firewall**
   - Windows Firewall may block port 5000
   - Add Flask to firewall exceptions
   - Or temporarily disable firewall for testing

4. **Try Different Browser**
   - Try Chrome, Firefox, or Edge
   - Clear browser cache

---

## Debug Mode

### Enable Verbose Logging

Edit enhanced_app.py and change:
```python
logging.basicConfig(level=logging.INFO)
```

To:
```python
logging.basicConfig(level=logging.DEBUG)
```

Then restart the app to see detailed logs.

---

## Quick Checklist

Before troubleshooting, verify:

- [ ] Flask app is running (`python enhanced_app.py`)
- [ ] Browser can access `http://localhost:5000`
- [ ] Camera is connected and not in use
- [ ] Video file is in supported format (MP4, AVI, MOV, MKV, WebM)
- [ ] `uploads/` directory exists
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] No other app using port 5000
- [ ] Browser console shows no JavaScript errors (F12)

---

## Getting Help

If issues persist:

1. Check the terminal output for error messages
2. Open browser DevTools (F12) and check Console tab
3. Check Network tab to see API responses
4. Try the test commands above to isolate the issue
5. Restart both Flask app and browser

---

## Performance Tips

- Use MP4 format for videos (best compatibility)
- Keep video resolution reasonable (1920x1080 or lower)
- Close other applications to free up resources
- Disable BEV and animations if FPS is low
- Use GPU if available (CUDA)

---

**Last Updated**: 2025-11-16
**Version**: 1.0.0
