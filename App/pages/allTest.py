import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from ThermalCameraPage import ThermalCameraPage
from LidarCameraPage import LidarCameraPage

class MultiSensorPage(QMainWindow):
    """Multi-Sensor Display (LiDAR, Thermal, Event, RGB)"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi-Sensor View")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget & layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout()
        central_widget.setLayout(layout)

        # ✅ Add actual sensor pages
        self.lidar_page = LidarCameraPage()  
        self.thermal_page = ThermalCameraPage()

        # Create QLabel placeholders
        self.event_label = QLabel("Event Camera")
        self.rgb_label = QLabel("RGB Camera")

        # Add widgets to layout (2x2 grid)
        layout.addWidget(self.lidar_page, 0, 0)   # Top-left (LiDAR)
        layout.addWidget(self.thermal_page, 0, 1)  # Top-right (Thermal)
        layout.addWidget(self.event_label, 1, 0)   # Bottom-left (Event)
        layout.addWidget(self.rgb_label, 1, 1)     # Bottom-right (RGB)

        # Timer for updating streams
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(33)  # ~30 FPS

    def update_frames(self):
        """Updates all sensor displays."""
        self.event_label.setPixmap(self.get_event_frame())
        self.rgb_label.setPixmap(self.get_rgb_frame())

    def get_event_frame(self):
        """Simulated event camera feed (replace with real event camera data)."""
        img = np.random.randint(0, 2, (300, 400), dtype=np.uint8) * 255  # Black & white noise
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return self.convert_to_pixmap(img)

    def get_rgb_frame(self):
        """Captures an RGB frame from webcam."""
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return self.convert_to_pixmap(frame)
        return self.get_blank_frame()

    def convert_to_pixmap(self, img):
        """Converts OpenCV image to QPixmap for QLabel display."""
        h, w, ch = img.shape
        bytes_per_line = ch * w
        q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def get_blank_frame(self):
        """Returns a blank black frame in case of error."""
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        return self.convert_to_pixmap(img)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiSensorPage()
    window.show()
    sys.exit(app.exec_())
