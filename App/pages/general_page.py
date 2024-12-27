from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt


class GeneralDemoPage(QWidget):
    def __init__(self, title: str, description: str):
        super().__init__()
        self.setWindowTitle(title)

        # Main layout (horizontal layout for video and right panel)
        main_layout = QHBoxLayout(self)

        # Video Stream Section (Left)
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumSize(400, 300)  # Minimum size for the video area
        main_layout.addWidget(self.video_frame, stretch=3)

        # Right Panel (Output and Description)
        right_panel = QVBoxLayout()

        # Output Section (Top of Right Panel)
        self.output_label = QLabel("Output Here")
        self.output_label.setStyleSheet(
            "background-color: lightgray; font-size: 16px; padding: 10px;"
        )
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setFixedHeight(150)  # Optional: Adjust height as needed
        right_panel.addWidget(self.output_label, stretch=1)

        # Description Section (Bottom of Right Panel)
        self.description_label = QLabel(description)
        self.description_label.setStyleSheet("font-size: 18px; color: gray;")
        self.description_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.description_label.setWordWrap(True)
        right_panel.addWidget(self.description_label, stretch=2)

        # Add the right panel to the main layout
        main_layout.addLayout(right_panel, stretch=2)

        # Set the main layout
        self.setLayout(main_layout)
