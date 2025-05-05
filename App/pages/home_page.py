"""Application Home page, contains general description and buttons that lead to relevant algs"""
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5 import uic
from App.pages.hand_gesture_page import HandGestureRecognitionPage
from App.pages.facial_expression_page import FacialExpressionRecognitionPage
from App.pages.general_page import GeneralDemoPage
from App.pages.thermal_page import ThermalCameraPage
from App.pages.event_page import EventCameraPage
from App.pages.lidar_page import LidarCameraPage
from utils import load_stylesheet, DeviceStatusChecker

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
        self.eventButton.clicked.connect(self.open_event_page)

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
        self.device_checker = DeviceStatusChecker()

        # Timer to update connection status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_connection_status)
        self.status_timer.start(5000)  # Update UI every 5 seconds

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
        """Update UI with current connection status."""
        # Get current status (these are fast lookups, not network operations)
        rgb_connected = self.device_checker.get_status("rgb")
        lidar_connected = self.device_checker.get_status("lidar")
        thermal_connected = self.device_checker.get_status("thermal")
        event_connected = self.device_checker.get_status("event")

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

    # Page opening handlers
    def open_hand_gesture_page(self):
        """show and run hand gesture page/alg"""
        self.close_other_pages()
        self.hand_gesture_page = HandGestureRecognitionPage()
        self.hand_gesture_page.showMaximized()

    def open_facial_expression_page(self):
        """show and run face/emotion expression page/alg"""
        self.close_other_pages()
        self.facial_expression_page = FacialExpressionRecognitionPage()
        self.facial_expression_page.showMaximized()

    def open_object_detection_page(self):
        """show and run object detection page/alg, pass in title and description"""
        self.close_other_pages()
        self.object_detection_page = GeneralDemoPage("object")
        self.object_detection_page.showMaximized()

    def open_colour_detection_page(self):
        """show and run colour detection page/alg, pass in title and description"""
        self.close_other_pages()
        self.colour_detection_page = GeneralDemoPage("colour")
        self.colour_detection_page.showMaximized()

    def open_lidar_page(self):
        """show and run lidar page"""
        self.close_other_pages()
        self.lidar_page=LidarCameraPage()
        self.lidar_page.showMaximized()

    def open_thermal_page(self):
        """show and run thermal page"""
        self.close_other_pages()
        self.thermal_page=ThermalCameraPage()
        self.thermal_page.showMaximized()

    def open_event_page(self):
        """show and run event camera high speed counting page/alg"""
        self.close_other_pages()
        self.event_page=EventCameraPage()
        self.event_page.showMaximized()

    def close_other_pages(self):
        """"close all other pages before opening another
        if self.hand_gesture_page:
            self.hand_gesture_page.close()
            self.hand_gesture_page=None
        if self.facial_expression_page:
            self.facial_expression_page.close()
            self.facial_expression_page=None
        if self.colour_detection_page:
            self.colour_detection_page.close()
            self.colour_detection_page=None
        if self.object_detection_page:
            self.object_detection_page.close()
            self.object_detection_page=None"""

    def closeEvent(self, event):
        """
        Popup to confirm exiting of app,
        Ensure the entire application closes when the home page is closed.
        """
        reply=QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you wish to close the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
            QApplication.quit()
            self.device_checker.stop()
        else:
            event.ignore()
