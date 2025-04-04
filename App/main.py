import sys
from PyQt5.QtWidgets import QApplication
from pages.home_page import HomePage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home_page = HomePage()
    home_page.show()
    sys.exit(app.exec_())
