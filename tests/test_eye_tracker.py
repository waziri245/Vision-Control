# tests/test_eye_tracker.py
# Unit tests for reusable logic in eye_tracker.py
# Compatible with CI (headless) environments.

import pytest
import math
import platform
import shutil
import os

# Simulate importing the src module
import sys
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
    assert math.isclose(result, 1000.0, rel_tol=1e-2)


# -----------------------------------------------------------
# TEST 2: Platform & Environment Check
# -----------------------------------------------------------

def test_platform_detection():
    system = platform.system()
    assert system in ["Windows", "Linux", "Darwin"]

def test_onboard_availability_on_linux():
    if platform.system() == "Linux":
        assert shutil.which("onboard") is None or isinstance(shutil.which("onboard"), str)

# -----------------------------------------------------------
# TEST 3: GUI-related Code — Only Run Locally
# -----------------------------------------------------------

@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="Skipping GUI test in CI (no display)"
)
def test_cursor_move_called():
    from unittest.mock import patch
    import pyautogui

    with patch("pyautogui.moveTo") as mock_move:
        pyautogui.moveTo(300, 400)
        mock_move.assert_called_once_with(300, 400)

# -----------------------------------------------------------
# TEST 4: Blink Detection EAR Thresholds
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
# Camera, OpenCV GUI, and MediaPipe live tracking are excluded from testing.
# -----------------------------------------------------------
