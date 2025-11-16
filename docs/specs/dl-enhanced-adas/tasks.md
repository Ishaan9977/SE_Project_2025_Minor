# Implementation Plan

- [x] 1. Set up project structure and configuration management


  - Create directory structure for new modules (dl_models, overlays, transforms, utils)
  - Create configuration file schema (YAML) for model paths, overlay settings, and performance parameters
  - Implement configuration loader with validation and default values
  - Add configuration update API endpoint for runtime changes
  - _Requirements: 6.3, 7.3, 8.3_




- [ ] 2. Implement Model Manager and hardware detection
  - Create ModelManager class with hardware detection (CUDA, OpenVINO, MPS, CPU)
  - Implement device selection logic with priority ordering
  - Add model loading interface supporting multiple formats (ONNX, PyTorch, TensorFlow)




  - Implement model benchmarking functionality to measure inference time
  - Add model information retrieval and logging
  - _Requirements: 7.1, 7.2, 7.3, 7.4_



- [ ] 3. Implement DL Lane Detection module with fallback mechanism
  - [ ] 3.1 Create DLLaneDetector base class with abstract methods
    - Define interface for detect_lanes, preprocess_frame, postprocess_output
    - Implement frame preprocessing (resize, normalize, tensor conversion)
    - Create standardized output format (LaneDetectionResult dataclass)


    - _Requirements: 1.1, 1.3_
  
  - [ ] 3.2 Implement ONNX model support
    - Add ONNX Runtime inference engine
    - Implement model loading and session creation


    - Add input/output tensor handling
    - Implement postprocessing for common lane detection outputs
    - _Requirements: 1.1, 1.2, 7.1_





  
  - [ ] 3.3 Implement confidence-based fallback logic
    - Add confidence threshold checking after DL detection
    - Implement automatic fallback to CV lane detector when confidence < 0.6

    - Add detection method tracking (DL vs CV) in results
    - Log fallback events for monitoring
    - _Requirements: 1.4, 10.1_
  
  - [ ] 3.4 Add lane polynomial calculation
    - Implement conversion from model output to polynomial coefficients

    - Add polynomial fitting for point-based outputs
    - Calculate lane curvature from polynomials
    - _Requirements: 1.3_

- [x] 4. Implement Enhanced Distance Estimator


  - [ ] 4.1 Create DistanceEstimator class with calibration support
    - Implement calibration file loader (JSON format)


    - Add camera matrix and distortion coefficient storage
    - Create DistanceEstimation dataclass for results
    - _Requirements: 4.1, 4.3_
  
  - [ ] 4.2 Implement calibrated distance estimation
    - Add pinhole camera model distance calculation
    - Implement pixel-to-meters conversion using focal length
    - Calculate distance for different object classes using known heights
    - Add confidence interval calculation
    - _Requirements: 4.1, 4.3, 4.5_
  
  - [ ] 4.3 Implement uncalibrated distance estimation
    - Add normalized distance estimation based on bbox size and position
    - Implement relative distance calculation with clear unit indicators
    - Add confidence scoring for uncalibrated estimates
    - _Requirements: 4.4_
  
  - [ ] 4.4 Integrate with FCWS for multi-object distance display
    - Update FCWS to use DistanceEstimator for all detections
    - Implement distance sorting to find three closest objects
    - Add distance display with confidence indicators
    - _Requirements: 4.2, 4.5_

- [x] 5. Implement Animation Engine

  - [x] 5.1 Create AnimationEngine class

    - Implement animation registration with name, duration, and easing type
    - Add time-based animation value calculation (0.0 to 1.0)
    - Implement frame-to-frame delta time tracking
    - _Requirements: 5.1, 5.3_
  
  - [x] 5.2 Implement easing functions

    - Add linear, ease-in, ease-out, ease-in-out easing functions
    - Implement bounce and elastic easing for attention-grabbing effects
    - Create easing function selector
    - _Requirements: 5.3_
  
  - [x] 5.3 Add animation state management

    - Implement animation lifecycle (start, update, complete)
    - Add animation looping and reverse playback
    - Create animation queue for coordinated effects
    - _Requirements: 5.4_

