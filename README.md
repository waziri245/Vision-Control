# 🖱️ Vision-Control — Head & Blink-Based Mouse Control System

**Vision-Control** is an assistive mouse control system designed for hands-free interaction with a computer. It enables users to move the mouse cursor using **head movement** (tracked via the nose tip) and perform **mouse clicks** by blinking either eye.

This project supports **Windows** and **Linux (X11/Xorg)** and is built using Python with real-time webcam input processing.

---

## 🚀 Features

- 🎯 **Head-Based Cursor Movement**  
  The mouse cursor follows the user's head movement, using nose position for tracking.

- 👁️ **Blink-Triggered Mouse Clicks**  
  - Left Eye Blink ⟶ Left Mouse Click  
  - Right Eye Blink ⟶ Right Mouse Click

- 📐 **Automatic Distance Feedback**  
  Detects whether the user is too close, too far, or at an ideal distance from the camera.

- ⚙️ **Cross-Platform Support**  
  Works on both **Windows** and **Linux** (X11/Xorg only).

- 🧪 **Continuous Integration (CI) Tested**  
  Automatically tested on GitHub Actions to ensure consistent behavior.

---

## 📷 How It Works

- The webcam captures a real-time video feed.
- `MediaPipe Face Mesh` detects key facial landmarks.
- The **nose tip** coordinates control the mouse position.
- The **eye aspect ratio (EAR)** is calculated to detect intentional blinks.
- Left and right blinks trigger the corresponding mouse click using `pyautogui`.

---

## 🧰 Technologies Used

| Component     | Description                                 |
|---------------|---------------------------------------------|
| Python 3.10+  | Core programming language                   |
| OpenCV        | Webcam frame processing                     |
| MediaPipe     | Facial landmark detection (face mesh)       |
| pyautogui     | OS-level mouse control                      |
| subprocess & platform | System OSK launch and environment detection |
| pytest        | Unit testing framework                      |
| GitHub Actions| CI for testing on push & PR events          |

---

## 🛠️ Installation & Setup

### 🔧 Requirements

- Python 3.10 or newer
- A working webcam
- On Linux: use **X11/Xorg** (Wayland is not supported)

---

### 📦 Installation Steps

1. **Clone the Repository:**

```bash
git clone https://github.com/waziri245/Vision-Control.git
cd Vision-Control
```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the Application:**

```bash
python src/eye_tracker.py
```

---

## 🧪 Running Tests

Unit tests are available for core reusable logic.

```bash
pytest tests/ -v
```

> GUI-related functionality is skipped in Continuous Integration environments.

---

## 📁 Project Structure

```
Vision-Control/
├── .github/
│   └── workflows/
│       └── python-tests.yml     # GitHub Actions workflow
├── src/
│   ├── eye_tracker.py           # Main application logic
│   └── __init__.py
├── tests/
│   ├── test_eye_tracker.py      # Unit tests
│   └── __init__.py
├── requirements.txt             # Required Python packages
├── LICENSE                      # MIT License
├── README.md                    # Project documentation
└── .gitignore                   # Git ignored files
```

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for more information.

---

## 💡 Additional Notes

- **Webcam Must Be Enabled**: The system relies entirely on live video input.
- **Startup Delay**: The app performs auto-calibration for a few seconds when launched.
- **On-Screen Keyboard (OSK)**:  
  - On Windows: `osk.exe` is launched and minimized.  
  - On Linux: `onboard` is launched if installed.
- **Sensitivity Settings**: Cursor speed can be fine-tuned inside the source code.

---

### 💻 Optional: Enable On-Screen Keyboard (Linux)

If you want to use the on-screen keyboard on Linux, make sure `onboard` is installed:

```bash
sudo apt update
sudo apt install onboard
```

---


> For optimal performance, ensure proper lighting and a stable camera angle. Avoid background movement near the face.

---

## Author

Developed with passion by Atal Abdullah Waziri, co-founder of [Stellar Organization](https://stellarorganization.mystrikingly.com/).

---