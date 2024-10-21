from ultralytics import YOLO

# Assuming you have opencv installed
import cv2 

MODEL = "yolov8x.pt" 
# Creating an instance of your chosen model
model = YOLO(MODEL) 

results = model("../../Datasets/dogbike.jpg",show=True) 
# "0" will display the window infinitely until any keypress (in case of videos)
# waitKey(1) will display a frame for 1 ms
cv2.waitKey(0) 