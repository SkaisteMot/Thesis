from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap

class HandGestureRecognitionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Gesture Recognition")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        self.left_hand_label = QLabel("Left Hand Gesture:")
        self.left_hand_emoji = QLabel()
        left_layout.addWidget(self.left_hand_label)
        left_layout.addWidget(self.left_hand_emoji)

        self.stream_frame = QFrame()
        self.stream_frame.setStyleSheet("background-color: black;")
        self.stream_frame.setFixedSize(400, 600)

        right_layout = QVBoxLayout()
        self.right_hand_label = QLabel("Right Hand Gesture:")
        self.right_hand_emoji = QLabel()
        right_layout.addWidget(self.right_hand_label)
        right_layout.addWidget(self.right_hand_emoji)

        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.stream_frame)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def update_emojis(self, left_emoji_path, right_emoji_path):
        self.left_hand_emoji.setPixmap(QPixmap(left_emoji_path))
        self.right_hand_emoji.setPixmap(QPixmap(right_emoji_path))
