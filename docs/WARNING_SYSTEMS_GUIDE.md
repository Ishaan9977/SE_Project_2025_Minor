# Warning Systems - Complete Guide

## 3. WARNING SYSTEMS

### 3.1 fcws.py - Forward Collision Warning System

**Purpose**: Detect collision risks and warn driver

**Algorithm**:
1. Filter detections in forward path (center region)
2. Calculate distance to each object
3. Sort by proximity
4. Determine warning level based on distance
5. Display appropriate warning

**Key Code**:
```python
class FCWS:
    """Forward Collision Warning System"""
    
    def __init__(self, warning_distance=150.0, critical_distance=80.0):
        """
        Initialize FCWS
        
        Args:
            warning_distance: Distance threshold for warning (pixels)
            critical_distance: Distance threshold for critical alert (pixels)
        """
        self.warning_distance = warning_distance
        self.critical_distance = critical_distance
        self.warning_state = "SAFE"  # SAFE, WARNING, CRITICAL
    
    def check_collision_risk(self, detections: List[Dict], 
                            frame_height: int) -> Tuple[str, List[Dict]]:
        """
        Check for collision risk
        
        Returns:
            (warning_state, risky_detections)
        """
        if not detections:
            self.warning_state = "SAFE"
            return self.warning_state, []
        
        # Filter detections in forward path (center 60% of frame)
        risky_detections = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            center_x = (x1 + x2) / 2
            
            # Check if in forward path
            if 0.2 < center_x / frame_height < 0.8:
                # Calculate distance (based on bbox bottom position)
                distance = self.calculate_distance(det, frame_height)
                det['distance'] = distance
                risky_detections.append(det)
        
        # Sort by distance (closest first)
        risky_detections.sort(key=lambda x: x['distance'])
        
        # Determine warning state
        if not risky_detections:
            self.warning_state = "SAFE"
        else:
            closest_distance = risky_detections[0]['distance']
            
            if closest_distance < self.critical_distance:
                self.warning_state = "CRITICAL"
            elif closest_distance < self.warning_distance:
                self.warning_state = "WARNING"
            else:
                self.warning_state = "SAFE"
        
        return self.warning_state, risky_detections
    
    def calculate_distance(self, detection: Dict, 
                          frame_height: int) -> float:
        """
        Calculate distance to object (simplified)
        
        Uses inverse relationship: closer objects appear lower in frame
        """
        x1, y1, x2, y2 = detection['bbox']
        
        # Distance based on bottom of bounding box
        # Objects at bottom of frame are closer
        distance = frame_height - y2
        
        return distance
    
    def draw_warning(self, frame: np.ndarray, 
                    risky_detections: List[Dict]) -> np.ndarray:
        """Draw collision warnings"""
        height, width = frame.shape[:2]
        
        # Draw warning overlay based on state
        if self.warning_state == "CRITICAL":
            # Red overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, height), 
                         (0, 0, 255), -1)
            frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
            
            # Critical text
            text = "CRITICAL: COLLISION IMMINENT!"
            font_scale = 1.5
            thickness = 3
            color = (255, 255, 255)
            
            (text_w, text_h), _ = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
            )
            text_x = (width - text_w) // 2
            text_y = 100
            
            cv2.putText(frame, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            
        elif self.warning_state == "WARNING":
            # Yellow warning text
            text = "WARNING: Vehicle Ahead"
            font_scale = 1.0
            thickness = 2
            color = (0, 255, 255)
            
            (text_w, text_h), _ = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
            )
            text_x = (width - text_w) // 2
            text_y = 80
            
            cv2.putText(frame, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        
        # Draw distance for risky detections
        for det in risky_detections[:3]:  # Show top 3
            x1, y1, x2, y2 = det['bbox']
            distance = det['distance']
            
            # Distance text
            dist_text = f"{distance:.0f}px"
            cv2.putText(frame, dist_text, (x1, y2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame
```

---

### 3.2 enhanced_fcws.py - Enhanced FCWS with Distance Estimation

**Purpose**: FCWS with real-world distance estimation

