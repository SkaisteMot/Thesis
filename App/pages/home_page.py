from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt
from .hand_gesture_page import HandGestureRecognitionPage

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SensorFusion: Home")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QHBoxLayout()

        # Left layout for logo and introduction
        left_layout = QVBoxLayout()

        # Logo using QSvgRenderer
        self.logo_label = QLabel(self)
        self.svg_renderer = QSvgRenderer("../Datasets/UGLogo.svg")  # Use SVG file path

        # Create a QPixmap from the SVG renderer
        desired_width = 150
        desired_height = int(desired_width / (self.svg_renderer.defaultSize().width() / self.svg_renderer.defaultSize().height()))

        # Set the logo pixmap by rendering the SVG
        pixmap = QPixmap(int((self.svg_renderer.defaultSize().width())/10) , int((self.svg_renderer.defaultSize().height())/10))
        pixmap.fill(Qt.transparent)  # Fill with transparent background

        # Create a painter to render the SVG onto the pixmap
        painter = QPainter(pixmap)
        self.svg_renderer.render(painter)
        painter.end()

        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)  # Allow scaling
        left_layout.addWidget(self.logo_label)

        # Introduction label
        welcome_label = QLabel("Welcome to SensorFusion", self)
        welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        left_layout.addWidget(welcome_label)

        # Add left layout to the main layout
        main_layout.addLayout(left_layout)

        # Layout for demo buttons
        button_layout = QVBoxLayout()
        demo_buttons = [
            ("Hand Gesture Recognition", self.open_hand_gesture_page),
            ("Facial Expression Recognition", self.open_facial_expression_page)
        ]

        for text, handler in demo_buttons:
            button = QPushButton(text, self)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        # Set the main layout
        self.setLayout(main_layout)

    def open_hand_gesture_page(self):
        self.hand_gesture_page = HandGestureRecognitionPage()
        self.hand_gesture_page.show()

    def open_facial_expression_page(self):
        print("Facial Expression Recognition demo selected")  # Placeholder for future implementation
