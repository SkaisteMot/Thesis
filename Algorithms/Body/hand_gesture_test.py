"""Hand Gesture Recogniziton using Googles MediaPipe, followed the documentation provided"""
from dataclasses import dataclass
from typing import Optional
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

@dataclass
class GestureResult:
    main_frame: np.ndarray
    left_label: str
    right_label: str

class GestureRecognizer:
    """Gesture Recognizer called by UI"""
    def __init__(self):
        self.recognizer = self._setup_recognizer()
        self.cap = cv2.VideoCapture(0)

    def _setup_recognizer(self):
        base_options = python.BaseOptions(model_asset_path='Algorithms/Body/gesture_recognizer.task')
        options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)
        return vision.GestureRecognizer.create_from_options(options)

    def process_frame(self) -> Optional[GestureResult]:
        """Process input and return relevant hand gesture labels"""
        ret, frame = self.cap.read()
        if not ret:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        recognition_result = self.recognizer.recognize(mp_image)

        gestures_and_landmarks = []
        if recognition_result.gestures:
            for hand_gestures, hand_landmarks in zip(recognition_result.gestures, recognition_result.hand_landmarks):
                gestures_and_landmarks.append((hand_gestures, hand_landmarks))

        frame_with_landmarks = self._draw_landmarks(frame.copy(), gestures_and_landmarks)
        left_label, right_label = self._get_gesture_labels(gestures_and_landmarks)

        return GestureResult(
            main_frame=frame_with_landmarks,
            left_label=left_label,
            right_label=right_label
        )

    def _get_gesture_labels(self, gestures_and_landmarks):
        labels = ["", ""]  # Default empty labels
        sorted_hands = sorted(gestures_and_landmarks, key=lambda x: x[1][0].x)

        for idx, (gestures, _) in enumerate(sorted_hands):
            labels[idx] = gestures[0].category_name

        return labels[0], labels[1]

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

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()