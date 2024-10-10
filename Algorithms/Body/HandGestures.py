# https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python
# https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb#scrollTo=Iy4r2_ePylIa
# https://towardsdatascience.com/real-time-hand-tracking-and-gesture-recognition-with-mediapipe-rerun-showcase-9ec57cb0c831
import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize MediaPipe Drawing module for drawing landmarks
mp_drawing = mp.solutions.drawing_utils

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)

# Function to detect simple hand gestures and return the corresponding emoji
def recognize_gesture(landmarks):
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Thumb Up (👍)
    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return "👍"  # Thumbs up emoji

    # Thumb Down (👎)
    if (thumb_tip.y > thumb_mcp.y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return "👎"  # Thumbs down emoji

    # Peace Sign (✌️)
    if (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return "✌️"  # Peace sign emoji

    # Pointing Up (☝️)
    if (index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return "☝️"  # Pointing up emoji

    # Fist (✊)
    if (thumb_tip.y > thumb_mcp.y and
        index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return "✊"  # Fist emoji

    # Waving Hand (👋)
    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return "👋"  # Waving hand emoji

    # Rock/ Love Gesture (🤟 - thumb, index, and pinky extended)
    if (thumb_tip.y < landmarks[mp_hands.HandLandmark.THUMB_IP].y and
        index_tip.y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y < landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
        return "🤟"  # Rock/love gesture emoji
    
    return None  # No recognized gesture

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        continue
    
    # Convert the frame to RGB format
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame to detect hands
    results = hands.process(frame_rgb)
    
    # Check if hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Recognize gesture and get emoji
            emoji = recognize_gesture(hand_landmarks.landmark)
            
            if emoji:
                # Display the emoji on the video frame
                cv2.putText(frame, emoji, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5, cv2.LINE_AA)
    
    # Display the frame with hand landmarks and recognized gestures
    cv2.imshow('Hand Recognition with Emoji', frame)
    
    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
