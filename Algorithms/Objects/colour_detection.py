"""
Colour detection

Code from:
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/
"""
import sys
import cv2
import numpy as np
import pandas as pd

# Load the colour ranges from the CSV file
def load_colour_ranges(csv_file):
    """Load in CSV file of colours"""
    colour_data = pd.read_csv(csv_file)
    colours = {}
    for _, row in colour_data.iterrows():
        colours[row['colour']] = (
            [row['h_min'], row['s_min'], row['v_min']],
            [row['h_max'], row['s_max'], row['v_max']]
        )
    return colours

# Load colour ranges from CSV file
colour_ranges = load_colour_ranges('../../Datasets/colour_ranges.csv')

def create_mask(hsv_img, lower, upper):
    """Create a mask for the selected colour"""
    return cv2.inRange(hsv_img, lower, upper)

def draw_bounding_box(image, contour, colour):
    """Draw bounding box and label for detected colour"""
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2, lineType=cv2.LINE_AA)
    cv2.putText(image, colour, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

def count_colours(image, contours, colour, min_area):
    """Count detected colours based on contours"""
    colour_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            colour_count += 1
            draw_bounding_box(image, contour, colour)
    return colour_count

def display_colour_counts(image, colour_counts):
    """Display the counts of detected colours on the image"""
    y_offset = 30  # Start drawing from the top of the image
    for i, (colour, count) in enumerate(colour_counts.items()):
        cv2.putText(
            image,
            f"{colour}: {count}",
            (10, y_offset + i * 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )

def detect_and_draw(image, colours, min_area=300):
    """Detect colours and draw bounding boxes with colour names"""
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    colour_counts = {}  # Dictionary to store the count of each colour detected

    for colour, (lower, upper) in colours.items():
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # Create a mask for the selected colour
        mask = create_mask(hsv_img, lower, upper)

        # Find contours (these will be the detected objects)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Count detected colours
        colour_counts[colour] = count_colours(image, contours, colour, min_area)

    # Display the colour counts at the top left of the image
    display_colour_counts(image, colour_counts)

    return image

# Initialize video capture (0 is the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    sys.exit()  # Use sys.exit() instead of exit()

try:
    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break

        # Detect and draw bounding boxes for selected colours
        result_frame = detect_and_draw(frame, colour_ranges, min_area=300)

        # Show the result
        cv2.imshow("Detected Colours", result_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:  # Catch all exceptions, but be cautious with this approach
    print(f"Error: {e}")
finally:
    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