**Key Code**:
```python
class EnhancedFCWS(FCWS):
    """Enhanced FCWS with distance estimation"""
    
    def __init__(self, warning_distance=30.0, critical_distance=15.0,
                 distance_estimator=None):
        """
        Initialize Enhanced FCWS
        
        Args:
            warning_distance: Warning threshold in meters
            critical_distance: Critical threshold in meters
            distance_estimator: DistanceEstimator instance
        """
        super().__init__(warning_distance, critical_distance)
        self.distance_estimator = distance_estimator
        
        # Statistics
        self.statistics = {
            'total_warnings': 0,
            'critical_alerts': 0,
            'safe_frames': 0
        }
    
    def check_collision_risk(self, detections: List[Dict],
                            frame_height: int) -> Tuple[str, List[Dict]]:
        """Enhanced collision risk check with distance estimation"""
        
        if not detections:
            self.warning_state = "SAFE"
            self.statistics['safe_frames'] += 1
            return self.warning_state, []
        
        # Filter forward path detections
        risky_detections = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            center_x = (x1 + x2) / 2
            
            if 0.2 < center_x / frame_height < 0.8:
                # Estimate distance
                if self.distance_estimator:
                    dist_info = self.distance_estimator.estimate_distance(
                        det['bbox'], frame_height, det['class']
                    )
                    det['distance_meters'] = dist_info['distance_meters']
                    det['distance_pixels'] = dist_info['distance_pixels']
                    det['distance_confidence'] = dist_info['confidence']
                else:
                    # Fallback to pixel distance
                    det['distance_meters'] = None
                    det['distance_pixels'] = frame_height - y2
                
                risky_detections.append(det)
        
        # Sort by distance
        if risky_detections:
            if risky_detections[0].get('distance_meters'):
                risky_detections.sort(key=lambda x: x['distance_meters'])
            else:
                risky_detections.sort(key=lambda x: x['distance_pixels'])
        
        # Determine warning state
        if not risky_detections:
            self.warning_state = "SAFE"
            self.statistics['safe_frames'] += 1
        else:
            # Use meters if available, else pixels
            if risky_detections[0].get('distance_meters'):
                closest = risky_detections[0]['distance_meters']
                warning_thresh = self.warning_distance
                critical_thresh = self.critical_distance
            else:
                closest = risky_detections[0]['distance_pixels']
                warning_thresh = 150.0
                critical_thresh = 80.0
            
            if closest < critical_thresh:
                self.warning_state = "CRITICAL"
                self.statistics['critical_alerts'] += 1
            elif closest < warning_thresh:
                self.warning_state = "WARNING"
                self.statistics['total_warnings'] += 1
            else:
                self.warning_state = "SAFE"
                self.statistics['safe_frames'] += 1
        
        return self.warning_state, risky_detections
    
    def get_statistics(self) -> Dict:
        """Get warning statistics"""
        total = sum(self.statistics.values())
        return {
            **self.statistics,
            'warning_rate': self.statistics['total_warnings'] / max(1, total),
            'critical_rate': self.statistics['critical_alerts'] / max(1, total),
            'safe_rate': self.statistics['safe_frames'] / max(1, total)
        }
```

---

### 3.3 ldws.py - Lane Departure Warning System

**Purpose**: Warn when vehicle departs from lane

**Key Code**:
```python
class LDWS:
    """Lane Departure Warning System"""
    
    def __init__(self, departure_threshold=30.0):
        """
        Initialize LDWS
        
        Args:
            departure_threshold: Offset threshold for warning (pixels)
        """
        self.departure_threshold = departure_threshold
        self.warning_state = "SAFE"  # SAFE, LEFT_WARNING, RIGHT_WARNING
        self.departure_count = 0
    
    def check_lane_departure(self, lane_center: Optional[float],
                            vehicle_offset: Optional[float],
                            frame_width: int) -> str:
        """
        Check for lane departure
        
        Args:
            lane_center: X coordinate of lane center
            vehicle_offset: Offset from lane center (+ = right, - = left)
            frame_width: Frame width
        
        Returns:
            Warning state string
        """
        if lane_center is None or vehicle_offset is None:
            self.warning_state = "SAFE"
            self.departure_count = 0
            return self.warning_state
        
        # Check for departure
        if vehicle_offset > self.departure_threshold:
            # Departing right
            self.warning_state = "RIGHT_WARNING"
            self.departure_count += 1
        elif vehicle_offset < -self.departure_threshold:
            # Departing left
            self.warning_state = "LEFT_WARNING"
            self.departure_count += 1
        else:
            # Centered
            self.warning_state = "SAFE"
            self.departure_count = 0
        
        return self.warning_state
    
    def draw_warning(self, frame: np.ndarray,
                    lane_center: Optional[float],
                    vehicle_offset: Optional[float]) -> np.ndarray:
        """Draw lane departure warnings"""
        height, width = frame.shape[:2]
        
        if self.warning_state == "LEFT_WARNING":
            # Draw left warning
            text = "LANE DEPARTURE: LEFT"
            color = (0, 255, 255)  # Yellow
            
            # Arrow pointing right (correction direction)
            arrow_start = (width // 4, height // 2)
            arrow_end = (width // 4 + 100, height // 2)
            cv2.arrowedLine(frame, arrow_start, arrow_end, color, 5, 
                           tipLength=0.3)
            
        elif self.warning_state == "RIGHT_WARNING":
            # Draw right warning
            text = "LANE DEPARTURE: RIGHT"
            color = (0, 255, 255)  # Yellow
            
            # Arrow pointing left (correction direction)
            arrow_start = (3 * width // 4, height // 2)
            arrow_end = (3 * width // 4 - 100, height // 2)
            cv2.arrowedLine(frame, arrow_start, arrow_end, color, 5,
                           tipLength=0.3)
        else:
            return frame
        
        # Draw warning text
        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2
        )
        text_x = (width - text_w) // 2
        text_y = 50
        
        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        # Draw lane center line
        if lane_center is not None:
            cv2.line(frame, (int(lane_center), 0),
                    (int(lane_center), height), (0, 255, 0), 2)
        
        # Draw vehicle center line
        vehicle_center = width // 2
        cv2.line(frame, (vehicle_center, 0),
                (vehicle_center, height), (255, 0, 0), 2)
        
        return frame
```

