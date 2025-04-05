from ultralytics import YOLO
import cv2

model = YOLO("yolov8n-seg.pt")
video = "../../Datasets/cycling2.mp4"
cap = cv2.VideoCapture(video)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]

    # Display live output
    annotated_frame = results.plot()
    cv2.imshow("YOLOv8 Output", annotated_frame)

    # Create a mask for each detected object
    for det in results.boxes.data:
        x1, y1, x2, y2, conf, cls = det
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Create a translucent mask
        mask = frame.copy()
        mask[y1:y2, x1:x2] = (mask[y1:y2, x1:x2] * 0.5).astype(int)

        # Overlay the mask on the original frame
        frame[y1:y2, x1:x2] = (frame[y1:y2, x1:x2] * 0.5 + mask[y1:y2, x1:x2] * 0.5).astype(int)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()