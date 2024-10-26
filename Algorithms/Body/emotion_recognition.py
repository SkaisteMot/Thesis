"""Emotion Recogntion and displaying emoji in seperate window"""
import cv2
from fer import FER

# Initialize the FER detector
detector = FER()

# Load emojis for each emotion
emoji_dict = {
    'happy': cv2.imread("../../Datasets/Emojis/happy.png"),
    'sad': cv2.imread("../../Datasets/Emojis/sad.png"),
    'angry': cv2.imread("../../Datasets/Emojis/angry.png"),
    'surprise': cv2.imread("../../Datasets/Emojis/surprised.png"),
    'fear': cv2.imread("../../Datasets/Emojis/fear.png"),
    'neutral': cv2.imread("../../Datasets/Emojis/neutral.png"),
    'disgust': cv2.imread("../../Datasets/Emojis/disgust.png"),
}

def recognize_emotion(emotion):
    """Recognize emotion and return image"""
    return emoji_dict[emotion]

# Start video capture from the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Detect emotions in the frame
    emotion_data = detector.detect_emotions(frame)

    if emotion_data:
        # Process each detected face and find the dominant emotion
        for face in emotion_data:
            emotions = face["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)

            emoji_img=recognize_emotion(dominant_emotion)

            if emoji_img is not None:
                cv2.imshow('Emoji', emoji_img)


    # Display the detected emotion on the frame
    cv2.putText(frame, f"Emotion: {dominant_emotion}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 255, 255), 2)

    # Display the frame with the detected emotion
    cv2.imshow("Emotion Recognition", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
