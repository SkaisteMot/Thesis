import sys
import os
import subprocess
import time
import threading
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QMetaObject, Q_ARG, pyqtSlot
from utils import load_stylesheet, close_event

class EventCameraPage(QWidget):
    """Prophesee Viewer Integration Page with Auto-Start"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Camera Stream")
        self.setGeometry(100, 100, 800, 600)
        
        # Track processes
        self.xming_process = None
        self.ssh_process = None
        self.is_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Load stylesheet (Uncomment if needed)
        # load_stylesheet(self, "App/styles/prophesee_viewer.qss")
        
        # Auto-start the viewer when the page is opened
        QTimer.singleShot(100, self.start_prophesee_viewer)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main layout
        self.layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Starting Event Camera Stream...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("status_label")
        self.layout.addWidget(self.status_label)
        
        # Instructions label
        instructions = (
            "The Event Camera stream is being displayed in a separate window.\n"
            "This window uses Xming X server to display the prophesee_viewer output.\n\n"
            "Closing this page will automatically stop the stream. \n"
            "To Do: open this to the left and add description"
        )
        self.info_label = QLabel(instructions)
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setObjectName("info_label")
        self.layout.addWidget(self.info_label)
        
        # Set main layout
        self.setLayout(self.layout)
    
    def start_prophesee_viewer(self):
        """Start the Prophesee Viewer automatically"""
        if not self.is_running:
            self.is_running = True
            self.status_label.setText("Starting Event Camera Stream...")
            
            # Run the setup in a separate thread to keep UI responsive
            thread = threading.Thread(target=self._run_prophesee_setup)
            thread.daemon = True
            thread.start()
    
    def _run_prophesee_setup(self):
        """Run the Prophesee setup process in a separate thread"""
        try:
            # Start Xming
            xming_path = "C:\\Program Files (x86)\\Xming\\Xming.exe"
            if not os.path.exists(xming_path):
                self.update_status("Error: Xming not found. Please install it.")
                return
                
            self.xming_process = subprocess.Popen(
                [xming_path, ":0", "-clipboard", "-multiwindow"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait for Xming to initialize
            self.update_status("Initializing X server...")
            time.sleep(5)
            
            # Set DISPLAY environment variable and run SSH command
            self.update_status("Connecting to event camera...")
            
            # Create environment with DISPLAY set
            env = os.environ.copy()
            env['DISPLAY'] = 'localhost:0.0'
            
            # Run SSH command
            self.ssh_process = subprocess.Popen(
                ["ssh", "-Y", "root@169.254.10.10", "sudo", "-E", "prophesee_viewer"],
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.update_status("Event Camera Stream: Running (displaying in external window)")
            
        except Exception as e:
            self.update_status(f"Error: Failed to start Event Camera Stream: {str(e)}")
    
    def stop_prophesee_viewer(self):
        """Stop the Prophesee Viewer"""
        if self.is_running:
            self.status_label.setText("Stopping Event Camera Stream...")
            
            # Terminate processes
            if self.ssh_process:
                try:
                    self.ssh_process.terminate()
                    self.ssh_process = None
                except:
                    pass
                    
            if self.xming_process:
                try:
                    self.xming_process.terminate()
                    self.xming_process = None
                except:
                    pass
            
            self.is_running = False
            self.status_label.setText("Event Camera Stream: Stopped")
    
    def update_status(self, message):
        """Update the status label (thread-safe)"""
        # This is a safer way to update UI from background threads
        from PyQt5.QtCore import QObject, pyqtSignal
        
        class Communicator(QObject):
            status_signal = pyqtSignal(str)
            
        try:
            # Create the communicator if it doesn't exist
            if not hasattr(self, '_communicator'):
                self._communicator = Communicator()
                self._communicator.status_signal.connect(self.status_label.setText)
            
            # Emit the signal with the message
            self._communicator.status_signal.emit(message)
        except:
            # Fallback method if signal approach fails
            pass
    
    def release(self):
        """Release resources properly"""
        self.stop_prophesee_viewer()
    
    def closeEvent(self, event):
        """Handle close event to release resources"""
        self.release()
        close_event(event, self)
