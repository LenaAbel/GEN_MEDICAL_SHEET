from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.spinner import LoadingSpinner
from ui.styles import DISCLAIMER_STYLE, INPUT_FIELD_STYLE, SEND_BUTTON_STYLE


INPUT_MAX_HEIGHT = 100
SEND_BUTTON_SIZE = 36

ASSETS_DIR = Path(__file__).parent / "img"
SEND_ICON_PATH = ASSETS_DIR / "send_icon.svg"


class InputWidget(QWidget):
    """Message input area with disclaimer, spinner, text field, and send button."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._input_container = self

        main_layout = QVBoxLayout(self._input_container)
        main_layout.setContentsMargins(60, 15, 60, 20)
        main_layout.setSpacing(8)

        # Disclaimer text
        self._disclaimer = QLabel("⚠ L'IA peut halluciner. Vérifiez toujours les informations importantes.")
        self._disclaimer.setWordWrap(True)
        self._disclaimer.setStyleSheet(DISCLAIMER_STYLE)
        main_layout.addWidget(self._disclaimer)

        # Input controls layout
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Loading spinner
        self._spinner = LoadingSpinner(self._input_container)
        layout.addWidget(self._spinner)

        # Input text area for user messages
        self._input_field = QTextEdit()
        self._input_field.setMaximumHeight(INPUT_MAX_HEIGHT)
        self._input_field.setPlaceholderText("Envoyer votre message...")
        self._input_field.setStyleSheet(INPUT_FIELD_STYLE)

        # Send button with icon
        self._send_button = QPushButton()
        self._send_button.setStyleSheet(SEND_BUTTON_STYLE)
        self._send_button.setCursor(Qt.PointingHandCursor)
        self._send_button.setFixedSize(SEND_BUTTON_SIZE, SEND_BUTTON_SIZE)

        if SEND_ICON_PATH.exists():
            self._send_button.setIcon(QIcon(str(SEND_ICON_PATH)))
        else:
            self._send_button.setText("→")

        layout.addWidget(self._input_field)
        layout.addWidget(self._send_button)

        main_layout.addLayout(layout)

    def get_text(self) -> str:
        """Return the current input text."""
        return self._input_field.toPlainText()

    def clear(self) -> None:
        """Clear the input text."""
        self._input_field.clear()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the input field and send button."""
        self._input_field.setEnabled(enabled)
        self._send_button.setEnabled(enabled)
