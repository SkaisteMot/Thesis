"""
Hand gesture recognition and display of relevant emojis in a seperate window

Code adapted from the following sources:
https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python
https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb#scrollTo=Iy4r2_ePylIa
https://towardsdatascience.com/real-time-hand-tracking-and-gesture-recognition-with-mediapipe-rerun-showcase-9ec57cb0c831
"""
from cv2 import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

mp_drawing = mp.solutions.drawing_utils

emoji_dict = {
    'thumb_up': cv2.imread('DevCode/Datasets/HandIcons/thumbs_up.png'),
    'thumb_down': cv2.imread('DevCode/Datasets/HandIcons/thumbs_down.png'),
    'point_up': cv2.imread('DevCode/Datasets/HandIcons/point_up.png'),
    'peace': cv2.imread('DevCode/Datasets/HandIcons/peace.png'),
    'fist': cv2.imread('DevCode/Datasets/HandIcons/fist.png'),
    'wave': cv2.imread('DevCode/Datasets/HandIcons/wave.png'),
    'rock': cv2.imread('DevCode/Datasets/HandIcons/rock.png')
}

for gesture, img in emoji_dict.items():
    if img is None:
        print(f"{gesture}: Image not found!")
    else:
        print(f"{gesture}: Image loaded successfully")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

def recognize_gesture(landmarks):
    """Recognize the gestures and return the equivalent image/emoji"""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['thumb_up']

    if (thumb_tip.y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return emoji_dict['thumb_down']

    if (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['peace']

    if (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['point_up']

    if (thumb_tip.y > landmarks[mp_hands.HandLandmark.THUMB_MCP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return emoji_dict['fist']

    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['wave']

    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y < landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return emoji_dict['rock']

    return None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame not captured.")
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            emoji_img = recognize_gesture(hand_landmarks.landmark)

            if emoji_img is not None:
                cv2.imshow('Emoji', emoji_img)

    cv2.imshow('Hand Recognition with Emoji', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
