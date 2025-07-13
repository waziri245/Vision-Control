import cv2
import mediapipe as mp
import pyautogui
import time
import math
import platform
import subprocess
import os
import shutil

# ——— Launch On-Screen Keyboard on Windows ———
if platform.system() == "Windows":
    try:
        # Start OSK
        subprocess.Popen("osk.exe")
        time.sleep(1)  # Give it a moment to start

        # Minimize OSK using powershell (Windows only)
        subprocess.Popen([
            "powershell", "-Command",
            "(New-Object -ComObject Shell.Application).MinimizeAll()"
        ])
        print("[INFO] OSK launched and minimized.")
    except Exception as e:
        print(f"[WARN] Could not launch OSK: {e}")

# ——— Launch On-Screen Keyboard on Linux (If available) ———
if platform.system() == "Linux":
    if shutil.which("onboard"):
        try:
            subprocess.Popen(["onboard"])
            print("[INFO] Onboard OSK launched")
        except Exception as e:
            print(f"[WARNING] Failed to launch onboard: {e}")
    else:
        print("[INFO] Onboard OSK not found, skipping")

# ——— Configuration ———
BLINK_COOLDOWN = 0.3   # Cooldown time for detecting a new blink (in seconds)
TOO_CLOSE = 150        # Eye distance threshold for "too close" warning
TOO_FAR = 70           # Eye distance threshold for "too far" warning
SMOOTHING = 0.1        # Cursor smoothing factor (higher = faster) (slower = smoother)

# Landmark indices (based on MediaPipe FaceMesh)
NOSE_TIP_ID = 1
RIGHT_EYE_CENTER_ID = 468
LEFT_EYE_CENTER_ID = 473

# Eye landmarks for blink detection
RIGHT_EYE_TOP = 159
RIGHT_EYE_BOTTOM = 145
LEFT_EYE_TOP = 386
LEFT_EYE_BOTTOM = 374

# ——— Initialization ———
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Blink timers
last_blink_r = 0
last_blink_l = 0

# Distance status
notified = None
status_text = ""

# Cursor smoothing trackers
smoothed_x = screen_w // 2
smoothed_y = screen_h // 2

# Head calibration
calibrated_nose_x = None
calibrated_nose_y = None
CALIBRATION_FRAMES = 30
calibration_count = 0
sum_nose_x = 0
sum_nose_y = 0

# ——— Main Loop ———
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror camera for natural interaction
    ih, iw = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_mesh.process(rgb)

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark

        # — Distance Check (for user feedback)
        rx, ry = int(lm[RIGHT_EYE_CENTER_ID].x * iw), int(lm[RIGHT_EYE_CENTER_ID].y * ih)
        lx, ly = int(lm[LEFT_EYE_CENTER_ID].x * iw), int(lm[LEFT_EYE_CENTER_ID].y * ih)
        eye_dist = math.hypot(rx - lx, ry - ly)

        if eye_dist > TOO_CLOSE and notified != "close":
            status_text, notified = "Too Close", "close"
        elif eye_dist < TOO_FAR and notified != "far":
            status_text, notified = "Too Far", "far"
        elif TOO_FAR <= eye_dist <= TOO_CLOSE and notified != "ok":
            status_text, notified = "Perfect Distance", "ok"

        # Draw status and eye centers
        cv2.circle(frame, (rx, ry), 3, (0, 255, 0), -1)
        cv2.circle(frame, (lx, ly), 3, (0, 0, 255), -1)
        cv2.putText(frame, status_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)

        def euclidean(p1, p2, iw, ih):
            x1, y1 = int(p1.x * iw), int(p1.y * ih)
            x2, y2 = int(p2.x * iw), int(p2.y * ih)
            return math.hypot(x2 - x1, y2 - y1)

        # Current time
        now = time.time()

        # — Visual RIGHT (landmarks LEFT)
        left_vert = euclidean(lm[386], lm[374], iw, ih)
        left_horiz = euclidean(lm[263], lm[362], iw, ih)
        left_ear = left_vert / (left_horiz + 1e-6)

        if left_ear < 0.20 and now - last_blink_r > BLINK_COOLDOWN:
            print("RIGHT CLICK")
            pyautogui.click(button="right")
            last_blink_r = now

        # — Visual LEFT (landmarks RIGHT)
        right_vert = euclidean(lm[159], lm[145], iw, ih)
        right_horiz = euclidean(lm[33], lm[133], iw, ih)
        right_ear = right_vert / (right_horiz + 1e-6)

        if right_ear < 0.20 and now - last_blink_l > BLINK_COOLDOWN:
            print("LEFT CLICK")
            pyautogui.click(button="left")
            last_blink_l = now


        # — Head Tracking (nose-based cursor control)
        nose_x = lm[NOSE_TIP_ID].x
        nose_y = lm[NOSE_TIP_ID].y

        # Calibration at the beginning (average over a few frames)
        if calibrated_nose_x is None:
            sum_nose_x += nose_x
            sum_nose_y += nose_y
            calibration_count += 1
            if calibration_count == CALIBRATION_FRAMES:
                calibrated_nose_x = sum_nose_x / CALIBRATION_FRAMES
                calibrated_nose_y = sum_nose_y / CALIBRATION_FRAMES
                print("[INFO] Calibration complete")
        else:
            # Calculate nose movement delta
            dx = nose_x - calibrated_nose_x
            dy = nose_y - calibrated_nose_y

            # Adjust sensitivity (fine-tune these if needed)
            sensitivity_x = 3.5
            sensitivity_y = 4.5

            move_x = dx * screen_w * sensitivity_x
            move_y = dy * screen_h * sensitivity_y

            # Target cursor position
            target_x = screen_w / 2 + move_x
            target_y = screen_h / 2 + move_y

            # Clamp to screen bounds
            target_x = max(0, min(screen_w, target_x))
            target_y = max(0, min(screen_h, target_y))

            # Smooth cursor movement
            smoothed_x = smoothed_x * (1 - SMOOTHING) + target_x * SMOOTHING
            smoothed_y = smoothed_y * (1 - SMOOTHING) + target_y * SMOOTHING

            # Move system cursor
            pyautogui.moveTo(smoothed_x, smoothed_y)
            print(f"Cursor at ({int(smoothed_x)}, {int(smoothed_y)})")

    # Show camera feed with overlay
    cv2.imshow("Head Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
