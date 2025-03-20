"""Thermal Page"""
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from utils import load_stylesheet, close_event,QRCodeWidget

class ThermalCameraPage(QWidget):
    """Thermal Camera Streaming Page"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Camera Stream")

        # Main layout (horizontal split)
        self.main_layout = QHBoxLayout()

        # Left side: Thermal feed
        self.video_layout = QVBoxLayout()
        self.thermal_feed = QLabel()
        self.thermal_feed.setObjectName("thermal_feed")
        self.thermal_feed.setAlignment(Qt.AlignCenter)
        self.thermal_feed.setScaledContents(True)
        self.video_layout.addWidget(self.thermal_feed)

        # Right side: Title and description
        self.info_layout = QVBoxLayout()
        self.title_label = QLabel("Thermal Camera Stream")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title")

        self.description_label = QLabel(
            "Thermal (infrared) cameras detect heat instead of "
            "visible light. Every object emits infrared radiation based "
            "on its temperature, and thermal cameras use special sensors "
            "to capture this radiation. Warmer objects emit more infrared "
            "energy, while cooler objects emit less. The camera converts "
            "these heat patterns into an image, where different temperatures "
            "appear as different colors—typically with warmer areas shown in "
            "red, orange, or white and cooler areas in blue or purple. This"
            " allows thermal cameras to see in complete darkness, through smoke, "
            "and in harsh weather conditions, making them useful for applications "
            "like night vision, search and rescue, and industrial inspections.")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setObjectName("description")

        self.qr_widget=QRCodeWidget("Datasets/QRcodes/thermal_QR.svg",
                                    "Scan this to learn more about thermal cameras!",
                                    label_width=800)

        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.description_label)
        self.info_layout.addStretch()
        self.info_layout.addWidget(self.qr_widget)

        # Add sections to main layout
        self.main_layout.addLayout(self.video_layout, 1)  # 50% width
        self.main_layout.addLayout(self.info_layout, 1)  # 50% width
        self.setLayout(self.main_layout)

        # Load stylesheet
        load_stylesheet(self, "App/styles/sensors.qss")

        # Initialize the RTSP stream
        self.rtsp_url = "rtsp://admin:valeo123@192.168.2.64:554/Streaming/Channels/101/"
        self.cap = None
        self.connect_to_thermal_stream()

        # Setup timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def connect_to_thermal_stream(self):
        """Connect to the RTSP thermal stream"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            if not self.cap.isOpened():
                print("Error: Could not connect to thermal stream")
                self.cap = cv2.VideoCapture(0)
            print("Successfully connected to thermal stream")
        except Exception as e:
            print(f"Error connecting to thermal stream: {e}")
            self.cap = cv2.VideoCapture(0)

    def update_frame(self):
        """Update frames from video stream"""
        if self.cap and self.cap.isOpened():
            ret, thermal_frame = self.cap.read()
            if ret:
                self.thermal_feed.setPixmap(self._convert_cv_to_qt(thermal_frame))
            else:
                print("Failed to read frame from thermal stream")

    def _convert_cv_to_qt(self, cv_img):
        """Convert cv2 img to qpixmap for display in QLabel"""
        if cv_img is None:
            return QPixmap()
        if len(cv_img.shape) == 2:
            h, w = cv_img.shape
            qt_image = QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8)
        else:
            h, w, ch = cv_img.shape
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)
                
    def release(self):
        """Release resources properly"""
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def use_close_event(self, event):
        """Handle close event to release resources"""
        close_event(event, self)
