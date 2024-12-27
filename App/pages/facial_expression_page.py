from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap

class FacialExpressionRecognitionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facial Expression Recognition")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()

        self.stream_frame = QFrame()
        self.stream_frame.setStyleSheet("background-color: black;")
        self.stream_frame.setFixedSize(400, 600)

        emoji_layout = QVBoxLayout()
        self.emoji_label = QLabel("Expression:")
        self.face_emoji = QLabel()
        emoji_layout.addWidget(self.emoji_label)
        emoji_layout.addWidget(self.face_emoji)

        main_layout.addWidget(self.stream_frame)
        main_layout.addLayout(emoji_layout)

        self.setLayout(main_layout)

    def update_emojis(self, emoji_path):
        self.face_emoji.setPixmap(QPixmap(emoji_path))
