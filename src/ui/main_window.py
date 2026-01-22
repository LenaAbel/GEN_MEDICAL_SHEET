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
    HEADER_STYLE, LOGO_STYLE
)
from services.mistral_service import MistralService
from services.mistral_request_thread import MistralRequestThread
from models.message import Role


# ==== CONSTANTS ====
WINDOW_TITLE = "Medical Sheet Generator"
WINDOW_MIN_SIZE = (900, 700)
INPUT_MAX_HEIGHT = 100
LOGO_HEIGHT = 40
HEADER_HEIGHT = 60
SEND_BUTTON_SIZE = 36

# Asset paths
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

    # ==================== HEADER SECTION ====================

    def _create_header(self) -> QWidget:
        """Create header with CHU logo."""
        header = QWidget()
        header.setStyleSheet(HEADER_STYLE)
        header.setFixedHeight(HEADER_HEIGHT)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Logo on left
        logo_label = QLabel()
        logo_label.setStyleSheet(LOGO_STYLE)
        if LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH))
            scaled = pixmap.scaledToHeight(LOGO_HEIGHT, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled)
        else:
            logo_label.setText("CHU")
        
        layout.addWidget(logo_label)
        layout.addStretch()
        
        return header

    # ==================== CHAT SECTION ====================

    def _create_chat_area(self) -> QWidget:
        """Create scrollable chat display area."""
        self._chat_widget = ChatWidget()
        return self._chat_widget

    # ==================== INPUT SECTION ====================

    def _create_input_area(self) -> QWidget:
        """Create message input area with spinner, text field and send button."""
        container = QWidget()
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(60, 15, 60, 20)
        layout.setSpacing(12)
        
        # Loading spinner (left of input)
        self._spinner = LoadingSpinner(container)
        layout.addWidget(self._spinner)
        
        # Text input field
        self._input_field = QTextEdit()
        self._input_field.setMaximumHeight(INPUT_MAX_HEIGHT)
        self._input_field.setPlaceholderText("Send a message...")
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
        
        return container

    # ==================== EVENT HANDLERS ====================

    def _on_send_clicked(self) -> None:
        """Handle send button click."""
        user_message = self._input_field.toPlainText().strip()
        if not user_message:
            return

        # Display user message and clear input
        self._chat_widget.add_message(user_message, Role.USER)
        self._input_field.clear()
        self._send_button.setEnabled(False)
        
        # Show loading spinner and prepare streaming bubble
        self._spinner.start()
        self._chat_widget.start_streaming_message()

        # Start background API request with streaming
        self._request_thread = MistralRequestThread(self._mistral_service, user_message)
        self._request_thread.chunk_received.connect(self._on_chunk_received)
        self._request_thread.stream_finished.connect(self._on_stream_finished)
        self._request_thread.error_occurred.connect(self._on_error)
        self._request_thread.finished.connect(self._on_thread_finished)
        self._request_thread.start()

    def _on_chunk_received(self, chunk: str) -> None:
        """Handle incoming text chunk (typewriter effect)."""
        # Hide spinner after first chunk arrives
        self._spinner.stop()
        self._chat_widget.append_streaming_chunk(chunk)

    def _on_stream_finished(self) -> None:
        """Handle end of streaming."""
        self._chat_widget.finish_streaming()
        self._send_button.setEnabled(True)

    def _on_error(self, error_message: str) -> None:
        """Handle API error."""
        self._spinner.stop()
        self._chat_widget.finish_streaming()
        QMessageBox.warning(self, "API Error", error_message)
        self._send_button.setEnabled(True)

    def _on_thread_finished(self) -> None:
        """Clean up thread connections after completion."""
        if self._request_thread:
            self._request_thread.chunk_received.disconnect(self._on_chunk_received)
            self._request_thread.stream_finished.disconnect(self._on_stream_finished)
            self._request_thread.error_occurred.disconnect(self._on_error)
            self._request_thread.finished.disconnect(self._on_thread_finished)
            self._request_thread = None
