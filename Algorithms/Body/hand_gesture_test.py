# hand_gestures_test.py
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class GestureResult:
    main_frame: np.ndarray
    left_emoji: np.ndarray
    right_emoji: np.ndarray

class GestureRecognizer:
    def __init__(self,icon_paths):
        self.icon_paths=icon_paths
        self.gesture_icons = self._load_icons()
        self.recognizer = self._setup_recognizer()
        self.cap = cv2.VideoCapture(0)
        self.blank_image = 255 * np.ones((200, 200, 3), dtype=np.uint8)

    def _load_icons(self):
        icons = {}
        for gesture_name, path in self.icon_paths.items():
            icon = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if icon is not None:
                # Convert BGRA to BGR if needed
                if icon.shape[2] == 4:
                    icon = cv2.cvtColor(icon, cv2.COLOR_BGRA2BGR)
                icons[gesture_name] = cv2.resize(icon, (200, 200))
            else:
                print(f"Warning: Could not load icon {path}")
        return icons

    def _get_gesture_emojis(self, gestures_and_landmarks):
        emoji_images = [self.blank_image.copy(), self.blank_image.copy()]

        if not gestures_and_landmarks:
            return emoji_images[0], emoji_images[1]

        sorted_hands = sorted(gestures_and_landmarks, key=lambda x: x[1][0].x)

        for idx, (gestures, _) in enumerate(sorted_hands):
            gesture_name = gestures[0].category_name
            if gesture_name in self.gesture_icons:
                emoji_images[idx] = self.gesture_icons[gesture_name].copy()

        return emoji_images[0], emoji_images[1]

    def _setup_recognizer(self):
        base_options = python.BaseOptions(model_asset_path='../Algorithms/Body/gesture_recognizer.task')
        options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)
        return vision.GestureRecognizer.create_from_options(options)

    def process_frame(self) -> Optional[GestureResult]:
        ret, frame = self.cap.read()
        if not ret:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        recognition_result = self.recognizer.recognize(mp_image)

        gestures_and_landmarks = []
        if recognition_result.gestures:
            for hand_gestures, hand_landmarks in zip(recognition_result.gestures,
                                                   recognition_result.hand_landmarks):
                gestures_and_landmarks.append((hand_gestures, hand_landmarks))

        frame_with_landmarks = self._draw_landmarks(frame.copy(), gestures_and_landmarks)
        left_emoji, right_emoji = self._get_gesture_emojis(gestures_and_landmarks)

        return GestureResult(
            main_frame=frame_with_landmarks,
            left_emoji=left_emoji,
            right_emoji=right_emoji
        )

    def _draw_landmarks(self, frame, gestures_and_landmarks):
        for idx, (gestures, landmarks) in enumerate(gestures_and_landmarks):
            gesture_name = gestures[0].category_name
            confidence = gestures[0].score
            cv2.putText(frame, f"{gesture_name} ({confidence:.2f})",
                       (10, 30 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            for landmark in landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame

    def _get_gesture_emojis(self, gestures_and_landmarks):
        emoji_images = [self.blank_image.copy(), self.blank_image.copy()]
        sorted_hands = sorted(gestures_and_landmarks, key=lambda x: x[1][0].x)

        for idx, (gestures, _) in enumerate(sorted_hands):
            gesture_name = gestures[0].category_name
            if gesture_name in self.gesture_icons:
                emoji_images[idx] = self.gesture_icons[gesture_name]

        return emoji_images[0], emoji_images[1]

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()