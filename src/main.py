import sys
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    load_dotenv()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
