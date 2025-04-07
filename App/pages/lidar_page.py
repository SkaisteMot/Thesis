"""LiDAR Page"""
import numpy as np
import vispy.scene
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
import cepton_sdk
import matplotlib.pyplot as plt
from cepton_sdk.common import *
from utils import load_stylesheet, QRCodeWidget

_all_builder = AllBuilder(__name__)

class PlotCanvas(vispy.scene.SceneCanvas):
    """Plot the Lidar points"""
    def __init__(self, sensor, **kwargs):
        super().__init__(keys='interactive', **kwargs)
        self.unfreeze()  # Unfreeze the class to allow dynamic attributes
        self.view = self.central_widget.add_view()
        self.view.camera = vispy.scene.cameras.make_camera("turntable")
        self.view.camera.azimuth = -10
        self.view.camera.depth_value = 10000
        self.view.camera.elevation = 8.5
        self.view.camera.fov = 0
        self.view.camera.scale_factor = 3.55
        #test to see if this will normalize the point colouring
        self.min_z = None
        self.max_z = None

        self.points_visual = vispy.scene.visuals.Markers()
        self.points_visual.antialias = 0
        self.view.add(self.points_visual)

        self.sensor = sensor
        self.listener = cepton_sdk.SensorFramesListener(self.sensor.serial_number)
        self.lidar_data = None
        self.colors = None

        # Set up the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(100)  # 100ms interval = 10 FPS

    def update_points(self, positions, colors=None, sizes=None):
        positions = positions - np.mean(positions, axis=0)
        num_points = positions.shape[0]

        if colors is None:
            # Calculate z-values
            z_values = positions[:, 2]
            
            # Update min/max z with a moving average or set them initially
            if self.min_z is None or self.max_z is None:
                self.min_z = np.min(z_values)
                self.max_z = np.max(z_values)
            else:
                # Gradual adjustment to avoid sudden color changes
                # You can adjust the alpha value (0.05) to control adaptation speed
                self.min_z = 0.95 * self.min_z + 0.05 * np.min(z_values)
                self.max_z = 0.95 * self.max_z + 0.05 * np.max(z_values)
                
            # Ensure there's always at least a small range to avoid division by zero
            if abs(self.max_z - self.min_z) < 0.1:
                self.max_z = self.min_z + 0.1
                
            # Normalize with consistent range
            norm_z = (z_values - self.min_z) / (self.max_z - self.min_z)
            # Clip to handle outliers
            norm_z = np.clip(norm_z, 0, 1)
            self.colors = plt.cm.viridis(norm_z)
            
        colors = self.colors

        if colors.shape[0] != num_points:
            colors = np.resize(colors, (num_points, 4))

        if sizes is None:
            sizes = np.full([num_points], 2)

        options = {
            "edge_width": 0,
            "face_color": colors,
            "pos": positions,
            "size": sizes,
        }
        self.points_visual.set_data(**options)
        self.update()  # Request canvas update

    def fetch_lidar_data(self):
        try:
            points_list = self.listener.get_points()
            if points_list:
                points = points_list[0]
                self.lidar_data = points.positions
                return self.lidar_data
            return None
        except Exception as e:
            print(f"Error fetching LiDAR data: {e}")
            return None

    def on_timer(self):
        try:
            positions = self.fetch_lidar_data()
            if positions is not None:
                self.update_points(positions)
        except Exception as e:
            print(f"Error in timer callback: {e}")


