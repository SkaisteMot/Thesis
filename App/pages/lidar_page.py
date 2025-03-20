import sys
import numpy as np
import vispy.app
import vispy.scene
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PyQt5.QtCore import QTimer, Qt
import cepton_sdk
import cv2
import matplotlib.pyplot as plt
from cepton_sdk.common import *
from utils import load_stylesheet

_all_builder = AllBuilder(__name__)

class PlotCanvas(vispy.scene.SceneCanvas):
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
            if self.colors is None or self.colors.shape[0] != num_points:
                z_values = positions[:, 2]
                min_z = np.min(z_values)
                max_z = np.max(z_values)
                norm_z = (z_values - min_z) / (max_z - min_z)
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
        points_list = self.listener.get_points()
        if points_list:
            points = points_list[0]
            self.lidar_data = points.positions
            return self.lidar_data
        return None

    def on_timer(self):
        positions = self.fetch_lidar_data()
        if positions is not None:
            self.update_points(positions)
        else:
            print("No LiDAR data available at the moment.")

import cepton_sdk

class LidarCameraPage(QWidget):
    _is_initialized = False  # Class-level flag to track SDK initialization

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiDAR Camera Stream")

        # Load stylesheet
        load_stylesheet(self, "App/styles/sensors.qss")

        # Main layout (horizontal split)
        self.main_layout = QHBoxLayout()

        # Left side: LiDAR feed
        self.video_layout = QVBoxLayout()
        
        # ✅ Check if SDK is already initialized
        if not LidarCameraPage._is_initialized:
            print("Initializing Cepton SDK...")
            cepton_sdk.initialize(enable_wait=True)
            LidarCameraPage._is_initialized = True  # Set flag to prevent reinitialization
        else:
            print("Cepton SDK already initialized.")

        self.sensor = cepton_sdk.Sensor.create_by_index(0)
        #print("Sensor Information:", self.sensor.information.to_dict()) 

        # Initialize canvas to display LiDAR stream and embed in PyQt
        self.canvas = PlotCanvas(sensor=self.sensor)
        
        # Create and configure a QWidget to embed the canvas
        from vispy.app import use_app
        app = use_app('pyqt5')
        self.canvas_widget = self.canvas.native
        self.video_layout.addWidget(self.canvas_widget)

        # Right side: Title and description
        self.info_layout = QVBoxLayout()
        self.title_label = QLabel("LiDAR Camera Stream")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title")

        self.description_label = QLabel("LiDAR (Light Detection and Ranging) works by emitting laser "
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
        self.description_label.setAlignment(Qt.AlignCenter)

        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.description_label)
        self.info_layout.addStretch()

        # Add sections to main layout
        self.main_layout.addLayout(self.video_layout, 2)
        self.main_layout.addLayout(self.info_layout, 1)
        self.setLayout(self.main_layout)

    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'canvas') and hasattr(self.canvas, 'timer'):
            self.canvas.timer.stop()
        event.accept()
