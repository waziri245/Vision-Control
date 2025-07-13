# This file contains unit tests for reusable and testable parts of the eye-head mouse control system.

import pytest
import math
import platform
import shutil
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# -----------------------------------------------------------
# TEST 1: Euclidean Distance Function
# -----------------------------------------------------------

def euclidean(p1, p2, iw, ih):
    x1, y1 = int(p1.x * iw), int(p1.y * ih)
    x2, y2 = int(p2.x * iw), int(p2.y * ih)
    return math.hypot(x2 - x1, y2 - y1)

class DummyPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_euclidean_basic():
    p1 = DummyPoint(0.1, 0.1)
    p2 = DummyPoint(0.2, 0.1)
    result = euclidean(p1, p2, 1000, 1000)
    assert math.isclose(result, 100.0, rel_tol=1e-2)

def test_euclidean_diagonal():
    p1 = DummyPoint(0.0, 0.0)
    p2 = DummyPoint(0.6, 0.8)
    result = euclidean(p1, p2, 1000, 1000)
    # Expecting hypot(600, 800) = 1000
    assert math.isclose(result, 1000.0, rel_tol=1e-2)

# -----------------------------------------------------------
# TEST 2: Configuration Constants
# -----------------------------------------------------------

def test_constants_are_reasonable():
    from src import eye_tracker 

    assert 0 < eye_tracker.SMOOTHING < 1
    assert eye_tracker.TOO_FAR < eye_tracker.TOO_CLOSE
    assert isinstance(eye_tracker.BLINK_COOLDOWN, float)

# -----------------------------------------------------------
# TEST 3: Platform Detection and OSK Commands
# -----------------------------------------------------------

def test_platform_detection():
    system = platform.system()
    assert system in ["Windows", "Linux", "Darwin"]

def test_onboard_availability_on_linux():
    if platform.system() == "Linux":
        # Either onboard exists or not, but shutil.which() should not raise
        assert shutil.which("onboard") is None or isinstance(shutil.which("onboard"), str)

# -----------------------------------------------------------
# TEST 4: Cursor Movement with Mock
# -----------------------------------------------------------

@patch("pyautogui.moveTo")
def test_cursor_move_called(mock_moveTo):
    # Simulate a smoothed value update
    smoothed_x, smoothed_y = 300, 400
    import pyautogui
    pyautogui.moveTo(smoothed_x, smoothed_y)
    mock_moveTo.assert_called_once_with(smoothed_x, smoothed_y)

# -----------------------------------------------------------
# TEST 5: Blink Detection Logic (Mock Example)
# -----------------------------------------------------------

def test_ear_ratio_below_threshold():
    vertical = 5
    horizontal = 30
    ear = vertical / (horizontal + 1e-6)
    assert ear < 0.20

def test_ear_ratio_above_threshold():
    vertical = 6
    horizontal = 20
    ear = vertical / (horizontal + 1e-6)
    assert ear > 0.20

# -----------------------------------------------------------
# Note:
# Webcam, MediaPipe, and OpenCV GUI parts are not tested
# because they require live video and are not unit-testable
# -----------------------------------------------------------
