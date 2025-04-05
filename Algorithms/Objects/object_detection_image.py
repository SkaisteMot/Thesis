"""Simple Object detection from videos/images"""
from ultralytics import YOLO

from cv2 import cv2

MODEL = "yolov8x.pt"
model = YOLO(MODEL)

results = model("../../Datasets/dogbike.jpg",show=True)
cv2.waitKey(0)