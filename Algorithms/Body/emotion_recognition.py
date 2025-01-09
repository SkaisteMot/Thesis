"""Emotion Recogntion, display relevent emoji in seperate window"""
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
from fer import FER

@dataclass
class EmotionResult:
    main_frame: np.ndarray
    emoji: np.ndarray

class EmotionRecognizer:
    """
    Emotion recognizer class called by the ui
    """
    def __init__(self, emoji_paths):
        self.emoji_paths = emoji_paths
        self.emoji_icons = self._load_emojis()
        self.detector = FER()
        self.cap = cv2.VideoCapture(0)
        self.blank_image = 255 * np.ones((200, 200, 3), dtype=np.uint8)

    def _load_emojis(self):
        emojis = {}
        for expression_name, path in self.emoji_paths.items():
            emoji = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if emoji is not None:
                # Convert BGRA to BGR if needed
                if emoji.shape[2] == 4:
                    emoji = cv2.cvtColor(emoji, cv2.COLOR_BGRA2BGR)
                emojis[expression_name] = cv2.resize(emoji, (200, 200))
            else:
                print(f"Warning: Could not load emoji {path}")
        return emojis

    def _get_emotion_emoji(self, emotion):
        return self.emoji_icons.get(emotion, self.blank_image)

    def process_frame(self) -> Optional[EmotionResult]:
        """Process the input and output the relevant emoji"""
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Detect emotions in the frame
        emotion_data = self.detector.detect_emotions(frame)

        # Default to neutral emoji if no emotions are detected
        emoji_img = self.blank_image

        if emotion_data:
            # Process each detected face and find the dominant emotion
            for face in emotion_data:
                emotions = face["emotions"]
                dominant_emotion = max(emotions, key=emotions.get)

                # Get the corresponding emoji for the dominant emotion
                emoji_img = self._get_emotion_emoji(dominant_emotion)

                # Display the detected emotion on the frame
                cv2.putText(frame, f"Emotion: {dominant_emotion}",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2)

        return EmotionResult(main_frame=frame, emoji=emoji_img)

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
