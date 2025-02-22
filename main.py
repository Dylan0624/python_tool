"""Entry point for the Converter application."""
#main.py
import sys
from PyQt6.QtWidgets import QApplication
from GUI.MainUI import MainUI


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()