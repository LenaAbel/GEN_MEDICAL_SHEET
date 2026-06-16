from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ui.constants import ASSETS_DIR
from ui.spinner import LoadingSpinner
from ui.styles import (
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

        self.transcription_button = QPushButton("Enregistrer")
        self.transcription_button.setToolTip("Démarrer un enregistrement audio")
        self.transcription_button.setCursor(Qt.PointingHandCursor)
        self.transcription_button.setStyleSheet(TRANSCRIPTION_BUTTON_STYLE)
        self.transcription_button.clicked.connect(self.transcription_toggled.emit)
        layout.addWidget(self.transcription_button)

        self.new_conversation_button = QPushButton("+")
        self.new_conversation_button.setToolTip("Nouvelle conversation")
        self.new_conversation_button.setCursor(Qt.PointingHandCursor)
        self.new_conversation_button.setStyleSheet(NEW_CONVERSATION_BUTTON_STYLE)
        self.new_conversation_button.clicked.connect(
            self.new_conversation_requested.emit
        )
        layout.addWidget(self.new_conversation_button)

        self._logo_label = self.logo_label
        self._audio_spinner = self.audio_spinner
        self._transcription_timer_label = self.transcription_timer_label
        self._transcription_button = self.transcription_button
        self._new_conversation_button = self.new_conversation_button