- [x] 6. Implement Advanced Overlay Renderer


  - [x] 6.1 Create AdvancedOverlayRenderer base class


    - Initialize with OverlayConfig dataclass
    - Implement alpha blending utility functions
    - Add color conversion and manipulation utilities
    - Create overlay layer management system
    - _Requirements: 2.4, 6.1_
  
  - [x] 6.2 Implement lane polygon rendering

    - Create filled polygon between left and right lane lines
    - Add semi-transparent overlay with configurable alpha
    - Implement gradient effect from near (opaque) to far (transparent)
    - Add color coding by lane type (ego: green, adjacent: blue)
    - _Requirements: 2.1_
  
  - [x] 6.3 Implement distance marker rendering

    - Draw horizontal lines at fixed distance intervals (10m, 20m, 30m, etc.)
    - Add distance labels with background boxes for readability
    - Implement color-coded confidence indicators
    - Add perspective scaling for realistic appearance
    - _Requirements: 2.2, 4.2_
  
  - [x] 6.4 Implement warning overlay rendering

    - Create warning banner with icon and message
    - Add severity-based color coding (green, yellow, red)
    - Implement pulsing effect for critical warnings using AnimationEngine
    - Add smooth fade in/out transitions
    - _Requirements: 2.3, 5.1_
  
  - [x] 6.5 Implement directional arrow rendering

    - Create animated arrow graphics for lane departure warnings
    - Add pulsing and sliding animations
    - Implement color coding by urgency (yellow warning, red critical)
    - Position arrows based on departure direction
    - _Requirements: 2.3, 5.2_
  
  - [x] 6.6 Implement performance-aware rendering

    - Add frame time monitoring
    - Implement selective overlay disabling when performance drops
    - Create rendering priority system (critical > important > optional)
    - _Requirements: 2.5, 9.3_

- [x] 7. Implement Bird's Eye View Transformer



  - [x] 7.1 Create BirdEyeViewTransformer class


    - Define source and destination points for perspective transform
    - Calculate and cache transformation matrix
    - Implement inverse transformation for coordinate mapping
    - _Requirements: 3.1_
  
  - [x] 7.2 Implement frame transformation

    - Apply perspective warp to create top-down view
    - Add lane line transformation to BEV coordinates
    - Implement vehicle position indicator at fixed reference point
    - _Requirements: 3.2, 3.3_
  
  - [x] 7.3 Implement drivable area highlighting

    - Detect when both left and right lanes are present
    - Fill polygon between lanes in BEV with semi-transparent color
    - Add lane boundary lines
    - _Requirements: 3.4_
  
  - [x] 7.4 Implement picture-in-picture overlay

    - Create PIP frame with border and background
    - Position BEV in configurable corner (default: bottom-right)
    - Add resize functionality for BEV output
    - Blend PIP onto main frame with proper alpha
    - _Requirements: 3.2, 3.5_

