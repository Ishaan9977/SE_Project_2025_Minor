# SE_Project_2025_Minor
Group Members : Ishaan Pratap 23106056 || Paarth Pokuri 23106027 || Sunandan Garg 23106040 || Anmol Verma 23106004
==================================================================================================================================================================================================================================
# Vehicle-CV-ADAS 🚗🛣️

**Advanced Driver Assistance System (ADAS) using Computer Vision**

This project demonstrates how **computer vision and deep learning** can be applied to improve road safety through an **ADAS (Advanced Driver Assistance System)** prototype. The system uses dashcam video input to detect lanes, vehicles, and potential hazards in real-time.

---

## 🔍 Project Overview

* **Lane Detection** → Identifies road lanes to support **Lane Keeping Assist (LKAS)** and **Lane Departure Warning (LDWS)**.
* **Object Detection** → Detects vehicles, pedestrians, and obstacles using **YOLO-based models**.
* **Collision Warning** → Calculates vehicle proximity for **Front Collision Warning System (FCWS)**.
* **Tracking** → Uses **ByteTrack** to track vehicles across frames for consistent monitoring.

---

## ⚙️ Technologies Used

* **Programming Language**: Python
* **Frameworks & Libraries**:

  * PyTorch (for training/conversion)
  * ONNX Runtime (for model inference)
  * OpenCV (for video processing & visualization)
  * NumPy, Matplotlib (data handling & visualization)

---

## 🧠 Models Used

* **YOLOv5 / YOLOv7 / YOLOv8** → For vehicle and object detection
* **Ultra-Fast Lane Detection v2 (UFLDv2)** → For lane marking detection
* **ByteTrack** → For object tracking

All models were exported and run in **ONNX format**, ensuring compatibility with CPU-based systems and real-time inference.

---

## 🎯 Applications

* Lane Departure Warning System (LDWS)
* Lane Keeping Assist System (LKAS)
* Front Collision Warning System (FCWS)
* Traffic monitoring & vehicle counting

---

## 📜 Academic Note

This project is submitted as part of a **Minor Project** in Computer Science & Engineering (Data Science). It serves as a demonstration of applying **AI and computer vision** in the automotive domain for **driver assistance and road safety**.
