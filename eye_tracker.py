import cv2
import mediapipe as mp

#Capture Video
cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, refine_landmarks=True)

while True:
    ret, frame = cap.read()

    if cv2.waitKey(1) == 27:  # Esc key
        break
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = mp_face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmark_right = face_landmarks.landmark[468]
            r_x_pixel = int(landmark_right.x * frame.shape[1])
            r_y_pixel = int(landmark_right.y * frame.shape[0])

            cv2.circle(frame, (r_x_pixel, r_y_pixel), radius=2, color=(0, 255, 0), thickness=-1)

            landmark_left = face_landmarks.landmark[473]
            l_x_pixel = int(landmark_left.x * frame.shape[1])
            l_y_pixel = int(landmark_left.y * frame.shape[0])

            cv2.circle(frame, (l_x_pixel, l_y_pixel), radius=2, color=(0, 0, 255), thickness=-1)

            landmark_right_top = face_landmarks.landmark[159]
            rt_x_pixel = int(landmark_right_top.x * frame.shape[1])
            rt_y_pixel = int(landmark_right_top.y * frame.shape[0])

            landmark_right_bot = face_landmarks.landmark[145]
            rb_x_pixel = int(landmark_right_bot.x * frame.shape[1])
            rb_y_pixel = int(landmark_right_bot.y * frame.shape[0])

            landmark_left_top = face_landmarks.landmark[386]
            lt_x_pixel = int(landmark_left_top.x * frame.shape[1])
            lt_y_pixel = int(landmark_left_top.y * frame.shape[0])

            landmark_left_bot = face_landmarks.landmark[374]
            lb_x_pixel = int(landmark_left_bot.x * frame.shape[1])
            lb_y_pixel = int(landmark_left_bot.y * frame.shape[0])

            right_eye_dist = abs(rt_y_pixel - rb_y_pixel)

            left_eye_dist = abs(lt_y_pixel - lb_y_pixel)

            if right_eye_dist < 5:
                print("RIGHT CLICK")
            
            if left_eye_dist < 5:
                print("LEFT CLICK")

    cv2.imshow("Webcam", frame)
    

cap.release()
cv2.destroyAllWindows()




