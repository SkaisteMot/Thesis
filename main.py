"""main file to start desktop application"""
import sys
from PyQt5.QtWidgets import QApplication
from App.pages.home_page import HomePage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home_page = HomePage()
    home_page.showMaximized()
    sys.exit(app.exec_())
