"""helper functions used throughout"""
import socket
import threading
import time
import cv2
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt

def load_stylesheet(window,style_sheet_path):
    """Load the stylesheet for the page."""
    with open(style_sheet_path, "r") as file:
        window.setStyleSheet(file.read())

def close_event(event, widget):
    """Handle cleanup when closing a page"""
    if hasattr(widget, "cap"):  # Ensure widget has a video capture instance
        widget.cap.release()
    if hasattr(widget, "timer"):  # Stop the timer if it exists
        widget.timer.stop()
    event.accept()

class DeviceStatusChecker:
    """Check if sensors are connected"""
    def __init__(self):
        self.devices={
            #"hdr_rgb":{"type":"ip","address":"169.254.186.74","port":135},
            "rgb":{"type":"usb","display_name":"RGB Camera"},
            "lidar":{"type":"ip","address":"169.254.65.122","port":135},
            "thermal":{"type":"ip","address":"192.168.2.1","port":135},
            "event":{"type":"ip","address":"169.254.10.1","port":135}
        }
        self.device_statuses = {}
        self.status_lock = threading.Lock()
        self.check_interval = 5  # seconds between checks
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._background_check, daemon=True)
        self._thread.start()

    def _background_check(self):
        while not self._stop_event.is_set():
            self._update_all_statuses()
            #debug print,remove later
            print("[DeviceStatusChecker] Updated statuses:")
            for ip, status in self.device_statuses.items():
                print(f"  {ip}: {'Online' if status else 'Offline'}")
            time.sleep(self.check_interval)

    def _update_all_statuses(self):
        statuses={}
        for device_id, config in self.devices.items():
            if config["type"]=="usb":
                statuses[device_id]=self._check_webcam_available()
            elif config["type"]=="ip":
                statuses[device_id] = self._check_device_connection(
                    config["address"],config.get("port",135)
                )

        with self.status_lock:
            self.device_statuses = statuses
    
    def _check_device_connection(self, ip, port=135, timeout=0.5):
        """Check if a device is connected by attempting a socket connection."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
        
    def _check_webcam_available(self):
        """Check if a USB webcam is available."""
        try:
            cap = cv2.VideoCapture(0)
            is_opened = cap.isOpened()
            cap.release()
            return is_opened
        except Exception:
            return False
            
    def get_status(self, device_id):
        """Get the current status of a device."""
        with self.status_lock:
            return self.device_statuses.get(device_id, False)
    
    def stop(self):
        """Stop the background thread."""
        self._stop_event.set()
        self._thread.join(timeout=1)

class QRCodeWidget(QWidget):
    """Reusable QR Code Widget"""
    def __init__(self, qr_path: str, text: str, label_width: int = 800, label_height: int = 150):
        super().__init__()
        load_stylesheet(self, "App/styles/sensors.qss")

        # QR Code Image
        self.qr_code = QSvgWidget(qr_path)
        self.qr_code.setFixedSize(150, 150)

        # Description Label
        self.qr_label = QLabel(text)
        self.qr_label.setObjectName("QR_desc")
        self.qr_label.setWordWrap(True)
        self.qr_label.setFixedSize(label_width, label_height)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.qr_code, alignment=Qt.AlignLeft)
        layout.addWidget(self.qr_label, alignment=Qt.AlignHCenter)
        self.setLayout(layout)
