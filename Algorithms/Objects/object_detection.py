# https://www.freecodecamp.org/news/how-to-detect-objects-in-images-using-yolov8/
# https://www.geeksforgeeks.org/object-detection-using-yolov8/
# https://medium.com/softplus-publication/video-object-tracking-with-yolov8-and-sort-library-e28444b189aa

from ultralytics import YOLO
from cv2 import cv2

# Load YOLOv8 model
model = YOLO('yolov8s.pt')

# Capture live video from default camera (0)
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Read and process frames
while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    # Detect objects and track them
    results = model.track(frame, persist=True)

    # Plot the detection results on the frame
    frame_ = results[0].plot()

    # Display the frame with detections
    cv2.imshow('YOLOv8 Live Object Detection', frame_)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
