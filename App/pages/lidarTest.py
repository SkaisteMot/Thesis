import sys
import numpy as np
import vispy.app
import vispy.scene
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
import cepton_sdk
import cv2
import matplotlib.pyplot as plt
from cepton_sdk.common import *

_all_builder = AllBuilder(__name__)

class PlotCanvas(vispy.scene.SceneCanvas):
    def __init__(self, sensor, **kwargs):
        super().__init__(**kwargs)
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

    def fetch_lidar_data(self):
        points_list = self.listener.get_points()
        if points_list:
            points = points_list[0]
            self.lidar_data = points.positions
            return self.lidar_data
        return None

    def on_timer(self, event):
        positions = self.fetch_lidar_data()
        if positions is not None:
            self.update_points(positions)
        else:
            print("No LiDAR data available at the moment.")

class LidarCameraPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiDAR Camera Stream")
        self.setGeometry(100, 100, 800, 600)

        # Main layout (horizontal split)
        self.main_layout = QHBoxLayout()

        # Left side: LiDAR feed
        self.video_layout = QVBoxLayout()
        self.lidar_feed = QLabel()
        self.lidar_feed.setObjectName("lidar_feed")
        self.lidar_feed.setAlignment(Qt.AlignCenter)
        self.lidar_feed.setScaledContents(True)
        self.video_layout.addWidget(self.lidar_feed)

        # Right side: Title and description
        self.info_layout = QVBoxLayout()
        self.title_label = QLabel("LiDAR Camera Stream")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("title_label")

        self.description_label = QLabel("LiDAR data stream visualization")
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setObjectName("description_label")

        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.description_label)
        self.info_layout.addStretch()

        # Add sections to main layout
        self.main_layout.addLayout(self.video_layout, 1)
        self.main_layout.addLayout(self.info_layout, 1)
        self.setLayout(self.main_layout)

        # Initialize Cepton SDK and start the LiDAR stream
        cepton_sdk.initialize(enable_wait=True)
        self.sensor = cepton_sdk.Sensor.create_by_index(0)
        print("Sensor Information:", self.sensor.information.to_dict())

        # Initialize canvas to display LiDAR stream
        self.canvas = PlotCanvas(sensor=self.sensor, keys='interactive', size=(800, 600))
        self.canvas.show()

        # Set a timer to call the on_timer method periodically
        self.canvas.timer = vispy.app.Timer(interval=0.1, connect=self.canvas.on_timer, start=True)

    def closeEvent(self, event):
        """Handle close event"""
        print("LiDAR page is closing.")
        cepton_sdk.cleanup()
        event.accept()


