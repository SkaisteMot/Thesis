def load_stylesheet(window,styleSheetPath):
        """Load the stylesheet for the page."""
        with open(styleSheetPath, "r") as file:
            window.setStyleSheet(file.read())

def close_event(event,recogniser):
    """handle close event to release resources"""
    recogniser.release()
    event.accept()