"""Facial expression page opened from home_Page.ui"""
import sys
import os
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import  QTimer, Qt

sys.path.append(os.path.abspath("C:\\Users\\skais\\ThesisProject\\DevCode"))
from Algorithms.Body.emotion_recognition import EmotionRecognizer

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

        self.load_stylesheet()

    def setup_ui(self):
        """setup face expression page ui"""
        self.setWindowTitle("Facial Expression Recognition")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()

        # Left panel for the video feed
        left_layout = QVBoxLayout()
        self.video_feed = QLabel()
        self.video_feed.setObjectName("video_feed")
        self.video_feed.setScaledContents(True)
        left_layout.addWidget(self.video_feed)
        left_layout.addStretch()

        # Right panel for emoji display
        right_layout = QVBoxLayout()
        self.emoji_label = QLabel("Expression:")
        self.emoji_label.setObjectName("emoji_label")
        self.face_emoji = QLabel()
        self.face_emoji.setObjectName("emoji_img")
        self.face_emoji.setScaledContents(True)
        self.face_emoji.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.emoji_label)
        right_layout.addWidget(self.face_emoji)
        right_layout.addStretch()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def load_stylesheet(self):
        """Load the stylesheet for the page."""
        with open("App/styles/facial_expression.qss", "r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

    def update_frame(self):
        """update frames from video stream and detected emotion"""
        result = self.expression_recognizer.process_frame()
        if result:
            self.video_feed.setPixmap(self._convert_cv_to_qt(result.main_frame))
            self.face_emoji.setPixmap(self._convert_cv_to_qt(result.emoji))

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
        return QPixmap.fromImage(qt_image)

    def close_event(self, event):
        """handle close event to release resources"""
        self.expression_recognizer.release()
        event.accept()
