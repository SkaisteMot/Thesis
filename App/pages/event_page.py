import os
import sys
import subprocess
import time
import threading
import pygetwindow as gw
import win32gui
import win32con
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import QTimer, Qt
from utils import load_stylesheet, close_event, QRCodeWidget

class EventCameraPage(QWidget):
    """Event Camera Page with Embedded VcXsrv"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Camera Stream")

        self.vcxsrv_process = None
        self.ssh_process = None
        self.is_running = False

        self.setup_ui()
        QTimer.singleShot(100, self.start_prophesee_viewer)

    def setup_ui(self):
        """Setup UI"""
        load_stylesheet(self, "App/styles/sensors.qss")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignRight)
        self.title_label = QLabel("Event Stream")
        #self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title")

        self.description = QLabel(
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

        self.qr_widget = QRCodeWidget("Datasets/QRcodes/event_QR.svg",
                                      "Scan this to learn more about event cameras!",
                                      label_width=800)
        
        self.layout.addStretch()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.description)
        self.layout.addStretch()
        self.layout.addWidget(self.qr_widget)

        self.setLayout(self.layout)

    def start_prophesee_viewer(self):
        """Start Prophesee Viewer embedded in PyQt"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._run_prophesee_setup)
            thread.daemon = True
            thread.start()

    def _run_prophesee_setup(self):
        """Start VcXsrv and Prophesee Viewer, then embed it"""
        try:
            # Start VcXsrv
            self.vcxsrv_process = self.start_vcxsrv()

            time.sleep(3)  # Allow VcXsrv to initialize

            # Set DISPLAY environment variable
            env = os.environ.copy()
            env['DISPLAY'] = 'localhost:0.0'

            # Start Prophesee Viewer via SSH
            self.ssh_process = subprocess.Popen(
                ["ssh", "-Y", "root@169.254.10.10", "sudo", "-E", "prophesee_viewer"],
                env=env
            )

            time.sleep(1)  # Wait for the window to appear
            self.embed_vcxsrv_window()

        except Exception as e:
            print(e)

    def start_vcxsrv(self):
        """Start VcXsrv in single window mode, minimized"""
        vcxsrv_path = "C:\\Program Files\\VcXsrv\\vcxsrv.exe"
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = win32con.SW_MINIMIZE  # Start minimized
        return subprocess.Popen([vcxsrv_path, ":0", "-screen", "0", "800x600+0+0"],
                                startupinfo=startupinfo)

    def get_vcxsrv_window(self):
        """Find the VcXsrv window handle (HWND)"""
        time.sleep(1)
        for window in gw.getAllWindows():
            if "VcXsrv" in window.title:
                return window._hWnd  # Return window handle
        return None

    def embed_vcxsrv_window(self):
        """Reparent and center the VcXsrv window inside the PyQt application"""
        hwnd_vcxsrv = self.get_vcxsrv_window()
        if hwnd_vcxsrv:
            win32gui.SetParent(hwnd_vcxsrv, self.winId())  
            win32gui.SetWindowLong(hwnd_vcxsrv, win32con.GWL_STYLE, win32con.WS_VISIBLE)

            # Get panel size
            panel_width = self.layout.geometry().width() //2
            panel_height = self.layout.geometry().height()

            # Center the VcXsrv window within the left panel
            win32gui.MoveWindow(hwnd_vcxsrv, (panel_width - 640) // 2, (panel_height - 480) // 2, 
                                640, 480, True)
            print(f"VcXsrv window {hwnd_vcxsrv} embedded and centered.")
        else:
            print("VcXsrv window not found.")


    def stop_prophesee_viewer(self):
        """Stop Prophesee Viewer"""
        if self.is_running:
            if self.ssh_process:
                self.ssh_process.terminate()
                self.ssh_process = None
            if self.vcxsrv_process:
                self.vcxsrv_process.terminate()
                self.vcxsrv_process = None
            self.is_running = False

    def closeEvent(self, event):
        """Handle close event"""
        self.stop_prophesee_viewer()
        close_event(event, self)
