"""Facial expression page opened from home_Page.ui"""
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt

from Algorithms.Body.emotion_recognition import EmotionRecognizer
from utils import load_stylesheet, close_event

class FacialExpressionRecognitionPage(QWidget):
    """Emotion Recognition"""
    def __init__(self):
        super().__init__()
        emoji_paths = {
            'happy': 'Datasets/Emojis/happy.png',
            'sad': 'Datasets/Emojis/sad.png',
            'angry': 'Datasets/Emojis/angry.png',
            'surprise': 'Datasets/Emojis/surprised.png',
            'fear': 'Datasets/Emojis/fear.png',
            'neutral': 'Datasets/Emojis/neutral.png',
            'disgust': 'Datasets/Emojis/disgust.png',
        }

        self.expression_recognizer = EmotionRecognizer(emoji_paths)
        self.setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        load_stylesheet(self, 'App/styles/facial_expression.qss')

    def setup_ui(self):
        """Setup face expression page UI"""
        self.setWindowTitle("Facial Expression Recognition")

        main_layout = QHBoxLayout()

        # Left panel for the video feed
        left_layout = QVBoxLayout()
        left_layout.addStretch()
        self.video_feed = QLabel()
        self.video_feed.setObjectName("video_feed")
        self.video_feed.setScaledContents(True)
        self.video_feed.setFixedSize(800, 800)  # More square aspect ratio
        self.video_feed.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_feed, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # Right panel for emoji display and description
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Align content to top and center horizontally

        emoji_layout = QVBoxLayout()  # Sub-layout to center emoji and label horizontally
        emoji_layout.setAlignment(Qt.AlignHCenter)  # Align horizontally center

        self.emoji_label = QLabel("Expression:")
        self.emoji_label.setObjectName("emoji_label")
        self.emoji_label.setAlignment(Qt.AlignCenter)

        self.face_emoji = QLabel()
        self.face_emoji.setFixedSize(500, 500)
        self.face_emoji.setObjectName("emoji_img")
        self.face_emoji.setScaledContents(True)
        self.face_emoji.setAlignment(Qt.AlignCenter)

        # Add emoji label and image to sub-layout
        emoji_layout.addWidget(self.emoji_label)
        emoji_layout.addWidget(self.face_emoji)

        # Add emoji section to the right layout
        right_layout.addLayout(emoji_layout)  

        # Instruction label positioned near the top
        self.discription = QLabel("Make one of the following faces: 😊☹️😨😠😮🤢\n"
                                "(Happy, Sad, Scared, Angry, Surprised, Disgusted)\n"
                                "\nFacial expression recognition begins by detecting a"
                                " face in the camera frame. Key facial landmarks, such as the eyes, eyebrows, nose, and mouth, are then "
                                "identified. The system analyzes the positions and movements of these landmarks to classify expressions"
                                " like happiness, sadness, anger, or surprise.")
        self.discription.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.discription.setObjectName("description")
        self.discription.setWordWrap(True)
        self.discription.setMaximumWidth(600)

        # Add description after emoji section, also centered horizontally
        right_layout.addWidget(self.discription, alignment=Qt.AlignTop | Qt.AlignLeft)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def update_frame(self):
        """Update frames from video stream and detected emotion"""
        result = self.expression_recognizer.process_frame()
        if result:
            self.video_feed.setPixmap(self._convert_cv_to_qt(result.main_frame))
            self.face_emoji.setPixmap(self._convert_cv_to_qt(result.emoji))

    def _convert_cv_to_qt(self, cv_img):
        """Convert cv2 img to QPixmap for display in QLabel"""
        if cv_img is None:
            return QPixmap()
        if len(cv_img.shape) == 2:  # Grayscale
            h, w = cv_img.shape
            qt_image = QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8)
        else:  # Color
            h, w, ch = cv_img.shape
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)

    def release(self):
        """Release resources properly"""
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

    def closeEvent(self, event):
        """Handle close event to release resources"""
        close_event(event, self)
