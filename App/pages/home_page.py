"""Application Home page, contains general description and buttons that lead to relevant algs"""
import win32com.client
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5 import uic
import subprocess

from App.pages.hand_gesture_page import HandGestureRecognitionPage
from App.pages.facial_expression_page import FacialExpressionRecognitionPage
from App.pages.general_page import GeneralDemoPage
from App.pages.thermalTest import ThermalCameraPage
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
        rgb_connected = self.is_device_connected("169.254.186.74")
        lidar_connected = self.is_device_connected("169.254.65.122")
        thermal_connected = self.is_device_connected("192.168.2.1")
        event_connected = self.is_device_connected("169.254.10.1")

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

    def is_device_connected(device_ip: str, timeout: int = 1) -> bool:
        """Check if a device is connected by its name."""
        """wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
        query = f"SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%{device_name}%'"
        devices = wmi.ExecQuery(query)
        return any(device.DeviceID for device in devices)"""
        """Check if a device is connected by its IP address."""
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(timeout * 1000), device_ip],  # Windows ping command
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return result.returncode == 0  # Return True if ping was successful
        except Exception as e:
            print(f"Error checking device: {e}")
            return False

    # Page opening handlers
    def open_hand_gesture_page(self):
        """show and run hand gesture page/alg"""
        self.close_other_pages()
        self.hand_gesture_page = HandGestureRecognitionPage()
        self.hand_gesture_page.show()

    def open_facial_expression_page(self):
        """show and run face/emotion expression page/alg"""
        self.close_other_pages()
        self.facial_expression_page = FacialExpressionRecognitionPage()
        self.facial_expression_page.show()

    def open_object_detection_page(self):
        """show and run object detection page/alg, pass in title and description"""
        self.close_other_pages()
        self.object_detection_page = GeneralDemoPage("object")
        self.object_detection_page.show()

    def open_colour_detection_page(self):
        """show and run colour detection page/alg, pass in title and description"""
        self.close_other_pages()
        self.colour_detection_page = GeneralDemoPage("colour")
        self.colour_detection_page.show()

    def open_lidar_page(self):
        """show and run lidar page"""
        self.close_other_pages()
        print("LiDAR demo selected.")

    def open_thermal_page(self):
        """show and run thermal page"""
        self.close_other_pages()
        self.thermal_page=ThermalCameraPage()
        self.thermal_page.show()

    def open_counting_page(self):
        """show and run event camera high speed counting page/alg"""
        self.close_other_pages()
        print("Event Camera Counting demo selected.")

    def close_other_pages(self):
        """"close all other pages before opening another"""
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
            self.object_detection_page=None

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
        else:
            event.ignore()