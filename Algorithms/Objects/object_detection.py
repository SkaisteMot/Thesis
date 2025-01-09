"""
Object detection using YOLOv8

Code adapted from the following:
https://www.freecodecamp.org/news/how-to-detect-objects-in-images-using-yolov8/
https://www.geeksforgeeks.org/object-detection-using-yolov8/
https://medium.com/softplus-publication/video-object-tracking-with-yolov8-and-sort-library-e28444b189aa
"""
from ultralytics import YOLO

class ObjectRecognizer:
    """Object Recognizer called from UI"""
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_and_draw(self, frame):
        """input into model"""
        results = self.model.track(frame, persist=True)
        return results[0].plot()
