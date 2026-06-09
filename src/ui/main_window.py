from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

from ui.chat_widget import ChatWidget
from ui.spinner import LoadingSpinner
from ui.styles import (
    MAIN_WINDOW_STYLE, INPUT_FIELD_STYLE, SEND_BUTTON_STYLE,
    HEADER_STYLE, LOGO_STYLE, DISCLAIMER_STYLE, NEW_CONVERSATION_BUTTON_STYLE
)
from services.mistral_service import MistralService
from services.mistral_request_thread import MistralRequestThread
from models.message import Role
from ui.responsive import main_window_metrics


# ==== CONSTANTS ====
WINDOW_TITLE = "Générateur de Fiche Médicale - CHU Besançon"
WINDOW_MIN_SIZE = (760, 560)
INPUT_MAX_HEIGHT = 100
LOGO_HEIGHT = 40
SEND_BUTTON_SIZE = 36

ASSETS_DIR = Path(__file__).parent / "img"
LOGO_PATH = ASSETS_DIR / "chu_logo.svg"
SEND_ICON_PATH = ASSETS_DIR / "send_icon.svg"


class MainWindow(QMainWindow):
    """Main chat window for Medical Sheet Generator."""

    def __init__(self) -> None:
        super().__init__()
        self._configure_window()
        self._mistral_service = MistralService()
        self._request_thread: MistralRequestThread | None = None
        self._conversation_session_id = 0
        self._setup_ui()

    # ==================== WINDOW CONFIGURATION ====================
    
    def _configure_window(self) -> None:
        """Set window title, size and theme."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

    # ==================== UI SETUP ====================

    def _setup_ui(self) -> None:
        """Build main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # UI sections
        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_chat_area(), stretch=1)
        main_layout.addWidget(self._create_input_area())
        self._apply_responsive_layout(self.width())

    # ==================== HEADER SECTION ====================

    def _create_header(self) -> QWidget:
        """Create header with CHU logo."""
        self._header = QWidget()
        self._header.setStyleSheet(HEADER_STYLE)
        
        layout = QHBoxLayout(self._header)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Logo on left
        self._logo_label = QLabel()
        self._logo_label.setStyleSheet(LOGO_STYLE)
        if LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH))
            scaled = pixmap.scaledToHeight(LOGO_HEIGHT, Qt.SmoothTransformation)
            self._logo_label.setPixmap(scaled)
        else:
            self._logo_label.setText("CHU")
        
        layout.addWidget(self._logo_label)
        layout.addStretch()

        self._new_conversation_button = QPushButton("+")
        self._new_conversation_button.setToolTip("Nouvelle conversation")
        self._new_conversation_button.setCursor(Qt.PointingHandCursor)
        self._new_conversation_button.setStyleSheet(NEW_CONVERSATION_BUTTON_STYLE)
        self._new_conversation_button.clicked.connect(self._start_new_conversation)
        layout.addWidget(self._new_conversation_button)
        
        return self._header

    # ==================== CHAT SECTION ====================

    def _create_chat_area(self) -> QWidget:
        """Create scrollable chat display area."""
        self._chat_widget = ChatWidget()
        return self._chat_widget

    # ==================== INPUT SECTION ====================

    def _create_input_area(self) -> QWidget:
        """Create message input area with spinner, text field and send button."""
        self._input_container = QWidget()
        
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
        self._send_button.clicked.connect(self._on_send_clicked)
        
        layout.addWidget(self._input_field)
        layout.addWidget(self._send_button)
        
        main_layout.addLayout(layout)
        self._apply_responsive_layout(self.width())
        
        return self._input_container

    # ==================== EVENT HANDLERS ====================

    def _on_send_clicked(self) -> None:
        """Handle send button click."""
        user_message = self._input_field.toPlainText().strip()
        if not user_message:
            return

        conversation_id = self._conversation_session_id

        # Display user message and clear input
        self._chat_widget.add_message(user_message, Role.USER)
        self._input_field.clear()
        self._send_button.setEnabled(False)
        
        # Show loading spinner and prepare streaming bubble
        self._spinner.start()
        self._chat_widget.start_streaming_message()

        # Start background API request with streaming
        self._request_thread = MistralRequestThread(self._mistral_service, user_message)
        self._request_thread.chunk_received.connect(
            lambda chunk, cid=conversation_id: self._on_chunk_received(cid, chunk)
        )
        self._request_thread.stream_finished.connect(
            lambda cid=conversation_id: self._on_stream_finished(cid)
        )
        self._request_thread.error_occurred.connect(
            lambda error_message, cid=conversation_id: self._on_error(cid, error_message)
        )
        self._request_thread.finished.connect(
            lambda cid=conversation_id: self._on_thread_finished(cid)
        )
        self._request_thread.start()

    def _on_chunk_received(self, conversation_id: int, chunk: str) -> None:
        """Handle incoming text chunk (typewriter effect)."""
        if conversation_id != self._conversation_session_id:
            return
        # Hide spinner after first chunk arrives
        self._spinner.stop()
        # Streaming chunk for typewriter effect
        self._chat_widget.append_streaming_chunk(chunk)

    def _on_stream_finished(self, conversation_id: int) -> None:
        """Handle end of streaming."""
        if conversation_id != self._conversation_session_id:
            return
        self._chat_widget.finish_streaming()
        self._send_button.setEnabled(True)

    def _on_error(self, conversation_id: int, error_message: str) -> None:
        """Handle API error."""
        if conversation_id != self._conversation_session_id:
            return
        self._spinner.stop()
        self._chat_widget.finish_streaming()
        QMessageBox.warning(self, "API Error", error_message)
        self._send_button.setEnabled(True)

    def _on_thread_finished(self, conversation_id: int) -> None:
        """Clean up thread connections after completion."""
        if conversation_id != self._conversation_session_id:
            return
        self._request_thread = None

    def _start_new_conversation(self) -> None:
        """Reset the UI and AI history for a fresh conversation."""
        self._conversation_session_id += 1
        self._request_thread = None
        self._spinner.stop()
        self._send_button.setEnabled(True)
        self._input_field.clear()
        self._chat_widget.clear_conversation()
        self._mistral_service.clear_history()

    def resizeEvent(self, event) -> None:
        """Keep the main view proportions comfortable as the window changes."""
        super().resizeEvent(event)
        self._apply_responsive_layout(event.size().width())

    def _apply_responsive_layout(self, width: int) -> None:
        """Update the main window spacing and control sizes for the current width."""
        metrics = main_window_metrics(width)

        if hasattr(self, "_header"):
            self._header.setMinimumHeight(metrics.header_height)
            header_layout = self._header.layout()
            if header_layout is not None:
                header_layout.setContentsMargins(*metrics.header_margins)

        if hasattr(self, "_logo_label") and LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH))
            self._logo_label.setPixmap(pixmap.scaledToHeight(metrics.logo_height, Qt.SmoothTransformation))

        if hasattr(self, "_input_container"):
            input_layout = self._input_container.layout()
            if input_layout is not None:
                input_layout.setContentsMargins(*metrics.input_margins)
                input_layout.setSpacing(metrics.input_spacing)

        if hasattr(self, "_disclaimer"):
            self._disclaimer.setWordWrap(True)

        if hasattr(self, "_input_field"):
            self._input_field.setMaximumHeight(metrics.input_max_height)

        if hasattr(self, "_send_button"):
            self._send_button.setFixedSize(metrics.send_button_size, metrics.send_button_size)

        if hasattr(self, "_spinner"):
            self._spinner.set_size(metrics.spinner_size)
