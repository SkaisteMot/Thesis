from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
from fer import FER

@dataclass
class EmotionResult:
    main_frame: np.ndarray
    emoji: np.ndarray
    emotion_text: str

class EmotionRecognizer:
    """
    Emotion recognizer class called by the UI
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
                if emoji.shape[2] == 4:
                    emoji = cv2.cvtColor(emoji, cv2.COLOR_BGRA2BGR)
                emojis[expression_name] = cv2.resize(emoji, (200, 200))
            else:
                print(f"Warning: Could not load emoji {path}")
        return emojis

    def _get_emotion_emoji(self, emotion):
        return self.emoji_icons.get(emotion, self.blank_image)

    def _compare_faces(self, face1, face2):
        """
        Compare two faces by checking if their bounding boxes are exactly the same
        """
        return (face1['box'] == face2['box']).all()

    def process_frame(self) -> Optional[EmotionResult]:
        """Process the input and output the relevant emoji"""
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.resize(frame, (960, 540))
        
        emotion_data = self.detector.detect_emotions(frame)
        emoji_img = self.blank_image
        dominant_emotion = "Neutral"

        if emotion_data:
            try:
                largest_face = max(emotion_data, key=lambda x: x['box'][2] * x['box'][3])
                emotions = largest_face["emotions"]
                box = largest_face["box"]
                dominant_emotion = max(emotions, key=emotions.get)
                emoji_img = self._get_emotion_emoji(dominant_emotion)
                
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                for face in emotion_data:
                    if not self._compare_faces(face, largest_face):
                        x, y, w, h = face['box']
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

                cv2.putText(frame, f"Emotion: {dominant_emotion}",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2)
            except Exception as e:
                print(f"Error processing emotion data: {e}")
                emoji_img = self.blank_image
                dominant_emotion = "Unknown"
        
        return EmotionResult(main_frame=frame, emoji=emoji_img, emotion_text=dominant_emotion)

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
