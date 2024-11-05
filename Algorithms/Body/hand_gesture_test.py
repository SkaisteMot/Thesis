"""Hand Gesture and Image display for Hand 1 and Hand 2, no distinction between left or right"""
import sys
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Define paths in a separate dictionary
icon_paths = {
    'Thumb_Up': '../../Datasets/HandIcons/thumbs_up.png',
    'Thumb_Down': '../../Datasets/HandIcons/thumbs_down.png',
    'Pointing_Up': '../../Datasets/HandIcons/point_up.png',
    'Victory': '../../Datasets/HandIcons/peace.png',
    'Closed_Fist': '../../Datasets/HandIcons/fist.png',
    'Open_Palm': '../../Datasets/HandIcons/wave.png',
    'ILoveYou': '../../Datasets/HandIcons/rock.png'
}

# Preload icons into a dictionary
gesture_icons = {}
for gesture_name, path in icon_paths.items():
    icon = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if icon is None:
        print(f"Warning: Unable to load image at {path}")  # Debugging print
    else:
        gesture_icons[gesture_name] = icon

# Create a GestureRecognizer object.
base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)

# Create the Gesture Recognizer instance
recognizer = vision.GestureRecognizer.create_from_options(options)

# Initialize video capture from webcam (0 for the default camera)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device.")
    sys.exit()  # Use sys.exit() instead of exit()

blank_image = 255 * np.ones((500, 600, 3), dtype=np.uint8)  # White blank image

def display_gesture_info(input_frame, gesture_data):
    """Draw gesture info and load corresponding icons."""
    emoji_images = [blank_image.copy(), blank_image.copy()]  # Initialize emoji for both hands

    # Sort hands based on their x-coordinates (leftmost hand first)
    sorted_hands = sorted(gesture_data, key=lambda x: x[1][0].x)

    for index, (current_hand_gestures, current_hand_landmarks) in enumerate(sorted_hands):
        # Get the top gesture for the hand
        top_gesture = current_hand_gestures[0]
        current_gesture_name = top_gesture.category_name  # Get the recognized gesture name

        # Prepare the text to display
        gesture_text = f"Hand {index + 1}: {current_gesture_name} ({top_gesture.score:.2f})"
        cv2.putText(input_frame, gesture_text, (10, 30 + index * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Load the icon for the recognized gesture
        if current_gesture_name in gesture_icons:
            icon_image = gesture_icons[current_gesture_name]
            emoji_images[index] = icon_image  # Load the icon for Hand 1 or Hand 2

        # Draw landmarks for each hand
        for landmark in current_hand_landmarks:  # Each landmark is a NormalizedLandmark
            x = int(landmark.x * input_frame.shape[1])
            y = int(landmark.y * input_frame.shape[0])
            cv2.circle(input_frame, (x, y), 5, (0, 255, 0), -1)

    return emoji_images

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame not captured.")
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Create a MediaPipe image from the RGB frame
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Recognize gestures in the input frame
    recognition_result = recognizer.recognize(mp_image)

    # Process the result for both hands
    gestures_and_landmarks = []
    if recognition_result.gestures:
        for hand_gestures, hand_landmarks in zip(recognition_result.gestures,
                                                 recognition_result.hand_landmarks):
            gestures_and_landmarks.append((hand_gestures, hand_landmarks))

    # Update emoji images with the recognized gestures
    hand_images = display_gesture_info(frame, gestures_and_landmarks)

    # Show emojis for both hands in separate windows
    cv2.imshow('Hand 1 Emoji', hand_images[0])  # Show Hand 1 emoji
    cv2.imshow('Hand 2 Emoji', hand_images[1])  # Show Hand 2 emoji
    cv2.imshow('Hand Recognition with Emoji', frame)  # Show the original frame

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the window
cap.release()
cv2.destroyAllWindows()
