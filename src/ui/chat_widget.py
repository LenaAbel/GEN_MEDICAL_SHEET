from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt, QTimer
from models.message import Role
from ui.styles import CHAT_WIDGET_STYLE, USER_BUBBLE_STYLE, ASSISTANT_BUBBLE_STYLE
from ui.markdown import Markdown


class ChatWidget(QScrollArea):
    """Scrollable chat widget displaying conversation as message bubbles."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_scroll_area()
        self._setup_message_container()
        self._streaming_label: Markdown | None = None

    # ==================== SETUP ====================

    def _setup_scroll_area(self) -> None:
        """Configure scroll area properties."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(CHAT_WIDGET_STYLE)

    def _setup_message_container(self) -> None:
        """Create container for message bubbles."""
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.addStretch()
        self._layout.setSpacing(4)
        self._layout.setContentsMargins(0, 20, 0, 20)
        self.setWidget(self._container)

    # ==================== PUBLIC METHODS ====================

    def add_message(self, text: str, role: Role) -> None:
        """Add a complete message bubble to the chat."""
        bubble = self._create_bubble(text, role)
        self._insert_bubble(bubble)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def start_streaming_message(self) -> None:
        """Create empty assistant bubble for streaming content."""
        bubble = QFrame()
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._streaming_label = Markdown("")
        layout.addWidget(self._streaming_label)
        
        bubble.setStyleSheet(ASSISTANT_BUBBLE_STYLE)
        self._streaming_label.setAlignment(Qt.AlignLeft)
        
        self._streaming_bubble = bubble
        self._streaming_text = ""
        self._insert_bubble(bubble)

    def append_streaming_chunk(self, chunk: str) -> None:
        """Append text chunk to streaming bubble (typewriter effect)."""
        if self._streaming_label:
            self._streaming_text += chunk
            self._streaming_label.set_markdown(self._streaming_text)
            QTimer.singleShot(10, self._scroll_to_bottom)

    def finish_streaming(self) -> None:
        """Mark streaming as complete and reset state."""
        self._streaming_label = None
        self._streaming_bubble = None
        self._streaming_text = ""

    # ==================== BUBBLE CREATION ====================

    def _create_bubble(self, text: str, role: Role) -> QFrame:
        """Create styled message bubble with markdown support."""
        bubble = QFrame()
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = Markdown(text)
        layout.addWidget(label)

        self._apply_bubble_style(bubble, label, role)
        return bubble

    def _apply_bubble_style(self, bubble: QFrame, label: Markdown, role: Role) -> None:
        """Apply style based on message role."""
        if role == Role.USER:
            bubble.setStyleSheet(USER_BUBBLE_STYLE)
            label.setAlignment(Qt.AlignRight)
        else:
            bubble.setStyleSheet(ASSISTANT_BUBBLE_STYLE)
            label.setAlignment(Qt.AlignLeft)

    # ==================== LAYOUT MANAGEMENT ====================

    def _insert_bubble(self, bubble: QFrame) -> None:
        """Insert bubble above the stretch spacer."""
        insert_position = self._layout.count() - 1
        self._layout.insertWidget(insert_position, bubble)

    def _scroll_to_bottom(self) -> None:
        """Scroll to show latest message."""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
