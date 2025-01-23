"""Application Home page, contains general description and buttons that lead to relevant algs"""
import win32com.client
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5 import uic

from App.pages.hand_gesture_page import HandGestureRecognitionPage
from App.pages.facial_expression_page import FacialExpressionRecognitionPage
from App.pages.general_page import GeneralDemoPage
from utils import load_stylesheet
class HomePage(QMainWindow):
    """Home page called from main.py"""
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi("App/home_page.ui", self)
        self.setWindowTitle("Home")

        #Init buttons for linting W0201
        self.hand_gesture_page=None
        self.facial_expression_page=None
        self.colour_detection_page=None
        self.object_detection_page=None

        # Connect button signals to slots
        self.handGestureButton.clicked.connect(self.open_hand_gesture_page)
        self.facialExpressionButton.clicked.connect(self.open_facial_expression_page)
        self.colourButton.clicked.connect(self.open_colour_detection_page)
        self.objectButton.clicked.connect(self.open_object_detection_page)
        self.lidarButton.clicked.connect(self.open_lidar_page)
        self.thermalButton.clicked.connect(self.open_thermal_page)
        self.eventButton.clicked.connect(self.open_counting_page)

        #Button Tooltips
        self.handGestureButton.setToolTip("Recognize hand signs and display equivalent emoji")
        self.facialExpressionButton.setToolTip("Detect facial emotions")
        self.colourButton.setToolTip("Detect the colours in a frame")
        self.objectButton.setToolTip("Detect objects in a frame")
        self.lidarButton.setToolTip("LiDAR point cloud")
        self.thermalButton.setToolTip("Demonstrate the temperatures in a frame")
        self.eventButton.setToolTip("Detect only movement in a frame")

        # Initialize status indicators
        self.set_status_to_searching()

        # Timer to update connection status
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.update_connection_status)
        self.connection_timer.start(2000)  # Check every 2 seconds

        load_stylesheet(self,'App/styles/home.qss')

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
        rgb_connected = self.is_device_connected("HXC32A99K_V2")
        lidar_connected = self.is_device_connected("HXC32A99K_V2")
        thermal_connected = self.is_device_connected("notconnectedNonesense")
        event_connected = self.is_device_connected("notconnectedNonesense")

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
        query = f"SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%{device_name}%'"
        devices = wmi.ExecQuery(query)
        return any(device.DeviceID for device in devices)

    # Page opening handlers
    def open_hand_gesture_page(self):
        """show and run hand gesture page/alg"""
        self.hand_gesture_page = HandGestureRecognitionPage()
        self.hand_gesture_page.show()

    def open_facial_expression_page(self):
        """show and run face/emotion expression page/alg"""
        self.facial_expression_page = FacialExpressionRecognitionPage()
        self.facial_expression_page.show()

    def open_object_detection_page(self):
        """show and run object detection page/alg, pass in title and description"""
        self.object_detection_page = GeneralDemoPage("Object Detection",
                                                      "dummy description",
                                                        "object")
        self.object_detection_page.show()

    def open_colour_detection_page(self):
        """show and run colour detection page/alg, pass in title and description"""
        self.colour_detection_page = GeneralDemoPage("Colour Detection",
                                                      "dummy description",
                                                        "colour")
        self.colour_detection_page.show()

    def open_lidar_page(self):
        """show and run lidar page"""
        print("LiDAR demo selected.")

    def open_thermal_page(self):
        """show and run thermal page"""
        print("Thermal demo selected.")

    def open_counting_page(self):
        """show and run event camera high speed counting page/alg"""
        print("Event Camera Counting demo selected.")
