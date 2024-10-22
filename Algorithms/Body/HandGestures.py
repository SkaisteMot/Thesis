# https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python
# https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb#scrollTo=Iy4r2_ePylIa
# https://towardsdatascience.com/real-time-hand-tracking-and-gesture-recognition-with-mediapipe-rerun-showcase-9ec57cb0c831
from cv2 import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize MediaPipe Drawing module for drawing landmarks
mp_drawing = mp.solutions.drawing_utils

# Load emoji images for recognized gestures
emoji_dict = {
    'thumb_up': cv2.imread('DevCode/Datasets/HandIcons/thumbs_up.png'),
    'thumb_down': cv2.imread('DevCode/Datasets/HandIcons/thumbs_down.png'),
    'point_up': cv2.imread('DevCode/Datasets/HandIcons/point_up.png'),
    'peace': cv2.imread('DevCode/Datasets/HandIcons/peace.png'),
    'fist': cv2.imread('DevCode/Datasets/HandIcons/fist.png'),
    'wave': cv2.imread('DevCode/Datasets/HandIcons/wave.png'),
    'rock': cv2.imread('DevCode/Datasets/HandIcons/rock.png')
}

# Check if all images are loaded
for gesture, img in emoji_dict.items():
    if img is None:
        print(f"{gesture}: Image not found!")
    else:
        print(f"{gesture}: Image loaded successfully")

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

# Function to detect simple hand gestures and return the corresponding PNG image
def recognize_gesture(landmarks):
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Thumb Up
    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['thumb_up']

    # Thumb Down
    if (thumb_tip.y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return emoji_dict['thumb_down']

    # Peace Sign
    if (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['peace']

    # Pointing Up
    if (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['point_up']

    # Fist
    if (thumb_tip.y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return emoji_dict['fist']

    # Waving Hand
    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['wave']

    # Rock/ Love Gesture
    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y < landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['rock']

    return None  # No recognized gesture

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame not captured.")
        continue  # Skip the iteration if frame is not captured

    # Convert the frame to RGB format for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame and get hand landmarks
    results = hands.process(frame_rgb)

    # Draw the hand landmarks on the frame if detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Recognize gesture and get emoji image
            emoji_img = recognize_gesture(hand_landmarks.landmark)
        
            if emoji_img is not None:
                # Display the emoji image in a separate window
                cv2.imshow('Emoji', emoji_img)

    # Display the frame with hand landmarks
    cv2.imshow('Hand Recognition with Emoji', frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