---

### 3.4 lkas.py - Lane Keeping Assistance System

**Purpose**: Provide steering guidance to maintain lane position

**Key Code**:
```python
class LKAS:
    """Lane Keeping Assistance System"""
    
    def __init__(self, assist_threshold=20.0):
        """
        Initialize LKAS
        
        Args:
            assist_threshold: Offset threshold to activate assistance (pixels)
        """
        self.assist_threshold = assist_threshold
        self.steering_angle = 0.0  # Calculated steering angle (degrees)
        self.assist_active = False
    
    def calculate_steering_angle(self, lane_center: Optional[float],
                                 vehicle_offset: Optional[float],
                                 frame_width: int) -> float:
        """
        Calculate recommended steering angle
        
        Args:
            lane_center: X coordinate of lane center
            vehicle_offset: Offset from lane center
            frame_width: Frame width
        
        Returns:
            Steering angle in degrees (- = left, + = right)
        """
        if lane_center is None or vehicle_offset is None:
            self.assist_active = False
            self.steering_angle = 0.0
            return self.steering_angle
        
        # Check if assistance needed
        if abs(vehicle_offset) > self.assist_threshold:
            self.assist_active = True
            
            # Calculate steering angle
            # Normalize offset to frame width and convert to angle
            normalized_offset = vehicle_offset / (frame_width / 2)
            self.steering_angle = normalized_offset * 30.0  # Max 30 degrees
            
            # Clamp to reasonable range
            self.steering_angle = np.clip(self.steering_angle, -45, 45)
        else:
            self.assist_active = False
            self.steering_angle = 0.0
        
        return self.steering_angle
    
    def draw_assistance(self, frame: np.ndarray,
                       lane_center: Optional[float],
                       vehicle_offset: Optional[float]) -> np.ndarray:
        """Draw lane keeping assistance guidance"""
        if not self.assist_active:
            return frame
        
        height, width = frame.shape[:2]
        
        # Draw steering wheel indicator
        wheel_center = (width - 150, height - 150)
        wheel_radius = 60
        
        # Draw wheel circle
        cv2.circle(frame, wheel_center, wheel_radius, (255, 255, 255), 3)
        
        # Draw steering indicator
        angle_rad = np.radians(self.steering_angle)
        end_x = int(wheel_center[0] + wheel_radius * 0.7 * np.sin(angle_rad))
        end_y = int(wheel_center[1] - wheel_radius * 0.7 * np.cos(angle_rad))
        
        # Color based on direction
        if self.steering_angle < 0:
            color = (0, 255, 255)  # Yellow for left
        else:
            color = (255, 0, 255)  # Magenta for right
        
        cv2.line(frame, wheel_center, (end_x, end_y), color, 5)
        
        # Draw steering text
        if self.steering_angle < 0:
            steer_text = f"Steer Left: {abs(self.steering_angle):.1f}°"
        else:
            steer_text = f"Steer Right: {self.steering_angle:.1f}°"
        
        text_size = cv2.getTextSize(steer_text, cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.7, 2)[0]
        text_x = wheel_center[0] - text_size[0] // 2
        text_y = wheel_center[1] + wheel_radius + 30
        
        cv2.putText(frame, steer_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
```

---

## Summary of Warning Systems

### FCWS (Forward Collision Warning)
- **Input**: Object detections, frame height
- **Output**: Warning state (SAFE/WARNING/CRITICAL), risky detections
- **Logic**: Distance-based thresholds
- **Visual**: Red overlay for critical, yellow text for warning

### Enhanced FCWS
- **Addition**: Real-world distance estimation in meters
- **Benefit**: More accurate warnings with calibrated camera
- **Statistics**: Tracks warning rates and patterns

### LDWS (Lane Departure Warning)
- **Input**: Lane center, vehicle offset
- **Output**: Warning state (SAFE/LEFT_WARNING/RIGHT_WARNING)
- **Logic**: Offset threshold-based
- **Visual**: Directional arrows, warning text

### LKAS (Lane Keeping Assistance)
- **Input**: Lane center, vehicle offset
- **Output**: Steering angle (-45° to +45°)
- **Logic**: Proportional to offset
- **Visual**: Steering wheel indicator with angle

All systems work together to provide comprehensive driver assistance!