class LidarCameraPage(QWidget):
    _is_initialized = False  # Class-level flag to track SDK initialization

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiDAR Camera Stream")

        # Load stylesheet
        load_stylesheet(self, "App/styles/sensors.qss")

        # Main layout (horizontal split)
        self.main_layout = QHBoxLayout()
        
        # Initialize the info layout that will be used in both cases
        self.setup_info_layout()

        try:
            # Try to initialize LiDAR and set up the visualization
            self.initialize_lidar()
        except Exception as e:
            # Show error message and set up a blank widget instead
            self.handle_lidar_error(str(e))
            
        # Set the main layout
        self.setLayout(self.main_layout)

    def setup_info_layout(self):
        """Set up the information panel on the right side"""
        self.info_layout = QVBoxLayout()
        self.title_label = QLabel("LiDAR Camera Stream")
        #self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title")

        self.description_label = QLabel(
            "LiDAR (Light Detection and Ranging) works by emitting laser "
            "pulses and measuring the time it takes for them to bounce back "
            "after hitting an object. Since the speed of light is constant, the "
            "system can calculate the exact distance to each object based on the "
            "time delay.By sending out millions of these laser pulses in different "
            "directions, LiDAR creates a detailed 3D map of its surroundings. It's "
            "commonly used in self-driving cars, drones, and mapping applications "
            "because it provides precise depth information, even in low light or "
            "foggy conditions.")
        self.description_label.setWordWrap(True)
        self.description_label.setObjectName("description")

        self.qr_widget = QRCodeWidget("Datasets/QRcodes/lidar_QR.svg",
                                    "Scan this to learn more about LiDAR sensors!",
                                    label_width=800)

        self.info_layout.addStretch()
        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.description_label)
        self.info_layout.addStretch()
        self.info_layout.addWidget(self.qr_widget)

    def initialize_lidar(self):
        """Initialize the LiDAR sensor and setup the visualization"""
        # Left side: LiDAR feed
        self.video_layout = QVBoxLayout()

        # Initialize Cepton SDK if not already initialized
        if not LidarCameraPage._is_initialized:
            print("Initializing Cepton SDK...")
            try:
                cepton_sdk.initialize(enable_wait=True)
                LidarCameraPage._is_initialized = True
            except Exception as e:
                # If initialization fails, raise the exception to be caught by the caller
                raise Exception(f"Failed to initialize Cepton SDK: {e}")
        else:
            print("Cepton SDK already initialized.")

        # Try to create sensor
        try:
            self.sensor = cepton_sdk.Sensor.create_by_index(0)
        except Exception as e:
            raise Exception(f"No LiDAR sensor detected: {e}")

        # Initialize canvas to display LiDAR stream and embed in PyQt
        self.canvas = PlotCanvas(sensor=self.sensor)

        # Create and configure a QWidget to embed the canvas
        from vispy.app import use_app
        app = use_app('pyqt5')
        self.canvas_widget = self.canvas.native
        self.video_layout.addWidget(self.canvas_widget)

        # Add sections to main layout
        self.main_layout.addLayout(self.video_layout, 2)
        self.main_layout.addLayout(self.info_layout, 1)

    def handle_lidar_error(self, error_message):
        """Handle cases where LiDAR initialization fails"""
        # Create a placeholder layout for the left side
        self.error_layout = QVBoxLayout()
        
        # Create an error message widget
        error_widget = QWidget()
        error_widget_layout = QVBoxLayout()
        
        error_label = QLabel("LiDAR Sensor Not Connected")
        error_label.setObjectName("error_title")
        error_label.setAlignment(Qt.AlignCenter)
        
        error_details = QLabel(f"Error: {error_message}")
        error_details.setObjectName("error_details")
        error_details.setWordWrap(True)
        error_details.setAlignment(Qt.AlignCenter)
        
        close_button = QPushButton("Close Page")
        close_button.setObjectName("close_button")
        close_button.clicked.connect(self.close)
        
        error_widget_layout.addStretch(1)
        error_widget_layout.addWidget(error_label)
        error_widget_layout.addWidget(error_details)
        error_widget_layout.addWidget(close_button)
        error_widget_layout.addStretch(1)
        
        error_widget.setLayout(error_widget_layout)
        self.error_layout.addWidget(error_widget)
        
        # Add to main layout
        self.main_layout.addLayout(self.error_layout, 2)
        self.main_layout.addLayout(self.info_layout, 1)
        
        # Log the error
        print(f"LiDAR initialization error: {error_message}")

    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'canvas') and hasattr(self.canvas, 'timer'):
            self.canvas.timer.stop()
        event.accept()