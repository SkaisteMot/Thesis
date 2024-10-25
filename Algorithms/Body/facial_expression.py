# https://github.com/manish-9245/Facial-Emotion-Recognition-using-OpenCV-and-Deepface/blob/main/emotion.py --->main
# https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector
# https://github.com/Aaditya1978/Face_Expression_Prediction/tree/main

import cv2
from deepface import DeepFace
import numpy as np

# Load DNN face detector
face_net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel')

# Load emojis for different emotions
emoji_dict = {
    'happy': cv2.imread('../../Datasets/Emojis/happy.png'),
    'sad': cv2.imread('../../Datasets/Emojis/sad.png'),
    'angry': cv2.imread('../../Datasets/Emojis/angry.png'),
    'surprised': cv2.imread('../../Datasets/Emojis/surprised.png'),
    'neutral': cv2.imread('../../Datasets/Emojis/neutral.png'),
    'fear': cv2.imread('../../Datasets/Emojis/fear.png')
}

# Check if emojis are loaded successfully
for emotion, img in emoji_dict.items():
    if img is None:
        print(f"{emotion}: Image not found!")
    else:
        print(f"{emotion}: Image loaded successfully")

# Start capturing video
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame not captured.")
        break

    # Prepare frame for face detection
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    face_net.setInput(blob)
    detections = face_net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # Confidence threshold
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            (x, y, x1, y1) = box.astype("int")

            # Extract the face ROI
            face_roi = frame[y:y1, x:x1]
            face_roi_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)

            # Perform emotion analysis on the face ROI
            result = DeepFace.analyze(face_roi_rgb, actions=['emotion'], enforce_detection=False)

            # Determine the dominant emotion
            emotion = result[0]['dominant_emotion']
            print(f"Detected Emotion: {emotion}")  # Log detected emotion

            # Draw rectangle around the face and label with the predicted emotion
            cv2.rectangle(frame, (x, y), (x1, y1), (0, 0, 255), 2)
            cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # Display corresponding emoji
            if emotion in emoji_dict:
                emoji_img = emoji_dict[emotion]
                # Resize the emoji to fit in the frame (optional)
                emoji_img = cv2.resize(emoji_img, (50, 50))  # Resize as needed
                # Overlay the emoji on the frame
                frame[y:y + 50, x:x + 50] = emoji_img

    # Display the resulting frame
    cv2.imshow('Real-time Emotion Detection with Emoji', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()
