"""Page that is used when only a stream is outputted, object detection, colour detection etc"""
from os import close
import sys
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtSvg import QSvgWidget

from Algorithms.Objects.colour_detection import ColourRecognizer
from Algorithms.Objects.object_detection import ObjectRecognizer
from utils import load_stylesheet,close_event
from PyQt5.QtCore import QTimer, Qt

from PyQt5.QtGui import QPixmap, QImage, QFontMetrics, QFont

class GeneralDemoPage(QWidget):
    """Page used for general display of streams"""
    def __init__(self, algorithm: str):
        super().__init__()

        self.algorithm = algorithm
        if self.algorithm == "colour":
            self.title="Colour Detection"
            self.recognizer = ColourRecognizer('Datasets/colour_ranges.csv')
            self.instructions = "Hold up one of the following colours: Red, Blue, Yellow, Green, Purple" ##change this to autofill based on csv
            self.description = ("The program detects colours in an image using predefined colour ranges. It "
                           "first creates a mask to highlight areas that match each colour. Then, it "
                           "finds the boundaries of these colour regions and draws outlines around them, "
                           "making it easy to identify and count different colours in the video.")
        elif self.algorithm == "object":
            self.title="Object Detection"
            self.instructions = "Hold up an object to detect and classify"
            self.recognizer = ObjectRecognizer('yolo11n.pt')
            self.description = ("YOLO is a fast object detection system that processes an image by dividing "
                           "it into a grid. Each grid cell predicts whether an object is present and, "
                           "if so, draws a box around it. The image passes through multiple layers of a "
                           "neural network, where early layers detect simple features like edges, while "
                           "deeper layers recognize complex patterns and object shapes. Each grid cell "
                           "outputs bounding boxes, confidence scores (how sure the model is about "
                           "the detection), and class labels. This allows YOLO to quickly "
                           "and accurately detect multiple objects in an image.")

        self.setup_ui()

    def setup_ui(self):
        """setup general page ui"""
        self.setWindowTitle(self.title)
        # Main layout
        main_layout = QHBoxLayout()

         # Left panel for the video feed
        left_layout = QVBoxLayout()
        left_layout.addStretch()
        self.video_feed = QLabel()
        self.video_feed.setObjectName("video_feed")
        self.video_feed.setScaledContents(True)
        self.video_feed.setFixedSize(900, 900)
        self.video_feed.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_feed, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # Right Panel (Instruction and Description)
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        #Instruction Section
        self.instruction_label = QLabel(self.instructions)
        self.instruction_label.setObjectName("instructions")
        self.instruction_label.setAlignment(Qt.AlignTop |Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)  # Allow text to wrap
        self.instruction_label.setMaximumWidth(800)
        self.adjust_instructions_height()  # Adjust height based on text

        # Description Section
        self.description_label = QLabel(self.description)
        self.description_label.setObjectName("description")
        self.instruction_label.setMaximumWidth(800)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        #QR
        self.qr_code=QSvgWidget("Datasets/QRcodes/rgb_QR.svg")
        self.qr_label=QLabel("Scan this to learn more about RGB cameras!")
        self.qr_code.setFixedSize(150,150)
        self.qr_label.setObjectName("description")
        self.qr_label.setWordWrap(True)
        self.qr_label.setFixedSize(650,150)

        qr_layout=QHBoxLayout()
        qr_layout.addWidget(self.qr_code, alignment=Qt.AlignLeft)
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignHCenter)

        right_layout.addWidget(self.instruction_label)
        right_layout.addWidget(self.description_label)
        right_layout.addStretch()
        right_layout.addLayout(qr_layout)

        # Add right panel to the main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
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

    def adjust_instructions_height(self):
        """Adjust output label height based on the text lines"""
        font = self.instruction_label.font()
        fm = QFontMetrics(font)
        text_height = fm.boundingRect(self.instruction_label.text()).height()
        self.instruction_label.setFixedHeight(text_height + 30)  # Add padding

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

        # Resize frame to match QLabel's minimum size
        frame = cv2.resize(frame, (self.video_feed.width(), self.video_feed.height()), interpolation=cv2.INTER_LINEAR)

        # Apply processing
        if self.algorithm == "colour":
            processed_frame = self.recognizer.detect_and_draw(frame)
        elif self.algorithm == "object":
            processed_frame = self.recognizer.detect_and_draw(frame)
        else:
            processed_frame = frame

        # Convert to QImage
        height, width, channels = processed_frame.shape
        bytes_per_line = channels * width
        qimg = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_BGR888)

        # Directly assign without scaling first
        pixmap = QPixmap.fromImage(qimg)
        self.video_feed.setPixmap(pixmap)

    def closeEvent(self, event):
        """Handle window close event to release resources"""
        self.cap.release()
        self.timer.stop()
        close_event(event, self)
