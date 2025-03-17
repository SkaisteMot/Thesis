"""page for hand gesture detection, opened from home_page.py button"""
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtSvg import QSvgWidget

from Algorithms.Body.hand_gesture_test import GestureRecognizer
from utils import load_stylesheet,close_event

class HandGestureRecognitionPage(QWidget):
    """Hand gesture recognizer"""
    def __init__(self):
        super().__init__()
        self.icon_paths = {
            'Thumb_Up': 'Datasets/HandIcons/thumbs_up.svg',
            'Thumb_Down': 'Datasets/HandIcons/thumbs_down.svg',
            'Pointing_Up': 'Datasets/HandIcons/point_up.svg',
            'Victory': 'Datasets/HandIcons/peace.svg',
            'Closed_Fist': 'Datasets/HandIcons/fist.svg',
            'Open_Palm': 'Datasets/HandIcons/wave.svg',
            'ILoveYou': 'Datasets/HandIcons/rock.svg'
        }

        self.blank_pixmap = QPixmap(200, 200)
        self.blank_pixmap.fill(Qt.white)

        self.gesture_recognizer = GestureRecognizer()
        self.setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        load_stylesheet(self,'App/styles/hand_gesture.qss')

    def setup_ui(self):
        """UI for hand page setup"""
        self.setWindowTitle("Hand Gesture Recognition")

        main_layout = QHBoxLayout()

        # Left panel
        left_layout = QVBoxLayout()
        self.left_label = QLabel("Hand 1:")
        self.left_label.setObjectName("label")
        self.left_emoji = QLabel()
        self.left_emoji.setObjectName("emoji")
        self.left_emoji.setScaledContents(True)
        self.left_emoji.setAlignment(Qt.AlignCenter)
        self.left_emoji.setFixedSize(400, 400)  # Ensure emoji box is square

        self.left_instruction = QLabel("Hold up one or two of the following gestures: 👍👎✌️☝️✊👋🤟\n\n"
                                    "(Thumbs up, Thumbs down, Peace, Point up, Wave, Rock )")
        self.left_instruction.setAlignment(Qt.AlignCenter)  # Centering instruction text
        self.left_instruction.setWordWrap(True)
        self.left_instruction.setMaximumWidth(500)
        self.left_instruction.setFixedSize(500,100)
        self.left_instruction.setObjectName("instructions")

        self.qr_code=QSvgWidget("Datasets/QRcodes/rgb_QR.svg")
        self.qr_label=QLabel("Scan this to learn more about RGB cameras!")
        self.qr_code.setFixedSize(150,150)
        self.qr_label.setObjectName("instructions")
        self.qr_label.setWordWrap(True)
        self.qr_label.setFixedSize(350,150)

        qr_layout=QHBoxLayout()
        qr_layout.addWidget(self.qr_code, alignment=Qt.AlignLeft)
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignHCenter)

        left_layout.addWidget(self.left_label, alignment=Qt.AlignHCenter)
        left_layout.addWidget(self.left_emoji, alignment=Qt.AlignHCenter)
        left_layout.addWidget(self.left_instruction, alignment=Qt.AlignHCenter)
        left_layout.addStretch()
        left_layout.addLayout(qr_layout)

        # Center video feed
        self.video_feed = QLabel()
        self.video_feed.setObjectName("video_feed")
        self.video_feed.setScaledContents(True)
        self.video_feed.setMinimumWidth(700)  # Ensuring the video feed is wide
        self.video_feed.setMinimumHeight(500)

        # Right panel
        right_layout = QVBoxLayout()
        self.right_label = QLabel("Hand 2:")
        self.right_label.setObjectName("label")
        self.right_emoji = QLabel()
        self.right_emoji.setObjectName("emoji")
        self.right_emoji.setScaledContents(True)
        self.right_emoji.setAlignment(Qt.AlignCenter)
        self.right_emoji.setFixedSize(400, 400)  # Ensure emoji box is square

        self.right_instruction = QLabel("Hand gesture recognition starts with detecting hands in the camera frame using a palm detection model."
                                        " Once a hand is found, a landmark model identifies 21 key points, including fingertips, knuckles, and the wrist."
                                        " These key points are then analyzed to classify different gestures based on their positions and movements.")
        self.right_instruction.setAlignment(Qt.AlignCenter)  # Centering instruction text
        self.right_instruction.setWordWrap(True)
        self.right_instruction.setMaximumWidth(500)
        self.right_instruction.setObjectName("instructions")

        right_layout.addWidget(self.right_label, alignment=Qt.AlignHCenter)
        right_layout.addWidget(self.right_emoji, alignment=Qt.AlignHCenter)
        right_layout.addWidget(self.right_instruction, alignment=Qt.AlignHCenter)
        right_layout.addStretch()

        # Distribute space properly
        main_layout.addLayout(left_layout, 1)  # Left panel takes equal space
        main_layout.addWidget(self.video_feed, 2)  # Make the video feed take more space
        main_layout.addLayout(right_layout, 1)  # Right panel takes equal space
        self.setLayout(main_layout)

    def update_frame(self):
        """Update the video feed and hand gesture icons"""
        result = self.gesture_recognizer.process_frame()
        if result:
            self.video_feed.setPixmap(self._convert_cv_to_qt(result.main_frame))
            self.left_emoji.setPixmap(self._get_icon(result.left_label))
            self.right_emoji.setPixmap(self._get_icon(result.right_label))

    def _get_icon(self, label):
        """Retrieve the correct icon based on the label"""
        if label in self.icon_paths:
            return QPixmap(self.icon_paths[label])
        return self.blank_pixmap  # Return blank image if label not found


    def _convert_cv_to_qt(self, cv_img):
        """convert cv2 img to qpixmap for display in qlabel"""
        if cv_img is None:
            return QPixmap()
        if len(cv_img.shape) == 2:  # Grayscale
            h, w = cv_img.shape
            qt_image = QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8)
        else:  # Color
            h, w, ch = cv_img.shape
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)
        return pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Keep emoji aspect ratio

    def call_close_event(self, event):
        """handle close event to release resources"""
        close_event(event,self)
