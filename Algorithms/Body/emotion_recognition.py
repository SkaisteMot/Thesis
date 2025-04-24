"""facial expression/emotion recognition algorithm"""
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
from fer import FER

@dataclass
class EmotionResult:
    """return the main frame from stream and the detected emotion text"""
    main_frame: np.ndarray
    emotion_text: str

class EmotionRecogniser:
    """
    Emotion recogniser class called by the UI
    """
    def __init__(self):
        self.detector = FER(mtcnn=True)
        self.cap = cv2.VideoCapture(0)

    def process_frame(self) -> Optional[EmotionResult]:
        """Process the input and return the relevant emotion"""
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.resize(frame, (960, 540))

        emotion_data = self.detector.detect_emotions(frame)
        dominant_emotion = "Neutral"

        if emotion_data:
            try:
                largest_face = max(emotion_data, key=lambda x: x['box'][2] * x['box'][3])
                emotions = largest_face["emotions"]
                box = largest_face["box"]
                dominant_emotion = max(emotions, key=emotions.get)

                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                cv2.putText(frame, f"Emotion: {dominant_emotion}",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2)
            except Exception as e:
                print(f"Error processing emotion data: {e}")
                dominant_emotion = "Unknown"

        return EmotionResult(main_frame=frame, emotion_text=dominant_emotion)

    def release(self):
        """release resources"""
        self.cap.release()
        cv2.destroyAllWindows()
