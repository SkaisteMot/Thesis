"""Page that is used when only a stream is outputted, object detection, colour detection etc"""
from os import close
import sys
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage

from Algorithms.Objects.colour_detection import ColourRecognizer
from Algorithms.Objects.object_detection import ObjectRecognizer
from utils import load_stylesheet,close_event
from PyQt5.QtCore import QTimer, Qt

class GeneralDemoPage(QWidget):
    """Page used for general display of streams"""
    def __init__(self, algorithm: str):
        super().__init__()

        self.algorithm = algorithm
        if self.algorithm == "colour":
            self.setWindowTitle("Colour Detection")
            self.recognizer = ColourRecognizer('Datasets/colour_ranges.csv')
            instructions = "Hold up one of the following colours:"
            description = ("The program detects colours in an image using predefined colour ranges. It "
                           "first creates a mask to highlight areas that match each colour. Then, it "
                           "finds the boundaries of these colour regions and draws outlines around them, "
                           "making it easy to identify and count different colours in the video.")

        elif self.algorithm == "object":
            self.setWindowTitle("Object Detection")
            instructions = "Hold up an object to detect and classify"
            self.recognizer = ObjectRecognizer('yolo11n.pt')
            description = ("YOLO is a fast object detection system that processes an image by dividing "
                           "it into a grid. Each grid cell predicts whether an object is present and, "
                           "if so, draws a box around it. The image passes through multiple layers of a "
                           "neural network, where early layers detect simple features like edges, while "
                           "deeper layers recognize complex patterns and object shapes. Each grid cell "
                           "outputs bounding boxes, confidence scores (how sure the model is about "
                           "the detection), and class labels. This allows YOLO to quickly "
                           "and accurately detect multiple objects in an image.")

        # Main layout
        main_layout = QHBoxLayout(self)

        # Video Stream Section (Left)
        self.video_label = QLabel()
        self.video_label.setObjectName("video_label")
        self.video_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.video_label, stretch=3)

        # Right Panel (Output and Description)
        right_panel = QVBoxLayout()

        # Output Section
        self.output_label = QLabel(instructions)
        self.output_label.setObjectName("output_label")
        self.output_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.output_label, stretch=1)

        # Description Section
        self.description_label = QLabel(description)
        self.description_label.setObjectName("description_label")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        right_panel.addWidget(self.description_label, stretch=2)

        # Add right panel to the main layout
        main_layout.addLayout(right_panel, stretch=2)
        self.setLayout(main_layout)

        # Load stylesheet
        load_stylesheet(self, 'App/styles/general.qss')

        # Start video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open video stream.")
            sys.exit()

        self.failed_frames = 0  # Counter for consecutive failed frames

        # Start Timer to Refresh Video Feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)  # 20ms interval

    def update_frame(self):
        """Capture and process frames for display"""
        ret, frame = self.cap.read()
        if not ret:
            self.failed_frames += 1
            print(f"Failed to grab frame {self.failed_frames} times.")

            if self.failed_frames > 10:
                print("Too many failed frames. Stopping the stream.")
                self.close()
            return

        self.failed_frames = 0  # Reset counter on successful capture

        # Apply the selected algorithm
        if self.algorithm == "colour":
            processed_frame = self.recognizer.detect_and_draw(frame)
        elif self.algorithm == "object":
            processed_frame = self.recognizer.detect_and_draw(frame)
        else:
            processed_frame = frame  # Fallback to original frame

        # Convert processed frame to QImage
        height, width, channels = processed_frame.shape  # Ensure all dimensions are captured
        bytes_per_line = channels * width
        qimg = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_BGR888)

        # Update QLabel with new frame
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        """Handle window close event to release resources"""
        self.cap.release()
        self.timer.stop()
        close_event(event, self)
