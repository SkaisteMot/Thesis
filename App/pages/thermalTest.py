import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from utils import load_stylesheet, close_event  # Reuse close event

class ThermalCameraPage(QWidget):
    """Thermal Camera Streaming Page"""
    def __init__(self, camera_index=0):
        super().__init__()
        self.setWindowTitle("Thermal Camera Stream")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        self.layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("video_label")
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)

        # Load stylesheet
        #load_stylesheet(self, "App/styles/thermal_camera.qss")

        # Open Thermal Camera Stream
        self.cap = cv2.VideoCapture(camera_index)  # Change index if needed
        if not self.cap.isOpened():
            print("Error: Cannot open thermal camera")
            return

        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms

    def update_frame(self):
        """Capture frame and display it"""
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        # Convert to grayscale (if necessary)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Convert to QPixmap
        height, width = gray_frame.shape
        bytes_per_line = width
        qimg = QImage(gray_frame.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)

    def release(self):
        """Release resources"""
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()

    def closeEvent(self, event):
        """Handle close event"""
        close_event(event, self)
