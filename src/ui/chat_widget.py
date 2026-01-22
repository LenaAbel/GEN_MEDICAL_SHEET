from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt, QTimer
from models.message import Role
from ui.styles import CHAT_WIDGET_STYLE, USER_BUBBLE_STYLE, ASSISTANT_BUBBLE_STYLE
from ui.markdown import MarkdownLabel


class ChatWidget(QScrollArea):
    """Scrollable chat widget displaying conversation as message bubbles."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_scroll_area()
        self._setup_message_container()

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
        """Add a message bubble to the chat."""
        bubble = self._create_bubble(text, role)
        self._insert_bubble(bubble)
        QTimer.singleShot(10, self._scroll_to_bottom)

    # ==================== BUBBLE CREATION ====================

    def _create_bubble(self, text: str, role: Role) -> QFrame:
        """Create styled message bubble with markdown support."""
        bubble = QFrame()
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use MarkdownLabel for rich text rendering
        label = MarkdownLabel(text)
        layout.addWidget(label)

        self._apply_bubble_style(bubble, label, role)
        return bubble

    def _apply_bubble_style(self, bubble: QFrame, label: MarkdownLabel, role: Role) -> None:
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
