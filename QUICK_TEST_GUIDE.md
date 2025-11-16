# Quick Test Guide

## Run All Tests (Recommended)

```bash
python tests/run_all_tests.py
```

This will run all 60+ tests and display a summary.

## Run Tests by Component

### Configuration Tests
```bash
python -m unittest tests.test_config_loader -v
```

### Model Management Tests
```bash
python -m unittest tests.test_model_manager -v
```

### Distance Estimation Tests
```bash
python -m unittest tests.test_distance_estimator -v
```

### Lane Utilities Tests
```bash
python -m unittest tests.test_lane_utils -v
```

### Animation Engine Tests
```bash
python -m unittest tests.test_animation_engine -v
```

### Overlay Renderer Tests
```bash
python -m unittest tests.test_overlay_renderer -v
```

### BEV Transformer Tests
```bash
python -m unittest tests.test_bev_transformer -v
```

## Run All Tests with Verbose Output

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Run Specific Test Class

```bash
python -m unittest tests.test_animation_engine.TestAnimationEngine -v
```

## Run Specific Test Method

```bash
python -m unittest tests.test_config_loader.TestConfigLoader.test_default_config_creation -v
```

## Expected Output

```
test_default_config_creation (tests.test_config_loader.TestConfigLoader) ... ok
test_get_config_value (tests.test_config_loader.TestConfigLoader) ... ok
test_set_config_value (tests.test_config_loader.TestConfigLoader) ... ok
...

======================================================================
TEST SUMMARY
======================================================================
Tests run: 60+
Successes: 60+
Failures: 0
Errors: 0
======================================================================
```

## Test Files Location

All test files are in the `tests/` directory:
- `test_config_loader.py` - 7 tests
- `test_model_manager.py` - 6 tests
- `test_distance_estimator.py` - 7 tests
- `test_lane_utils.py` - 9 tests
- `test_animation_engine.py` - 16 tests
- `test_overlay_renderer.py` - 12 tests
- `test_bev_transformer.py` - 11 tests

## Test Coverage

- **Phase 1 (Foundation)**: 13 tests
- **Phase 2 (Core Detection)**: 16 tests
- **Phase 3 (Visualization)**: 31 tests
- **Total**: 60+ tests

## Troubleshooting

### Import Errors
Make sure you're running tests from the project root directory:
```bash
cd /path/to/ADAS_Project
python tests/run_all_tests.py
```

### Missing Dependencies
Install required packages:
```bash
pip install -r requirements.txt
```

### Specific Test Failures
Run individual test to see detailed error:
```bash
python -m unittest tests.test_name.TestClass.test_method -v
```

## Documentation

For detailed test documentation, see:
- `tests/TEST_DOCUMENTATION.md` - Complete test reference
- `TESTING_SUMMARY.md` - Testing overview and statistics
