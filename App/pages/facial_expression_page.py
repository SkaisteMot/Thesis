"""Facial expression page opened from home_Page.ui"""
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtSvg import QSvgWidget

from Algorithms.Body.emotion_recognition import EmotionRecognizer
from utils import load_stylesheet, close_event

class FacialExpressionRecognitionPage(QWidget):
    """Emotion Recognition"""
    def __init__(self):
        super().__init__()
        self.expression_recognizer = EmotionRecognizer()
        self.emoji_icons = self._load_emojis()  # Load emojis in the UI class
        self.blank_image = QPixmap(200, 200)
        self.blank_image.fill(Qt.white)  # Blank white image for no emotion

        self.setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        load_stylesheet(self, 'App/styles/facial_expression.qss')

    def _load_emojis(self):
        """Load emoji images from file paths"""
        emoji_paths = {
            'happy': 'Datasets/Emojis/happy.png',
            'sad': 'Datasets/Emojis/sad.png',
            'angry': 'Datasets/Emojis/angry.png',
            'surprise': 'Datasets/Emojis/surprised.png',
            'fear': 'Datasets/Emojis/fear.png',
            'neutral': 'Datasets/Emojis/neutral.png',
            'disgust': 'Datasets/Emojis/disgust.png',
        }

        emojis = {}
        for expression, path in emoji_paths.items():
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"Warning: Could not load emoji {path}")
            else:
                emojis[expression] = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        return emojis

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
        self.video_feed.setFixedSize(900, 900)
        self.video_feed.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.video_feed, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # Right panel for emoji display
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        emoji_layout = QVBoxLayout()
        emoji_layout.setAlignment(Qt.AlignHCenter)

        self.emoji_label = QLabel("Expression:")
        self.emoji_label.setObjectName("emoji_label")
        self.emoji_label.setAlignment(Qt.AlignCenter)

        self.face_emoji = QLabel()
        self.face_emoji.setFixedSize(500, 500)
        self.face_emoji.setObjectName("emoji_img")
        self.face_emoji.setScaledContents(True)
        self.face_emoji.setAlignment(Qt.AlignCenter)

        
        self.qr_code=QSvgWidget("Datasets/QRcodes/rgb_QR.svg")
        self.qr_label=QLabel("Scan this to learn more about RGB cameras!")
        self.qr_code.setFixedSize(150,150)
        self.qr_label.setObjectName("description")
        self.qr_label.setWordWrap(True)
        self.qr_label.setFixedSize(750,150)

        qr_layout=QHBoxLayout()
        qr_layout.addWidget(self.qr_code, alignment=Qt.AlignLeft)
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignHCenter)

        emoji_layout.addWidget(self.emoji_label)
        emoji_layout.addWidget(self.face_emoji)
        right_layout.addLayout(emoji_layout)

        # Instruction label
        self.description = QLabel("Make one of the following faces: 😊☹️😨😠😮🤢\n"
                                  "(Happy, Sad, Scared, Angry, Surprised, Disgusted)\n"
                                  "\nFacial expression recognition begins by detecting a"
                                  " face in the camera frame. Key facial landmarks, such as the eyes, eyebrows, nose, and mouth, are then "
                                  "identified. The system analyzes the positions and movements of these landmarks to classify expressions"
                                  " like happiness, sadness, anger, or surprise.")
        self.description.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.description.setObjectName("description")
        self.description.setWordWrap(True)
        self.description.setMaximumWidth(900)
        right_layout.addWidget(self.description, alignment=Qt.AlignTop | Qt.AlignLeft)
        right_layout.addStretch()
        right_layout.addLayout(qr_layout)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def update_frame(self):
        """Update frames from video stream and detected emotion"""
        result = self.expression_recognizer.process_frame()
        if result:
            self.video_feed.setPixmap(self._convert_cv_to_qt(result.main_frame))
            self.face_emoji.setPixmap(self.emoji_icons.get(result.emotion_text, self.blank_image))

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
