# https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/

from cv2 import cv2
import numpy as np
import pandas as pd

# Load the colour ranges from the CSV file
def load_colour_ranges(csv_file):
    colour_data = pd.read_csv(csv_file)
    colour_ranges = {}
    for _, row in colour_data.iterrows():
        colour_ranges[row['colour']] = (
            [row['h_min'], row['s_min'], row['v_min']],
            [row['h_max'], row['s_max'], row['v_max']]
        )
    return colour_ranges

# Load colour ranges from CSV file
colour_ranges = load_colour_ranges('../../Datasets/colour_ranges.csv')

# Use all colours from the CSV file
selected_colours = list(colour_ranges.keys())

# Function to detect colours and draw bounding boxes with colour names
def detect_and_draw(image, colour_ranges, selected_colours, min_area=300):
    # Convert the image to HSV format
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for colour in selected_colours:
        lower, upper = colour_ranges[colour]
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # Create a mask for the selected colour
        mask = cv2.inRange(hsv_img, lower, upper)

        # Find contours (these will be the detected objects)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw bounding boxes around detected colours with a black line
        for contour in contours:
            area = cv2.contourArea(contour)  # Calculate the area of the contour

            if area > min_area:  # Check if the area is above the minimum threshold
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2, lineType=cv2.LINE_AA)
                # Display the colour name above the bounding box
                cv2.putText(image, colour, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    return image

# Initialize video capture (0 is the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

try:
    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break

        # Detect and draw bounding boxes for selected colours
        result_frame = detect_and_draw(frame, colour_ranges, selected_colours, min_area=300)

        # Show the result
        cv2.imshow("Detected Colours", result_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print(f"Error: {e}")
finally:
    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
