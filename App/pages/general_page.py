from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import sys
import os
import cv2

# Add the DevCode directory to the Python path
sys.path.append(os.path.abspath("C:\\Users\\skais\\ThesisProject\\DevCode"))
from Algorithms.Objects.colour_detection import ColourRecognizer
from Algorithms.Objects.object_detection import ObjectRecognizer

class GeneralDemoPage(QWidget):
    def __init__(self, title: str, description: str, algorithm: str):
        super().__init__()
        self.setWindowTitle(title)

        self.algorithm = algorithm
        if self.algorithm == "colour":
            self.recognizer = ColourRecognizer('../Datasets/colour_ranges.csv')
        elif self.algorithm == "object":
            self.recognizer = ObjectRecognizer('yolo11n.pt')

        # Main layout (horizontal layout for video right panel)
        main_layout = QHBoxLayout(self)

        # Video Stream Section (Left) - Change QFrame to QLabel
        self.video_label = QLabel()
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(400, 300)  # Minimum size for the video area
        main_layout.addWidget(self.video_label, stretch=3)

        # Right Panel (Output and Description)
        right_panel = QVBoxLayout()

        # Output Section (Top of Right Panel)
        self.output_label = QLabel("Output Here")
        self.output_label.setStyleSheet(
            "background-color: lightgray; font-size: 16px; padding: 10px;"
        )
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setFixedHeight(150)  # Optional: Adjust height as needed
        right_panel.addWidget(self.output_label, stretch=1)

        # Description Section (Bottom of Right Panel)
        self.description_label = QLabel(description)
        self.description_label.setStyleSheet("font-size: 18px; color: gray;")
        self.description_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.description_label.setWordWrap(True)
        right_panel.addWidget(self.description_label, stretch=2)

        # Add the right panel to the main layout
        main_layout.addLayout(right_panel, stretch=2)

        # Set the main layout
        self.setLayout(main_layout)

        # Start video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open video stream.")
            sys.exit()

        self.timer = self.startTimer(20)

    def timerEvent(self, event):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame.")
            return

        if self.algorithm == "colour":
            processed_frame = self.recognizer.detect_and_draw(frame)
        elif self.algorithm == "object":
            processed_frame = self.recognizer.detect_and_draw(frame)

        # Convert processed frame to QImage
        height, width, channel = processed_frame.shape
        bytes_per_line = 3 * width
        qimg = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_BGR888)

        # Update the video frame (using QLabel's setPixmap)
        pixmap = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # Release the video capture and stop the algorithm
        self.cap.release()

        # If the recognizer uses any other background tasks or threads, stop them here
        # For example, if there are timers or other resources, clean them up

        # Accept the close event (closes the window)
        event.accept()
