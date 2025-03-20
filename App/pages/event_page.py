"""Event page"""
import os
import subprocess
import time
import threading
import pygetwindow as gw
import pyautogui
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from utils import load_stylesheet, close_event

class EventCameraPage(QWidget):
    """Prophesee Viewer Integration Page with Auto-Start"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Camera Stream")

        self.xming_process = None
        self.ssh_process = None
        self.is_running = False

        self.setup_ui()

        QTimer.singleShot(100, self.start_prophesee_viewer)

    def setup_ui(self):
        """Setup UI"""
        # Load stylesheet
        load_stylesheet(self, "App/styles/sensors.qss")

        self.layout = QHBoxLayout()  # Horizontal layout
        self.layout.setAlignment(Qt.AlignRight)  # Align everything to the right

        self.status_label = QLabel("Starting Event Camera Stream...")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to right
        self.status_label.setObjectName("status_label")

        self.description=QLabel(
            "An event camera is a neuromorphic sensor that detects changes "
            "in brightness at each pixel instead of capturing full images at "
            "a fixed rate. Each pixel operates independently, generating an 'event'"
            " only when a brightness change occurs, allowing for ultra-fast response "
            "times, low power consumption, and high dynamic range. This makes event "
            "cameras ideal for applications requiring real-time motion detection, such "
            "as robotics, autonomous vehicles, and high-speed tracking, especially in "
            "challenging lighting conditions. Inspired by the human eye, they efficiently"
            " capture dynamic scenes with minimal data redundancy.")
        self.description.setWordWrap(True)
        self.description.setObjectName("description")

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.description)

        # Set layout
        container = QWidget()
        container.setLayout(self.layout)
        self.setLayout(self.layout)

    def start_prophesee_viewer(self):
        """Start the Prophesee Viewer automatically"""
        if not self.is_running:
            self.is_running = True
            self.status_label.setText("Starting Event Camera Stream...")
            thread = threading.Thread(target=self._run_prophesee_setup)
            thread.daemon = True
            thread.start()

    def _run_prophesee_setup(self):
        """Run the Prophesee setup in a separate thread"""
        try:
            # Hide command line window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # Start Xming
            xming_path = "C:\\Program Files (x86)\\Xming\\Xming.exe"
            if not os.path.exists(xming_path):
                self.update_status("Error: Xming not found.")
                return

            self.xming_process = subprocess.Popen(
                [xming_path, ":0", "-clipboard", "-multiwindow"],
                startupinfo=startupinfo
            )

            self.update_status("Initializing X server...")
            time.sleep(3)

            # Maximize Xming to left half
            self.maximize_xming_left()

            # Set DISPLAY and run SSH command
            self.update_status("Connecting to event camera...")
            env = os.environ.copy()
            env['DISPLAY'] = 'localhost:0.0'

            self.ssh_process = subprocess.Popen(
                ["ssh", "-Y", "root@169.254.10.10", "sudo", "-E", "prophesee_viewer"],
                env=env,
                startupinfo=startupinfo
            )

            self.update_status("Event Camera Stream Running")

        except Exception as e:
            self.update_status(f"Error: {str(e)}")

    def maximize_xming_left(self):
        """Maximize Xming window on the left half of the screen"""
        time.sleep(3)
        windows = gw.getWindowsWithTitle("Xming")
        print(gw.getAllTitles())
        if windows:
            xming_window = windows[0]
            screen_width, screen_height = pyautogui.size()
            xming_window.moveTo(0, 0)
            xming_window.resizeTo(screen_width // 2, screen_height)

    def stop_prophesee_viewer(self):
        """Stop Prophesee Viewer"""
        if self.is_running:
            self.status_label.setText("Stopping Event Camera Stream...")
            if self.ssh_process:
                self.ssh_process.terminate()
                self.ssh_process = None
            if self.xming_process:
                self.xming_process.terminate()
                self.xming_process = None
            self.is_running = False
            self.status_label.setText("Event Camera Stream: Stopped")

    def update_status(self, message):
        """Update status safely"""
        from PyQt5.QtCore import QObject, pyqtSignal

        class Communicator(QObject):
            status_signal = pyqtSignal(str)

        if not hasattr(self, '_communicator'):
            self._communicator = Communicator()
            self._communicator.status_signal.connect(self.status_label.setText)

        self._communicator.status_signal.emit(message)

    def use_close_event(self, event):
        """Handle close event"""
        self.stop_prophesee_viewer()
        close_event(event, self)
