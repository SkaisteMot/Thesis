"""
Hand gesture recognition and display of relevant emojis in a seperate window

Code adapted from the following sources:
https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python
https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb#scrollTo=Iy4r2_ePylIa
https://towardsdatascience.com/real-time-hand-tracking-and-gesture-recognition-with-mediapipe-rerun-showcase-9ec57cb0c831
"""
import cv2
import mediapipe as mp
import numpy as np
import sys  # Import sys for using sys.exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

mp_drawing = mp.solutions.drawing_utils

emoji_dict = {
    'thumb_up': cv2.imread('../../Datasets/HandIcons/thumbs_up.png'),
    'thumb_down': cv2.imread('../../Datasets/HandIcons/thumbs_down.png'),
    'point_up': cv2.imread('../../Datasets/HandIcons/point_up.png'),
    'peace': cv2.imread('../../Datasets/HandIcons/peace.png'),
    'fist': cv2.imread('../../Datasets/HandIcons/fist.png'),
    'wave': cv2.imread('../../Datasets/HandIcons/wave.png'),
    'rock': cv2.imread('../../Datasets/HandIcons/rock.png')
}

for gesture, img in emoji_dict.items():
    if img is None:
        print(f"{gesture}: Image not found!")
    else:
        print(f"{gesture}: Image loaded successfully")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video device.")
    sys.exit()  # Use sys.exit() instead of exit()

# Create a blank image (assuming your emoji images are 100x100)
blank_image = 255 * np.ones((100, 100, 3), dtype=np.uint8)  # White blank image

def recognize_gesture(landmarks):
    """Recognize the gestures and return the equivalent image/emoji"""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Define gesture conditions
    gestures = {
        'thumb_up': (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
                     index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                     middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                     ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
                     pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y),
        'thumb_down': (thumb_tip.y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y and
                       index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
                       middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
                       ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
                       pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y),
        'peace': (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                  middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                  ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
                  pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y),
        'point_up': (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                     middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                     ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
                     pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y),
        'fist': (thumb_tip.y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y and
                  index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
                  middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
                  ring_tip.y < landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
                  pinky_tip.y < landmarks[mp_hands.HandLandmark.PINKY_MCP].y),
        'wave': (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
                 index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                 middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                 ring_tip.y < landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
                 pinky_tip.y < landmarks[mp_hands.HandLandmark.PINKY_PIP].y)
    }

    for gesture, condition in gestures.items():
        if condition:
            print(f"Detected Gesture: {gesture}")  # Debug print
            return emoji_dict[gesture]

    return None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame not captured.")
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    left_emoji_img = blank_image  # Initialize emoji images for both hands
    right_emoji_img = blank_image

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Determine which hand is detected
            handedness = results.multi_handedness[results.multi_hand_landmarks.index(hand_landmarks)].classification[0].label

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            detected_emoji_img = recognize_gesture(hand_landmarks.landmark)

            # Assign the detected emoji to the correct hand's variable
            if handedness == 'Left':
                left_emoji_img = detected_emoji_img if detected_emoji_img is not None else blank_image
            elif handedness == 'Right':
                right_emoji_img = detected_emoji_img if detected_emoji_img is not None else blank_image

    # Show emojis for both hands in separate windows
    cv2.imshow('Left Hand Emoji', right_emoji_img)  # Show right hand in left window
    cv2.imshow('Right Hand Emoji', left_emoji_img)  # Show left hand in right window
    cv2.imshow('Hand Recognition with Emoji', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
