# https://www.freecodecamp.org/news/how-to-detect-objects-in-images-using-yolov8/
# https://www.geeksforgeeks.org/object-detection-using-yolov8/
# https://medium.com/softplus-publication/video-object-tracking-with-yolov8-and-sort-library-e28444b189aa
from ultralytics import YOLO
import cv2


# load yolov8 model
model = YOLO('yolov8n.pt')

# load video
video_path = '../../Datasets/l.mp4'
cap = cv2.VideoCapture(video_path)

ret = True
# read frames
while ret:
    ret, frame = cap.read()

    if ret:

        # detect objects
        # track objects
        results = model.track(frame, persist=True)

        # plot results
        # cv2.rectangle
        # cv2.putText
        frame_ = results[0].plot()

        # visualize
        cv2.imshow('frame', frame_)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break