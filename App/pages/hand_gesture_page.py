# hand_gesture_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt

import sys
import os

# Add the DevCode directory to the Python path
sys.path.append(os.path.abspath("C:\\Users\\skais\\ThesisProject\\DevCode"))
from Algorithms.Body.hand_gesture_test import GestureRecognizer

import cv2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap

        icon_paths = {
            'Thumb_Up': '../Datasets/HandIcons/thumbs_up.png',
            'Thumb_Down': '../Datasets/HandIcons/thumbs_down.png',
            'Pointing_Up': '../Datasets/HandIcons/point_up.png',
            'Victory': '../Datasets/HandIcons/peace.png',
            'Closed_Fist': '../Datasets/HandIcons/fist.png',
            'Open_Palm': '../Datasets/HandIcons/wave.png',
            'ILoveYou': '../Datasets/HandIcons/rock.png'
        }
        self.gesture_recognizer = GestureRecognizer(icon_paths)
        self.setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def setup_ui(self):
        self.setWindowTitle("Hand Gesture Recognition")
        self.setGeometry(100, 100, 1200, 600)

        main_layout = QHBoxLayout()

        # Left panel
        left_layout = QVBoxLayout()
        self.left_label = QLabel("Left Hand:")
        self.left_emoji = QLabel()
        self.left_emoji.setFixedSize(200, 200)
        self.left_emoji.setScaledContents(True)
        self.left_emoji.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.left_label)
        left_layout.addWidget(self.left_emoji)
        left_layout.addStretch()

        # Center video feed
        self.video_feed = QLabel()
        self.video_feed.setFixedSize(640, 480)
        self.video_feed.setScaledContents(True)

        # Right panel
        right_layout = QVBoxLayout()
        self.right_label = QLabel("Right Hand:")
        self.right_emoji = QLabel()
        self.right_emoji.setFixedSize(200, 200)
        self.right_emoji.setScaledContents(True)
        self.right_emoji.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.right_label)
        right_layout.addWidget(self.right_emoji)
        right_layout.addStretch()

        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.video_feed)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def update_frame(self):
        result = self.gesture_recognizer.process_frame()
        if result:
            self.video_feed.setPixmap(self._convert_cv_to_qt(result.main_frame))
            self.left_emoji.setPixmap(self._convert_cv_to_qt(result.left_emoji))
            self.right_emoji.setPixmap(self._convert_cv_to_qt(result.right_emoji))

    def _convert_cv_to_qt(self, cv_img):
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


    def closeEvent(self, event):
        self.gesture_recognizer.release()
        event.accept()
"""
def main():
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = HandGestureRecognitionPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    """