- [x] 8. Integrate components into EnhancedADASSystem





  - [ ] 8.1 Create EnhancedADASSystem class extending ADASSystem
    - Initialize all new components (DLLaneDetector, AdvancedOverlayRenderer, etc.)
    - Implement component initialization with error handling
    - Add configuration-based component enabling/disabling

    - _Requirements: 7.4, 10.2_
  
  - [ ] 8.2 Implement enhanced process_frame method
    - Integrate DL lane detection with fallback to CV
    - Add distance estimation for all detected objects
    - Calculate lane metrics (center, offset, curvature)

    - Determine warning states for FCWS, LDWS, LKAS
    - _Requirements: 1.4, 4.1, 10.1_
  
  - [ ] 8.3 Implement overlay rendering pipeline
    - Render lane polygons with animation
    - Draw distance markers on detected objects
    - Add warning overlays based on system states

    - Apply directional arrows for lane departure
    - Overlay bird's eye view if enabled
    - _Requirements: 2.1, 2.2, 2.3, 3.2_
  
  - [ ] 8.4 Add performance monitoring and adaptive quality
    - Track frame processing time per component

    - Implement frame skipping when behind real-time
    - Add automatic overlay disabling on performance degradation
    - Log performance metrics for analysis
    - _Requirements: 9.1, 9.2, 9.3, 9.4_




  
  - [ ] 8.5 Implement error handling and safe mode
    - Add try-catch blocks around each processing stage
    - Implement consecutive error counting
    - Add safe mode activation when error threshold exceeded
    - Create fallback frame output on processing errors

    - _Requirements: 10.1, 10.2, 10.3, 10.5_

- [ ] 9. Update Flask web interface for enhanced features
  - [ ] 9.1 Add configuration panel UI
    - Create HTML form for overlay toggles (lane polygon, distance markers, BEV, animations)
    - Add sliders for alpha values and animation speed

    - Implement color pickers for overlay colors
    - Add model selection dropdown
    - _Requirements: 6.1, 8.3_
  
  - [ ] 9.2 Implement configuration API endpoints
    - Create POST /api/config/update endpoint for runtime config changes

    - Add GET /api/config endpoint to retrieve current configuration
    - Implement configuration validation and error responses
    - Add configuration persistence to file
    - _Requirements: 6.3, 8.3_
  
  - [x] 9.3 Add performance metrics display

    - Create real-time FPS counter display
    - Add per-component latency breakdown
    - Show current model in use (DL vs CV fallback)
    - Display error count and safe mode status
    - _Requirements: 8.4, 9.5_
  
  - [ ] 9.4 Implement video upload progress tracking
    - Add progress bar for video processing
    - Calculate and display estimated completion time
    - Show current frame number and total frames
    - Add cancel button for long-running processes
    - _Requirements: 8.2_
  
  - [ ] 9.5 Add error display and recovery UI
    - Create error notification system with dismissible alerts
    - Add detailed error messages with recovery suggestions
    - Implement retry button for failed operations
    - Show model loading status and fallback notifications
    - _Requirements: 8.5, 10.2_

- [ ] 10. Create sample models and calibration files
  - Download or create sample ONNX lane detection model (e.g., Ultra-Fast-Lane-Detection)
  - Create sample camera calibration JSON file with example parameters
  - Add model download script for large pre-trained models
  - Create README with model sources and licenses
  - _Requirements: 7.1, 4.1_

- [ ] 11. Update documentation and examples
  - Update main README with new features and configuration options
  - Create configuration guide explaining all settings
  - Add example calibration workflow
  - Create performance tuning guide
  - Document model compatibility and requirements
  - _Requirements: 6.3, 7.3_

- [ ] 12. Testing and validation
  - [ ] 12.1 Create unit tests for core components
    - Test DLLaneDetector with mock model outputs
    - Test DistanceEstimator with various bbox sizes
    - Test AnimationEngine easing functions
    - Test BEV transformation matrix calculations
    - _Requirements: All_
  
  - [ ] 12.2 Create integration tests
    - Test end-to-end frame processing pipeline
    - Test fallback mechanism activation
    - Test configuration updates during runtime
    - Test error handling and recovery
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ] 12.3 Performance benchmarking
    - Measure per-component latency on target hardware
    - Test sustained frame rate over extended periods
    - Benchmark memory usage and stability
    - Test with various video resolutions and conditions
    - _Requirements: 9.1, 9.2_
  
  - [ ] 12.4 Visual validation
    - Test overlay rendering with sample videos
    - Validate animation smoothness
    - Check BEV transformation accuracy
    - Verify distance marker positioning
    - _Requirements: 2.1, 2.2, 2.3, 3.2_
