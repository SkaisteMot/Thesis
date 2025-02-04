def load_stylesheet(window,styleSheetPath):
        """Load the stylesheet for the page."""
        with open(styleSheetPath, "r") as file:
            window.setStyleSheet(file.read())

def close_event(event, widget):
    """Handle cleanup when closing a page"""
    if hasattr(widget, "cap"):  # Ensure widget has a video capture instance
        widget.cap.release()
    if hasattr(widget, "timer"):  # Stop the timer if it exists
        widget.timer.stop()
    event.accept()