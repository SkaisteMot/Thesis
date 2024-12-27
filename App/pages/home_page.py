import win32com.client
from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QWidget,
    QSizePolicy,
    QHBoxLayout,
)
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer
from .hand_gesture_page import HandGestureRecognitionPage
from .facial_expression_page import FacialExpressionRecognitionPage
from .general_page import GeneralDemoPage


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SensorFusion: Home")
        self.load_styles()

        # Main layout
        main_layout = QGridLayout()

        self.setLayout(main_layout)

        # SVG Renderer for the logo
        self.svg_renderer = QSvgRenderer("../Datasets/UGLogo.svg")

        # Logo in the top-left corner
        self.logo_label = QLabel(self)
        self.logo_label.setStyleSheet("background-color: blue;")
        main_layout.addWidget(self.logo_label, 0, 0, 1, 1, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Title and introduction below the logo
        intro_container = QWidget()
        intro_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        intro_container.setObjectName("intro_container")  # Add object name for styling
        intro_container.setStyleSheet("background-color: green;")
        intro_layout = QVBoxLayout()
        title_label = QLabel("Welcome to SensorFusion", self)
        title_label.setObjectName("title")  # For styling via QSS
        intro_label = QLabel("Explore multi-sensor demos with cutting-edge technology!", self)
        intro_label.setObjectName("intro_label")  # Add object name for styling
        intro_label.setWordWrap(True)  # Allow wrapping of long text
        intro_container.setLayout(intro_layout)
        intro_layout.addWidget(title_label)
        intro_layout.addWidget(intro_label)
        main_layout.addWidget(intro_container, 1, 0, 1, 1, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Demo buttons on the right side
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout()
        self.buttons = []  # Store buttons to resize dynamically
        demo_buttons = [
            ("Hand Gesture Recognition", self.open_hand_gesture_page),
            ("Facial Expression Recognition", self.open_facial_expression_page),
            ("Object Detection", self.open_object_detection_page),
            ("Colour Detection", self.open_colour_detection_page),
            ("LiDAR", self.open_lidar_page),
            ("Thermal", self.open_thermal_page),
            ("High Speed Counting", self.open_counting_page),
        ]

        for text, handler in demo_buttons:
            button = QPushButton(text, self)
            button.setObjectName("button")  # Add object name for styling
            button.clicked.connect(handler)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.button_layout.addWidget(button)
            self.buttons.append(button)

        self.button_container.setLayout(self.button_layout)
        main_layout.addWidget(self.button_container, 0, 1, 3, 1, alignment=Qt.AlignCenter)

        # Connection status at the bottom-left
        self.connection_status_container = QWidget()
        self.connection_status_layout = QHBoxLayout()
        self.connection_status_container.setLayout(self.connection_status_layout)

        self.mouse_status = QLabel(self)
        self.keyboard_status = QLabel(self)
        self.mouse_status.setAlignment(Qt.AlignCenter)
        self.keyboard_status.setAlignment(Qt.AlignCenter)

        self.connection_status_layout.addWidget(QLabel("Mouse:"))
        self.connection_status_layout.addWidget(self.mouse_status)
        self.connection_status_layout.addWidget(QLabel("Keyboard:"))
        self.connection_status_layout.addWidget(self.keyboard_status)
        self.set_status_to_searching()

        main_layout.addWidget(
            self.connection_status_container, 2, 0, 1, 1, alignment=Qt.AlignBottom | Qt.AlignLeft
        )

        # Timer to update connection status
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.update_connection_status)
        self.connection_timer.start(2000)  # Check every 2 seconds

    def load_styles(self):
        with open("styles/base.qss", "r") as file:
            self.setStyleSheet(file.read())

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
        """Check actual connection status for mouse and keyboard."""

        mouse_connected = self.is_device_connected("notconnectedNonesense")  # Modify this for your device
        keyboard_connected = self.is_device_connected("HXC32A99K_V2")  # Modify this for your device
        #USB\VID_2F81&PID_2108\HXC32A99K_V2

        # Update the mouse status
        if mouse_connected:
            self.mouse_status.setPixmap(self.draw_circle("green"))
        else:
            self.mouse_status.setPixmap(self.draw_circle("red"))

        # Update the keyboard status
        if keyboard_connected:
            self.keyboard_status.setPixmap(self.draw_circle("green"))
        else:
            self.keyboard_status.setPixmap(self.draw_circle("red"))

    def set_status_to_searching(self):
        """Set both mouse and keyboard status to searching (yellow/orange) while loading."""
        self.mouse_status.setPixmap(self.draw_circle("orange"))
        self.keyboard_status.setPixmap(self.draw_circle("orange"))

    def is_device_connected(self, device_name):
        """Check if a device is connected by its name."""
        wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")

        # Modify the query to check if device_name appears in the device name or DeviceID
        query = "SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%{}%'".format(device_name)
        devices = wmi.ExecQuery(query)

        # If the query returns any matching device, it means the device is connected
        return any(device.DeviceID for device in devices)

    def render_logo(self, width, height):
        """Render the SVG logo to a QPixmap of specified dimensions."""
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)  # Transparent background
        painter = QPainter(pixmap)
        self.svg_renderer.render(painter)
        painter.end()
        return pixmap

    def resizeEvent(self, event):
        """Dynamically update the logo and buttons size based on the window dimensions."""
        window_height = self.height()
        window_width = self.width()

        # Logo: Height is 1/5th of the window height
        desired_logo_height = int(window_height / 5)
        aspect_ratio = self.svg_renderer.defaultSize().width() / self.svg_renderer.defaultSize().height()
        desired_logo_width = int(desired_logo_height * aspect_ratio)
        pixmap = self.render_logo(desired_logo_width, desired_logo_height)
        self.logo_label.setPixmap(pixmap)

        # Buttons: Adjust font size and margins
        button_height = int(window_height / 10)
        button_width = int(window_width / 4)
        font_size = max(12, int(window_height / 40))  # Dynamically adjust font size

        for button in self.buttons:
            button.setFixedSize(button_width, button_height)
            button.setFont(QFont("Arial", font_size))

        super().resizeEvent(event)

    # Handlers for demo buttons
    def open_hand_gesture_page(self):
        self.hand_gesture_page=HandGestureRecognitionPage()
        self.hand_gesture_page.show()

    def open_facial_expression_page(self):
        self.facial_expression_page=FacialExpressionRecognitionPage()
        self.facial_expression_page.show()

    def open_object_detection_page(self):
        self.object_detection_page=GeneralDemoPage("Object Detection","dummy description","object")
        self.object_detection_page.show()

    def open_colour_detection_page(self):
        self.colour_detection_page=GeneralDemoPage("Colour Detection","dummy description","colour")
        self.colour_detection_page.show()

    def open_lidar_page(self):
        print("LiDAR demo selected.")

    def open_thermal_page(self):
        print("Thermal demo selected.")

    def open_counting_page(self):
        print("Event Camera Counting demo selected.")
