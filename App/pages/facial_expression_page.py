"""Facial expression page opened from home_Page.ui"""
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QTimer, Qt
from Algorithms.Body.emotion_recognition import EmotionRecogniser
from utils import load_stylesheet, close_event, QRCodeWidget

class FacialExpressionRecognitionPage(QWidget):
    """Emotion Recognition"""
    def __init__(self):
        super().__init__()
        self.expression_recogniser = EmotionRecogniser()
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

        # Instruction label
        self.instructions = QLabel(
            "Make one of the following faces: 😊☹️😨😠😮🤢\n"
            "(Happy, Sad, Scared, Angry, Surprised, Disgusted)\n"
        )
        self.instructions.setFont(QFont("Segoe UI Emoji"))
        self.instructions.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.instructions.setObjectName("instructions")
        self.instructions.setWordWrap(True)
        #self.instructions.setMaximumWidth(900)

        self.description=QLabel(
            "\nFacial expression recognition begins by detecting a"
            " face in the camera frame. Key facial landmarks, such "
            "as the eyes, eyebrows, nose, and mouth, are then "
            "identified. The system analyzes the positions and movements "
            "of these landmarks to classify expressions"
            " like happiness, sadness, anger, or surprise.")
        self.description.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.description.setObjectName("description")
        self.description.setWordWrap(True)
        self.description.setMaximumWidth(900)

        self.qr_widget=QRCodeWidget("Datasets/QRcodes/rgb_QR.svg",
                                    "Scan this to learn more about RGB cameras!",
                                    label_width=750)

        emoji_layout.addWidget(self.emoji_label)
        emoji_layout.addWidget(self.face_emoji)
        right_layout.addLayout(emoji_layout)
        right_layout.addWidget(self.instructions)
        right_layout.addWidget(self.description, alignment=Qt.AlignTop | Qt.AlignLeft)
        right_layout.addStretch()
        right_layout.addWidget(self.qr_widget)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def update_frame(self):
        """Update frames from video stream and detected emotion"""
        result = self.expression_recogniser.process_frame()
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

    def use_close_event(self, event):
        """Handle close event to release resources"""
        close_event(event, self)
