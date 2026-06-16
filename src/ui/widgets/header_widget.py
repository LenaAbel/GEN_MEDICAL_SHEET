from pathlib import Path

from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from config.constants import (
    ASSETS_DIR,
    HEADER_ACTION_BUTTON_SIZE,
    HEADER_ACTION_ICON_SIZE,
    NEW_CONVERSATION_ICON_PATH,
    RECORD_ICON_PATH,
)
from ui.widgets.spinner import LoadingSpinner
from ui.style.styles import (
    HEADER_STYLE,
    LOGO_STYLE,
    NEW_CONVERSATION_BUTTON_STYLE,
    TRANSCRIPTION_BUTTON_STYLE,
    TRANSCRIPTION_TIMER_STYLE,
)


LOGO_HEIGHT = 40

LOGO_PATH = ASSETS_DIR / "chu_logo.svg"


class HeaderWidget(QWidget):
    """Header containing the CHU logo and conversation actions."""

    transcription_toggled = Signal()
    new_conversation_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(HEADER_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)

        # Logo on left
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet(LOGO_STYLE)
        if LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH))
            scaled = pixmap.scaledToHeight(LOGO_HEIGHT, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("CHU")

        layout.addWidget(self.logo_label)
        layout.addStretch()

        self.audio_spinner = LoadingSpinner(self, size=20)
        layout.addWidget(self.audio_spinner)

        self.transcription_timer_label = QLabel("Enregistrement 00:00")
        self.transcription_timer_label.setStyleSheet(TRANSCRIPTION_TIMER_STYLE)
        self.transcription_timer_label.hide()
        layout.addWidget(self.transcription_timer_label)

        self.transcription_button = self._build_transcription_button()
        self.transcription_button.clicked.connect(self.transcription_toggled.emit)
        layout.addWidget(self.transcription_button)

        self.new_conversation_button = self._build_new_conversation_button()
        self.new_conversation_button.clicked.connect(
            self.new_conversation_requested.emit
        )
        layout.addWidget(self.new_conversation_button)

        self._logo_label = self.logo_label
        self._audio_spinner = self.audio_spinner
        self._transcription_timer_label = self.transcription_timer_label
        self._transcription_button = self.transcription_button
        self._new_conversation_button = self.new_conversation_button

    def _build_transcription_button(self) -> QPushButton:
        """Create the icon-only audio recording action."""
        return self._build_header_action_button(
            accessible_name="Enregistrer l'audio",
            tooltip="Démarrer un enregistrement audio",
            status_tip="Démarrer un enregistrement audio",
            stylesheet=TRANSCRIPTION_BUTTON_STYLE,
            icon_path=RECORD_ICON_PATH,
            fallback_text="●",
        )

    def _build_new_conversation_button(self) -> QPushButton:
        """Create the icon-only new conversation action."""
        return self._build_header_action_button(
            accessible_name="Nouvelle conversation",
            tooltip="Démarrer une nouvelle conversation",
            status_tip="Démarrer une nouvelle conversation",
            stylesheet=NEW_CONVERSATION_BUTTON_STYLE,
            icon_path=NEW_CONVERSATION_ICON_PATH,
            fallback_text="+",
        )

    def _build_header_action_button(
        self,
        accessible_name: str,
        tooltip: str,
        status_tip: str,
        stylesheet: str,
        icon_path: Path,
        fallback_text: str,
    ) -> QPushButton:
        """Create a consistently sized header icon button."""
        button = QPushButton()
        button.setAccessibleName(accessible_name)
        button.setAccessibleDescription(tooltip)
        button.setToolTip(tooltip)
        button.setStatusTip(status_tip)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(HEADER_ACTION_BUTTON_SIZE, HEADER_ACTION_BUTTON_SIZE)
        button.setStyleSheet(stylesheet)

        if icon_path.exists():
            button.setIcon(QIcon(str(icon_path)))
            button.setIconSize(QSize(HEADER_ACTION_ICON_SIZE, HEADER_ACTION_ICON_SIZE))
        else:
            button.setText(fallback_text)

        return button
