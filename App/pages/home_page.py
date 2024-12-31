import win32com.client
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5 import uic
from .hand_gesture_page import HandGestureRecognitionPage
from .facial_expression_page import FacialExpressionRecognitionPage
from .general_page import GeneralDemoPage

class HomePage(QMainWindow):  # Changed from QWidget to QMainWindow
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi("App/home_page.ui", self)  # Updated path to match your project structure
        self.setWindowTitle("Home")

        # Connect button signals to slots
        self.handGestureButton.clicked.connect(self.open_hand_gesture_page)
        self.facialExpressionButton.clicked.connect(self.open_facial_expression_page)
        self.colourButton.clicked.connect(self.open_colour_detection_page)
        self.objectButton.clicked.connect(self.open_object_detection_page)
        self.lidarButton.clicked.connect(self.open_lidar_page)
        self.thermalButton.clicked.connect(self.open_thermal_page)
        self.eventButton.clicked.connect(self.open_counting_page)

        # Initialize status indicators
        self.set_status_to_searching()

        # Timer to update connection status
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.update_connection_status)
        self.connection_timer.start(2000)  # Check every 2 seconds

    def draw_circle(self, color, size=20):
        """Draw a circle with the specified color and size."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return pixmap

    def update_connection_status(self):
        """Check actual connection status for devices."""
        rgb_connected = self.is_device_connected("HXC32A99K_V2")  # Using previous keyboard ID
        lidar_connected = self.is_device_connected("HXC32A99K_V2")  # Using previous keyboard ID
        thermal_connected = self.is_device_connected("notconnectedNonesense")  # Using previous mouse ID
        event_connected = self.is_device_connected("notconnectedNonesense")  # Using previous mouse ID

        # Update status indicators
        self.rgbCircle.setPixmap(self.draw_circle("green" if rgb_connected else "red"))
        self.lidarCircle.setPixmap(self.draw_circle("green" if lidar_connected else "red"))
        self.thermalCircle.setPixmap(self.draw_circle("green" if thermal_connected else "red"))
        self.eventCircle.setPixmap(self.draw_circle("green" if event_connected else "red"))

    def set_status_to_searching(self):
        """Set all status indicators to searching (yellow/orange) while loading."""
        self.rgbCircle.setPixmap(self.draw_circle("orange"))
        self.lidarCircle.setPixmap(self.draw_circle("orange"))
        self.thermalCircle.setPixmap(self.draw_circle("orange"))
        self.eventCircle.setPixmap(self.draw_circle("orange"))

    def is_device_connected(self, device_name):
        """Check if a device is connected by its name."""
        wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
        query = "SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%{}%'".format(device_name)
        devices = wmi.ExecQuery(query)
        return any(device.DeviceID for device in devices)

    # Page opening handlers
    def open_hand_gesture_page(self):
        self.hand_gesture_page = HandGestureRecognitionPage()
        self.hand_gesture_page.show()

    def open_facial_expression_page(self):
        self.facial_expression_page = FacialExpressionRecognitionPage()
        self.facial_expression_page.show()

    def open_object_detection_page(self):
        self.object_detection_page = GeneralDemoPage("Object Detection", "dummy description", "object")
        self.object_detection_page.show()

    def open_colour_detection_page(self):
        self.colour_detection_page = GeneralDemoPage("Colour Detection", "dummy description", "colour")
        self.colour_detection_page.show()

    def open_lidar_page(self):
        print("LiDAR demo selected.")

    def open_thermal_page(self):
        print("Thermal demo selected.")

    def open_counting_page(self):
        print("Event Camera Counting demo selected.")