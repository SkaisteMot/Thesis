"""
Object detection using YOLOv8

Code adapted from the following:
https://www.freecodecamp.org/news/how-to-detect-objects-in-images-using-yolov8/
https://www.geeksforgeeks.org/object-detection-using-yolov8/
https://medium.com/softplus-publication/video-object-tracking-with-yolov8-and-sort-library-e28444b189aa
"""
from ultralytics import YOLO
import numpy as np

class ObjectRecognizer:
    """Object Recognizer called from UI"""
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_and_draw(self, frame):
        """Input into model with confidence filtering"""
        results = self.model.track(frame, persist=True)

        if results:
            result = results[0]  # Extract first result
            confs = result.boxes.conf.cpu().numpy()  # Get confidence scores as NumPy array
            
            # Filter out boxes below 50% confidence
            mask = confs >= 0.5
            result.boxes = result.boxes[mask]  # Apply mask to filter boxes

            return result.plot()

        return frame  # Return original frame if no detections

