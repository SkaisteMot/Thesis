"""
Colour detection

Code from:
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/
"""
import cv2
import pandas as pd
import numpy as np

class ColourRecogniser:
    """Colour Recogniser called by UI"""
    def __init__(self, colour_ranges_csv):
        self.colour_ranges = self.load_colour_ranges(colour_ranges_csv)
        self.bgr_colour_dict = {
            'red': (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255),
            "orange": (0, 165, 255),
            "purple": (128, 0, 128),
            "pink":(203,192,255)
         }

    def load_colour_ranges(self, csv_file):
        """load predefined hsv colour range from csv file"""
        colour_data = pd.read_csv(csv_file)
        colours = {}
        for _, row in colour_data.iterrows():
            colours[row['colour']] = (
                [row['h_min'], row['s_min'], row['v_min']],
                [row['h_max'], row['s_max'], row['v_max']]
            )
        return colours

    def create_mask(self, hsv_img, lower, upper):
        """mask to only show colours in predefined ranges"""
        return cv2.inRange(hsv_img, lower, upper)

    def draw_bounding_box(self, image, contour, colour):
        """draw boxes around detected colours"""
        x, y, w, h = cv2.boundingRect(contour)
        box_color = self.bgr_colour_dict.get(colour, (0, 0, 0))
        cv2.rectangle(image, (x, y), (x + w, y + h), box_color, 2, lineType=cv2.LINE_AA)
        cv2.putText(image, colour, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

    def count_colours(self, image, contours, colour, min_area):
        """count borders to check the amount for each colour"""
        colour_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                colour_count += 1
                self.draw_bounding_box(image, contour, colour)
        return colour_count

    def display_colour_counts(self, image, colour_counts):
        """display the colour and its count """
        y_offset = 30
        for i, (colour, count) in enumerate(colour_counts.items()):
            cv2.putText(image, f"{colour}: {count}", (10, y_offset + i * 20),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    def detect_and_draw(self, image, min_area=300):
        """Main can change min area depending on scene"""
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        colour_counts = {}
        for colour, (lower, upper) in self.colour_ranges.items():
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")
            mask = self.create_mask(hsv_img, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            colour_counts[colour] = self.count_colours(image, contours, colour, min_area)
        self.display_colour_counts(image, colour_counts)
        return image
