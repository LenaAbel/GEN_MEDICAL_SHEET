from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.constants import (
    INPUT_MAX_HEIGHT,
    RECORD_ICON_PATH,
    SEND_BUTTON_SIZE,
    SEND_ICON_PATH,
)
from ui.widgets.spinner import LoadingSpinner
from ui.style.styles import (
    AUDIO_CONTEXT_BADGE_STYLE,
    DISCLAIMER_STYLE,
    INPUT_FIELD_STYLE,
    SEND_BUTTON_STYLE,
)


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

        self._audio_context_badge = QFrame()
        self._audio_context_badge.setObjectName("audioContextBadge")
        self._audio_context_badge.setStyleSheet(AUDIO_CONTEXT_BADGE_STYLE)
        self._audio_context_badge.setVisible(False)
        badge_layout = QHBoxLayout(self._audio_context_badge)
        badge_layout.setContentsMargins(10, 6, 10, 6)
        badge_layout.setSpacing(6)

        self._audio_context_icon = QLabel()
        self._audio_context_icon.setFixedSize(14, 14)
        if RECORD_ICON_PATH.exists():
            pixmap = QPixmap(str(RECORD_ICON_PATH))
            self._audio_context_icon.setPixmap(
                pixmap.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self._audio_context_icon.setText("Audio")
        badge_layout.addWidget(self._audio_context_icon)

        self._audio_context_label = QLabel("Audio pré-op ajouté")
        badge_layout.addWidget(self._audio_context_label)
        main_layout.addWidget(self._audio_context_badge, alignment=Qt.AlignLeft)

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

    def show_audio_context_badge(self) -> None:
        """Show that structured audio data is attached to the chat context."""
        self._audio_context_badge.setVisible(True)

    def hide_audio_context_badge(self) -> None:
        """Hide the structured audio context indicator."""
        self._audio_context_badge.setVisible(False)
