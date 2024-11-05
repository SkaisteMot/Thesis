"""
https://medium.com/the-click-reader/semantic-and-instance-segmentation-on-videos-using-pixellib-in-python-41b578d012b9
https://pixellib.readthedocs.io/en/latest/video_instance.html#
https://stackoverflow.com/questions/78564241/problem-with-loading-h5-weights-into-modellib-maskrcnn-model
"""
import cv2
import torch
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet101, DeepLabV3_ResNet101_Weights
from PIL import Image

# Load the pretrained DeepLabV3 model from torchvision
weights = DeepLabV3_ResNet101_Weights.COCO_WITH_VOC_LABELS_V1
model = deeplabv3_resnet101(weights=weights)
model.eval()

preprocess = weights.transforms()

input_video_path = "../../Datasets/pplWalking2.mp4"
cap = cv2.VideoCapture(input_video_path)

# Class index for "person" in COCO dataset
PERSON_CLASS_INDEX = 15

# Counter for frames processed
frame_counter = 0

# Process the video frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Increment the frame counter
    frame_counter += 1

    # Process only every 10th frame
    if frame_counter % 10 == 0:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        input_tensor = preprocess(frame_pil).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)['out'][0]
        output_predictions = output.argmax(0).cpu().numpy()

        person_mask = (output_predictions == PERSON_CLASS_INDEX).astype('uint8') * 255
        mask_colored = cv2.applyColorMap(person_mask, cv2.COLORMAP_JET)
        mask_colored_resized = cv2.resize(mask_colored, (frame.shape[1], frame.shape[0]))
        translucent_mask = cv2.addWeighted(frame, 0.7, mask_colored_resized, 0.5, 0)

        cv2.imshow("Segmented Frame", translucent_mask)
    else:
        # Just display the original frame for the frames not processed
        cv2.imshow("Segmented Frame", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
