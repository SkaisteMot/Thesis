import sys
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from utils import load_stylesheet, close_event

class LidarCameraPage(QWidget):
    """Lidar Camera Streaming Page"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiDAR Camera Stream")
        self.setGeometry(100, 100, 800, 600)

        # Main layout (horizontal split)
        self.main_layout = QHBoxLayout()

        # Left side: LiDAR feed
        self.video_layout = QVBoxLayout()
        self.LiDAR_feed = QLabel()
        self.LiDAR_feed.setObjectName("LiDAR_feed")
        self.LiDAR_feed.setAlignment(Qt.AlignCenter)
        self.LiDAR_feed.setScaledContents(True)
        self.video_layout.addWidget(self.LiDAR_feed)
        
        # Right side: Title and description
        self.info_layout = QVBoxLayout()
        self.title_label = QLabel("LiDAR Camera Stream")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title_label")
        
        self.description_label = QLabel("This page displays a real-time LiDAR camera feed from CeptonViewer.")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setObjectName("description_label")
        
        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.description_label)
        self.info_layout.addStretch()
        
        # Add sections to main layout
        self.main_layout.addLayout(self.video_layout, 1)  # 50% width
        self.main_layout.addLayout(self.info_layout, 1)  # 50% width
        self.setLayout(self.main_layout)

        # Load stylesheet
        # load_stylesheet(self, "App/styles/LiDAR_camera.qss")
        
        # Initialize and run the CeptonViewer stream
        self.run_cepton_viewer()

    def run_cepton_viewer(self):
        """Launch CeptonViewer as a separate process"""
        try:
            # PowerShell script to launch CeptonViewer
            ps_script = '''start "C:\\Program Files\\cepton_sdk\\bin\\CeptonViewer.exe"'''
            subprocess.Popen(['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script])
            print("Successfully launched CeptonViewer.")
        except Exception as e:
            print(f"Error launching CeptonViewer: {e}")
    
    def closeEvent(self, event):
        """Handle close event to release resources"""
        close_event(event, self)
