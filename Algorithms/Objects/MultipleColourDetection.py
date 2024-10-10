# https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/

import numpy as np
import cv2
import csv

# Function to load colour ranges and BGR values from CSV file
def load_colour_ranges(csv_file):
    colour_ranges = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            colour_ranges.append({
                'colour': row['colour'],
                'lower': np.array([int(row['h_min']), int(row['s_min']), int(row['v_min'])], np.uint8),
                'upper': np.array([int(row['h_max']), int(row['s_max']), int(row['v_max'])], np.uint8),
                'bgr': (int(row['B']), int(row['G']), int(row['R']))  # Use BGR values from CSV
            })
    return colour_ranges

# Load colour ranges from CSV
colour_ranges = load_colour_ranges('../../Datasets/colour_ranges.csv')

# Capturing video through webcam
webcam = cv2.VideoCapture(0)

# Start a while loop
while True:
    # Reading the video from the webcam in image frames
    _, imageFrame = webcam.read()

    # Convert the imageFrame in BGR to HSV colour space
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # Kernel for morphological transformation (dilation)
    kernel = np.ones((5, 5), "uint8")

    # Iterate over the colour ranges loaded from CSV
    for colour in colour_ranges:
        # Create the mask for the colour
        mask = cv2.inRange(hsvFrame, colour['lower'], colour['upper'])
        mask = cv2.dilate(mask, kernel)
        res = cv2.bitwise_and(imageFrame, imageFrame, mask=mask)

        # Find contours to detect shapes of the colour
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 300:  # Only track larger objects
                x, y, w, h = cv2.boundingRect(contour)
                imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), color['bgr'], 2)

                # Display the name of the colour
                cv2.putText(imageFrame, f"{color['color']} Colour", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, color['bgr'])

    # Display the frame with the detected colours
    cv2.imshow("Multiple Colour Detection in Real-Time", imageFrame)

    # Terminate the program when 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break
