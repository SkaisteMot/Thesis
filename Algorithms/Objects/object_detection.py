"""
Object detection using YOLOv8

Code adapted from the following:
https://www.freecodecamp.org/news/how-to-detect-objects-in-images-using-yolov8/
https://www.geeksforgeeks.org/object-detection-using-yolov8/
https://medium.com/softplus-publication/video-object-tracking-with-yolov8-and-sort-library-e28444b189aa
"""
from ultralytics import YOLO
from cv2 import cv2

model = YOLO('yolov8s.pt')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    results = model.track(frame, persist=True)

    frame_ = results[0].plot()

    cv2.imshow('YOLOv8 Live Object Detection', frame_)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
