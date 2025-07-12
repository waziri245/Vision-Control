import cv2
import mediapipe as mp
import pyautogui
import time
import math

# ——— Configuration ———
BLINK_COOLDOWN = 0.5  # seconds between blinks
TOO_CLOSE = 150       # eye pixel distance threshold for being "too close"
TOO_FAR   = 70        # eye pixel distance threshold for being "too far"
SMOOTHING = 0.2       # cursor smoothing factor (0 < x < 1, higher is faster)

# Face landmark index for the nose tip (used for head tracking)
NOSE_TIP_ID = 1
RIGHT_EYE_CENTER_ID = 468
LEFT_EYE_CENTER_ID = 473

# For blinking
RIGHT_EYE_TOP = 159
RIGHT_EYE_BOTTOM = 145
LEFT_EYE_TOP = 386
LEFT_EYE_BOTTOM = 374

# ——— Setup ———
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

# Reduce resolution for speed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# MediaPipe FaceMesh with iris landmarks
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Trackers
last_blink_r = last_blink_l = 0
notified = None
status_text = ""
smoothed_x = screen_w // 2
smoothed_y = screen_h // 2

# Calibrate nose position on start
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

    frame = cv2.flip(frame, 1)  # Mirror the camera
    ih, iw = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_mesh.process(rgb)

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark

        # — Distance Feedback (based on iris landmark distance)
        rx, ry = int(lm[RIGHT_EYE_CENTER_ID].x * iw), int(lm[RIGHT_EYE_CENTER_ID].y * ih)
        lx, ly = int(lm[LEFT_EYE_CENTER_ID].x * iw), int(lm[LEFT_EYE_CENTER_ID].y * ih)
        eye_dist = math.hypot(rx - lx, ry - ly)

        if eye_dist > TOO_CLOSE and notified != "close":
            status_text, notified = "Too Close", "close"
        elif eye_dist < TOO_FAR and notified != "far":
            status_text, notified = "Too Far", "far"
        elif TOO_FAR <= eye_dist <= TOO_CLOSE and notified != "ok":
            status_text, notified = "Perfect Distance", "ok"

        # — Draw Eye Centers and Status Text
        cv2.circle(frame, (rx, ry), 3, (0,255,0), -1)
        cv2.circle(frame, (lx, ly), 3, (0,0,255), -1)
        cv2.putText(frame, status_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        # — Blink Detection (adjusted for flipped cam)
        # — Blink detection (corrected for flipped frame)
        now = time.time()

        # Visual Right Eye (actually left eye in landmarks due to flip)
        visual_right_top = int(lm[386].y * ih)
        visual_right_bottom = int(lm[374].y * ih)
        if abs(visual_right_top - visual_right_bottom) < 5 and now - last_blink_r > BLINK_COOLDOWN:
            print("RIGHT CLICK")
            last_blink_r = now

        # Visual Left Eye (actually right eye in landmarks due to flip)
        visual_left_top = int(lm[159].y * ih)
        visual_left_bottom = int(lm[145].y * ih)
        if abs(visual_left_top - visual_left_bottom) < 5 and now - last_blink_l > BLINK_COOLDOWN:
            print("LEFT CLICK")
            last_blink_l = now


        # — Head Tracking (using nose tip)
        nose_x = lm[NOSE_TIP_ID].x
        nose_y = lm[NOSE_TIP_ID].y

        # — Calibration (average over first N frames)
        if calibrated_nose_x is None:
            sum_nose_x += nose_x
            sum_nose_y += nose_y
            calibration_count += 1
            if calibration_count == CALIBRATION_FRAMES:
                calibrated_nose_x = sum_nose_x / CALIBRATION_FRAMES
                calibrated_nose_y = sum_nose_y / CALIBRATION_FRAMES
                print("[INFO] Calibration complete")
        else:
            # Relative movement from calibrated center (adjusted sensitivity)
            dx = nose_x - calibrated_nose_x
            dy = nose_y - calibrated_nose_y

            # Reverse x-axis (because of flip) and scale sensitivity
            sensitivity_x = 2.5  # adjust to make movement cover full screen
            sensitivity_y = 3.5
            move_x = dx * screen_w * sensitivity_x
            move_y = dy * screen_h * sensitivity_y

            target_x = screen_w / 2 + move_x
            target_y = screen_h / 2 + move_y

            # Clamp inside screen
            target_x = max(0, min(screen_w, target_x))
            target_y = max(0, min(screen_h, target_y))

            # Smooth movement
            smoothed_x = smoothed_x * (1 - SMOOTHING) + target_x * SMOOTHING
            smoothed_y = smoothed_y * (1 - SMOOTHING) + target_y * SMOOTHING

            # Move cursor
            pyautogui.moveTo(smoothed_x, smoothed_y)
            print(f"Cursor at ({int(smoothed_x)}, {int(smoothed_y)})")

    # — Webcam Output —
    cv2.imshow("Head Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
